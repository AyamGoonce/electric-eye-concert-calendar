from unittest import TestCase

from concert_calendar.scrapers import dice
from concert_calendar.scrapers.dice import parse_event


def event(title):
    return parse_event({
        "id": "test-id",
        "name": title,
        "dates": {"event_start_date": "2026-11-03T20:00:00+00:00"},
        "venues": [{"name": "Test venue", "city": {"name": "Paris"}}],
    })


class DiceBillingNormalizationTests(TestCase):
    def test_explicit_first_part_title_is_support(self):
        parsed = event("Eivør | 1ère Partie : Rabbitology")
        self.assertEqual("Eivør", parsed.headliner)
        self.assertEqual(["Rabbitology"], parsed.openers)
    def test_festival_suffix_is_series_metadata(self):
        parsed = event("ear + guests — Pitchfork Music Festival 2026")
        self.assertEqual("ear", parsed.headliner)
        self.assertIsNone(parsed.co_headliners)
        self.assertEqual("Pitchfork Music Festival 2026", parsed.series_name)

    def test_presentation_and_pass_wrappers_are_removed(self):
        parsed = event("LEYA, en concert à Paris + guest : Aesthesis")
        self.assertEqual("LEYA", parsed.headliner)
        self.assertEqual(["Aesthesis"], parsed.openers)
        parsed = event("Pass 2 Jours Trabendo : ear + Bassvictim — Pitchfork Music Festival 2026")
        self.assertEqual("ear", parsed.headliner)
        self.assertEqual(["Bassvictim"], parsed.co_headliners)
        self.assertEqual("Pitchfork Music Festival 2026", parsed.series_name)

    def test_named_guest_is_support(self):
        for title, name in (
            ("LEYA, en concert à Paris + guest : Aesthesis", "Aesthesis"),
            ("Omar Doom + special guest : Verset Zero", "Verset Zero"),
            ("Deathchant + special guests : Fangus", "Fangus"),
            ("Heretoir + very special guest : Unreqvited", "Unreqvited"),
        ):
            parsed = event(title)
            self.assertEqual(name, parsed.openers[0])
            self.assertIsNone(parsed.co_headliners)

    def test_anonymous_guests_are_not_artists(self):
        for title in (
            "ear + guests — Pitchfork Music Festival 2026",
            "Bassvictim + guests — Pitchfork Music Festival 2026",
            "Nirosta Steel + guest — Pitchfork Music Festival Paris 2026",
            "THE PRIZE (AUS) + BROWER (US) + ROBERTA LIPS + GUEST SUPRISE",
        ):
            parsed = event(title)
            if "GUEST SUPRISE" in title:
                self.assertEqual(["BROWER (US)", "ROBERTA LIPS"], parsed.co_headliners)
            else:
                self.assertFalse(parsed.co_headliners)
                self.assertFalse(parsed.openers)
            self.assertNotIn("guest", parsed.headliner.casefold())

    def test_legitimate_ampersand_and_ordinary_cobill_are_preserved(self):
        for title in (
            "Charlotte Adigéry & Bolis Pupul + Tracey — Pitchfork Music Festival Paris 2026",
            "Florence + The Machine",
            "Bigflo & Oli",
            "Peter Hook & The Light",
        ):
            parsed = event(title)
            self.assertTrue(parsed.headliner)
        parsed = event("Artist A + Artist B + Artist C")
        self.assertEqual(["Artist B", "Artist C"], parsed.co_headliners)

    def test_unrecognized_dash_title_is_not_stripped(self):
        parsed = event("Artist — A Night To Remember")
        self.assertEqual("Artist — A Night To Remember", parsed.headliner)
        self.assertIsNone(parsed.series_name)

    def test_presentation_protections(self):
        self.assertEqual("Paris Paloma", event("Paris Paloma").headliner)
        self.assertEqual("Artist, en concert à Lyon", event("Artist, en concert à Lyon").headliner)
        self.assertEqual("Tabber : Modern Goth Paris", event("Tabber : Modern Goth Paris").headliner)
        self.assertEqual("Passionate Artist", event("Passionate Artist").headliner)

    def test_high_value_diagnostics_are_prioritized_within_cap(self):
        dice._DIAGNOSTICS.clear()
        for index in range(205):
            parse_event({
                "id": str(index),
                "name": f"Artist {index} + Support {index}",
                "dates": {"event_start_date": "2027-01-02T20:00:00+00:00"},
                "venues": [{"name": "Ordinary Room", "id": "v1", "city": {"name": "Paris"}}],
            })
        parse_event({
            "id": "priority",
            "name": "Iceage (Double show) — Pitchfork Music Festival Paris 2026",
            "dates": {"event_start_date": "2026-11-02T20:00:00+00:00"},
            "venues": [{"name": "Main Room", "id": "main", "room": "Main Room", "city": {"name": "Paris"}}],
        })
        diagnostics = dice.get_diagnostics()
        self.assertEqual(200, len(diagnostics))
        selected = next(item for item in diagnostics if item["source_event_id"] == "priority")
        self.assertEqual("Main Room", selected["raw_venue"])
        self.assertEqual("Main Room", selected["raw_room"])
        self.assertEqual("Pitchfork Music Festival Paris 2026", selected["series_name"])
