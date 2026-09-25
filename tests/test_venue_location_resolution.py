import unittest

from concert_calendar.models import ConcertEvent
from concert_calendar.venues import (
    normalize_event_venue,
    resolve_venue_name,
)


class VenueLocationResolutionTests(unittest.TestCase):

    def test_historical_existing_aliases_resolve(self):
        cases = {
            "Zénith": "Le Zénith Paris – La Villette",
            "Accorhotels Arena": "Accor Arena",
            "Accorhotels Arena Bercy": "Accor Arena",
            "Palais Omnisports Paris Bercy": "Accor Arena",
            "P.O.P.B.": "Accor Arena",
            "La Défense Arena": "Plénitude Arena",
            "U Arena": "Plénitude Arena",
            "Palais des Congrès": "Le Palais des Congrès de Paris",
            "Grand Rex": "Le Grand Rex",
            "Hasard Ludique": "Le Hasard Ludique",
            "l'Auditorium de la Seine Musicale": "La Seine Musicale",
            "la Machine": "La Machine du Moulin Rouge",
            "Bataclan Paris": "Bataclan",
            "Élyée-Montmartre": "Élysée Montmartre",
            "O'Sullivan's Backstage By The Mill": "Backstage By The Mill",
            "O' Sullivans Backstage By The Mill": "Backstage By The Mill",
        }

        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(expected, resolve_venue_name(raw))

    def test_new_canonical_venues_resolve_to_themselves(self):
        cases = (
            ("Divan du Monde", "Paris"),
            ("Le Klub", "Paris"),
            ("La Bellevilloise", "Paris"),
            ("Badaboum", "Paris"),
            ("Batofar", "Paris"),
            ("Grande Halle de la Villette", "Paris"),
            ("Glazart", "Paris"),
            ("La Dame de Canton", "Paris"),
            ("La Mécanique Ondulatoire", "Paris"),
            ("Mains d'Oeuvres", "Saint-Ouen"),
            ("Palais de la Porte Dorée", "Paris"),
            ("Quartier Général Oberkampf", "Paris"),
            ("Le Sub Pigalle", "Paris"),
            ("Hippodrome de Longchamp", "Paris"),
            ("Cité de la Musique", "Paris"),
            ("Pan Piper", "Paris"),
            ("La Flèche d'Or", "Paris"),
            ("Le 104", "Paris"),
            ("Le Zèbre de Belleville", "Paris"),
            ("Sunset/Sunside", "Paris"),
            ("Flow", "Paris"),
            ("Jazz Club Étoile", "Paris"),
            ("Athénée-Théatre Louis Jouvet", "Paris"),
            ("Théatre du Châtelet", "Paris"),
            ("Studio Sextan", "Malakoff"),
            ("Chateau de Chantilly", "Chantilly"),
            ("FNAC Ternes", "Paris"),
            ("FNAC Forum", "Paris"),
            ("Gibert Disc", "Paris"),
            ("Radio Nova", "Paris"),
            ("Novotel Les Halles", "Paris"),
            ("The Mixtape", "Paris"),
            ("Alabama Bar", "Paris"),
            ("Hellfest", "Clisson"),
        )

        for venue, city in cases:
            with self.subTest(venue=venue):
                self.assertEqual(venue, resolve_venue_name(venue, city))

    def test_city_aware_ambiguous_names_resolve_only_with_matching_city(self):
        cases = {
            ("Le Forum", "Vauréal"): "Le Forum",
            ("Maison des Arts", "Créteil"): "Maison des Arts de Créteil",
            ("Salle Jacques Brel", "Fontenay-sous-Bois"): "Salle Jacques Brel",
            ("Greek Theatre", "Los Angeles"): "Greek Theatre",
            ("SSE Arena", "Wembley"): "SSE Arena Wembley",
        }

        for (venue, city), expected in cases.items():
            with self.subTest(venue=venue, city=city):
                self.assertEqual(expected, resolve_venue_name(venue, city))

        self.assertIsNone(resolve_venue_name("Maison des Arts", "Paris"))
        self.assertIsNone(resolve_venue_name("Greek Theatre", "Paris"))

    def test_current_venue_names_resolve_to_existing_canonicals(self):
        self.assertEqual(
            "Dôme de Paris – Palais des Sports",
            resolve_venue_name("Le Dôme de Paris", "Paris"),
        )
        self.assertEqual(
            "Batofar",
            resolve_venue_name("Bateau Phare", "Paris"),
        )
        self.assertEqual(
            "Batofar",
            resolve_venue_name("Le Bateau Phare", "Paris"),
        )

    def test_event_normalization_can_use_city_context(self):
        event = ConcertEvent(
            "2027-01-01",
            "Artist",
            "Maison des Arts",
            "Créteil",
            "94",
        )

        normalize_event_venue(event)

        self.assertEqual("Maison des Arts de Créteil", event.venue)
        self.assertEqual(("Créteil", "94"), (event.city, event.department))

    def test_mondial_and_tattoo_planetarium_resolve_to_grande_halle(self):
        for raw in ("Mondial du Tatouage", "Tattoo Planetarium"):
            with self.subTest(raw=raw):
                self.assertEqual(
                    "Grande Halle de la Villette",
                    resolve_venue_name(raw, "Paris"),
                )

    def test_download_and_jazz_a_la_villette_remain_unresolved(self):
        self.assertIsNone(resolve_venue_name("Download Paris", "Brétigny-sur-Orge"))
        self.assertIsNone(resolve_venue_name("Jazz à la Villette", "Paris"))

    def test_generic_unknown_venue_is_still_not_guessed(self):
        self.assertIsNone(resolve_venue_name("Main Room", "Paris"))
        self.assertIsNone(resolve_venue_name("Club", "Paris"))
        self.assertIsNone(resolve_venue_name("Imaginary Hall", "Paris"))


if __name__ == "__main__":
    unittest.main()
