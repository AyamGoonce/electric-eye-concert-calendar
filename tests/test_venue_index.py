import unittest

from concert_calendar.venue_index import build_venue_index


class VenueIndexTests(unittest.TestCase):

    def test_groups_events_by_canonical_venue(self):
        metadata = {
            "Le Trianon": {
                "city": "Paris",
                "department": "75",
                "address": "80 boulevard de Rochechouart, 75018 Paris",
                "lat": 48.8830683,
                "lng": 2.3429332,
                "website": "https://www.letrianon.fr/",
                "type": "",
            }
        }

        events = [
            {
                "d": "2026-10-10",
                "h": "Artist One",
                "o": [],
                "v": "Le Trianon",
                "c": "Paris",
                "x": [],
                "p": [],
                "t": "https://tickets.example/1",
                "f": False,
                "so": False,
                "fs": "2026-01-01T00:00:00Z",
                "i": "1111111111111111",
                "ts": "tickets",
                "st": "20:00",
            },
            {
                "d": "2026-11-12",
                "h": "Artist Two",
                "o": ["Support"],
                "v": "Le Trianon",
                "c": "Paris",
                "x": [],
                "p": [],
                "t": "https://tickets.example/2",
                "f": False,
                "so": False,
                "fs": "2026-01-02T00:00:00Z",
                "i": "2222222222222222",
                "ts": "tickets",
                "st": None,
            },
        ]

        index = build_venue_index(events, metadata)

        self.assertEqual(list(index), ["Le Trianon"])
        self.assertEqual(len(index["Le Trianon"]["events"]), 2)
        self.assertEqual(
            index["Le Trianon"]["events"][0]["headliner"],
            "Artist One",
        )
        self.assertEqual(
            index["Le Trianon"]["events"][1]["eventId"],
            "2222222222222222",
        )

    def test_venue_without_upcoming_events_is_still_present(self):
        metadata = {
            "Bataclan": {
                "city": "Paris",
                "department": "75",
                "address": "50 boulevard Voltaire, 75011 Paris",
                "lat": 48.8630357,
                "lng": 2.3706465,
                "website": "https://www.bataclan.fr/",
                "type": "",
            }
        }

        index = build_venue_index([], metadata)

        self.assertIn("Bataclan", index)
        self.assertEqual(index["Bataclan"]["events"], [])

    def test_unknown_calendar_venue_is_reported_not_invented(self):
        metadata = {}

        events = [
            {
                "d": "2026-10-10",
                "h": "Artist",
                "o": [],
                "v": "Imaginary Hall",
                "c": "Paris",
                "x": [],
                "p": [],
                "t": "",
                "f": False,
                "so": False,
                "fs": "2026-01-01T00:00:00Z",
                "i": "aaaaaaaaaaaaaaaa",
                "ts": None,
                "st": None,
            }
        ]

        index, diagnostics = build_venue_index(
            events,
            metadata,
            include_diagnostics=True,
        )

        self.assertEqual(index, {})
        self.assertEqual(
            diagnostics["unknownEventVenues"],
            ["Imaginary Hall"],
        )

    def test_historical_articles_are_attached_to_venue(self):
        metadata = {
            "Bataclan": {
                "lat": 48.863,
                "lng": 2.371,
            }
        }

        articles = {
            "Bataclan": [
                {
                    "date": "2025-05-01",
                    "title": "Artist @ Bataclan, Paris - May 1st, 2025",
                    "url": "https://www.electriceyerock.com/example.html",
                }
            ]
        }

        index = build_venue_index(
            [],
            metadata,
            articles=articles,
        )

        self.assertEqual(len(index["Bataclan"]["articles"]), 1)
        self.assertEqual(
            index["Bataclan"]["articles"][0]["date"],
            "2025-05-01",
        )

    def test_article_diagnostics(self):
        metadata = {
            "Bataclan": {"lat": 48.863, "lng": 2.371},
            "Le Trianon": {"lat": 48.883, "lng": 2.343},
        }

        articles = {
            "Bataclan": [
                {
                    "date": "2025-01-01",
                    "title": "Review",
                    "url": "https://www.electriceyerock.com/test.html",
                }
            ]
        }

        _, diagnostics = build_venue_index(
            [],
            metadata,
            articles=articles,
            include_diagnostics=True,
        )

        self.assertEqual(diagnostics["venuesWithArticles"], 1)
        self.assertEqual(diagnostics["articleAssociations"], 1)


    def test_map_ready_flag_requires_both_coordinates(self):
        metadata = {
            "Mapped": {
                "lat": 48.1,
                "lng": 2.1,
            },
            "Unmapped": {
                "lat": None,
                "lng": None,
            },
        }

        index = build_venue_index([], metadata)

        self.assertTrue(index["Mapped"]["mapReady"])
        self.assertFalse(index["Unmapped"]["mapReady"])


if __name__ == "__main__":
    unittest.main()
