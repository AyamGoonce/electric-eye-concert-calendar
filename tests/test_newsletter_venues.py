"""Regression tests for newsletter venue filtering."""

import unittest

from newsletter.venues import (
    VENUE_ALIASES,
    approved_venue,
    filter_concerts_by_venue,
)


class NewsletterVenueTests(unittest.TestCase):

    def test_all_approved_venues(self):
        for venue in VENUE_ALIASES:
            with self.subTest(venue=venue):
                self.assertEqual(approved_venue(venue), venue)

    def test_venue_aliases(self):
        cases = {
            "AccorHotels Arena": "Accor Arena",
            "Paris-Bercy": "Accor Arena",
            "Le Zénith Paris – La Villette": "Zénith",
            "L'Olympia Bruno Coquatrix": "Olympia",
            "L’Élysée Montmartre": "Élysée Montmartre",
            "La Machine du Moulin Rouge – Central": "La Machine du Moulin Rouge",
        }
        for original, expected in cases.items():
            with self.subTest(venue=original):
                self.assertEqual(approved_venue(original), expected)

    def test_unapproved_venues(self):
        for venue in ("Supersonic", "Glazart", "Nouveau Casino", "La Bellevilloise"):
            with self.subTest(venue=venue):
                self.assertIsNone(approved_venue(venue))

    def test_filter_preserves_all_eligible_concerts(self):
        concerts = [
            {"id": "1", "venue": "Bataclan"},
            {"id": "2", "venue": "Supersonic"},
            {"id": "3", "venue": "Petit Bain"},
            {"id": "4", "venue": "Bataclan"},
        ]
        result = filter_concerts_by_venue(concerts)
        self.assertEqual([item["id"] for item in result], ["1", "3", "4"])


if __name__ == "__main__":
    unittest.main()
