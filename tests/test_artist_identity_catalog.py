"""Tests for conservative artist identities harvested from current source records."""
import unittest

from concert_calendar.artist_identity_catalog import (
    artist_candidate,
    collect_structured_artist_evidence,
)
from concert_calendar.artist_billings import apply_reviewed_artist_billings
from concert_calendar.models import ConcertEvent


def record(title, *, source="Official source", performers=None, day="2026-12-18"):
    return ConcertEvent(
        date=day, headliner=title, raw_title=title,
        venue="Le Chinois", city="Montreuil", department="93",
        source_names=[source], performers=performers,
        ticket_url="https://example.org/event/" + day,
    )


class SourceIdentityHarvestTests(unittest.TestCase):
    def test_real_separately_credited_artists_expand_catalogue(self):
        source = record("Blackgold + Sumo Cyco + Hyro The Hero",
                        performers=["Blackgold", "Sumo Cyco", "Hyro The Hero"])
        additions, audit = collect_structured_artist_evidence([source])
        self.assertEqual(set(additions), {
            "blackgold", "sumo cyco", "hyro the hero",
        })
        self.assertEqual(audit["new_verified"], 3)
        self.assertTrue(all(
            row["evidence"][0]["evidence_type"] == "separate_source_performer_field"
            for row in audit["verified_records"]
        ))

    def test_unstructured_flat_title_is_not_proof(self):
        title = "Blackgold + Sumo Cyco + Hyro The Hero"
        additions, audit = collect_structured_artist_evidence([record(title)])
        self.assertEqual(additions, {})
        self.assertEqual(audit["new_verified"], 0)

    def test_short_name_requires_two_independent_sources(self):
        events = [
            record("Cha + ThelmA", source="DICE", performers=["Cha", "ThelmA"]),
        ]
        additions, audit = collect_structured_artist_evidence(events)
        self.assertNotIn("cha", additions)
        self.assertEqual(audit["unresolved"], 1)
        events.append(record("Cha + Psykasya", source="Official venue",
                             performers=["Cha", "Psykasya"]))
        additions, _ = collect_structured_artist_evidence(events)
        self.assertEqual(additions["cha"], "Cha")

    def test_unknown_alias_and_conflicting_spelling_not_invented(self):
        events = [
            record("AC/DC + First Act", performers=["AC/DC", "First Act"]),
            record("AC DC + Second Act", performers=["AC DC", "Second Act"]),
        ]
        additions, audit = collect_structured_artist_evidence(events)
        self.assertNotIn("ac dc", additions)
        self.assertTrue(any(row["reason"] == "variant_spelling_requires_review"
                            for row in audit["unresolved_records"]))

    def test_reviewed_canonical_identity_wins(self):
        row = record("HYRO THE HERO + Blackgold",
                     performers=["HYRO THE HERO", "Blackgold"])
        additions, audit = collect_structured_artist_evidence(
            [row], existing={"hyro the hero": "Hyro The Hero"})
        self.assertNotIn("hyro the hero", additions)
        self.assertEqual(audit["already_known"], 1)

    def test_opaque_or_nonmusical_performer_fields_rejected(self):
        titles = [
            ("Artist + Guests", ["Artist", "Guests"]),
            ("Release Party + Actual Musician", ["Release Party", "Actual Musician"]),
            ("Mystery + Event", ["Mystery + Event", "Other"]),
        ]
        for title, performers in titles:
            with self.subTest(title=title):
                additions, audit = collect_structured_artist_evidence(
                    [record(title, performers=performers)])
                self.assertFalse(additions)
                self.assertTrue(audit["rejected"])

    def test_band_names_and_separator_protection(self):
        self.assertTrue(artist_candidate("Hyro The Hero"))
        self.assertFalse(artist_candidate("One + Two"))
        self.assertFalse(artist_candidate("Guest"))
        self.assertFalse(artist_candidate("VIP release party"))
        self.assertFalse(artist_candidate("Bliss My Heart x Cliff Estatof"))
        self.assertFalse(artist_candidate("THE DEAD DAISIES ft. KELLY HANSEN"))
        self.assertFalse(artist_candidate("Artist vs. Artist"))
        self.assertTrue(artist_candidate("The xx"))


    def test_source_identity_can_resolve_a_separate_opaque_billing(self):
        title = "Blackgold + Sumo Cyco + Hyro The Hero"
        opaque = record(title, source="DICE")
        verified = record(title, source="Official venue",
                          performers=["Blackgold", "Sumo Cyco", "Hyro The Hero"])
        diagnostics = {}
        apply_reviewed_artist_billings(
            [opaque, verified], diagnostics,
            identity_catalog={},
        )
        self.assertEqual(opaque.headliner, "Blackgold")
        self.assertEqual(opaque.co_headliners, ["Sumo Cyco", "Hyro The Hero"])
        self.assertEqual(diagnostics["artist_identity_catalog"]["new_verified"], 3)


if __name__ == "__main__":
    unittest.main()
