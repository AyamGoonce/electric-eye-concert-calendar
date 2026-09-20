import unittest
from datetime import date, datetime, timezone, timedelta
from bs4 import BeautifulSoup

from concert_calendar.billing_semantics import (
    apply_structured_performer_semantics,
)
from concert_calendar.event_state import canonical_event_identity, reconcile_state, build_change_report
from concert_calendar.deduplication import deduplicate_events, merge_events
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import prepare_upcoming_events
from concert_calendar.scrapers.gaite_lyrique import detail_performers
from concert_calendar.scrapers.nouveau_casino import parse_items
from concert_calendar.scrapers.machine_moulin_rouge import detail_performers as machine_performers
from concert_calendar.content_index import build_index, enrich_events
from concert_calendar.scrapers.sunset_sunside import parse_detail_payload
from concert_calendar.scrapers.new_morning import infer_performers_from_detail_html
from tests.clock_helpers import freeze_date
from tests.test_content_index import entry
from tests import test_trianon_sunset


def event(
    headliner,
    *,
    start_time=None,
    performers=None,
    event_title=None,
):
    return ConcertEvent(
        date="2027-01-01",
        headliner=headliner,
        venue="Example Venue",
        city="Paris",
        department="75",
        start_time=start_time,
        performers=performers,
        event_title=event_title,
    )


class CalendarBillingHardeningTests(unittest.TestCase):
    def finish_pipeline(self, events, names):
        index = build_index([entry(name + ' @ Example Hall, Paris - August 10th, 2026', ['Concert Review', name],
                                   '2026-08-' + str(10 + i),
                                   image='https://example.test/' + str(i) + '.jpg')
                             for i, name in enumerate(names)], generated_at='2026-09-20T00:00:00Z')
        events = deduplicate_events(events)
        enrich_events(events, index)
        state = reconcile_state(events, None, now=datetime(2026, 9, 20, tzinfo=timezone.utc))
        rows = prepare_upcoming_events(events, today=date(2026, 9, 20))
        return events, state, rows

    @freeze_date('concert_calendar.scrapers.sunset_sunside')
    def test_bruna_programme_source_to_content_state_and_export(self):
        title = 'Hommage à Chico Buarque avec Bruna Hetzel + jam Brésil'
        payload = test_trianon_sunset.SunsetSunsideScraperTests().payload([
            {'startDate': '2026-10-10T19:00:00+02:00'},
            {'startDate': '2026-10-10T21:00:00+02:00'},
        ], room='Sunside', title=title)
        payload['props']['pageProps']['entities']['ticketing']['description'] = 'La jam est animée par Bruna Hetzel.'
        parsed = parse_detail_payload(payload, 'https://example.test/bruna')
        events, state, rows = self.finish_pipeline(parsed, ['Bruna Hetzel', 'Chico Buarque'])
        self.assertEqual(2, len(rows))
        self.assertEqual(2, len(state['events']))
        self.assertEqual(2, len({row['i'] for row in rows}))
        for item, row in zip(events, rows):
            self.assertEqual('Bruna Hetzel', row['h'])
            self.assertEqual('Hommage à Chico Buarque + jam Brésil', row['et'])
            self.assertEqual(['Bruna Hetzel'], [link['name'] for link in item.electric_eye_links])
            self.assertEqual('Electric Eye concert review', item.image_source)

    def test_gaite_named_programme_individual_links(self):
        names = detail_performers('<h1>ARTE Dans le club So La Lune, Moha MMZ &amp; Surprise sont dans le club</h1>', 'ARTE Dans le club')
        item = event(
            'ARTE Dans le club',
            performers=names,
            event_title='ARTE Dans le club',
        )
        events, _, rows = self.finish_pipeline([item], ['So La Lune', 'Moha MMZ', 'Surprise'])
        self.assertEqual('So La Lune', rows[0]['h'])
        self.assertEqual(['Moha MMZ', 'Surprise'], rows[0]['ch'])
        self.assertEqual('ARTE Dans le club', rows[0]['et'])
        self.assertEqual(3, len(events[0].electric_eye_links))

    def test_new_morning_independent_names_survive_complete_pipeline(self):
        names, _ = infer_performers_from_detail_html(
            '<h2>Présentation</h2><strong>Ludivine Issambourg</strong><strong>Brian Jackson</strong><strong>Eric Legnini</strong>',
            'Jackson - Issambourg - Legnini')
        events, _, rows = self.finish_pipeline([event('Jackson - Issambourg - Legnini', performers=names)], names)
        self.assertEqual('Brian Jackson', rows[0]['h'])
        self.assertEqual(['Ludivine Issambourg', 'Eric Legnini'], rows[0]['ch'])
        self.assertEqual(3, len(events[0].electric_eye_links))

    def test_legacy_time_labelled_rows_migrate_without_new_or_removed(self):
        now = datetime(2026, 9, 20, tzinfo=timezone.utc)
        legacy = [event('Example Artist – 19h00', start_time='19:00'), event('Example Artist – 21h00', start_time='21:00')]
        state = reconcile_state(legacy, None, now=now)
        expected = {item.start_time: item._public_id for item in legacy}
        current = [event('Example Artist', start_time='21:00'), event('Example Artist', start_time='19:00')]
        new_state = reconcile_state(current, state, now=now + timedelta(days=1))
        self.assertEqual(expected, {item.start_time: item._public_id for item in current})
        self.assertEqual(2, len(new_state['events']))
        report = build_change_report(current, state, new_state, now=now + timedelta(days=1))
        self.assertEqual((0, 0), (report['new_events'], report['no_longer_present']))

    def test_performance_state_survives_reordering_and_disappearance(self):
        now = datetime(2026, 9, 20, tzinfo=timezone.utc)
        early, late = event('Bruna Hetzel', start_time='19:00'), event('Bruna Hetzel', start_time='21:00')
        events = deduplicate_events([early, late])
        self.assertEqual(2, len(events))
        baseline = reconcile_state(events, None, now=now)
        self.assertEqual(2, len(baseline['events']))
        rows = prepare_upcoming_events(events, today=now.date())
        ids = {row['st']: row['i'] for row in rows}
        self.assertEqual(2, len(set(ids.values())))
        age = early.first_seen
        newer = [event('Bruna Hetzel', start_time='21:00'), event('Bruna Hetzel', start_time='19:00')]
        state = reconcile_state(newer, baseline, now=now + timedelta(days=1))
        self.assertEqual(ids, {row['st']: row['i'] for row in prepare_upcoming_events(newer, today=now.date())})
        self.assertTrue(all(item.first_seen == age for item in newer))
        report = build_change_report(newer, baseline, state, now=now + timedelta(days=1))
        self.assertEqual(0, report['new_events'])
        self.assertEqual(0, report['no_longer_present'])
        only_late = [event('Bruna Hetzel', start_time='21:00')]
        reconcile_state(only_late, state, now=now + timedelta(days=2))
        self.assertEqual(ids['21:00'], prepare_upcoming_events(only_late, today=now.date())[0]['i'])

    def test_legacy_single_row_migration_preserves_route_and_age(self):
        now = datetime(2026, 9, 20, tzinfo=timezone.utc)
        original = event('Example Artist')
        state = reconcile_state([original], None, now=now)
        state['version'] = 2
        for record in state['events'].values():
            record.pop('base_identity')
            record.pop('performance')
        performances = [event('Example Artist', start_time='19:00'), event('Example Artist', start_time='21:00')]
        reconcile_state(performances, state, now=now + timedelta(days=1))
        self.assertEqual(canonical_event_identity(original)[:16], performances[0]._public_id)
        self.assertNotEqual(performances[0]._public_id, performances[1]._public_id)
        self.assertTrue(all(item.first_seen == original.first_seen for item in performances))

    def test_nouveau_source_billing_lines_are_individual_neutral_artists(self):
        html = '''<li class="day_item"><time><span class="date">01.10</span></time>
        <li class="event_item" data-type="concert"><div class="event_header">
        <h3><span class="grey">Xandria</span><br/>Seven Spires<br/>Tulip</h3>
        </div></li></li>'''
        events = parse_items(BeautifulSoup(html, 'html.parser'), today=date(2026, 9, 20))
        apply_structured_performer_semantics(events)
        row = prepare_upcoming_events(events, today=date(2026, 9, 20))[0]
        self.assertEqual('Xandria', row['h'])
        self.assertEqual(['Seven Spires', 'Tulip'], row['ch'])
        self.assertFalse(row.get('o'))
        self.assertFalse(row.get('et'))

    def test_machine_artist_headings_not_title_punctuation(self):
        names = ["HUMANITY’S LAST BREATH", 'VILDHJARTA', 'ENTERPRISE EARTH', 'KARMANJAKAH']
        html = ''.join('<h2 class="nomartiste">' + name + '</h2>' for name in names)
        item = event(' + '.join(names), performers=machine_performers(html))
        events, _, rows = self.finish_pipeline([item], ["Humanity’s Last Breath", 'Vildhjarta', 'Enterprise Earth', 'Karmanjakah'])
        row = rows[0]
        self.assertEqual("Humanity’s Last Breath", row['h'])
        self.assertEqual(3, len(row['ch']))
        self.assertFalse(row.get('et'))
        self.assertEqual(4, len(events[0].electric_eye_links))
        self.assertEqual('Electric Eye concert review', events[0].image_source)
        self.assertEqual([], machine_performers('<h1>Artist + Project</h1>'))

    def test_merge_retains_semantic_evidence(self):
        left = event('Artist'); right = event('Artist', performers=['Artist', 'Peer'])
        right.tags = ['live']; right.description = 'Authoritative artist description'
        right.raw_title = 'Series: Artist + Peer'
        merged = merge_events(left, right)
        apply_structured_performer_semantics([merged])
        self.assertEqual(['Peer'], merged.co_headliners)
        self.assertEqual(right.description, merged.description)
        self.assertEqual(['live'], merged.tags)
        self.assertEqual(right.raw_title, merged.raw_title)

    def test_richer_structured_bill_wins_in_either_source_order(self):
        for reverse in (False, True):
            flat = event('Alpha + Beta & Company', start_time='20:00')
            structured = event('Alpha', start_time='20:00', performers=['Alpha', 'Beta & Company'])
            flat.source_names = ['Venue']; structured.source_names = ['Promoter']
            records = [flat, structured]
            result = deduplicate_events(list(reversed(records)) if reverse else records)
            self.assertEqual(1, len(result))
            self.assertEqual('Alpha', result[0].headliner)
            self.assertEqual(['Beta & Company'], result[0].co_headliners)
            self.assertEqual({'Venue', 'Promoter'}, set(result[0].source_names))

    def test_apostrophes_acronyms_and_mixed_case(self):
        from concert_calendar.production_export import event_to_data
        for raw, display in [("HUMANITY'S LAST BREATH", "Humanity's Last Breath"),
                             ("HUMANITY’S LAST BREATH", "Humanity’s Last Breath"),
                             ("O'CONNOR", "O'Connor"), ('AC/DC', 'AC/DC'), ('LiSA', 'LiSA')]:
            self.assertEqual(display, event_to_data(event(raw))['h'])

    def test_time_label_is_not_public_artist_identity(self):
        cases = [
            ("Example Artist – 19h00", "19:00"),
            ("Example Artist – 19h30", "19:30"),
            ("Example Artist – 19h", "19:00"),
            ("Example Artist – 16H", "16:00"),
        ]

        for raw, start_time in cases:
            with self.subTest(raw=raw):
                item = event(raw, start_time=start_time)
                apply_structured_performer_semantics([item])

                self.assertEqual("Example Artist", item.headliner)
                self.assertIsNone(item.event_title)

    def test_explicit_description_performer_becomes_public_artist(self):
        item = event(
            "Tribute programme avec Example Artist – 19h00",
            start_time="19:00",
        )
        item.event_title = "Tribute programme avec Example Artist"
        item.description = (
            "Après le concert, la jam est animée par Example Artist."
        )

        apply_structured_performer_semantics([item])
        self.assertEqual(
            "Example Artist",
            item.headliner,
        )

        # Canonical semantics are established before export.
        self.assertEqual(
            "Example Artist",
            item.headliner,
        )

    def test_description_cannot_invent_artist_absent_from_title(self):
        item = event(
            "Named Programme – 19h00",
            start_time="19:00",
        )
        item.description = (
            "La soirée est animée par Example Artist."
        )

        apply_structured_performer_semantics([item])
        self.assertEqual(
            "Named Programme",
            item.headliner,
        )

    def test_mismatched_time_suffix_is_not_removed(self):
        cases = [
            ("Example Artist – 19h00", "21:00"),
            ("Example Artist – 19h", "21:00"),
            ("Example Artist – 16H", "18:00"),
        ]

        for raw, start_time in cases:
            with self.subTest(raw=raw):
                item = event(raw, start_time=start_time)
                apply_structured_performer_semantics([item])
                self.assertEqual(raw, item.headliner)

    def test_two_performances_share_artist_but_keep_distinct_ids(self):
        early = event(
            "Example Artist – 19h00",
            start_time="19:00",
        )
        late = event(
            "Example Artist – 21h00",
            start_time="21:00",
        )

        self.assertNotEqual(
            canonical_event_identity(early),
            canonical_event_identity(late),
        )

        apply_structured_performer_semantics([early, late])
        rows = prepare_upcoming_events(
            [early, late],
            today=date(2026, 9, 20),
        )

        self.assertEqual(
            ["Example Artist", "Example Artist"],
            [row["h"] for row in rows],
        )
        self.assertEqual(
            {"19:00", "21:00"},
            {row["st"] for row in rows},
        )
        self.assertEqual(
            2,
            len({row["i"] for row in rows}),
        )

    def test_flattened_artist_bill_is_not_promoted_to_event_title(self):
        item = event(
            "Artist One + Artist Two",
            performers=["Artist One", "Artist Two"],
        )

        apply_structured_performer_semantics([item])

        self.assertEqual("Artist One", item.headliner)
        self.assertEqual(["Artist Two"], item.co_headliners)
        self.assertIsNone(item.event_title)

    def test_programme_title_is_retained_with_explicit_performers(self):
        item = event(
            "Named Programme",
            performers=[
                "Artist One",
                "Artist Two",
                "Artist Three",
            ],
        )
        # Programme context must be supplied explicitly by source semantics;
        # a generic flattened artist heading must never be promoted here.
        item.event_title = "Named Programme"

        apply_structured_performer_semantics([item])

        self.assertEqual(
            "Artist One",
            item.headliner,
        )
        self.assertEqual(
            ["Artist Two", "Artist Three"],
            item.co_headliners,
        )
        apply_structured_performer_semantics([item])
        self.assertEqual(
            "Named Programme",
            item.event_title,
        )

    def test_gaite_heading_provides_multi_artist_evidence(self):
        html = """
        <h1>
          Named Programme
          Artist One, Artist Two & Artist Three
          sont dans le rendez-vous
        </h1>
        """

        self.assertEqual(
            [
                "Artist One",
                "Artist Two",
                "Artist Three",
            ],
            detail_performers(
                html,
                "Named Programme",
            ),
        )

    def test_plain_heading_does_not_invent_performers(self):
        html = """
        <h1>
          Named Programme revient pour une nouvelle édition
        </h1>
        """

        self.assertEqual(
            [],
            detail_performers(
                html,
                "Named Programme",
            ),
        )


if __name__ == "__main__":
    unittest.main()
