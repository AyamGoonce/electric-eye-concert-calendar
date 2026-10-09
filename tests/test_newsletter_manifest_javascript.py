"""Tests for the Blogger-compatible latest-edition manifest."""

import json
import unittest

from newsletter.manifest import (
    build_manifest,
    render_latest_javascript,
)


class NewsletterJavaScriptManifestTests(unittest.TestCase):

    def test_latest_weekly_edition(self):
        manifest = build_manifest(
            weekly="2026-W41",
            monthly="2026-09",
        )
        script = render_latest_javascript(manifest)

        prefix = "window.ElectricEyeNewsletterLatest = Object.freeze("
        self.assertTrue(script.startswith(prefix))
        self.assertTrue(script.endswith(");\n"))

        data = json.loads(script[len(prefix):-3])

        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["latest"]["path"], "weekly/2026-W41.html")
        self.assertEqual(
            data["editions"]["monthly"]["path"],
            "monthly/2026-09.html",
        )

    def test_latest_monthly_edition(self):
        manifest = build_manifest(
            weekly="2026-W40",
            monthly="2026-10",
        )
        script = render_latest_javascript(manifest)

        self.assertIn('"path":"monthly/2026-10.html"', script)

    def test_empty_manifest_rejected(self):
        with self.assertRaises(ValueError):
            render_latest_javascript(build_manifest())


if __name__ == "__main__":
    unittest.main()
