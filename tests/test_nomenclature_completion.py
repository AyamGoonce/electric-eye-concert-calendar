import unittest

from concert_calendar.deduplication import (
    _apply_display_capitalization,
    _display_candidates,
)
from concert_calendar.event_titles import is_non_artist_event_title
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import _display_title_parts, event_to_data


def event(headliner, *, co_headliners=None, event_title=None):
    return ConcertEvent(
        date="2030-01-01",
        headliner=headliner,
        venue="Example Hall",
        city="Paris",
        department="75",
        source_names=["Example Source"],
        co_headliners=co_headliners,
        event_title=event_title,
    )


class NomenclatureCompletionTests(unittest.TestCase):

    def test_all_caps_falls_back_to_word_initial_capitalization(self):
        item = event("BETWEEN THE BURIED AND ME")
        _apply_display_capitalization([item], {})
        self.assertEqual(
            item.headliner,
            "Between The Buried And Me",
        )

    def test_all_caps_accented_name_is_normalized(self):
        item = event("AGNÈS OBEL")
        _apply_display_capitalization([item], {})
        self.assertEqual(item.headliner, "Agnès Obel")

    def test_verified_stylization_wins_over_fallback(self):
        item = event("EXAMPLE")
        _apply_display_capitalization(
            [item],
            {"example": "EXAMPLE"},
        )
        self.assertEqual(item.headliner, "EXAMPLE")

    def test_country_tag_is_not_artist_identity(self):
        item = event("Glazyhaze (IT)")
        self.assertEqual(
            _display_title_parts(item),
            ("Glazyhaze", None),
        )

    def test_parenthetical_release_party_is_not_artist_identity(self):
        item = event(
            "Lea Jacta Est (Release Party)",
            co_headliners=["Sunwell", "Marius Atherton"],
            event_title=(
                "Lea Jacta Est (Release Party) "
                "+ Sunwell + Marius Atherton"
            ),
        )
        self.assertEqual(
            _display_title_parts(item),
            ("Lea Jacta Est", "Release Party"),
        )

    def test_new_album_suffix_moves_out_of_artist(self):
        item = event(
            'Chloé Cassandre & Primetime Jazz - '
            'Nouvel album "Rêves fous"'
        )
        self.assertEqual(
            _display_title_parts(item),
            (
                "Chloé Cassandre & Primetime Jazz",
                'Nouvel album "Rêves fous"',
            ),
        )

    def test_live_performance_title_moves_out_of_artist(self):
        item = event("Cotonete - Sunday School (Live)")
        self.assertEqual(
            _display_title_parts(item),
            ("Cotonete", "Sunday School (Live)"),
        )

    def test_quoted_programme_moves_out_of_artist(self):
        item = event(
            "Yann Benoist “des bises et des shows”"
        )
        self.assertEqual(
            _display_title_parts(item),
            ("Yann Benoist", "des bises et des shows"),
        )

    def test_reversed_tribute_keeps_only_performers_on_main_line(self):
        item = event(
            "HOMMAGE À RAY CHARLES avec "
            "Big Dez + Jam blues"
        )
        self.assertEqual(
            _display_title_parts(item),
            (
                "Big Dez + Jam blues",
                "HOMMAGE À RAY CHARLES",
            ),
        )

    def test_live_programme_list_becomes_artist_bill(self):
        item = event(
            "Deadbeat Dubtechno Special: "
            "Tikiman live, Neida live, re:ni"
        )
        self.assertEqual(
            _display_title_parts(item),
            (
                "Tikiman + Neida + re:ni",
                "Deadbeat Dubtechno Special",
            ),
        )

    def test_structured_coheadliners_are_not_rendered_twice(self):
        item = event(
            "FRENCH V.I.P. Women : Marie Amali",
            co_headliners=["Sopycal", "Illa"],
            event_title=(
                "FRENCH V.I.P. Women : "
                "Marie Amali + Sopycal + Illa"
            ),
        )

        self.assertEqual(
            _display_title_parts(item),
            (
                "Marie Amali + Sopycal + Illa",
                "FRENCH V.I.P. Women",
            ),
        )

        public = event_to_data(item)

        self.assertEqual(
            public["h"],
            "Marie Amali + Sopycal + Illa",
        )
        self.assertNotIn("ch", public)

    def test_slash_theme_night_is_non_artist_event(self):
        self.assertTrue(
            is_non_artist_event_title(
                "Electric Feel / Nuit Indie & Synth Pop"
            )
        )

    def test_genre_night_is_non_artist_event(self):
        self.assertTrue(
            is_non_artist_event_title(
                "Emo Night Brooklyn"
            )
        )

    def test_magazine_launch_is_non_artist_event(self):
        self.assertTrue(
            is_non_artist_event_title(
                "NOIZE MAGAZINE - VOL. 3 LAUNCH FESTIVAL"
            )
        )

    def test_artist_with_night_in_name_is_not_rejected(self):
        self.assertFalse(
            is_non_artist_event_title(
                "The Night Flight Orchestra"
            )
        )


    def test_genre_mapping_does_not_override_artist_casing(self):
        item = event("AGNÈS OBEL")
        candidates = _display_candidates([item])
        _apply_display_capitalization([item], candidates)
        self.assertEqual(item.headliner, "Agnès Obel")

    def test_genre_mapping_all_caps_is_not_styling_evidence(self):
        item = event("DEFTONES")
        candidates = _display_candidates([item])
        _apply_display_capitalization([item], candidates)
        self.assertEqual(item.headliner, "Deftones")

    def test_verified_all_caps_artist_style_is_preserved(self):
        item = event("KATSEYE")
        candidates = _display_candidates([item])
        _apply_display_capitalization([item], candidates)
        self.assertEqual(item.headliner, "KATSEYE")

    def test_contextual_all_caps_artist_is_fixed_for_public_display(self):
        item = event(
            "LEA JACTA EST (RELEASE PARTY)",
            co_headliners=["Sunwell"],
            event_title="LEA JACTA EST (RELEASE PARTY) + SUNWELL",
        )
        public = event_to_data(item)
        self.assertEqual(public["h"], "Lea Jacta Est")

    def test_album_rule_beats_mismatched_quoted_title(self):
        item = event(
            'Héloïse Bay - Nouvel album « Une belle histoire"'
        )
        self.assertEqual(
            _display_title_parts(item),
            (
                "Héloïse Bay",
                'Nouvel album « Une belle histoire"',
            ),
        )



if __name__ == "__main__":
    unittest.main()
