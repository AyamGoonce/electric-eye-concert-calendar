"""Regression for late artist reconciliation overlapping a degraded source snapshot."""
import unittest
from concert_calendar.models import ConcertEvent
from concert_calendar.sources import suppress_reconciled_retained_overlaps


def concert(headliner, source, *, ticket="https://tickets.test/concert"):
    return ConcertEvent(
        date="2027-03-17", headliner=headliner,
        venue="Le Zénith Paris – La Villette", city="Paris", department="75",
        source_names=[source], ticket_url=ticket,
    )


class LateRetentionOverlapTests(unittest.TestCase):
    def test_same_concert_preserves_fresh_source_and_suppresses_stale_duplicate(self):
        fresh = concert("Waxx", "Live Nation")
        stale = concert("Waxx", "Alias Production", ticket="https://alias.test/old")
        health = [
            {"source_name": "Alias Production", "status": "failed",
             "fallback_event_count": 1, "fallback_suppressed_count": 0},
            {"source_name": "Live Nation", "status": "ok",
             "fallback_event_count": 0, "fallback_suppressed_count": 0},
        ]
        result, suppressed = suppress_reconciled_retained_overlaps(
            [fresh], [stale], health
        )
        self.assertEqual([], result)
        self.assertEqual([stale], suppressed)
        self.assertEqual("Waxx", fresh.headliner)
        self.assertEqual(["Live Nation"], fresh.source_names)
        self.assertEqual("https://tickets.test/concert", fresh.ticket_url)
        self.assertEqual(1, health[0]["fallback_suppressed_count"])
        self.assertEqual(0, health[0]["fallback_event_count"])

    def test_similar_artist_on_different_day_or_venue_is_not_suppressed(self):
        fresh = concert("Waxx", "Live Nation")
        other_date = concert("Waxx", "Alias Production")
        other_date.date = "2027-03-18"
        other_venue = concert("Waxx", "Alias Production")
        other_venue.venue = "Bataclan"
        health = [
            {"source_name": "Alias Production", "status": "failed",
             "fallback_event_count": 2, "fallback_suppressed_count": 0},
        ]
        result, suppressed = suppress_reconciled_retained_overlaps(
            [fresh], [other_date, other_venue], health,
        )
        self.assertEqual([other_date, other_venue], result)
        self.assertEqual([], suppressed)
        self.assertEqual(2, health[0]["fallback_event_count"])


if __name__ == "__main__":
    unittest.main()
