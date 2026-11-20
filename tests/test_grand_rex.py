from datetime import date
from pathlib import Path
from unittest import TestCase

from bs4 import BeautifulSoup

from concert_calendar.scrapers.grand_rex import parse_events


FIXTURE = Path(__file__).parent / "fixtures" / "grand_rex" / "programme.html"


class GrandRexTests(TestCase):
    def setUp(self):
        self.events = parse_events(
            BeautifulSoup(FIXTURE.read_text(), "html.parser"), today=date(2026, 9, 1)
        )

    def test_only_explicit_non_cancelled_concerts_are_accepted(self):
        self.assertEqual(
            ["JAMES BLAKE", "JAMES BLAKE", "SECOND CONCERT", "La Légende de Korra en Concert"],
            [e.headliner for e in self.events],
        )

    def test_multi_date_metadata(self):
        self.assertEqual(["2026-10-12", "2026-10-13"], [e.date for e in self.events[:2]])
        for event in self.events[:2]:
            self.assertEqual("20:00", event.start_time)
            self.assertEqual("sold_out", event.ticket_status)
            self.assertEqual("https://tickets.example/james", event.ticket_url)
            self.assertEqual("https://www.legrandrex.com/images/james.jpg", event.image_url)

    def test_generic_booking_search_uses_event_specific_official_url(self):
        self.assertEqual(
            "https://www.legrandrex.com/evenement/2", self.events[2].ticket_url
        )

    def test_explicit_full_concert_title_in_card_copy_is_preserved(self):
        self.assertEqual("La Légende de Korra en Concert", self.events[3].headliner)

    def test_empty_canonical_listing_tries_legacy_path(self):
        from unittest.mock import Mock, patch
        from concert_calendar.scrapers.grand_rex import load_events

        canonical = Mock(text="<html></html>")
        legacy = Mock(text=FIXTURE.read_text())
        session = Mock()
        session.get.side_effect = [canonical, legacy]

        with patch("concert_calendar.scrapers.grand_rex.requests.Session", return_value=session), \
             patch("concert_calendar.scrapers.grand_rex.parse_events", side_effect=lambda soup: parse_events(soup, today=date(2026, 9, 1))):
            events = load_events()

        self.assertGreater(len(events), 0)
        self.assertEqual(
            [call.args[0] for call in session.get.call_args_list],
            ["https://www.legrandrex.com/evenement", "https://www.legrandrex.com/evenement/"],
        )

    def test_canonical_listing_with_concerts_skips_legacy_path(self):
        from unittest.mock import Mock, patch
        from concert_calendar.scrapers.grand_rex import load_events

        session = Mock()
        session.get.return_value = Mock(text=FIXTURE.read_text())

        with patch("concert_calendar.scrapers.grand_rex.requests.Session", return_value=session), \
             patch("concert_calendar.scrapers.grand_rex.parse_events", side_effect=lambda soup: parse_events(soup, today=date(2026, 9, 1))):
            events = load_events()

        self.assertGreater(len(events), 0)
        self.assertEqual(session.get.call_count, 1)

    def test_redesigned_concert_cards_are_scraped_without_shows_or_date_ranges(self):
        html = """
        <main>
          <article class="carte carte--anis"><a class="carte__lien" href="/evenement/1">
            <span class="carte__categorie">Sport &amp; Aventure</span>
            <h3 class="carte__titre">THE SKI FILM</h3><span class="carte__date">08/01/2027</span>
          </a></article>
          <article class="carte carte--violet"><a class="carte__lien" href="/evenement/1780">
            <span class="carte__categorie">Concert</span>
            <div class="carte__affiche"><img src="/images/evenements/sofloyd.jpg"></div>
            <h3 class="carte__titre"><span class="carte__libelle">SO FLOYD</span></h3>
            <span class="carte__date">08/01/2027</span>
          </a></article>
          <article class="carte carte--violet"><a class="carte__lien" href="/evenement/1999">
            <span class="carte__categorie">Concert</span>
            <h3 class="carte__titre">DATE RANGE</h3>
            <span class="carte__date">du 08 au 09/01/2027</span>
          </a></article>
          <article class="carte carte--vert"><a class="carte__lien" href="/evenement/3">
            <span class="carte__categorie">Spectacle</span>
            <h3 class="carte__titre">STAND-UP SHOW</h3>
            <span class="carte__date">12/01/2027</span>
          </a></article>
        </main>
        """
        events = parse_events(BeautifulSoup(html, "html.parser"), today=date(2026, 11, 20))
        self.assertEqual(["SO FLOYD"], [e.headliner for e in events])
        self.assertEqual("2027-01-08", events[0].date)
        self.assertEqual("https://www.legrandrex.com/evenement/1780", events[0].ticket_url)
        self.assertEqual("https://www.legrandrex.com/images/evenements/sofloyd.jpg", events[0].image_url)
