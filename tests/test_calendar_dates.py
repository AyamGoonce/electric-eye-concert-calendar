from datetime import datetime, timezone
import unittest

from concert_calendar.calendar_dates import quick_date_range


class QuickDateTests(unittest.TestCase):
    def test_tonight_uses_paris_date_at_utc_boundary(self):
        now = datetime(2026, 8, 23, 22, 30, tzinfo=timezone.utc)
        self.assertEqual(("2026-08-24", "2026-08-24"), quick_date_range("tonight", now))

    def test_week_is_monday_through_sunday_across_month_boundary(self):
        now = datetime(2026, 9, 2, 12, tzinfo=timezone.utc)
        self.assertEqual(("2026-08-31", "2026-09-06"), quick_date_range("week", now))

    def test_weekend_rolls_to_upcoming_on_weekday(self):
        now = datetime(2026, 12, 30, 12, tzinfo=timezone.utc)
        self.assertEqual(("2027-01-01", "2027-01-03"), quick_date_range("weekend", now))

    def test_friday_saturday_and_sunday_use_current_weekend(self):
        expected = ("2026-08-21", "2026-08-23")
        for day in (21, 22, 23):
            with self.subTest(day=day):
                self.assertEqual(expected, quick_date_range("weekend", datetime(2026, 8, day, 12, tzinfo=timezone.utc)))

    def test_all_dates_has_no_range(self):
        self.assertIsNone(quick_date_range("all", datetime.now(timezone.utc)))
