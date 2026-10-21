"""Tests for the Electric Eye newsletter archive index."""

import json
import unittest

from newsletter.archive import build_archive, render_archive_json


class NewsletterArchiveTests(unittest.TestCase):

    def test_collects_and_sorts_editions(self):
        archive = build_archive([
            "weekly/2026-W41.html",
            "monthly/2026-09.html",
            "weekly/2026-W42.html",
            "monthly/2026-08.html",
            "weekly/2026-W42.html",
        ])

        self.assertEqual(
            [e["identifier"] for e in archive["editions"]["weekly"]],
            ["2026-W42", "2026-W41"],
        )
        self.assertEqual(
            [e["identifier"] for e in archive["editions"]["monthly"]],
            ["2026-09", "2026-08"],
        )

    def test_excludes_invalid_and_unrelated_files(self):
        archive = build_archive([
            "weekly/2026-W54.html",
            "monthly/2026-13.html",
            "weekly/index.html",
            "archives/index.html",
            "latest.json",
            "weekly/2026-W42.html",
        ])

        self.assertEqual(
            len(archive["editions"]["weekly"]), 1
        )
        self.assertEqual(
            len(archive["editions"]["monthly"]), 0
        )

    def test_empty_archive(self):
        archive = build_archive([])
        self.assertEqual(archive["editions"]["weekly"], [])
        self.assertEqual(archive["editions"]["monthly"], [])

    def test_json_is_valid(self):
        archive = build_archive(["weekly/2026-W42.html"])
        decoded = json.loads(render_archive_json(archive))
        self.assertEqual(decoded, archive)


if __name__ == "__main__":
    unittest.main()
