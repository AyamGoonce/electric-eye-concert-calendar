"""Regression tests for Electric Eye newsletter edition metadata."""

import unittest

from newsletter.manifest import build_manifest, latest_edition


class NewsletterManifestTests(unittest.TestCase):

    def test_weekly_and_monthly_paths(self):
        manifest = build_manifest(
            weekly="2026-W41",
            monthly="2026-09",
        )
        self.assertEqual(
            manifest["editions"]["weekly"]["path"],
            "weekly/2026-W41.html",
        )
        self.assertEqual(
            manifest["editions"]["monthly"]["path"],
            "monthly/2026-09.html",
        )

    def test_latest_weekly_edition(self):
        manifest = build_manifest(
            weekly="2026-W41",
            monthly="2026-09",
        )
        self.assertEqual(
            latest_edition(manifest)["identifier"],
            "2026-W41",
        )

    def test_latest_monthly_edition(self):
        manifest = build_manifest(
            weekly="2026-W40",
            monthly="2026-10",
        )
        self.assertEqual(
            latest_edition(manifest)["identifier"],
            "2026-10",
        )

    def test_year_boundary(self):
        manifest = build_manifest(
            weekly="2026-W53",
            monthly="2026-12",
        )
        self.assertEqual(
            latest_edition(manifest)["identifier"],
            "2026-W53",
        )

    def test_invalid_iso_week(self):
        with self.assertRaises(ValueError):
            build_manifest(weekly="2027-W53")

    def test_empty_manifest(self):
        self.assertIsNone(latest_edition(build_manifest()))


if __name__ == "__main__":
    unittest.main()
