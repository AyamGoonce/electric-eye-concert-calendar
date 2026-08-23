import json
from datetime import date
from pathlib import Path
import tempfile
import unittest

from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import (
    ARTIST_SORT_OVERRIDES,
    alphabetical_sort_key,
    export_production_calendar,
    genre_categories,
    prepare_upcoming_events,
)


def make_event(
    event_date,
    headliner,
    venue="Bataclan",
    city="Paris",
    **kwargs,
):
    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        venue=venue,
        city=city,
        department="75" if city == "Paris" else "95",
        **kwargs,
    )


class ProductionDataTests(unittest.TestCase):
    def test_article_aware_sort_keys_are_conservative(self):
        examples = {
            "The Black Keys": "black keys",
            "La Maroquinerie": "maroquinerie",
            "Le Trianon": "trianon",
            "Les Femmes s'en Mêlent": "femmes s'en melent",
            "L'Olympia": "olympia",
            "L’Olympia": "olympia",
            "Alice Cooper": "alice cooper",
            "Sammy Hagar": "sammy hagar",
            "An Pierlé": "an pierle",
        }

        for displayed_name, expected_key in examples.items():
            with self.subTest(displayed_name=displayed_name):
                self.assertEqual(expected_key, alphabetical_sort_key(displayed_name))

    def test_explicit_artist_sort_override_is_separate_and_conservative(self):
        self.assertEqual(
            "perfect circle",
            alphabetical_sort_key("A Perfect Circle", ARTIST_SORT_OVERRIDES),
        )
        self.assertEqual("a perfect circle", alphabetical_sort_key("A Perfect Circle"))

    def test_upcoming_only_and_deterministic_sorting(self):
        events = [
            make_event("2026-08-31", "Zulu"),
            make_event("2026-08-30", "Past"),
            make_event("2026-08-31", "Álpha"),
        ]

        prepared = prepare_upcoming_events(events, today=date(2026, 8, 31))

        self.assertEqual(["Álpha", "Zulu"], [event["h"] for event in prepared])

    def test_production_fields_preserve_structured_city(self):
        event = make_event(
            "2026-09-01",
            "Long Artist + Another Artist",
            venue="Le Forum",
            city="Vauréal",
            openers=["Première Partie"],
            promoters=["Official Promoter"],
            genre="Rock alternatif",
            ticket_url="https://tickets.example/event",
        )

        prepared = prepare_upcoming_events([event], today=date(2026, 8, 31))[0]

        self.assertEqual("Le Forum", prepared["v"])
        self.assertEqual("Vauréal", prepared["c"])
        self.assertEqual(["Première Partie"], prepared["o"])
        self.assertEqual(["Rock / Indie / Punk"], prepared["x"])
        self.assertEqual("Long Artist + Another Artist", prepared["h"])
        self.assertEqual("Le Forum", prepared["v"])

    def test_invalid_ticket_url_is_omitted(self):
        event = make_event(
            "2026-09-01",
            "Artist",
            ticket_url="/relative-ticket",
        )

        prepared = prepare_upcoming_events([event], today=date(2026, 8, 31))[0]

        self.assertIsNone(prepared["t"])

    def test_genre_categories_are_broad_and_meaningful(self):
        self.assertEqual(
            ["Rock / Indie / Punk", "Pop"],
            genre_categories("Concert - Indie Pop"),
        )
        self.assertEqual([], genre_categories(None))


class ProductionHTMLTests(unittest.TestCase):
    def setUp(self):
        self.events = [
            make_event("2026-09-01", "Paris Artist"),
            make_event(
                "2026-09-02",
                "Énorme co-bill " + "+ Artist " * 20,
                venue="Le Forum",
                city="Vauréal",
                openers=["Support Act"],
                genre="Rock",
            ),
            make_event("2026-09-03", "No Ticket", ticket_url=None),
        ]

    def test_generated_shell_contains_required_controls_and_states(self):
        with tempfile.TemporaryDirectory() as directory:
            path = export_production_calendar(
                self.events,
                output_path=str(Path(directory) / "calendar.html"),
                today=date(2026, 8, 31),
            )
            soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

        for element_id in (
            "search",
            "month-filter",
            "venue-filter",
            "genre-filter",
            "sort-order",
            "result-count",
            "event-list",
            "no-results",
        ):
            self.assertIsNotNone(soup.select_one(f"#{element_id}"))

        self.assertIn("@media (max-width: 680px)", soup.style.string)
        self.assertIn("No concerts match your current filters.", soup.get_text(" "))
        self.assertEqual(
            ["date-asc", "date-desc", "artist-asc", "venue-asc"],
            [option.get("value") for option in soup.select("#sort-order option")],
        )

    def test_embedded_json_is_compact_complete_and_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            path = export_production_calendar(
                self.events,
                output_path=str(Path(directory) / "calendar.html"),
                today=date(2026, 8, 31),
            )
            soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
            data = json.loads(soup.select_one("#calendar-data").string)

        self.assertEqual(3, len(data))
        self.assertEqual("Vauréal", data[1]["c"])
        self.assertEqual([], data[2]["o"])

    def test_javascript_contains_combined_filter_and_venue_display_rules(self):
        with tempfile.TemporaryDirectory() as directory:
            path = export_production_calendar(
                self.events,
                output_path=str(Path(directory) / "calendar.html"),
                today=date(2026, 8, 31),
            )
            html = path.read_text(encoding="utf-8")

        self.assertIn("event.s.includes(query)", html)
        self.assertIn("event.d.startsWith(month)", html)
        self.assertIn("event.v === venue", html)
        self.assertIn("event.x.includes(genre)", html)
        self.assertIn('const order = sortOrder.value;', html)
        self.assertIn('order === "date-desc"', html)
        self.assertIn('order === "artist-asc"', html)
        self.assertIn('order === "venue-asc"', html)
        self.assertIn('"a perfect circle":"Perfect Circle"', html)
        self.assertIn("articleAwareKey(event.h, artistSortOverrides)", html)
        self.assertIn("articleAwareKey(event.v, venueSortOverrides)", html)
        self.assertNotIn('sortOrder.value = ""', html)
        self.assertIn('=== "paris" ? event.v : event.v + " (" + event.c + ")"', html)
        self.assertIn('target = "_blank"', html)
        self.assertIn('rel = "noopener noreferrer"', html)


if __name__ == "__main__":
    unittest.main()
