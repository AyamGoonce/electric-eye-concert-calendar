"""Tests for synchronizing Blogger's latest.js with latest.json."""

import base64
import json
import unittest
from unittest.mock import Mock

import requests

from newsletter.github_publish import update_latest_javascript
from newsletter.manifest import build_manifest, render_latest_javascript


def response(status, data=None):
    result = Mock()
    result.status_code = status
    result.json.return_value = data or {}
    result.raise_for_status.side_effect = (
        requests.HTTPError(f"HTTP {status}") if status >= 400 else None
    )
    return result


def encoded(text):
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def manifest_response(manifest):
    return response(200, {
        "content": encoded(json.dumps(manifest)),
        "sha": "manifest-sha",
    })


def javascript_response(manifest, sha="old-js-sha"):
    return response(200, {
        "content": encoded(render_latest_javascript(manifest)),
        "sha": sha,
    })


class JavaScriptPublisherTests(unittest.TestCase):

    def test_creates_latest_javascript(self):
        manifest = build_manifest(monthly="2026-09")
        session = Mock()
        session.get.side_effect = [
            manifest_response(manifest),
            response(200),  # Published monthly edition exists
            response(404),  # latest.js does not exist yet
        ]
        session.put.return_value = response(
            201, {"commit": {"sha": "created-sha"}}
        )

        result = update_latest_javascript(
            manifest, token="test-token", session=session
        )

        self.assertEqual(result["action"], "updated")
        payload = session.put.call_args.kwargs["json"]
        self.assertNotIn("sha", payload)
        self.assertEqual(
            base64.b64decode(payload["content"]).decode("utf-8"),
            render_latest_javascript(manifest),
        )

    def test_unchanged_manifest_does_not_write(self):
        manifest = build_manifest(weekly="2026-W41")
        session = Mock()
        session.get.side_effect = [
            manifest_response(manifest),
            response(200),
            javascript_response(manifest),
        ]

        result = update_latest_javascript(
            manifest, token="test-token", session=session
        )

        self.assertEqual(result["action"], "unchanged")
        session.put.assert_not_called()

    def test_missing_edition_prevents_update(self):
        manifest = build_manifest(monthly="2026-09")
        session = Mock()
        session.get.side_effect = [
            manifest_response(manifest),
            response(404),
        ]

        with self.assertRaises(RuntimeError):
            update_latest_javascript(
                manifest, token="test-token", session=session
            )

        session.put.assert_not_called()

    def test_conflict_reloads_authoritative_manifest(self):
        old = build_manifest(weekly="2026-W40")
        newer = build_manifest(
            weekly="2026-W41",
            monthly="2026-09",
        )
        session = Mock()
        session.get.side_effect = [
            manifest_response(old),
            response(200),
            response(404),
            manifest_response(newer),
            response(200),
            response(200),
            response(404),
        ]
        session.put.side_effect = [
            response(409),
            response(201, {"commit": {"sha": "newer-sha"}}),
        ]

        result = update_latest_javascript(
            old, token="test-token", session=session
        )

        self.assertEqual(result["action"], "updated")
        self.assertEqual(session.put.call_count, 2)
        final_payload = session.put.call_args.kwargs["json"]
        self.assertEqual(
            base64.b64decode(final_payload["content"]).decode("utf-8"),
            render_latest_javascript(newer),
        )

    def test_manifest_fetch_failure_does_not_write(self):
        session = Mock()
        session.get.return_value = response(403)

        with self.assertRaises(requests.HTTPError):
            update_latest_javascript(
                build_manifest(monthly="2026-09"),
                token="test-token",
                session=session,
            )

        session.put.assert_not_called()


if __name__ == "__main__":
    unittest.main()
