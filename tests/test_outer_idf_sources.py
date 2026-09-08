import copy
import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

import requests
from bs4 import BeautifulSoup

from concert_calendar.automation import validate_source_report
from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent
from concert_calendar.scraper_loader import discover_scrapers_with_issues
from concert_calendar.scrapers import empreinte, le_plan, forum_vaureal
from concert_calendar.scrapers._official_mapado import entities, parse_detail, complete_members
from concert_calendar.sources import load_events_with_report
from concert_calendar.venues import normalize_event_venue

FIXTURE = Path(__file__).parent / "fixtures/outer_idf/official_extracts.json"
TODAY = date(2026, 9, 7)


class OuterIdfTests(TestCase):
    def setUp(self):
        self.pages = json.loads(FIXTURE.read_text())

    def get(self, url, **kwargs):
        self.assertEqual(30, kwargs["timeout"])
        return Mock(text=self.pages[url], raise_for_status=lambda: None)

    def mapado(self):
        listing = entities(self.pages[empreinte.PROGRAMME_URL])["ticketings"]["hydra:member"][0]
        detail = entities(self.pages[empreinte.PROGRAMME_URL + "event/" + listing["slug"]])
        return listing, detail

    def parse_mapado(self, listing, detail):
        return parse_detail(detail, listing, base_url=empreinte.PROGRAMME_URL,
                            venue=empreinte.SOURCE_NAME, city="Savigny-le-Temple", department="77", today=TODAY)

    def forum(self):
        card = BeautifulSoup(self.pages[forum_vaureal.PROGRAMME_URL], "html.parser").select_one('a[aria-label="LES FATALS PICARDS"]')
        html = self.pages["https://leforum.cergypontoise.fr" + card["href"]]
        return card, json.loads(BeautifulSoup(html, "html.parser").script.text)

    def parse_forum(self, card, data):
        return forum_vaureal.parse_detail('<script type="application/ld+json">' + json.dumps(data) + '</script>', card, TODAY)

    def test_registration(self):
        modules, issues = discover_scrapers_with_issues()
        self.assertFalse(issues)
        for module in (empreinte, le_plan, forum_vaureal):
            self.assertEqual(1, modules.count(module))

    def test_official_loaders_fixture(self):
        with patch('requests.Session.get', side_effect=self.get):
            for module, count, city, dep in [(empreinte, 2, 'Savigny-le-Temple', '77'), (le_plan, 2, 'Ris-Orangis', '91')]:
                events = module.load_events(today=TODAY)
                self.assertEqual(count, len(events))
                for event in events:
                    self.assertEqual((city, dep), (event.city, event.department))
                    self.assertTrue(event.image_url.startswith('https://'))
                    self.assertTrue(event.ticket_url.startswith('https://'))
                    self.assertFalse(event.promoters)

    def test_flat_billing_not_invented(self):
        listing, detail = self.mapado()
        event = self.parse_mapado(listing, detail)[0]
        self.assertEqual('RONNIE ROMERO + GUS G', event.headliner)
        self.assertFalse(event.openers)
        self.assertFalse(event.co_headliners)

    def test_mapado_occurrences_not_end_range(self):
        listing, detail = self.mapado()
        dates = detail['eventDates']
        first = dates['hydra:member'][0]
        second = copy.deepcopy(first)
        second['startDate'] = '2026-10-07T22:00:00+02:00'
        dates['hydra:member'].append(second)
        dates['hydra:totalItems'] = 2
        first['endDate'] = '2026-10-08T01:00:00+02:00'
        events = self.parse_mapado(listing, detail)
        self.assertEqual(['20:00', '22:00'], [e.start_time for e in events])
        self.assertEqual(['2026-10-07'] * 2, [e.date for e in events])

    def test_mapado_past_and_cancelled(self):
        listing, detail = self.mapado()
        occurrence = detail['eventDates']['hydra:member'][0]
        occurrence['status'] = 'cancelled'
        self.assertEqual([], self.parse_mapado(listing, detail))
        occurrence['status'] = 'opened'
        occurrence['startDate'] = '2020-01-01T20:00:00+01:00'
        self.assertEqual([], self.parse_mapado(listing, detail))

    def test_explicit_category_and_status(self):
        listing, detail = self.mapado()
        listing['ticketingCategory'] = {'name': 'Concert - Rock,Punk'}
        detail['eventDates']['hydra:member'][0]['availabilityStatus'] = 'soldOut'
        event = self.parse_mapado(listing, detail)[0]
        self.assertEqual('Rock,Punk', event.genre)
        self.assertEqual('sold_out', event.ticket_status)
        listing['ticketingCategory'] = {'name': 'Atelier'}
        self.assertEqual([], self.parse_mapado(listing, detail))

    def test_postponed_mapado_occurrence_is_not_emitted(self):
        listing, detail = self.mapado()
        detail['eventDates']['hydra:member'][0]['status'] = 'postponed'
        self.assertEqual([], self.parse_mapado(listing, detail))

    def test_mapado_distinct_dates_are_explicit_not_inferred(self):
        listing, detail = self.mapado()
        dates = detail['eventDates']
        second = copy.deepcopy(dates['hydra:member'][0])
        second['startDate'] = '2026-10-09T20:00:00+02:00'
        dates['hydra:member'].append(second)
        dates['hydra:totalItems'] = 2
        self.assertEqual(['2026-10-07', '2026-10-09'], [e.date for e in self.parse_mapado(listing, detail)])

    def test_existing_editorial_hero_and_links_win_overlap(self):
        listing, detail = self.mapado()
        official = self.parse_mapado(listing, detail)[0]
        editorial = copy.deepcopy(official)
        editorial.image_url = 'https://electriceyerock.com/review-hero.jpg'
        editorial.image_source = 'Electric Eye concert review'
        editorial.electric_eye_links = [{'url': 'https://electriceyerock.com/review', 'artist': official.headliner}]
        for records in ([official, editorial], [editorial, official]):
            event = deduplicate_events(copy.deepcopy(records))[0]
            self.assertEqual(editorial.image_url, event.image_url)
            self.assertEqual(editorial.electric_eye_links, event.electric_eye_links)

    def test_incomplete_collection_fails_loudly(self):
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            complete_members({'hydra:member': [], 'hydra:totalItems': 3})

    def test_forum_billing_genre_and_sold_out(self):
        card, data = self.forum()
        event = self.parse_forum(card, data)[0]
        self.assertEqual('LES FATALS PICARDS + LOU AND THE BEGINNERS', event.headliner)
        self.assertFalse(event.openers)
        self.assertEqual('ROCK', event.genre)
        self.assertEqual('sold_out', event.ticket_status)

    def test_other_forum_and_offsite_not_relocated(self):
        card, data = self.forum()
        data['location']['address']['postalCode'] = '75001'
        self.assertEqual([], self.parse_forum(card, data))
        data['location']['address']['postalCode'] = '95490'
        data['location']['address'].pop('addressLocality')
        self.assertEqual([], self.parse_forum(card, data))

    def test_le_plan_both_rooms_keep_physical_venue_and_correct_swapped_geography(self):
        listing = entities(self.pages[le_plan.PROGRAMME_URL])['ticketings']['hydra:member']
        self.assertEqual({'Club', 'Grande Salle'}, {i['venue']['seatingName'] for i in listing})
        self.assertTrue(all(i['venue']['city'] == '91130' and i['venue']['zipCode'] == 'RIS-ORANGIS' for i in listing))
        with patch('requests.Session.get', side_effect=self.get):
            events = le_plan.load_events(today=TODAY)
        self.assertEqual({'Le Plan'}, {e.venue for e in events})
        self.assertEqual({'Ris-Orangis'}, {e.city for e in events})
        self.assertEqual({'91'}, {e.department for e in events})

    def test_forum_real_offsite_performances_use_explicit_venues(self):
        with patch('requests.Session.get', side_effect=self.get):
            events = forum_vaureal.load_events(today=TODAY)
        self.assertEqual(4, len(events))
        offsite = [e for e in events if e.venue != 'Le Forum']
        self.assertEqual(['2026-10-08', '2026-10-09', '2026-12-05'], [e.date for e in offsite])
        self.assertEqual(['Pontoise', 'Pontoise', 'CERGY'], [e.city for e in offsite])
        self.assertEqual(['Points Communs - Théâtre des Louvrais'] * 2 + ['Le Douze'], [e.venue for e in offsite])
        self.assertTrue(all(e.department == '95' and e.image_url and e.ticket_url for e in events))

    def test_forum_does_not_expand_unenumerated_or_inconsistent_ranges(self):
        item = {'startDate': '2026-10-08T20:00:00+02:00', 'endDate': '2026-10-09T23:00:00+02:00',
                'description': 'Rendez-vous les jeudi 8 et vendredi 9 octobre à 20h00'}
        self.assertEqual(['2026-10-08', '2026-10-09'], [x.date().isoformat() for x in forum_vaureal.performance_starts(item)])
        for text in ['du 8 au 9 octobre', 'les jeudi 8 et vendredi 9 octobre à 19h00', 'les lundi 8 et mardi 9 octobre à 20h00']:
            item['description'] = text
            with self.assertRaises(ValueError):
                forum_vaureal.performance_starts(item)

    def test_non_idf_forum_event_is_excluded(self):
        card, data = self.forum()
        data['location']['name'] = 'Explicit other venue'
        data['location']['address']['postalCode'] = '69001'
        self.assertEqual([], self.parse_forum(card, data))

    def test_forum_visible_full_bill_separate_from_event_wrapper(self):
        _, data = self.forum()
        data['name'] = 'A touring festival'
        card = BeautifulSoup('<div class="agenda--title"><span class="ssks-event-over-title">A touring festival</span>Band One + Band Two</div><div class="agenda--subtitle">+ Band Three</div>', 'html.parser')
        event = self.parse_forum(card, data)[0]
        self.assertEqual('Band One + Band Two + Band Three', event.headliner)
        self.assertEqual('A touring festival', event.event_title)
        self.assertFalse(event.openers)
        self.assertFalse(event.co_headliners)

    def test_forum_past_cancelled_and_multiday(self):
        card, data = self.forum()
        data['eventStatus'] = 'https://schema.org/EventCancelled'
        self.assertEqual([], self.parse_forum(card, data))
        data['eventStatus'] = ''
        data['endDate'] = '2026-09-13T22:00:00+02:00'
        with self.assertRaisesRegex(ValueError, 'multi-day'):
            self.parse_forum(card, data)
        data.pop('endDate')
        data['startDate'] = '2020-01-01T20:00:00+01:00'
        self.assertEqual([], self.parse_forum(card, data))

    def test_geography_and_metadata_overlap(self):
        a = ConcertEvent(date='2026-11-19', headliner='LAURA COX', venue="L'Empreinte", city='Paris', department='75', promoters=['VeryShow'], first_seen='2026-01-01T00:00:00Z', source_names=['VeryShow'], openers=['Support'])
        b = ConcertEvent(date=a.date, headliner=a.headliner, venue='L’Empreinte', city='Savigny-le-Temple', department='77', source_names=['L’Empreinte'], image_url='https://venue.example/art.jpg', image_source='L’Empreinte', ticket_url='https://venue.example/ticket')
        events = deduplicate_events([normalize_event_venue(a), normalize_event_venue(b)])
        self.assertEqual(1, len(events))
        e = events[0]
        self.assertEqual({'VeryShow', 'L’Empreinte'}, set(e.source_names))
        self.assertEqual('2026-01-01T00:00:00Z', e.first_seen)
        self.assertEqual(['Support'], e.openers)
        self.assertTrue(e.image_url)
        self.assertTrue(e.ticket_url)
        self.assertEqual(('Savigny-le-Temple', '77'), (e.city, e.department))
        other = copy.deepcopy(e)
        other.venue = 'Le Plan'
        self.assertEqual(2, len(deduplicate_events([e, other])))

    def test_failure_isolation_and_empty_protection(self):
        for failure in [False, True]:
            bad = SimpleNamespace(__name__='test.bad', SOURCE_NAME=empreinte.SOURCE_NAME, load_events=Mock(side_effect=requests.Timeout('offline')) if failure else Mock(return_value=[]))
            good = SimpleNamespace(__name__='test.good', SOURCE_NAME=le_plan.SOURCE_NAME, load_events=lambda: [ConcertEvent(date='2030-01-01', headliner='Synthetic', venue='Le Plan', city='Ris-Orangis', department='91')])
            with patch('concert_calendar.sources.discover_scrapers_with_issues', return_value=([bad, good], {})):
                events, report = load_events_with_report(scraper_attempts=1, retry_delay_seconds=0)
            self.assertEqual(1, len(events))
            self.assertEqual(2, len(report.source_health))
            with patch('concert_calendar.automation.CORE_SOURCES', {le_plan.SOURCE_NAME}):
                if failure:
                    self.assertIn(empreinte.SOURCE_NAME, report.source_failures)
                    validate_source_report(report)
                else:
                    with self.assertRaisesRegex(Exception, 'unexpectedly returned zero'):
                        validate_source_report(report)
