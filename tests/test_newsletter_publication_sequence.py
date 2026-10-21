"""Tests for the newsletter runner's publication sequence."""

import sys
import unittest
from unittest.mock import patch

from newsletter.run import main


SNAPSHOT = {
    "frequency": "weekly",
    "identifier": "2026-W41",
    "counts": {"concerts": 2},
}
MANIFEST = {
    "schema_version": 1,
    "editions": {
        "weekly": {
            "identifier": "2026-W41",
            "path": "weekly/2026-W41.html",
        }
    },
}


class NewsletterPublicationSequenceTests(unittest.TestCase):

    @patch("newsletter.run.publish_archive")
    @patch("newsletter.run.publish_landing_pages")
    @patch("newsletter.run.update_latest_javascript")
    @patch("newsletter.run.update_latest_manifest")
    @patch("newsletter.run.publish_edition")
    @patch("newsletter.run.generate")
    def test_successful_publication_order(
        self, generate, publish, update_manifest, update_javascript, landing_pages, archive
    ):
        from unittest.mock import Mock

        calls = Mock()
        generate.return_value = (SNAPSHOT, "<html>OK</html>", {})
        def record_publish(*args):
            calls.publish()
            return {"action": "created"}

        def record_manifest(*args):
            calls.manifest()
            return {"action": "updated", "manifest": MANIFEST}

        def record_javascript(*args):
            calls.javascript()
            return {"action": "updated"}

        def record_landing_pages(*args):
            calls.landing_pages()
            return {"weekly": {"action": "created"}, "monthly": {"action": "created"}}

        def record_archive(*args):
            calls.archive()
            return {
                "counts": {"weekly": 2, "monthly": 1},
                "data": {"action": "updated"},
                "page": {"action": "created"},
            }

        archive.side_effect = record_archive
        landing_pages.side_effect = record_landing_pages
        publish.side_effect = record_publish
        update_manifest.side_effect = record_manifest
        update_javascript.side_effect = record_javascript

        with patch.object(
            sys, "argv",
            ["newsletter.run", "--frequency", "weekly", "--publish"],
        ):
            main()

        self.assertEqual(
            calls.mock_calls,
            [
                unittest.mock.call.publish(),
                unittest.mock.call.manifest(),
                unittest.mock.call.javascript(),
                unittest.mock.call.landing_pages(),
                unittest.mock.call.archive(),
            ],
        )
        update_javascript.assert_called_once_with(MANIFEST)

    @patch("newsletter.run.publish_archive")
    @patch("newsletter.run.publish_landing_pages")
    @patch("newsletter.run.update_latest_javascript")
    @patch("newsletter.run.update_latest_manifest")
    @patch("newsletter.run.publish_edition")
    @patch("newsletter.run.generate")
    def test_failed_publication_stops_manifest_updates(
        self, generate, publish, update_manifest, update_javascript, landing_pages, archive
    ):
        generate.return_value = (SNAPSHOT, "<html>OK</html>", {})
        publish.side_effect = RuntimeError("Upload failed")

        with patch.object(
            sys, "argv",
            ["newsletter.run", "--frequency", "weekly", "--publish"],
        ):
            with self.assertRaisesRegex(RuntimeError, "Upload failed"):
                main()

        update_manifest.assert_not_called()
        update_javascript.assert_not_called()
        landing_pages.assert_not_called()
        archive.assert_not_called()

    @patch("newsletter.run.publish_archive")
    @patch("newsletter.run.publish_landing_pages")
    @patch("newsletter.run.update_latest_javascript")
    @patch("newsletter.run.update_latest_manifest")
    @patch("newsletter.run.publish_edition")
    @patch("newsletter.run.generate")
    def test_existing_edition_repairs_javascript(
        self, generate, publish, update_manifest, update_javascript, landing_pages, archive
    ):
        generate.return_value = (SNAPSHOT, "<html>OK</html>", {})
        publish.return_value = {"action": "skip"}
        update_manifest.return_value = {
            "action": "unchanged",
            "manifest": MANIFEST,
        }
        update_javascript.return_value = {"action": "updated"}

        with patch.object(
            sys, "argv",
            ["newsletter.run", "--frequency", "weekly", "--publish"],
        ):
            main()

        update_javascript.assert_called_once_with(MANIFEST)


if __name__ == "__main__":
    unittest.main()
