"""Tests for publishing Electric Eye email templates."""

import unittest
from unittest.mock import patch

from newsletter.template_publish import publish_email_template


class NewsletterTemplatePublishTests(unittest.TestCase):

    @patch("newsletter.template_publish.publish_page")
    def test_weekly_template(self, publish_page):
        publish_page.return_value = {
            "action": "created",
            "path": "templates/weekly.html",
        }

        result = publish_email_template("weekly", token="test-token")

        self.assertEqual(result["action"], "created")
        publish_page.assert_called_once()

        args = publish_page.call_args
        self.assertEqual(args.args[0], "templates/weekly.html")
        self.assertIn("ELECTRIC EYE", args.args[1])
        self.assertIn(
            "https://newsletter.electriceyerock.com/weekly/",
            args.args[1],
        )

    @patch("newsletter.template_publish.publish_page")
    def test_invalid_frequency_rejected(self, publish_page):
        with self.assertRaises(ValueError):
            publish_email_template("daily")

        publish_page.assert_not_called()

    @patch("newsletter.template_publish.publish_page")
    def test_monthly_template(self, publish_page):
        publish_page.return_value = {
            "action": "created",
            "path": "templates/monthly.html",
        }

        result = publish_email_template("monthly", token="test-token")

        self.assertEqual(result["action"], "created")
        publish_page.assert_called_once()

        args = publish_page.call_args
        self.assertEqual(args.args[0], "templates/monthly.html")
        self.assertIn("ELECTRIC EYE", args.args[1])
        self.assertIn(
            "https://newsletter.electriceyerock.com/monthly/",
            args.args[1],
        )


if __name__ == "__main__":
    unittest.main()
