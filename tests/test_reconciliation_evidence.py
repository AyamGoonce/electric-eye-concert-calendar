"""Regression tests for source-attributed artist, billing and genre reconciliation."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from concert_calendar.artist_billings import apply_reviewed_artist_billings
from concert_calendar.genres import enrich_event_genres
from concert_calendar.models import ConcertEvent
from concert_calendar.official_programmes import (
    apply_official_programme_credits, load_official_credits,
)


def event(title, day="2027-01-13", venue="Maison des Métallos", **kwargs):
    return ConcertEvent(
        date=day, headliner=title, venue=venue, city="Paris",
        department="75", **kwargs,
    )


class OfficialProgrammeCreditTests(unittest.TestCase):
    def setUp(self):
        self.credit = {
            "venue": "Maison des Métallos",
            "eventTitle": "Si me ves ir con todo, es porque a la noche lloro",
            "artist": "Baby Volcano",
            "startDate": "2027-01-13",
            "endDate": "2027-01-15",
            "sourceUrl": "https://www.maisondesmetallos.paris/spectacle-baby-volcano-si-me-ves-ir-con-todo-es-porque-a-la-noche-lloro",
            "evidenceType": "official_venue_programme_credit",
            "reviewedAt": "2026-11-15",
        }

    def test_official_credit_applies_to_each_separate_performance(self):
        original = self.credit["eventTitle"]
        records = [event(original, day=f"2027-01-{day}", start_time="20:30",
                         ticket_url=f"https://dice.fm/event/{day}",
                         source_names=["DICE"])
                   for day in ("13", "14", "15")]
        report = apply_official_programme_credits(records, records=[self.credit])
        self.assertEqual(len(report["corrected"]), 3)
        self.assertEqual({record.headliner for record in records}, {"Baby Volcano"})
        self.assertEqual({record.event_title for record in records}, {original})
        self.assertTrue(all(record.performers == ["Baby Volcano"] for record in records))
        self.assertEqual(len({record.ticket_url for record in records}), 3)
        self.assertTrue(all(record.raw_title == original for record in records))
        self.assertTrue(all(not record.identity_aliases for record in records))

    def test_other_dates_venues_titles_or_independent_performers_are_untouched(self):
        title = self.credit["eventTitle"]
        records = [
            event(title, "2027-01-16"),
            event(title, "2027-01-13", venue="Café de la Danse"),
            event("Unrelated performance", "2027-01-13"),
            event(title, "2027-01-13", performers=["Different Musician"]),
        ]
        report = apply_official_programme_credits(records, records=[self.credit])
        self.assertEqual(report["corrected"], [])
        self.assertEqual(len(report["skipped"]), 1)
        self.assertTrue(all(r.headliner != "Baby Volcano" for r in records))

    def test_conflicting_official_evidence_is_not_silently_selected(self):
        title = self.credit["eventTitle"]
        duplicate = dict(self.credit, artist="Another Artist")
        row = event(title)
        result = apply_official_programme_credits([row], records=[self.credit, duplicate])
        self.assertEqual(row.headliner, title)
        self.assertEqual(len(result["ambiguous"]), 1)

    def test_source_registry_requires_grounded_records(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "credits.json"
            path.write_text(json.dumps({"schemaVersion": 1, "records": [self.credit]}))
            self.assertEqual(len(load_official_credits(path)), 1)
            path.write_text(json.dumps({"schemaVersion": 1, "records": [
                dict(self.credit, sourceUrl="http://example.com/show")
            ]}))
            with self.assertRaises(ValueError):
                load_official_credits(path)


class ArtistEntityEvidenceTests(unittest.TestCase):
    def test_verified_complete_slash_bill_is_separated(self):
        raw = "Dorado Schmitt / Noé Reinhardt / William Brunard"
        row = event(raw, venue="Sunset/Sunside — Sunside", source_names=["DICE"])
        identities = {
            "dorado schmitt": "Dorado Schmitt",
            "noe reinhardt": "Noé Reinhardt",
            "william brunard": "William Brunard",
        }
        apply_reviewed_artist_billings([row], identity_catalog=identities, reviews={})
        self.assertEqual(row.headliner, "Dorado Schmitt")
        self.assertEqual(row.co_headliners, ["Noé Reinhardt", "William Brunard"])
        self.assertEqual(row.raw_title, raw)

    def test_unknown_components_and_known_whole_band_are_preserved(self):
        rows = [
            event("Dorado Schmitt / Unknown Project", source_names=["DICE"]),
            event("Earth, Wind & Fire", source_names=["DICE"]),
        ]
        identities = {
            "dorado schmitt": "Dorado Schmitt",
            "earth wind fire": "Earth, Wind & Fire",
        }
        apply_reviewed_artist_billings(rows, identity_catalog=identities, reviews={})
        self.assertEqual(rows[0].headliner, "Dorado Schmitt / Unknown Project")
        self.assertIsNone(rows[0].co_headliners)
        self.assertEqual(rows[1].headliner, "Earth, Wind & Fire")
        self.assertIsNone(rows[1].co_headliners)

    def test_structured_independent_artist_can_validate_other_full_bill(self):
        combined = event(
            "Cha + ThelmA + Psykasya", source_names=["DICE"])
        names = ["Cha", "ThelmA", "Psykasya"]
        standalone = [
            event(name, "2027-01-14", source_names=["DICE"], performers=[name])
            for name in names
        ]
        apply_reviewed_artist_billings(
            [combined, *standalone], identity_catalog={}, reviews={}
        )
        self.assertEqual(combined.headliner, "Cha")
        self.assertEqual(combined.co_headliners, ["ThelmA", "Psykasya"])


class GenreEvidenceConsensusTests(unittest.TestCase):
    def test_repeated_source_genre_is_reused_for_exact_solo_artist(self):
        rows = [
            event("Example Quartet", "2027-01-13", venue="New Morning",
                  genre="Jazz", genre_source="New Morning"),
            event("Example Quartet", "2027-01-14", venue="Café de la Danse",
                  genre="Jazz", genre_source="Café de la Danse"),
            event("Example Quartet", "2027-01-15", venue="Le Chinois"),
        ]
        result = enrich_event_genres(rows)
        self.assertEqual(rows[2].genre_public, "Jazz / Blues")
        self.assertEqual(rows[2].genre_method, "artist_source_consensus")
        self.assertGreaterEqual(result["artist_source_consensus"], 1)

    def test_one_source_or_conflicting_genres_do_not_guess(self):
        single = [
            event("Unclassified Example", "2027-01-13", venue="New Morning",
                  genre="Jazz"),
            event("Unclassified Example", "2027-01-14", venue="Le Chinois"),
        ]
        enrich_event_genres(single)
        self.assertIsNone(single[1].genre_public)
        conflicting = [
            event("Mixed Example", "2027-01-13", venue="New Morning",
                  genre="Jazz"),
            event("Mixed Example", "2027-01-14", venue="Le Chinois",
                  genre="Rock"),
            event("Mixed Example", "2027-01-15", venue="Le Hasard Ludique"),
        ]
        enrich_event_genres(conflicting)
        self.assertIsNone(conflicting[-1].genre_public)


if __name__ == "__main__":
    unittest.main()
