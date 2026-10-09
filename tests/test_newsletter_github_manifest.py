"""Tests for publishing the Electric Eye latest-edition manifest."""

import base64
import json
import unittest
from unittest.mock import Mock

from newsletter.github_publish import update_latest_manifest
from newsletter.manifest import build_manifest


SNAPSHOT = {"frequency": "weekly", "identifier": "2026-W41"}


def response(status, data=None):
    result = Mock()
    result.status_code = status
    result.json.return_value = data or {}

    if status >= 400:
        from requests import HTTPError
        result.raise_for_status.side_effect = HTTPError(f"HTTP {status}")

    return result


def manifest_response(manifest, sha="old-sha"):
    return response(200, {
        "sha": sha,
        "content": base64.b64encode(
            json.dumps(manifest).encode()
        ).decode(),
    })


class GitHubManifestTests(unittest.TestCase):

    def test_existing_manifest_updated(self):
        session = Mock()
        session.get.side_effect = [
            response(200),
            manifest_response(build_manifest(monthly="2026-09")),
        ]
        session.put.return_value = response(
            200, {"commit": {"sha": "new-commit"}}
        )

        result = update_latest_manifest(
            SNAPSHOT, token="test-token", session=session
        )

        self.assertEqual(result["action"], "updated")
        self.assertEqual(
            result["manifest"]["editions"]["monthly"]["identifier"],
            "2026-09",
        )
        self.assertEqual(
            result["manifest"]["editions"]["weekly"]["identifier"],
            "2026-W41",
        )

        payload = session.put.call_args.kwargs["json"]
        self.assertEqual(payload["sha"], "old-sha")

    def test_missing_edition_blocks_update(self):
        session = Mock()
        session.get.return_value = response(404)

        with self.assertRaises(RuntimeError):
            update_latest_manifest(
                SNAPSHOT, token="test-token", session=session
            )

        session.put.assert_not_called()

    def test_new_manifest_created(self):
        session = Mock()
        session.get.side_effect = [
            response(200),
            response(404),
        ]
        session.put.return_value = response(
            201, {"commit": {"sha": "first-commit"}}
        )

        result = update_latest_manifest(
            SNAPSHOT, token="test-token", session=session
        )

        self.assertEqual(result["action"], "updated")
        self.assertNotIn(
            "sha", session.put.call_args.kwargs["json"]
        )

    def test_older_edition_does_not_rewind_manifest(self):
        session = Mock()
        session.get.side_effect = [
            response(200),
            manifest_response(build_manifest(weekly="2026-W42")),
        ]

        result = update_latest_manifest(
            SNAPSHOT, token="test-token", session=session
        )

        self.assertEqual(result["action"], "unchanged")
        session.put.assert_not_called()

    def test_conflict_reloads_manifest(self):
        session = Mock()
        session.get.side_effect = [
            response(200),
            manifest_response(build_manifest(monthly="2026-09")),
            manifest_response(
                build_manifest(
                    weekly="2026-W40",
                    monthly="2026-10",
                ),
                sha="new-sha",
            ),
        ]
        session.put.side_effect = [
            response(409),
            response(200, {"commit": {"sha": "final-commit"}}),
        ]

        result = update_latest_manifest(
            SNAPSHOT, token="test-token", session=session
        )

        self.assertEqual(result["action"], "updated")
        self.assertEqual(session.put.call_count, 2)
        self.assertEqual(
            result["manifest"]["editions"]["monthly"]["identifier"],
            "2026-10",
        )
        self.assertEqual(
            session.put.call_args.kwargs["json"]["sha"],
            "new-sha",
        )


if __name__ == "__main__":
    unittest.main()
