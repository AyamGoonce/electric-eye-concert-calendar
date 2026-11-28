"""Regressions for live-first retention overlap reconciliation."""
import unittest
from copy import deepcopy

from concert_calendar.models import ConcertEvent
from concert_calendar.deduplication import deduplicate_events
from concert_calendar.sources import suppress_reconciled_retained_overlaps


def row(headliner, source, date="2027-03-17", venue="Le Zénith Paris – La Villette", **extras):
    return ConcertEvent(
        date=date,
        headliner=headliner,
        venue=venue,
        city="Paris",
        department="75",
        source_names=[source],
        **extras,
    )


class CanonicalFreshRetentionTests(unittest.TestCase):
    def test_canonical_live_billing_suppresses_only_matching_stale_row(self):
        # The venue's independently verified bill was normalized from a
        # presentation title in the fresh-only deduplication pass.
        raw = row("WAXX LIVE AT THE ZENITH 2027", "AEG Presents France")
        canonical = row("Waxx", "AEG Presents France")
        stale = row("Waxx", "Alias Production")
        other_stale = row("Another Artist", "Alias Production")
        health = [{"source_name": "Alias Production",
                   "fallback_suppressed_count": 0,
                   "fallback_event_count": 2}]
        kept, suppressed = suppress_reconciled_retained_overlaps(
            [raw, canonical], [stale, other_stale], health,
        )
        self.assertEqual([other_stale], kept)
        self.assertEqual([stale], suppressed)
        self.assertEqual(1, health[0]["fallback_suppressed_count"])
        self.assertEqual(1, health[0]["fallback_event_count"])
        self.assertEqual(["AEG Presents France"], canonical.source_names)
        self.assertEqual(["Alias Production"], stale.source_names)

    def test_different_day_or_room_remains_retained(self):
        fresh = row("Waxx", "AEG Presents France")
        stale = [
            row("Waxx", "Alias Production", date="2027-03-18"),
            row("Waxx", "Alias Production", venue="L'Olympia Bruno Coquatrix"),
        ]
        health = [{"source_name": "Alias Production",
                   "fallback_suppressed_count": 0,
                   "fallback_event_count": 2}]
        kept, suppressed = suppress_reconciled_retained_overlaps(
            [fresh], stale, health,
        )
        self.assertEqual(stale, kept)
        self.assertEqual([], suppressed)

    def test_independent_canonicalization_does_not_mutate_raw_fresh_input(self):
        fresh = row("Waxx", "AEG Presents France")
        original = deepcopy(fresh)
        canonical = deduplicate_events([deepcopy(fresh)])
        self.assertEqual(original, fresh)
        self.assertEqual(["AEG Presents France"], canonical[0].source_names)


if __name__ == "__main__":
    unittest.main()
