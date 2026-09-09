import unittest
from datetime import date

from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import prepare_upcoming_events


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


if __name__ == "__main__":
    unittest.main()
