"""Tests for create-only GitHub newsletter publication."""

import base64
import unittest
from unittest.mock import Mock

import requests

from newsletter.github_publish import publish_edition


SNAPSHOT = {
    "frequency": "weekly",
    "identifier": "2026-W41",
}

HTML = "<!doctype html><html><body>Newsletter</body></html>"


def response(status, data=None):
    result = Mock()
    result.status_code = status
    result.json.return_value = data or {}
    result.raise_for_status.side_effect = (
        requests.HTTPError(f"HTTP {status}") if status >= 400 else None
    )
    return result


class GitHubPublisherTests(unittest.TestCase):

    def test_new_edition_created(self):
        session = Mock()
        session.get.return_value = response(404)
        session.put.return_value = response(
            201, {"commit": {"sha": "abc123"}}
        )

        result = publish_edition(
            SNAPSHOT, HTML, token="test-token", session=session
        )

        self.assertEqual(result["action"], "created")
        self.assertEqual(result["commit"], "abc123")

        args, kwargs = session.put.call_args
        self.assertEqual(kwargs["json"]["branch"], "main")
        self.assertNotIn("sha", kwargs["json"])
        self.assertEqual(
            base64.b64decode(kwargs["json"]["content"]).decode(),
            HTML,
        )

    def test_existing_edition_not_overwritten(self):
        session = Mock()
        session.get.return_value = response(200)

        result = publish_edition(
            SNAPSHOT, HTML, token="test-token", session=session
        )

        self.assertEqual(result["action"], "skip")
        session.put.assert_not_called()

    def test_missing_token_rejected(self):
        with unittest.mock.patch.dict(
            "os.environ", {"NEWSLETTER_PUBLISH_TOKEN": ""}, clear=False
        ):
            with self.assertRaises(RuntimeError):
                publish_edition(SNAPSHOT, HTML)

    def test_failed_upload_does_not_retry(self):
        session = Mock()
        session.get.return_value = response(404)
        session.put.return_value = response(422)

        with self.assertRaises(requests.HTTPError):
            publish_edition(
                SNAPSHOT, HTML, token="test-token", session=session
            )

        self.assertEqual(session.put.call_count, 1)

    def test_unexpected_lookup_failure(self):
        session = Mock()
        session.get.return_value = response(403)

        with self.assertRaises(requests.HTTPError):
            publish_edition(
                SNAPSHOT, HTML, token="test-token", session=session
            )

        session.put.assert_not_called()


if __name__ == "__main__":
    unittest.main()
