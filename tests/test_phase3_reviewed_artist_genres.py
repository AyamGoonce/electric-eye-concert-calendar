"""Reviewed artist genre tranche (Phase 3), without event-specific exceptions."""
import unittest

from concert_calendar.genres import enrich_event_genres, load_reviewed_mappings
from concert_calendar.models import ConcertEvent


REVIEWED = {
    "Brooke Combe": "R&B / Soul / Funk",
    "Damien Rice": "Folk / Country",
    "Groundation": "Reggae / Dub / Ska",
    "Joe Yorke": "Reggae / Dub / Ska",
    "Lambrini Girls": "Rock / Indie / Punk",
    "Les Garçons Bouchers": "Rock / Indie / Punk",
    "Marlon Hoffstadt": "Electronic",
    "Moha MMZ": "Hip-hop / Rap",
    "Poppy-Fusée": "Pop",
    "Sonny Gullage": "Jazz / Blues",
    "You Said Strange": "Rock / Indie / Punk",
}


def event(name, **updates):
    values = {
        "date": "2027-03-15", "headliner": name,
        "venue": "Le Trabendo", "city": "Paris", "department": "75",
    }
    values.update(updates)
    return ConcertEvent(**values)


class Phase3ArtistReviewTests(unittest.TestCase):
    def test_approved_sources_are_recorded_with_date_and_artist_identity(self):
        mappings = load_reviewed_mappings()
        from concert_calendar.deduplication import normalize_artist_component
        for name, label in REVIEWED.items():
            with self.subTest(artist=name):
                record = mappings["artists"][normalize_artist_component(name)]
                self.assertEqual(record["genre"], label)
                self.assertTrue(record["evidence_source"].startswith("https://"))
                self.assertEqual(record["review_date"], "2026-11-16")
                self.assertEqual(record["evidence_type"], "reviewed_artist_profile_genre")

    def test_exact_new_identities_resolve_without_source_genre(self):
        events = [event(name) for name in REVIEWED]
        report = enrich_event_genres(events)
        self.assertEqual(report["blank"], 0)
        for name, row in zip(REVIEWED, events):
            with self.subTest(artist=name):
                self.assertEqual(row.genre_public, REVIEWED[name])
                self.assertEqual(row.genre_method, "artist_mapping")

    def test_explicit_source_taxonomy_still_wins(self):
        row = event("Lambrini Girls", genre="Electronic", genre_source="Venue")
        enrich_event_genres([row])
        self.assertEqual(row.genre_public, "Electronic")
        self.assertEqual(row.genre_method, "source_explicit")


if __name__ == "__main__":
    unittest.main()
