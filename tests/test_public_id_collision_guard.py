import unittest
from datetime import date

from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import prepare_upcoming_events
from concert_calendar.event_state import canonical_event_identity


def event(start_time):
    return ConcertEvent(
        "2027-03-06",
        "Example Artist",
        "Example Venue",
        "Paris",
        "75",
        start_time=start_time,
    )


class PublicIdCollisionGuardTests(unittest.TestCase):
    def test_duplicate_preserved_id_is_disambiguated_stably(self):
        early = event("18:30")
        late = event("19:30")

        early._public_id = "a" * 16
        late._public_id = "a" * 16

        rows = prepare_upcoming_events(
            [late, early],
            today=date(2027, 1, 1),
        )
        ids = {row["st"]: row["i"] for row in rows}

        self.assertEqual("a" * 16, ids["18:30"])
        self.assertNotEqual(ids["18:30"], ids["19:30"])
        self.assertEqual(2, len(set(ids.values())))

        reversed_rows = prepare_upcoming_events(
            [early, late],
            today=date(2027, 1, 1),
        )
        reversed_ids = {
            row["st"]: row["i"]
            for row in reversed_rows
        }

        self.assertEqual(ids, reversed_ids)

        # Fresh objects represent a new standalone export, not merely reuse of
        # the allocator's attributes from the first call.
        fresh = [event('19:30'), event('18:30')]
        for item in fresh:
            item._public_id = 'a' * 16
        self.assertEqual(ids, {row['st']: row['i'] for row in prepare_upcoming_events(fresh, today=date(2027, 1, 1))})

    def test_single_supplied_route_is_preserved(self):
        item = event('19:30')
        item._public_id = 'b' * 16
        row = prepare_upcoming_events([item], today=date(2027, 1, 1))[0]
        self.assertEqual('b' * 16, row['i'])

    def test_later_preserved_base_is_reserved_before_earlier_allocation(self):
        early, late = event('18:30'), event('19:30')
        late._public_id = canonical_event_identity(late)[:16]
        rows = prepare_upcoming_events([early, late], today=date(2027, 1, 1))
        ids = {row['st']: row['i'] for row in rows}
        self.assertEqual(late._public_id, ids['19:30'])
        self.assertNotEqual(ids['18:30'], ids['19:30'])

    def test_ordinary_event_without_preserved_route_uses_legacy_base(self):
        item = event('19:30')
        self.assertEqual(canonical_event_identity(item)[:16],
                         prepare_upcoming_events([item], today=date(2027, 1, 1))[0]['i'])


if __name__ == "__main__":
    unittest.main()
