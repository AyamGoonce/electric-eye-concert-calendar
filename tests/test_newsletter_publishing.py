"""Tests for safe Electric Eye newsletter publication planning."""

import unittest

from newsletter.publishing import edition_path, publication_plan


class NewsletterPublishingTests(unittest.TestCase):

    def test_monthly_path(self):
        snapshot = {
            "frequency": "monthly",
            "identifier": "2026-10",
        }
        self.assertEqual(edition_path(snapshot), "monthly/2026-10.html")

    def test_weekly_path(self):
        snapshot = {
            "frequency": "weekly",
            "identifier": "2026-W41",
        }
        self.assertEqual(edition_path(snapshot), "weekly/2026-W41.html")

    def test_existing_edition_is_preserved(self):
        snapshot = {
            "frequency": "monthly",
            "identifier": "2026-09",
        }
        plan = publication_plan(
            snapshot,
            {"monthly/2026-09.html"},
        )
        self.assertEqual(plan["action"], "skip")
        self.assertEqual(plan["reason"], "Edition already published")

    def test_new_edition_can_be_created(self):
        snapshot = {
            "frequency": "monthly",
            "identifier": "2026-10",
        }
        plan = publication_plan(
            snapshot,
            {"monthly/2026-09.html"},
        )
        self.assertEqual(plan["action"], "create")
        self.assertEqual(plan["path"], "monthly/2026-10.html")

    def test_invalid_identifiers_rejected(self):
        invalid = [
            {"frequency": "monthly", "identifier": "2026-13"},
            {"frequency": "weekly", "identifier": "2026-W00"},
            {"frequency": "monthly", "identifier": "../index"},
            {"frequency": "daily", "identifier": "2026-10-09"},
        ]
        for snapshot in invalid:
            with self.subTest(snapshot=snapshot):
                with self.assertRaises(ValueError):
                    edition_path(snapshot)


if __name__ == "__main__":
    unittest.main()
