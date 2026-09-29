import unittest
from unittest.mock import patch

from concert_calendar.billing_semantics import normalize_event_semantics
from concert_calendar.content_index import enrich_events
from concert_calendar.deduplication import deduplicate_events, normalize_headliner
from concert_calendar.event_state import assign_performance_identities, canonical_event_identity
from concert_calendar.genres import enrich_event_genres
from concert_calendar.models import ConcertEvent
from concert_calendar.scrapers.supersonic import is_non_concert_event
from concert_calendar.sources import classify_event_eligibility


TRIBUTE_IDENTITIES = (
    ("ABBA MANIA", "ABBA"),
    ("The Australian Pink Floyd Show", "Pink Floyd"),
    ("Nirvana U.K.", "Nirvana"),
    ("One Night of Queen", "Queen"),
    ("The Iron Maidens", "Iron Maiden"),
    ("Dark Star Orchestra", "Grateful Dead"),
    ("The Musical Box", "Genesis"),
    ("A Tribute to Queen", "Queen"),
)


def event(name, **kwargs):
    return ConcertEvent(
        date="2027-10-09", headliner=name, venue="Le Dôme de Paris",
        city="Paris", department="75", **kwargs,
    )


class TributeIdentityBarrierTests(unittest.TestCase):
    def test_tribute_acts_and_generic_productions_are_eligible(self):
        for tribute, _ in TRIBUTE_IDENTITIES:
            with self.subTest(tribute=tribute):
                self.assertEqual((True, None), classify_event_eligibility(event(tribute)))
        self.assertEqual(
            (True, None),
            classify_event_eligibility(event("Mania, The Abba Tribute")),
        )
        self.assertFalse(is_non_concert_event("A Tribute to Queen"))

    def test_tribute_names_do_not_normalize_to_referenced_artists(self):
        for tribute, original in TRIBUTE_IDENTITIES:
            with self.subTest(tribute=tribute):
                self.assertNotEqual(normalize_headliner(tribute), normalize_headliner(original))
                self.assertNotEqual(
                    canonical_event_identity(event(tribute)),
                    canonical_event_identity(event(original)),
                )
                original_identity = canonical_event_identity(event(original))
                candidate = event(tribute)
                assign_performance_identities([candidate], {
                    original_identity: {
                        "public_id": original_identity[:16],
                        "first_seen": "2026-01-01T00:00:00Z",
                        "base_identity": original_identity,
                    },
                })
                self.assertNotEqual(original_identity[:16], candidate._public_id)

    def test_generic_tribute_production_is_not_replaced_by_subject_in_description(self):
        tribute = event(
            "A Tribute to Queen",
            description="Concert animé par Queen, en hommage au groupe.",
        )
        normalize_event_semantics(tribute)
        self.assertEqual("A Tribute to Queen", tribute.headliner)

    def test_tribute_and_original_concert_do_not_deduplicate(self):
        for tribute, original in TRIBUTE_IDENTITIES:
            with self.subTest(tribute=tribute):
                result = deduplicate_events([event(tribute), event(original)])
                self.assertEqual(2, len(result))
                self.assertEqual(
                    {normalize_headliner(tribute), normalize_headliner(original)},
                    {normalize_headliner(item.headliner) for item in result},
                )

    def test_original_artist_index_does_not_link_to_tribute_act(self):
        for tribute, original in TRIBUTE_IDENTITIES:
            with self.subTest(tribute=tribute):
                record = event(tribute)
                enrich_events([record], {
                    "artists": {
                        "original": {"n": original, "al": [], "ar": ["article-1"]},
                    },
                })
                self.assertIsNone(record.electric_eye_links)

    def test_genre_lookup_uses_tribute_identity_not_referenced_artist(self):
        mappings = {
            "artists": {"queen": {"genre": "Rock", "evidence_source": "Queen evidence"}},
            "overrides": {},
        }
        record = event("A Tribute to Queen")
        with patch("concert_calendar.genres.load_reviewed_mappings", return_value=mappings):
            enrich_event_genres([record])
        self.assertIsNone(record.genre_public)
        mappings["artists"]["a tribute to queen"] = {
            "genre": "Pop", "evidence_source": "Production evidence",
        }
        with patch("concert_calendar.genres.load_reviewed_mappings", return_value=mappings):
            enrich_event_genres([record])
        self.assertEqual("Pop", record.genre_public)
        self.assertEqual("Production evidence", record.genre_source)


if __name__ == "__main__":
    unittest.main()
