import json
import unittest
from datetime import date

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.event_titles import artist_title_parts
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import prepare_upcoming_events, serialize_data
from concert_calendar.scrapers.dice import parse_event


def event(title, **kwargs):
    return ConcertEvent("2027-03-29", title, "Casino de Paris", "Paris", "75", **kwargs)


def serialized(events):
    return json.loads(serialize_data(prepare_upcoming_events(
        deduplicate_events(events), today=date(2026, 9, 1))))


class EventTitleIdentityTests(unittest.TestCase):
    def test_concert_wrappers_merge_and_keep_metadata(self):
        rows = serialized([
            event("L’Étrangère : Release party en full band", source_names=["Official"],
                  ticket_url="https://example.test/ticket", first_seen="2026-08-01T00:00:00Z"),
            event("L’Étrangère en concert (côté Records)", source_names=["DICE"]),
        ])
        self.assertEqual(1, len(rows))
        self.assertEqual("L’Étrangère", rows[0]["h"])
        self.assertEqual("2026-08-01T00:00:00Z", rows[0]["fs"])
        self.assertEqual("https://example.test/ticket", rows[0]["t"])
        self.assertIn("Release party", rows[0]["et"])
        self.assertEqual("Ash Grunwald", serialized([event("Ash Grunwald en concert (côté Records)")])[0]["h"])

    def test_distinct_performances_are_not_merged(self):
        rows = serialized([event("Artist en concert", start_time="19:00"),
                           event("Artist en concert (côté Records)", start_time="21:00")])
        self.assertEqual(2, len(rows))

    def test_bare_concert_requires_independent_plain_identity(self):
        self.assertEqual("Project en Concert", serialized([event("Project en Concert")])[0]["h"])
        rows = serialized([event("Silver Orchard", source_names=["Casino de Paris"]),
                           event("Silver Orchard en concert", source_names=["DICE"])])
        self.assertEqual(1, len(rows))
        self.assertEqual("Silver Orchard", rows[0]["h"])

    def test_existing_dice_neutral_bill_retains_descriptor_free_entities(self):
        parsed = parse_event({"id": "fixture", "name": "Kanaan (Psychedelic Rock - Norvège) + Caduta Massi",
                              "dates": {"event_start_date": "2027-03-29T20:00:00+02:00"},
                              "venues": [{"name": "Casino de Paris", "city": {"name": "Paris"}}]})
        row = serialized([parsed])[0]
        self.assertEqual("Kanaan", row["h"])
        self.assertEqual(["Caduta Massi"], row["ch"])
        self.assertEqual([], row["o"])

    def test_explicit_featured_artist_and_quoted_programme(self):
        row = serialized([event("Stéphane Belmondo « Love for Chet » ft. Jesse Van Ruller")])[0]
        self.assertEqual("Stéphane Belmondo", row["h"])
        self.assertEqual(["Jesse Van Ruller"], row["ch"])
        self.assertEqual([], row["o"])
        self.assertIn("Love for Chet", row["et"])

    def test_colon_branding_requires_plain_official_corroboration(self):
        plain = event("PETER HOOK & THE LIGHT", source_names=["Casino de Paris"])
        marked = event("PETER HOOK & THE LIGHT : A JOY DIVISION CELEBRATION", source_names=["DICE"])
        row = serialized([plain, marked])[0]
        self.assertEqual("Peter Hook & The Light", row["h"])
        self.assertIn("CELEBRATION", row["et"])
        self.assertEqual(
            "Peter Hook & The Light : A Joy Division Celebration",
            serialized([event(marked.headliner)])[0]["h"],
        )

    def test_no_generic_punctuation_or_project_splitting(self):
        from concert_calendar.scrapers.dice import parse_neutral_cobill
        for title in ["Florence & The Machine", "Artist+Artist", "Artist (UK)",
                      "Artist (The Band)", "Artist: Name", "Artist - Name", "Live", "Release",
                      "Project en Concert", "Artist ft. Guest – 19h00", "Artist ft. One & Two",
                      "MONKEYS ON MARS (Mars Red Sky + Monkey3)"]:
            with self.subTest(title=title):
                self.assertEqual((title, []), artist_title_parts(title))
        title = "MONKEYS ON MARS (Mars Red Sky + Monkey3) + Guest"
        self.assertEqual((title, None), parse_neutral_cobill(title))

    def test_generic_forms_and_content_lookup_use_artist_entities_only(self):
        from concert_calendar.content_index import build_index, enrich_events
        from tests.test_content_index import entry
        parsed = deduplicate_events([event("Silver Orchard « Programme Name » feat. Copper Lantern")])
        index = build_index([
            entry("Silver Orchard @ Bataclan, Paris", ["Concert Review", "Silver Orchard"], "2026-01-01"),
            entry("Copper Lantern @ Bataclan, Paris", ["Concert Review", "Copper Lantern"], "2026-01-02"),
            entry("Programme Name @ Bataclan, Paris", ["Concert Review", "Programme Name"], "2026-01-03"),
        ], generated_at="2026-09-01T00:00:00Z")
        enrich_events(parsed, index)
        self.assertEqual({"Silver Orchard", "Copper Lantern"},
                         {link["name"] for link in parsed[0].electric_eye_links})
        self.assertEqual(("Example Artist", []), artist_title_parts("Example Artist en concert (côté Records)"))
        self.assertEqual(("Example Artist", []), artist_title_parts("Example Artist : Release party en full band"))
        self.assertEqual(("Example Artist", []), artist_title_parts("Example Artist (Indie Rock - France)"))


if __name__ == "__main__":
    unittest.main()
