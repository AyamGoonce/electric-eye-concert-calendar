import unittest

from concert_calendar.venue_index import build_venue_index


class VenueIndexTests(unittest.TestCase):

    @staticmethod
    def event(venue, *, city="Paris", event_id="aaaaaaaaaaaaaaaa"):
        return {
            "d": "2026-10-10",
            "h": "Artist",
            "o": [],
            "v": venue,
            "c": city,
            "x": [],
            "p": [],
            "t": "",
            "f": False,
            "so": False,
            "fs": "2026-01-01T00:00:00Z",
            "i": event_id,
            "ts": None,
            "st": None,
        }

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

    def test_new_calendar_venue_becomes_visible_provisionally(self):
        index, diagnostics = build_venue_index(
            [self.event("New Independent Hall")],
            {},
            include_diagnostics=True,
        )

        self.assertIn("New Independent Hall", index)
        self.assertEqual(
            1,
            len(index["New Independent Hall"]["events"]),
        )
        self.assertTrue(index["New Independent Hall"]["provisional"])
        self.assertEqual(
            "provisional",
            index["New Independent Hall"]["status"],
        )
        self.assertEqual(
            diagnostics["unknownEventVenues"],
            ["New Independent Hall"],
        )
        self.assertEqual(
            diagnostics["provisionalEventVenues"],
            ["New Independent Hall"],
        )
        self.assertEqual(1, diagnostics["venueCount"])
        self.assertEqual(0, diagnostics["canonicalVenueCount"])
        self.assertEqual(1, diagnostics["provisionalVenueCount"])

    def test_provisional_venue_does_not_invent_metadata(self):
        record = build_venue_index(
            [self.event("New Independent Hall", city="Montreuil")],
            {},
        )["New Independent Hall"]

        self.assertEqual("Montreuil", record["city"])
        self.assertFalse(record["mapReady"])
        for field in (
            "address", "department", "website", "lat", "lng",
            "currentName", "aliases",
        ):
            self.assertNotIn(field, record)

    def test_reviewed_alias_resolves_without_provisional_duplicate(self):
        metadata = {
            "Current Hall": {
                "former_names": ["Old Hall"],
                "city": "Paris",
                "lat": 48.1,
                "lng": 2.1,
            }
        }

        index, diagnostics = build_venue_index(
            [self.event("Old Hall")],
            metadata,
            include_diagnostics=True,
        )

        self.assertNotIn("Old Hall", index)
        self.assertEqual(1, len(index["Current Hall"]["events"]))
        self.assertNotIn("provisional", index["Current Hall"])
        self.assertEqual([], diagnostics["unknownEventVenues"])
        self.assertEqual([], diagnostics["provisionalEventVenues"])

    def test_later_reviewed_metadata_absorbs_provisional_venue(self):
        event = self.event("Pop-Up Hall")
        provisional = build_venue_index([event], {})
        self.assertTrue(provisional["Pop-Up Hall"]["provisional"])

        reviewed = build_venue_index(
            [event],
            {
                "Permanent Hall": {
                    "former_names": ["Pop-Up Hall"],
                    "city": "Paris",
                }
            },
        )

        self.assertNotIn("Pop-Up Hall", reviewed)
        self.assertIn("Permanent Hall", reviewed)
        self.assertNotIn("provisional", reviewed["Permanent Hall"])
        self.assertEqual(1, len(reviewed["Permanent Hall"]["events"]))

    def test_empty_and_placeholder_venues_are_not_provisional(self):
        labels = [
            "", "   ", "-", "TBA", "Unknown", "Venue", "N/A",
            "Main Room", "Room 1", "Multi-lieux : Hall A, Hall B",
            "https://tickets.example/venue",
        ]
        events = [
            self.event(label, event_id=f"invalid-{index}")
            for index, label in enumerate(labels)
        ]

        index, diagnostics = build_venue_index(
            events,
            {},
            include_diagnostics=True,
        )

        self.assertEqual({}, index)
        self.assertEqual([], diagnostics["provisionalEventVenues"])
        self.assertEqual(
            {
                "-", "N/A", "TBA", "Unknown", "Venue", "Main Room",
                "Room 1", "Multi-lieux : Hall A, Hall B",
                "https://tickets.example/venue",
            },
            set(diagnostics["excludedInvalidEventVenues"]),
        )

    def test_reviewed_suffix_in_contaminated_label_resolves_canonically(self):
        metadata = {
            "Bal Chavaux": {
                "city": "Montreuil",
                "lat": 48.858,
                "lng": 2.435,
            }
        }

        index, diagnostics = build_venue_index(
            [self.event("Disorder Fest @ Bal Chavaux", city="Montreuil")],
            metadata,
            include_diagnostics=True,
        )

        self.assertEqual(["Bal Chavaux"], list(index))
        self.assertEqual(1, len(index["Bal Chavaux"]["events"]))
        self.assertEqual([], diagnostics["provisionalEventVenues"])
        self.assertEqual([], diagnostics["unknownEventVenues"])

    def test_conflicting_provisional_cities_are_blank_and_audited(self):
        events = [
            self.event("Shared Hall", city="Paris", event_id="paris"),
            self.event("Shared Hall", city="Montreuil", event_id="montreuil"),
        ]

        index, diagnostics = build_venue_index(
            events,
            {},
            include_diagnostics=True,
        )

        self.assertEqual("", index["Shared Hall"]["city"])
        self.assertEqual(
            [{"venue": "Shared Hall", "cities": ["Montreuil", "Paris"]}],
            diagnostics["provisionalVenueCityConflicts"],
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

    def test_exports_reviewed_canonical_aliases_for_search(self):
        index = build_venue_index(
            [],
            {
                "Accor Arena": {
                    "city": "Paris",
                    "lat": 48.839,
                    "lng": 2.379,
                }
            },
        )

        aliases = index["Accor Arena"]["aliases"]

        self.assertIn("bercy", aliases)
        self.assertIn("popb", aliases)
        self.assertIn("p o p b", aliases)
        self.assertIn("accorhotels arena", aliases)
        self.assertIn("palais omnisports de paris bercy", aliases)
        self.assertNotIn("accor arena", aliases)

    def test_renamed_venue_promotes_current_name_and_keeps_former_alias(self):
        metadata = {
            "Batofar": {
                "city": "Paris",
                "department": "75",
                "lat": 48.833,
                "lng": 2.379,
                "status": "renamed",
                "current_name": "Le Bateau Phare",
            }
        }
        events = [{
            "d": "2027-01-01", "h": "Artist", "v": "Le Bateau Phare",
            "c": "Paris", "i": "venue-rename", "t": "", "so": False,
            "ts": None, "st": None,
        }]
        articles = {
            "Le Bateau Phare": [{
                "date": "2014-11-28",
                "title": "Artist @ Batofar, Paris",
                "url": "https://www.electriceyerock.com/batofar.html",
            }]
        }

        index = build_venue_index(events, metadata, articles=articles)

        self.assertNotIn("Batofar", index)
        self.assertIn("Le Bateau Phare", index)
        self.assertEqual(
            ["bateau phare", "Batofar"],
            index["Le Bateau Phare"]["aliases"],
        )
        self.assertEqual(1, len(index["Le Bateau Phare"]["events"]))
        self.assertEqual(1, len(index["Le Bateau Phare"]["articles"]))


if __name__ == "__main__":
    unittest.main()
