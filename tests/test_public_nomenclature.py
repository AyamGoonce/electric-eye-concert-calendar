import unittest

from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import _display_title_parts


def event(headliner, event_title=None):
    return ConcertEvent(
        date="2030-01-01",
        headliner=headliner,
        venue="Example Hall",
        city="Paris",
        department="75",
        source_names=["Example Source"],
        event_title=event_title,
    )


class PublicNomenclatureTests(unittest.TestCase):

    def test_presents_wrapper_moves_below_artist(self):
        item = event(
            "Les Nuits de la Bomba présentent Sonido Bomba"
        )

        self.assertEqual(
            _display_title_parts(item),
            ("Sonido Bomba", "Les Nuits de la Bomba"),
        )

    def test_release_party_wrapper_moves_below_artist(self):
        item = event(
            "RELEASE PARTY NO BITCHES - PETASSE ENGAGEE"
        )

        self.assertEqual(
            _display_title_parts(item),
            ("PETASSE ENGAGEE", "RELEASE PARTY NO BITCHES"),
        )

    def test_programme_prefix_before_multi_artist_bill_moves_below(self):
        item = event(
            "FRENCH V.I.P. Women : Marie Amali + Sopycal + Illa"
        )

        self.assertEqual(
            _display_title_parts(item),
            (
                "Marie Amali + Sopycal + Illa",
                "FRENCH V.I.P. Women",
            ),
        )

    def test_richer_same_programme_event_title_restores_full_bill(self):
        item = event(
            "FRENCH V.I.P. Women : Marie Amali",
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

    def test_unrelated_event_title_does_not_replace_artist_bill(self):
        item = event(
            "Example Series : Alpha",
            event_title="Different Series : Alpha + Beta",
        )

        self.assertEqual(
            _display_title_parts(item),
            (
                "Alpha",
                "Different Series : Alpha + Beta",
            ),
        )

    def test_tribute_suffix_moves_below_artist(self):
        item = event(
            "De Chassy / Ghomari / Nisse – Hommage à Carla Bley"
        )

        self.assertEqual(
            _display_title_parts(item),
            (
                "De Chassy / Ghomari / Nisse",
                "Hommage à Carla Bley",
            ),
        )

    def test_sentence_like_performance_title_moves_below_artist(self):
        item = event(
            "RAMON PIPIN – Une folle envie de bisser"
        )

        self.assertEqual(
            _display_title_parts(item),
            (
                "RAMON PIPIN",
                "Une folle envie de bisser",
            ),
        )

    def test_tour_suffix_moves_below_artist(self):
        item = event(
            "Example Artist - The Example World Tour"
        )

        self.assertEqual(
            _display_title_parts(item),
            (
                "Example Artist",
                "Example Artist - The Example World Tour",
            ),
        )

    def test_dash_between_possible_artist_names_is_not_blindly_split(self):
        item = event(
            "Alpha – Alice on the Roof"
        )

        self.assertEqual(
            _display_title_parts(item),
            (
                "Alpha – Alice on the Roof",
                None,
            ),
        )

    def test_independent_event_title_is_preserved(self):
        item = event(
            "Example Artist – Hommage à Example Composer",
            event_title="Special Anniversary Programme",
        )

        self.assertEqual(
            _display_title_parts(item),
            (
                "Example Artist",
                "Special Anniversary Programme",
            ),
        )


if __name__ == "__main__":
    unittest.main()
