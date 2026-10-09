"""Tests for Electric Eye newsletter scheduling and dry-run safety."""

import sys
import unittest
from datetime import date, datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from newsletter.run import generate, is_publication_day, main

PARIS = ZoneInfo("Europe/Paris")


class NewsletterRunnerTests(unittest.TestCase):

    def test_weekly_publication_day(self):
        self.assertTrue(is_publication_day("weekly", date(2026, 10, 12)))
        self.assertFalse(is_publication_day("weekly", date(2026, 10, 13)))

    def test_monthly_publication_day(self):
        self.assertTrue(is_publication_day("monthly", date(2026, 11, 1)))
        self.assertFalse(is_publication_day("monthly", date(2026, 11, 2)))

    def test_unsupported_frequency_rejected(self):
        with self.assertRaises(ValueError):
            is_publication_day("daily", date(2026, 10, 12))

    @patch("newsletter.run.render_newsletter", return_value="<html>OK</html>")
    @patch("newsletter.run.build_snapshot")
    @patch("newsletter.run.fetch_calendar")
    @patch("newsletter.run.fetch_entries")
    def test_generate_uses_existing_sources(
        self, fetch_entries, fetch_calendar, build_snapshot, render
    ):
        fetch_entries.return_value = [{"id": "article"}]
        fetch_calendar.return_value = ([{"id": "concert"}], {"count": 1})
        build_snapshot.return_value = {
            "frequency": "weekly",
            "identifier": "2026-W41",
            "counts": {},
        }

        snapshot, html, manifest = generate(
            "weekly",
            now=datetime(2026, 10, 12, 8, tzinfo=PARIS),
        )

        self.assertEqual(snapshot["identifier"], "2026-W41")
        self.assertEqual(html, "<html>OK</html>")
        self.assertEqual(manifest["count"], 1)
        fetch_entries.assert_called_once()
        fetch_calendar.assert_called_once()
        render.assert_called_once()

    @patch("newsletter.run.update_latest_manifest")
    @patch("newsletter.run.publish_edition")
    @patch("newsletter.run.generate")
    def test_dry_run_never_publishes(
        self, generate_mock, publish_mock, manifest_mock
    ):
        generate_mock.return_value = (
            {"identifier": "2026-W41", "counts": {}},
            "<html>OK</html>",
            {},
        )
        with patch.object(
            sys, "argv", ["newsletter.run", "--frequency", "weekly"]
        ):
            main()

        publish_mock.assert_not_called()
        manifest_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
