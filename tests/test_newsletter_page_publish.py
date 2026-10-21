"""Tests for safe publication of permanent newsletter pages."""

import base64
import unittest
from unittest.mock import Mock

from newsletter.page_publish import publish_page


class NewsletterPagePublishTests(unittest.TestCase):

    def setUp(self):
        self.session = Mock()

    def test_creates_new_page(self):
        self.session.get.return_value.status_code = 404
        self.session.put.return_value.status_code = 201
        self.session.put.return_value.json.return_value = {
            "commit": {"sha": "abc123"}
        }

        result = publish_page(
            "weekly/index.html",
            "<html>Weekly</html>",
            token="test-token",
            session=self.session,
        )

        self.assertEqual(result["action"], "created")
        payload = self.session.put.call_args.kwargs["json"]
        self.assertEqual(
            base64.b64decode(payload["content"]).decode(),
            "<html>Weekly</html>",
        )
        self.assertNotIn("sha", payload)

    def test_identical_page_is_unchanged(self):
        content = "<html>Monthly</html>"
        self.session.get.return_value.status_code = 200
        self.session.get.return_value.json.return_value = {
            "sha": "existing",
            "content": base64.b64encode(content.encode()).decode(),
        }

        result = publish_page(
            "monthly/index.html",
            content,
            token="test-token",
            session=self.session,
        )

        self.assertEqual(result["action"], "unchanged")
        self.session.put.assert_not_called()

    def test_existing_page_is_updated_with_sha(self):
        self.session.get.return_value.status_code = 200
        self.session.get.return_value.json.return_value = {
            "sha": "old-sha",
            "content": base64.b64encode(b"old").decode(),
        }
        self.session.put.return_value.status_code = 200
        self.session.put.return_value.json.return_value = {
            "commit": {"sha": "new-sha"}
        }

        result = publish_page(
            "archives/index.html",
            "<html>Archives</html>",
            token="test-token",
            session=self.session,
        )

        self.assertEqual(result["action"], "updated")
        self.assertEqual(
            self.session.put.call_args.kwargs["json"]["sha"],
            "old-sha",
        )

    def test_cannot_overwrite_newsletter_edition(self):
        with self.assertRaises(ValueError):
            publish_page(
                "weekly/2026-W42.html",
                "<html>Replacement</html>",
            )
        self.session.put.assert_not_called()

    def test_empty_content_rejected(self):
        with self.assertRaises(ValueError):
            publish_page("weekly/index.html", "   ")


if __name__ == "__main__":
    unittest.main()
