"""Regression coverage for structural non-concert programme classification."""

import unittest

from concert_calendar.models import ConcertEvent
from concert_calendar.sources import (
    classify_event_eligibility,
    filter_eligible_retained_events,
)


def event(headliner, **changes):
    fields = {
        "date": "2026-12-16",
        "headliner": headliner,
        "venue": "Ground Control Gare de Lyon",
        "city": "Paris",
        "department": "75",
    }
    fields.update(changes)
    return ConcertEvent(**fields)


class NonConcertProgrammeTests(unittest.TestCase):
    def test_off_air_political_discussion_without_specific_brand_exception(self):
        row = event(
            "Hors Antenne : Socialter & Au Poste - Face à l'extrême droite, "
            "quelle riposte écolo ?",
            genre="Pop / Rock",
        )
        self.assertEqual(
            classify_event_eligibility(row), (False, "non_music_discussion")
        )

    def test_raw_title_survives_headliner_rewrite(self):
        row = event(
            "Socialter",
            raw_title="Hors Antenne : Socialter & Au Poste - Face à "
            "l'extrême droite, quelle riposte écolo ?",
        )
        self.assertEqual(
            classify_event_eligibility(row), (False, "non_music_discussion")
        )

    def test_activity_formats_are_structural_not_venue_specific(self):
        for title in (
            "Table ronde : le futur des médias",
            "Conférence-débat : écologie et culture",
            "Cin é-débat : le documentaire".replace("Cin é", "Ciné"),
            "Projection : un film documentaire",
            "Atelier de dessin",
            "Rencontre avec une autrice",
            "Stand-up comedy : soirée humour",
        ):
            with self.subTest(title=title):
                self.assertEqual(
                    classify_event_eligibility(
                        event(title, venue="La Maroquinerie", genre="Rock")
                    )[0], False,
                )

    def test_artist_name_or_theme_alone_does_not_exclude(self):
        for title in (
            "Hors Antenne",
            "La Politique",
            "Débat",
            "Socialter",
            "Face à Face",
            "Les Ateliers",
        ):
            with self.subTest(title=title):
                self.assertTrue(classify_event_eligibility(event(title))[0])

    def test_clear_music_context_preserves_hybrid_formats(self):
        for title in (
            "Hors Antenne : Concert live music",
            "Rencontre avec le groupe - concert acoustique",
            "Table ronde et concert de jazz",
        ):
            with self.subTest(title=title):
                self.assertTrue(classify_event_eligibility(event(title))[0])

    def test_retained_snapshot_cannot_reintroduce_nonconcert(self):
        concert = event("Groupe Exemple", genre="Rock")
        discussion = event(
            "Hors Antenne : Au Poste - Quelle riposte écolo ?"
        )
        self.assertEqual(
            filter_eligible_retained_events([discussion, concert]),
            [concert],
        )

    def test_structured_category_still_excludes_discussion(self):
        self.assertFalse(
            classify_event_eligibility(
                event("Débattre demain", category="table ronde")
            )[0]
        )


if __name__ == "__main__":
    unittest.main()
