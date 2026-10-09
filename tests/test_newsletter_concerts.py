"""Regression tests for Electric Eye newsletter concert selection."""

import unittest

from newsletter.concerts import extract_concerts


PERIOD = {
    "start": "2026-10-05",
    "end_exclusive": "2026-10-12",
}

PUBLICATION_DATE = "2026-10-12"


def concert(event_id, first_seen, concert_date, artist="Test Artist"):
    return {
        "i": event_id,
        "fs": first_seen,
        "d": concert_date,
        "h": artist,
        "v": "Le Bataclan",
        "c": "Paris",
        "st": "20:00",
    }


class NewsletterConcertTests(unittest.TestCase):

    def test_new_upcoming_concert(self):
        events = [
            concert(
                "0123456789abcdef",
                "2026-10-08T12:00:00Z",
                "2026-11-20",
            )
        ]
        result = extract_concerts(events, PERIOD, PUBLICATION_DATE)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["artist"], "Test Artist")
        self.assertEqual(
            result[0]["url"],
            "https://www.electriceyerock.com"
            "/p/paris-area-concert-calendar.html"
            "#event-0123456789abcdef",
        )

    def test_past_performance_excluded(self):
        events = [
            concert(
                "0123456789abcdef",
                "2026-10-08T12:00:00Z",
                "2026-10-11",
            )
        ]
        self.assertEqual(
            extract_concerts(events, PERIOD, PUBLICATION_DATE),
            [],
        )

    def test_previous_week_discovery_excluded(self):
        events = [
            concert(
                "0123456789abcdef",
                "2026-10-03T12:00:00Z",
                "2026-11-20",
            )
        ]
        self.assertEqual(
            extract_concerts(events, PERIOD, PUBLICATION_DATE),
            [],
        )

    def test_duplicate_event_id(self):
        event = concert(
            "0123456789abcdef",
            "2026-10-08T12:00:00Z",
            "2026-11-20",
        )
        result = extract_concerts(
            [event, event], PERIOD, PUBLICATION_DATE
        )
        self.assertEqual(len(result), 1)

    def test_archived_newsletter_hides_expired_concert(self):
        events = [
            concert(
                "0123456789abcdef",
                "2026-10-08T12:00:00Z",
                "2026-11-20",
            )
        ]
        result = extract_concerts(
            events,
            PERIOD,
            PUBLICATION_DATE,
            as_of="2026-11-21",
        )
        self.assertEqual(result, [])

    def test_paris_timezone_boundary(self):
        events = [
            concert(
                "0123456789abcdef",
                "2026-10-11T22:30:00Z",
                "2026-11-20",
            )
        ]
        # 22:30 UTC on October 11 is 00:30 in Paris on October 12.
        self.assertEqual(
            extract_concerts(events, PERIOD, PUBLICATION_DATE),
            [],
        )

    def test_invalid_public_id_rejected(self):
        events = [
            concert("invalid-id", "2026-10-08T12:00:00Z", "2026-11-20")
        ]
        with self.assertRaises(ValueError):
            extract_concerts(events, PERIOD, PUBLICATION_DATE)


if __name__ == "__main__":
    unittest.main()
