"""Tests for permanent Electric Eye newsletter landing pages."""

import unittest

from newsletter.landing_pages import render_landing_page


class NewsletterLandingPageTests(unittest.TestCase):

    def test_weekly_page(self):
        html = render_landing_page("weekly")
        self.assertIn("Electric Eye — Latest Weekly Newsletter", html)
        self.assertIn('var frequency = "weekly";', html)
        self.assertIn('<script src="../latest.js"></script>', html)
        self.assertIn("manifest.editions[frequency]", html)
        self.assertIn("window.location.replace(", html)

    def test_monthly_page(self):
        html = render_landing_page("monthly")
        self.assertIn("Electric Eye — Latest Monthly Newsletter", html)
        self.assertIn('var frequency = "monthly";', html)
        self.assertIn('<script src="../latest.js"></script>', html)
        self.assertIn("manifest.editions[frequency]", html)

    def test_invalid_frequency_rejected(self):
        with self.assertRaises(ValueError):
            render_landing_page("daily")

    def test_pages_use_relative_paths(self):
        for frequency in ("weekly", "monthly"):
            html = render_landing_page(frequency)
            self.assertIn('new URL("../" + edition.path, window.location.href)', html)
            self.assertNotIn("ayamgoonce.github.io", html)


if __name__ == "__main__":
    unittest.main()
