import unittest
from unittest.mock import patch

from concert_calendar.automation import ProductionValidationError, validate_events


def row(*, time=None, event_id="a" * 16, title=None):
    return {
        "d": "2026-11-24",
        "h": "José Gonzalez",
        "o": [],
        "v": "Le Trianon",
        "c": "Paris",
        "x": [],
        "p": [],
        "t": None,
        "f": False,
        "so": False,
        "fs": "2026-08-20T11:02:59Z",
        "i": event_id,
        "ts": None,
        "st": time,
        **({"et": title} if title else {}),
    }


def validate_renderer_rows(rows):
    with patch("concert_calendar.automation.MINIMUM_EVENT_COUNT", 0):
        validate_events(rows)


class RendererPerformanceIdentityTests(unittest.TestCase):
    def test_distinct_times_are_valid_renderer_records(self):
        validate_renderer_rows([
            row(time="18:30"),
            row(time="19:30", event_id="b" * 16),
        ])

    def test_identical_renderer_copy_still_fails(self):
        with self.assertRaises(ProductionValidationError):
            validate_renderer_rows([
                row(),
                row(),
            ])

    def test_same_time_with_different_ids_still_fails(self):
        with self.assertRaises(ProductionValidationError):
            validate_renderer_rows([
                row(time="19:30"),
                row(time="19:30", event_id="b" * 16),
            ])


if __name__ == "__main__":
    unittest.main()
