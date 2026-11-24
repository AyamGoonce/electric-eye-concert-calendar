"""Current official-name and programme-context billing regressions.

These examples require corroborated identities; punctuation alone never
authorizes a generic split.
"""
import unittest

from concert_calendar.artist_billings import resolve_artist_billings
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import event_to_data


def event(title, date, venue, *, source=None, event_title=None):
    return ConcertEvent(
        date=date, headliner=title, venue=venue, city="Paris",
        department="75", source_names=[source or venue],
        event_title=event_title,
    )


class CurrentArtistBillingDisplayRegressions(unittest.TestCase):
    def assert_bill(self, title, date, venue, expected, *, source=None, context=None, event_title=None):
        item = event(title, date, venue, source=source, event_title=event_title)
        resolve_artist_billings([item])
        self.assertEqual(expected[0], item.headliner)
        self.assertEqual(expected[1:], item.co_headliners or [])
        exported = event_to_data(item)
        self.assertEqual(expected[0], exported["h"])
        self.assertEqual(expected[1:], exported.get("ch", []))
        if context is not None:
            self.assertEqual(context, item.event_title)
            self.assertEqual(context, exported.get("et"))
        self.assertEqual(title, item.raw_title)

    def test_with_artist_connector_is_supported_only_for_known_identities(self):
        self.assert_bill(
            "BOY GEORGE w/CULTURE CLUB & SHAGGY", "2026-12-04", "Accor Arena",
            ["Boy George", "Culture Club", "Shaggy"],
        )

    def test_nyokobop_festival_context_and_two_artists(self):
        for title, expected, day, venue in (
            ("Jimena Amarillo + Chico Blanco | NYOKOBOP Festival",
             ["Jimena Amarillo", "Chico Blanco"], "2026-12-05", "Le Hasard Ludique"),
            ("Internet Girl + Cruel Santino | NYOKOBOP Festival",
             ["Internet Girl", "Cruel Santino"], "2026-12-11", "Le Trabendo"),
        ):
            with self.subTest(title=title):
                self.assert_bill(title, day, venue, expected, context="NYOKOBOP Festival")

    def test_bal_chavaux_independent_lineup(self):
        self.assert_bill(
            "Schlaasss + Corto Malaise", "2026-12-09", "Bal Chavaux",
            ["Schlaasss", "Corto Malaise"],
        )

    def test_joint_project_ampersand_is_not_split_into_separate_artists(self):
        self.assert_bill(
            "Tahiti 80 + Maxwell Farrington & Le SuperHomard",
            "2026-12-11", "L'Alhambra",
            ["Tahiti 80", "Maxwell Farrington & Le SuperHomard"],
            source="Alhambra",
        )

    def test_typo_resolves_to_established_artist_name(self):
        self.assert_bill(
            "Steeve Hackett", "2027-09-18", "Le Grand Rex", ["Steve Hackett"],
        )

    def test_programme_title_is_not_an_artist(self):
        self.assert_bill(
            "Sentinelle - Cygnes de la mer d'Egée", "2026-12-06",
            "New Morning", ["Naïssam Jalal", "Safaa Fathy", "Héctor Cavallaro"],
            context="Sentinelle – Cygnes de la mer d'Égée",
        )

    def test_new_album_wrapper_is_not_part_of_artist_name(self):
        self.assert_bill(
            "Stephen McCraven Quintet - Nouvel album", "2026-12-11",
            "Sunset/Sunside — Sunside", ["Stephen McCraven Quintet"],
            event_title="Heritage", context="Heritage",
        )

    def test_unverified_bills_and_legitimate_plus_band_remain_intact(self):
        for title in ("One Unknown + Other Unknown", "Mike + The Mechanics"):
            with self.subTest(title=title):
                item = event(title, "2027-01-01", "Alhambra")
                resolve_artist_billings([item])
                self.assertEqual(title, item.headliner)
                self.assertIsNone(item.co_headliners)

    def test_generic_festival_suffix_does_not_justify_unknown_artist_split(self):
        title = "Unknown First + Unknown Second | Some Festival"
        item = event(title, "2027-01-01", "Le Hasard Ludique")
        resolve_artist_billings([item])
        self.assertEqual("Unknown First + Unknown Second", item.headliner)
        self.assertIsNone(item.co_headliners)
        self.assertEqual("Some Festival", item.event_title)


if __name__ == "__main__":
    unittest.main()
