"""Regression tests for combined Electric Eye newsletter snapshots."""

import unittest

from newsletter.snapshot import build_snapshot


PERIOD = {
    "frequency": "weekly",
    "identifier": "2026-W41",
    "start": "2026-10-05",
    "end_exclusive": "2026-10-12",
}


def article(post_id, label, published="2026-10-08T12:00:00+02:00"):
    return {
        "id": {"$t": f"tag:blogger.com,1999:blog-123.post-{post_id}"},
        "title": {"$t": f"Test {label}"},
        "published": {"$t": published},
        "category": [{"term": label}],
        "link": [{
            "rel": "alternate",
            "type": "text/html",
            "href": f"https://www.electriceyerock.com/test-{post_id}.html",
        }],
        "summary": {"$t": "Test summary."},
    }


def concert(event_id, venue):
    return {
        "i": event_id,
        "fs": "2026-10-08T12:00:00Z",
        "d": "2026-11-20",
        "h": "Test Artist",
        "v": venue,
        "c": "Paris",
    }


class NewsletterSnapshotTests(unittest.TestCase):

    def test_combined_snapshot(self):
        entries = [
            article("1", "Concert Review"),
            article("2", "News"),
            article("3", "Friday's Playlist"),
        ]
        events = [
            concert("0123456789abcdef", "Bataclan"),
            concert("fedcba9876543210", "Supersonic"),
            concert("1111111111111111", "Petit Bain"),
        ]

        snapshot = build_snapshot(
            entries, events, PERIOD, "2026-10-12"
        )

        self.assertEqual(snapshot["identifier"], "2026-W41")
        self.assertEqual(snapshot["counts"]["concert_review"], 1)
        self.assertEqual(snapshot["counts"]["news"], 1)
        self.assertEqual(snapshot["counts"]["playlist"], 1)
        self.assertEqual(snapshot["counts"]["concerts"], 2)
        self.assertEqual(snapshot["articles"]["interview"], [])
        self.assertEqual(snapshot["articles"]["album_review"], [])
        self.assertEqual(
            [item["venue"] for item in snapshot["concerts"]],
            ["Bataclan", "Petit Bain"],
        )

    def test_empty_editorial_category_is_valid(self):
        snapshot = build_snapshot(
            [article("1", "News")],
            [concert("0123456789abcdef", "Olympia")],
            PERIOD,
            "2026-10-12",
        )
        self.assertEqual(snapshot["counts"]["interview"], 0)
        self.assertEqual(snapshot["counts"]["album_review"], 0)

    def test_empty_blogger_source_rejected(self):
        with self.assertRaises(ValueError):
            build_snapshot(
                [],
                [concert("0123456789abcdef", "Olympia")],
                PERIOD,
                "2026-10-12",
            )

    def test_empty_calendar_source_rejected(self):
        with self.assertRaises(ValueError):
            build_snapshot(
                [article("1", "News")],
                [],
                PERIOD,
                "2026-10-12",
            )


if __name__ == "__main__":
    unittest.main()
