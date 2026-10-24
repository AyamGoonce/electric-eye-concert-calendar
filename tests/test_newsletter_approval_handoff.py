"""Tests for the newsletter publication-to-approval handoff."""

import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
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


class ApprovalHandoffTests(unittest.TestCase):

    def execute(self, *, failure=False, scheduled_skip=False):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "github_output"
            output_path.touch()

            with (
                patch.dict(os.environ, {"GITHUB_OUTPUT": str(output_path)}),
                patch("newsletter.run.generate") as generate,
                patch("newsletter.run.publish_edition") as publish,
                patch("newsletter.run.update_latest_manifest") as manifest,
                patch("newsletter.run.update_latest_javascript"),
                patch("newsletter.run.publish_landing_pages"),
                patch("newsletter.run.publish_archive") as archive,
                patch("newsletter.run.is_publication_day") as publication_day,
            ):
                generate.return_value = (
                    SNAPSHOT,
                    "<html>OK</html>",
                    {},
                )
                publish.return_value = {"action": "created"}
                manifest.return_value = {
                    "action": "updated",
                    "manifest": MANIFEST,
                }
                archive.return_value = {
                    "counts": {"weekly": 1, "monthly": 0},
                    "data": {"action": "updated"},
                    "page": {"action": "updated"},
                }
                publication_day.return_value = not scheduled_skip

                if failure:
                    publish.side_effect = RuntimeError("Simulated upload failure")

                argv = [
                    "newsletter.run",
                    "--frequency",
                    "weekly",
                    "--publish",
                ]
                if scheduled_skip:
                    argv.append("--scheduled")

                with patch.object(sys, "argv", argv):
                    if failure:
                        with self.assertRaisesRegex(
                            RuntimeError, "Simulated upload failure"
                        ):
                            main()
                    else:
                        main()

                output = output_path.read_text(encoding="utf-8")

                if scheduled_skip:
                    generate.assert_not_called()
                    publish.assert_not_called()

                return output

    def test_successful_publication_exposes_edition(self):
        output = self.execute()
        self.assertEqual(
            output,
            "frequency=weekly\nidentifier=2026-W41\n",
        )

    def test_failed_publication_does_not_expose_edition(self):
        self.assertEqual(self.execute(failure=True), "")

    def test_scheduled_skip_does_not_expose_edition(self):
        self.assertEqual(self.execute(scheduled_skip=True), "")


if __name__ == "__main__":
    unittest.main()
