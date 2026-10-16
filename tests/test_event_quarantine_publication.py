import unittest
from datetime import datetime, timedelta, timezone
from concert_calendar.event_state import (
    EventStateError, canonical_event_identity, reconcile_state,
    reconcile_state_quarantining_collisions,
)
from concert_calendar.models import ConcertEvent
from concert_calendar.source_retention import validate_retained_identities, SourceStateError

def event(name, status=None):
    return ConcertEvent(date="2026-11-12", headliner=name, venue="Petit Bain",
                        city="Paris", department="75", ticket_status=status)

class QuarantineTests(unittest.TestCase):
    def test_collision_does_not_block_unrelated_event(self):
        now = datetime(2026, 10, 16, tzinfo=timezone.utc)
        original = event("Other Artist")
        prior = reconcile_state([original], None, now=now)
        existing_id = original._public_id
        events = [event("Erykah Badu", "postponed"),
                  event("Erykah Badu", "cancelled"), event("Other Artist")]
        state, quarantined = reconcile_state_quarantining_collisions(
            events, prior, now=now + timedelta(days=1))
        self.assertEqual([e.headliner for e in events], ["Other Artist"])
        self.assertEqual(events[0]._public_id, existing_id)
        self.assertEqual(quarantined, {canonical_event_identity(event("Erykah Badu"))})
        self.assertIn(events[0]._state_identity, state["events"])

    def test_status_change_is_not_a_new_identity(self):
        now = datetime(2026, 10, 16, tzinfo=timezone.utc)
        original = event("Erykah Badu", "postponed")
        prior = reconcile_state([original], None, now=now)
        current = event("Erykah Badu", "cancelled")
        state, quarantined = reconcile_state_quarantining_collisions(
            [current], prior, now=now + timedelta(days=1))
        self.assertFalse(quarantined)
        self.assertEqual(current._public_id, original._public_id)
        self.assertEqual(state["events"][current._state_identity]["ticket_status"], "cancelled")

    def test_retained_source_validation_still_strict(self):
        now = datetime(2026, 10, 16, tzinfo=timezone.utc)
        original = event("Other Artist")
        prior = reconcile_state([original], None, now=now)
        snapshot = {"public_id":original._public_id,
                    "first_seen": original.first_seen,
                    "event":{"date":original.date,
                             "headliner":original.headliner,"venue":original.venue}}
        current = event("Other Artist")
        current.source_names = ["SOURCE"]
        state, _ = reconcile_state_quarantining_collisions(
            [current], prior, now=now + timedelta(days=1))
        validate_retained_identities([current], state, {"SOURCE":[snapshot]})
        with self.assertRaises(SourceStateError):
            validate_retained_identities([current], state, {"WRONG_SOURCE":[snapshot]})

    def test_empty_after_quarantine_is_fatal(self):
        now=datetime(2026,10,16,tzinfo=timezone.utc)
        with self.assertRaisesRegex(EventStateError, "All events were quarantined"):
            reconcile_state_quarantining_collisions(
                [event("Erykah Badu"),event("Erykah Badu")],None,now=now)

if __name__ == "__main__":
    unittest.main()
