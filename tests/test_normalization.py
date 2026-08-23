import unittest

from concert_calendar.deduplication import (
    deduplicate_events,
    normalize_headliner,
)
from concert_calendar.models import ConcertEvent
from concert_calendar.venues import normalize_event_venue


def make_event(headliner, venue="La Boule Noire"):
    return ConcertEvent(
        date="2026-09-27",
        headliner=headliner,
        venue=venue,
        city="Paris",
        department="75",
    )


class ArtistNormalizationTests(unittest.TestCase):
    def test_known_joined_artist_alias_merges(self):
        events = deduplicate_events(
            [make_event("Day We Ran"), make_event("DAYWERAN")]
        )

        self.assertEqual(1, len(events))

    def test_known_diacritic_variant_merges(self):
        events = deduplicate_events(
            [make_event("GAËLLE JOLY"), make_event("GAELLE JOLY")]
        )

        self.assertEqual(1, len(events))

    def test_known_source_punctuation_variants_merge(self):
        pairs = [
            ("LA P’TITÉ FUMÉE", "LA P’TITE FUMÉE"),
            (
                "ZOH AMBA (LES FEMMES S’EN MÊLENT)",
                "Zoh Amba (Les Femmes s'en Mêlent)",
            ),
        ]

        for left, right in pairs:
            with self.subTest(left=left, right=right):
                self.assertEqual(
                    1,
                    len(deduplicate_events([make_event(left), make_event(right)])),
                )

    def test_unlisted_spacing_difference_does_not_merge(self):
        events = deduplicate_events(
            [make_event("AB CD"), make_event("ABCD")]
        )

        self.assertEqual(2, len(events))

    def test_meaningful_punctuation_is_preserved(self):
        self.assertNotEqual(
            normalize_headliner("Artist + Guest"),
            normalize_headliner("Artist Guest"),
        )

    def test_distinct_time_suffixes_do_not_merge(self):
        events = deduplicate_events(
            [make_event("TIGERCUB – 16H"), make_event("TIGERCUB – 20H")]
        )

        self.assertEqual(2, len(events))

    def test_duplicate_metadata_is_merged(self):
        first = make_event("Day We Ran")
        first.promoters = ["AEG Presents France"]
        second = make_event("DAYWERAN")
        second.openers = ["Support Act"]
        second.genre = "Rock"
        second.ticket_url = "https://example.com/tickets"

        merged = deduplicate_events([first, second])[0]

        self.assertEqual(["AEG Presents France"], merged.promoters)
        self.assertEqual(["Support Act"], merged.openers)
        self.assertEqual("Rock", merged.genre)
        self.assertEqual("https://example.com/tickets", merged.ticket_url)


class VenueNormalizationTests(unittest.TestCase):
    def test_article_variant_normalizes_to_point_ephemere(self):
        event = normalize_event_venue(
            make_event("MERYL STREEK", "LE POINT ÉPHÉMÈRE")
        )

        self.assertEqual("Point Éphémère", event.venue)

    def test_distinct_neighboring_venues_remain_distinct(self):
        cigale = normalize_event_venue(make_event("Artist", "La Cigale"))
        boule_noire = normalize_event_venue(
            make_event("Artist", "La Boule Noire")
        )

        self.assertNotEqual(cigale.venue, boule_noire.venue)

    def test_distinct_rooms_remain_distinct(self):
        sunset = normalize_event_venue(make_event("Artist", "Sunset"))
        sunside = normalize_event_venue(make_event("Artist", "Sunside"))

        self.assertNotEqual(sunset.venue, sunside.venue)


if __name__ == "__main__":
    unittest.main()
