"""Regression tests for calendar publication watchdog decisions."""
import json
from datetime import datetime, timedelta, timezone
import unittest

from concert_calendar.schedule_watchdog import decide, published_at

NOW = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)


def pointer(age_hours):
    stamp = (NOW - timedelta(hours=age_hours)).isoformat().replace("+00:00", "Z")
    return '(function(){ var manifest = Object.freeze({"publishedAt":"' + stamp + '","count":2106}); }());'


def runs(*items):
    return {"workflow_runs": list(items)}


def run(status, hours_ago):
    return {"status": status, "created_at": (NOW - timedelta(hours=hours_ago)).isoformat()}


class WatchdogTests(unittest.TestCase):
    def test_fresh_publication_never_dispatches(self):
        self.assertEqual(decide(pointer(3), runs(), NOW)["action"], "fresh")

    def test_exact_five_hours_not_stale(self):
        self.assertEqual(decide(pointer(5), runs(), NOW)["action"], "fresh")

    def test_stale_and_idle_requests_recovery(self):
        self.assertEqual(decide(pointer(6), runs(run("completed", 4)), NOW)["action"], "recover")

    def test_running_calendar_blocks_duplicate(self):
        self.assertEqual(decide(pointer(6), runs(run("in_progress", 4)), NOW)["action"], "active")

    def test_queued_calendar_blocks_duplicate(self):
        self.assertEqual(decide(pointer(6), runs(run("queued", 4)), NOW)["action"], "active")

    def test_recent_failed_run_starts_cooldown(self):
        self.assertEqual(decide(pointer(8), runs(run("completed", 1)), NOW)["action"], "cooldown")

    def test_recent_success_with_unmoved_pointer_starts_cooldown(self):
        self.assertEqual(decide(pointer(8), runs(run("completed", 1.5)), NOW)["action"], "cooldown")

    def test_stale_without_any_runs_requests_recovery(self):
        self.assertEqual(decide(pointer(9), runs(), NOW)["action"], "recover")

    def test_future_timestamp_fails_closed(self):
        with self.assertRaises(ValueError):
            decide(pointer(-1), runs(), NOW)

    def test_missing_history_fails_closed(self):
        with self.assertRaises(ValueError):
            decide(pointer(8), {}, NOW)

    def test_bad_pointer_fails_closed(self):
        with self.assertRaises(ValueError):
            published_at("not a manifest")


if __name__ == "__main__":
    unittest.main()
