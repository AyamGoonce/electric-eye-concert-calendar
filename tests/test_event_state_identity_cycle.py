import unittest
from datetime import datetime, timedelta, timezone

from concert_calendar.event_state import (
    EventStateError,
    canonical_event_identity,
    reconcile_state,
)
from concert_calendar.models import ConcertEvent


def event():
    return ConcertEvent(
        date="2026-10-26",
        headliner="Example Artist",
        venue="Petit Bain",
        city="Paris",
        department="75",
    )


class HistoricalStateKeyReclaimTests(unittest.TestCase):
    def test_event_can_reclaim_exact_historical_key_when_base_cycles_back(self):
        now = datetime(2026, 9, 20, tzinfo=timezone.utc)

        original = event()
        previous = reconcile_state([original], None, now=now)

        stable_key = original._state_identity
        public_id = original._public_id
        first_seen = original.first_seen

        # Reproduce a legitimate historical state transition:
        # the stable state key remains A while a later representation
        # records a different canonical base B.
        alternate_base = "f" * 64
        self.assertNotEqual(stable_key, alternate_base)
        previous["events"][stable_key]["base_identity"] = alternate_base

        current = event()
        candidate = reconcile_state(
            [current],
            previous,
            now=now + timedelta(days=1),
        )

        self.assertEqual(stable_key, canonical_event_identity(current))
        self.assertEqual(stable_key, current._state_identity)
        self.assertEqual(public_id, current._public_id)
        self.assertEqual(first_seen, current.first_seen)
        self.assertEqual(
            stable_key,
            candidate["events"][stable_key]["base_identity"],
        )

    def test_historical_key_reclaim_does_not_allow_true_duplicate(self):
        now = datetime(2026, 9, 20, tzinfo=timezone.utc)

        original = event()
        previous = reconcile_state([original], None, now=now)

        stable_key = original._state_identity
        previous["events"][stable_key]["base_identity"] = "f" * 64

        with self.assertRaisesRegex(
            EventStateError,
            "Unresolved duplicate without a performance discriminator",
        ):
            reconcile_state(
                [event(), event()],
                previous,
                now=now + timedelta(days=1),
            )


if __name__ == "__main__":
    unittest.main()
