"""Tests for automatic publication of newsletter archives."""

import json
import unittest
from unittest.mock import Mock, patch

from newsletter.archive_publish import publish_archive


class NewsletterArchivePublishTests(unittest.TestCase):

    def setUp(self):
        self.session = Mock()

        weekly = Mock()
        weekly.json.return_value = [
            {"type": "file", "path": "weekly/2026-W42.html"},
            {"type": "file", "path": "weekly/2026-W41.html"},
            {"type": "file", "path": "weekly/index.html"},
        ]

        monthly = Mock()
        monthly.json.return_value = [
            {"type": "file", "path": "monthly/2026-09.html"},
            {"type": "file", "path": "monthly/index.html"},
        ]

        self.session.get.side_effect = [weekly, monthly]

    @patch("newsletter.archive_publish.publish_page")
    def test_publishes_complete_archive(self, publish_page):
        publish_page.return_value = {"action": "created"}

        result = publish_archive(
            token="test-token",
            session=self.session,
        )

        self.assertEqual(
            result["counts"],
            {"weekly": 2, "monthly": 1},
        )
        self.assertEqual(publish_page.call_count, 2)

        data_call = publish_page.call_args_list[0]
        page_call = publish_page.call_args_list[1]

        self.assertEqual(
            data_call.args[0], "archives/index.json"
        )
        self.assertEqual(
            page_call.args[0], "archives/index.html"
        )

        archive = json.loads(data_call.args[1])

        self.assertEqual(
            [e["identifier"] for e in archive["editions"]["weekly"]],
            ["2026-W42", "2026-W41"],
        )
        self.assertEqual(
            [e["identifier"] for e in archive["editions"]["monthly"]],
            ["2026-09"],
        )

    @patch("newsletter.archive_publish.publish_page")
    def test_github_failure_prevents_publication(self, publish_page):
        self.session.get.side_effect = RuntimeError("GitHub unavailable")

        with self.assertRaisesRegex(
            RuntimeError, "GitHub unavailable"
        ):
            publish_archive(
                token="test-token",
                session=self.session,
            )

        publish_page.assert_not_called()

    @patch("newsletter.archive_publish.publish_page")
    def test_rejects_incomplete_directory(self, publish_page):
        response = Mock()
        response.json.return_value = [
            {"type": "file", "path": "weekly/2026-W42.html"}
        ] * 1000
        self.session.get.side_effect = [response]

        with self.assertRaisesRegex(
            RuntimeError, "requires pagination"
        ):
            publish_archive(
                token="test-token",
                session=self.session,
            )

        publish_page.assert_not_called()


if __name__ == "__main__":
    unittest.main()
