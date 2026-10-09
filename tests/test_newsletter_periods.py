"""Regression tests for Electric Eye newsletter reporting periods."""

import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from newsletter.periods import reporting_period

PARIS = ZoneInfo("Europe/Paris")


class NewsletterPeriodTests(unittest.TestCase):

    def check_period(self, frequency, current, identifier, start, end):
        result = reporting_period(
            frequency,
            now=datetime.fromisoformat(current).replace(tzinfo=PARIS),
        )
        self.assertEqual(result["identifier"], identifier)
        self.assertEqual(result["start"], start)
        self.assertEqual(result["end_exclusive"], end)

    def test_weekly(self):
        self.check_period(
            "weekly", "2026-10-12",
            "2026-W41", "2026-10-05", "2026-10-12",
        )

    def test_monthly(self):
        self.check_period(
            "monthly", "2026-11-01",
            "2026-10", "2026-10-01", "2026-11-01",
        )

    def test_iso_year_boundary(self):
        self.check_period(
            "weekly", "2027-01-04",
            "2026-W53", "2026-12-28", "2027-01-04",
        )

    def test_invalid_frequency(self):
        with self.assertRaises(ValueError):
            reporting_period("daily")


if __name__ == "__main__":
    unittest.main()
