from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.event_state import (
    canonical_event_identity,
    is_new,
    reconcile_state,
)
from concert_calendar.models import ConcertEvent


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "concert_calendar" / "static" / "calendar-renderer.js"


class NewlyAddedTests(unittest.TestCase):
    NOW = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)

    @staticmethod
    def event(**changes):
        values = {
            "date": "2026-10-16",
            "headliner": "Behemoth & Dimmu Borgir",
            "venue": "Le Zénith Paris – La Villette",
            "city": "Paris",
            "department": "75",
        }
        values.update(changes)
        return ConcertEvent(**values)

    def test_first_state_bootstraps_existing_events_as_old(self):
        event = self.event()
        reconcile_state([event], None, now=self.NOW)

        self.assertFalse(is_new(event.first_seen, now=self.NOW))

    def test_genuinely_new_deduplicated_event_gets_current_timestamp(self):
        baseline = reconcile_state(
            [self.event(headliner="Existing artist")], None, now=self.NOW
        )
        venue = self.event(source_names=["Le Zénith Paris – La Villette"])
        promoter = self.event(
            headliner="Behemoth x Dimmu Borgir",
            source_names=["Live Nation"],
        )

        deduplicated = deduplicate_events([venue, promoter])
        state = reconcile_state(
            deduplicated, baseline, now=self.NOW + timedelta(hours=6)
        )

        self.assertEqual(1, len(deduplicated))
        self.assertEqual("2026-09-01T18:00:00Z", deduplicated[0].first_seen)
        self.assertEqual(2, len(state["events"]))

    def test_first_seen_persists_when_metadata_changes(self):
        baseline = reconcile_state([self.event()], None, now=self.NOW)
        improved = self.event(
            openers=["Dark Funeral"],
            promoters=["Live Nation"],
            ticket_url="https://tickets.example/behemoth",
            genre_public="Metal / Hard Rock",
        )

        current = reconcile_state(
            [improved], baseline, now=self.NOW + timedelta(hours=24)
        )

        identity = canonical_event_identity(improved)
        self.assertEqual(
            baseline["events"][identity]["first_seen"],
            current["events"][identity]["first_seen"],
        )

    def test_new_window_ends_after_72_hours(self):
        timestamp = "2026-09-01T12:00:00Z"
        self.assertTrue(is_new(timestamp, now=self.NOW + timedelta(hours=72)))
        self.assertFalse(
            is_new(timestamp, now=self.NOW + timedelta(hours=72, seconds=1))
        )

    def test_renderer_derives_new_from_persistent_first_seen(self):
        renderer = RENDERER.read_text(encoding="utf-8")

        self.assertIn("now-Date.parse(e.fs)>=0", renderer)
        self.assertIn("now-Date.parse(e.fs)<=NEW_WINDOW_MS", renderer)
        self.assertNotIn("now-Date.parse(e.an)", renderer)

    def test_new_filter_is_url_addressable_and_combines_with_other_filters(self):
        renderer = RENDERER.read_text(encoding="utf-8")

        self.assertIn('controls.newly.checked=p.get("new")==="1"', renderer)
        self.assertIn('if(controls.newly.checked)p.set("new","1")', renderer)
        self.assertIn('&&(!controls.newly.checked||e.n)', renderer)
        self.assertIn('[controls.venue,controls.newly]', renderer)


if __name__ == "__main__":
    unittest.main()
