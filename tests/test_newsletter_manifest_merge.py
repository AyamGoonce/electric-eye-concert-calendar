"""Regression tests for newsletter manifest updates."""

import unittest

from newsletter.manifest import build_manifest, merge_manifest


class NewsletterManifestMergeTests(unittest.TestCase):

    def test_new_weekly_preserves_monthly(self):
        existing = build_manifest(
            weekly="2026-W40",
            monthly="2026-09",
        )
        result = merge_manifest(
            existing,
            {"frequency": "weekly", "identifier": "2026-W41"},
        )
        self.assertEqual(
            result["editions"]["weekly"]["identifier"], "2026-W41"
        )
        self.assertEqual(
            result["editions"]["monthly"]["identifier"], "2026-09"
        )

    def test_new_monthly_preserves_weekly(self):
        existing = build_manifest(
            weekly="2026-W41",
            monthly="2026-09",
        )
        result = merge_manifest(
            existing,
            {"frequency": "monthly", "identifier": "2026-10"},
        )
        self.assertEqual(
            result["editions"]["weekly"]["identifier"], "2026-W41"
        )
        self.assertEqual(
            result["editions"]["monthly"]["identifier"], "2026-10"
        )

    def test_older_weekly_cannot_replace_newer(self):
        existing = build_manifest(weekly="2026-W42")
        result = merge_manifest(
            existing,
            {"frequency": "weekly", "identifier": "2026-W41"},
        )
        self.assertEqual(result, existing)

    def test_existing_edition_is_idempotent(self):
        existing = build_manifest(monthly="2026-09")
        result = merge_manifest(
            existing,
            {"frequency": "monthly", "identifier": "2026-09"},
        )
        self.assertEqual(result, existing)

    def test_invalid_existing_manifest_rejected(self):
        with self.assertRaises(ValueError):
            merge_manifest(
                {"schema_version": 2, "editions": {}},
                {"frequency": "weekly", "identifier": "2026-W41"},
            )

    def test_iso_year_boundary(self):
        existing = build_manifest(weekly="2026-W53")
        result = merge_manifest(
            existing,
            {"frequency": "weekly", "identifier": "2027-W01"},
        )
        self.assertEqual(
            result["editions"]["weekly"]["identifier"], "2027-W01"
        )


if __name__ == "__main__":
    unittest.main()
