import copy
import unittest

from concert_calendar.deduplication import _deduplicate_exact, deduplicate_events
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import prepare_upcoming_events
from datetime import date
from datetime import datetime, timezone
from concert_calendar.event_state import reconcile_state


def event(**kwargs):
    return ConcertEvent('2027-03-06', 'Example Artist', 'Example Venue', 'Paris', '75', **kwargs)


class EarlyDedupSafetyTests(unittest.TestCase):
    def test_different_times_separate_before_and_after_reconciliation(self):
        for run in (_deduplicate_exact, deduplicate_events):
            self.assertEqual(2, len(run([event(start_time='19:00'), event(start_time='21:00')])))

    def test_official_venue_equal_time_merges_rich_metadata(self):
        from copy import deepcopy

        official = event(
            start_time="18:30",
            source_names=["Example Venue"],
            image_url="https://venue.example/show.jpg",
            image_source="Example Venue",
            ticket_url="https://venue.example/show",
        )
        external = event(
            start_time="18:30",
            source_names=["DICE"],
            genre="Rap",
            genre_evidence=[{"raw": "Rap", "source": "DICE"}],
            sold_out=True,
            ticket_status="sold_out",
            ticket_url="https://dice.fm/event/example",
        )

        for records in (
            [official, external],
            [external, official],
        ):
            result = deduplicate_events(
                [deepcopy(item) for item in records]
            )

            self.assertEqual(1, len(result))
            merged = result[0]

            self.assertEqual("18:30", merged.start_time)
            self.assertEqual(
                "https://venue.example/show",
                merged.ticket_url,
            )
            self.assertEqual(
                "https://venue.example/show.jpg",
                merged.image_url,
            )
            self.assertEqual("Example Venue", merged.image_source)
            self.assertEqual("Rap", merged.genre)
            self.assertEqual(
                [{"raw": "Rap", "source": "DICE"}],
                merged.genre_evidence,
            )
            self.assertTrue(merged.sold_out)
            self.assertEqual("sold_out", merged.ticket_status)
            self.assertEqual(
                {"Example Venue", "DICE"},
                set(merged.source_names or []),
            )

    def test_untimed_independent_sources_keep_established_merging(self):
        for run in (_deduplicate_exact, deduplicate_events):
            self.assertEqual(1, len(run([event(source_names=['One']), event(source_names=['Two'])])))

    def test_equal_normalized_time(self):
        self.assertEqual(1, len(_deduplicate_exact([
            event(start_time='19:00', source_names=['One']),
            event(start_time='19h00', source_names=['Two'])])))

    def test_same_event_url_preserves_source_duplicates(self):
        a = event(ticket_url='https://tickets.example/event/123?utm_source=one')
        b = event(ticket_url='https://tickets.example/event/123', openers=['Support'])
        result = _deduplicate_exact([a, b])
        self.assertEqual(1, len(result))
        self.assertEqual(['Support'], result[0].openers)

    def test_identical_representation_collapses(self):
        a = event()
        self.assertEqual(1, len(_deduplicate_exact([a, copy.deepcopy(a)])))

    def test_explicit_sets_override_shared_url(self):
        self.assertEqual(2, len(_deduplicate_exact([
            event(event_title='Example Artist — first set', ticket_url='https://tickets.example/event/123'),
            event(event_title='Example Artist — second set', ticket_url='https://tickets.example/event/123')])))

    def test_untimed_does_not_bridge_separate_sets(self):
        self.assertEqual(2, len(_deduplicate_exact([
            event(start_time='19:00', ticket_url='https://tickets.example/event/123'),
            event(ticket_url='https://tickets.example/event/123'),
            event(start_time='21:00', ticket_url='https://tickets.example/event/123')])))

    def test_collision_aware_ids_are_unique_and_order_stable(self):
        records = [event(start_time='19:00'), event(start_time='21:00')]
        rows = prepare_upcoming_events(records, today=date(2027, 1, 1))
        reversed_rows = prepare_upcoming_events(list(reversed(records)), today=date(2027, 1, 1))
        self.assertEqual(2, len({row['i'] for row in rows}))
        self.assertEqual({row['i'] for row in rows}, {row['i'] for row in reversed_rows})

    def test_untimed_programme_collision_gets_stable_distinct_ids(self):
        def programme_pair():
            north, south = event(), event()
            north.event_title = "Northern Tour"
            south.event_title = "Southern Tour"
            return [north, south]

        first = programme_pair()
        rows = prepare_upcoming_events(first, today=date(2027, 1, 1))
        ids = {row["et"]: row["i"] for row in rows}

        reversed_rows = prepare_upcoming_events(
            list(reversed(programme_pair())),
            today=date(2027, 1, 1),
        )
        reversed_ids = {row["et"]: row["i"] for row in reversed_rows}

        self.assertEqual(2, len(set(ids.values())))
        self.assertEqual(ids, reversed_ids)

        now = datetime(2026, 9, 20, tzinfo=timezone.utc)
        baseline_events = programme_pair()
        baseline = reconcile_state(baseline_events, None, now=now)
        baseline_ids = {
            item.event_title: item._public_id
            for item in baseline_events
        }

        reordered = list(reversed(programme_pair()))
        current = reconcile_state(
            reordered,
            baseline,
            now=datetime(2026, 9, 21, tzinfo=timezone.utc),
        )
        self.assertEqual(
            baseline_ids,
            {item.event_title: item._public_id for item in reordered},
        )

        survivor = programme_pair()[1]
        reconcile_state(
            [survivor],
            current,
            now=datetime(2026, 9, 22, tzinfo=timezone.utc),
        )
        self.assertEqual(
            baseline_ids["Southern Tour"],
            survivor._public_id,
        )

    def test_single_untimed_programme_keeps_legacy_base_id(self):
        item = event()
        item.event_title = "Northern Tour"

        from concert_calendar.event_state import canonical_event_identity

        row = prepare_upcoming_events(
            [item],
            today=date(2027, 1, 1),
        )[0]
        self.assertEqual(
            canonical_event_identity(item)[:16],
            row["i"],
        )

    def test_ordinary_id_remains_legacy_base(self):
        row = prepare_upcoming_events([event()], today=date(2027, 1, 1))[0]
        from concert_calendar.event_state import canonical_event_identity
        self.assertEqual(canonical_event_identity(event())[:16], row['i'])

    def test_canonical_cleanup_carries_old_public_id_and_first_seen(self):
        old = event('') if False else event()
        old.headliner = 'Example Artist - World Tour'
        old.first_seen = '2026-08-01T00:00:00Z'
        state = reconcile_state([old], None, now=datetime(2026, 9, 1, tzinfo=timezone.utc))
        clean = event()
        clean.identity_aliases = [old.headliner]
        current = reconcile_state([clean], state, now=datetime(2026, 9, 2, tzinfo=timezone.utc))
        self.assertEqual(old.first_seen, clean.first_seen)
        old_id = next(iter(state['events']))[:16]
        old_key = next(iter(state['events']))
        self.assertEqual({old_key}, set(current['events']))
        self.assertEqual(old_id, current['events'][old_key].get('public_id'))
        self.assertEqual(old_id, prepare_upcoming_events([clean], today=date(2027, 1, 1))[0]['i'])
