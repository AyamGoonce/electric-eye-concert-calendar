"""Calendar alert contract: only degraded or failed runs email the administrator."""

import unittest

from concert_calendar.degradation_notice import build_message


class CalendarDegradationNoticeTests(unittest.TestCase):
    def test_healthy_run_does_not_email(self):
        self.assertIsNone(build_message(
            {"source_health": [{"source_name": "Venue", "status": "ok"}]},
            run_url="https://github.com/example/actions/runs/1", failed=False,
        ))

    def test_partial_publication_includes_retention_details(self):
        message = build_message(
            {
                "event_count": 2023,
                "published_at": "2026-11-09T12:00:00Z",
                "source_health": [
                    {
                        "source_name": "U-Turn Touring", "status": "failed",
                        "error": "Unexpected empty inventory after 3 attempts",
                        "fresh_event_count": 0, "fallback_event_count": 7,
                        "last_successful_at": "2026-11-09T06:00:00Z",
                        "fallback_expired_count": 0, "fallback_unavailable": False,
                    },
                ],
            },
            run_url="https://github.com/example/actions/runs/2",
            failed=False,
        )
        self.assertIn("WARNING", message["Subject"])
        self.assertIn("U-Turn Touring", message.get_content())
        self.assertIn("Retained records: 7", message.get_content())
        self.assertEqual("eric@electriceyerock.com", message["To"])

    def test_failure_without_report_still_alerts(self):
        message = build_message(
            None, run_url="https://github.com/example/actions/runs/3", failed=True,
        )
        self.assertIn("FAILED", message["Subject"])
        self.assertIn("No completed automation report", message.get_content())
