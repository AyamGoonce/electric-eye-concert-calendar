import unittest
from datetime import date

from bs4 import BeautifulSoup

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import prepare_upcoming_events
from concert_calendar.scrapers.popup_label import parse_events


class CalendarCorrectnessAcceptanceTests(unittest.TestCase):

    def test_explicit_tour_suffix_changes_display_not_identity(self):
        original = "KATSEYE - THE WILDWORLD TOUR"

        record = ConcertEvent(
            "2026-09-09",
            original,
            "Accor Arena",
            "Paris",
            "75",
            source_names=["Accor Arena"],
        )

        result = deduplicate_events([record])

        # Dedup/state identity remains untouched.
        self.assertEqual(1, len(result))
        self.assertEqual(original, result[0].headliner)
        self.assertIsNone(result[0].event_title)

        # Only the serialized public denomination is cleaned.
        rows = prepare_upcoming_events(
            result,
            today=date(2026, 9, 1),
        )

        self.assertEqual("KATSEYE", rows[0]["h"])
        self.assertEqual(original, rows[0]["et"])

    def test_correlated_wrapper_spelling_variants_merge(self):
        plain = ConcertEvent(
            "2026-10-02",
            "L’Étrangère",
            "Supersonic Records",
            "Paris",
            "75",
            source_names=["DICE"],
        )

        wrapped = ConcertEvent(
            "2026-10-02",
            "L’Êtrangêre en concert (côté Records)",
            "Supersonic Records",
            "Paris",
            "75",
            source_names=["Supersonic"],
        )

        result = deduplicate_events([plain, wrapped])

        self.assertEqual(1, len(result))
        self.assertEqual("L’Étrangère", result[0].headliner)

    def test_popup_upstairs_programme_without_ticket_is_not_concert(self):
        html = """
        <div class="concert mois" id="septembre2026"></div>

        <div class="concert">
          <div class="jour">24.09</div>
          <div class="infos">À L'ÉTAGE DÈS 20H30</div>
          <div class="titre">The Vinyl Hour</div>
          <div class="infos_bis">W/ CAROLEFE</div>
          <div class="liens"></div>
        </div>

        <div class="concert">
          <div class="jour">25.09</div>
          <div class="titre">Legitimate Free Concert</div>
          <div class="infos_bis">+ Support Artist</div>
          <div class="liens"></div>
        </div>
        """

        events = parse_events(
            BeautifulSoup(html, "html.parser"),
            today=date(2026, 9, 1),
        )

        self.assertEqual(
            ["Legitimate Free Concert"],
            [record.headliner for record in events],
        )

    def test_distinct_performance_times_remain_separate(self):
        early = ConcertEvent(
            "2026-11-24",
            "Example Artist",
            "Le Trianon",
            "Paris",
            "75",
            start_time="18:30",
        )

        late = ConcertEvent(
            "2026-11-24",
            "Example Artist",
            "Le Trianon",
            "Paris",
            "75",
            start_time="19:30",
        )

        result = deduplicate_events([early, late])

        self.assertEqual(2, len(result))

        rows = prepare_upcoming_events(
            result,
            today=date(2026, 9, 1),
        )

        self.assertEqual(2, len({row["i"] for row in rows}))


if __name__ == "__main__":
    unittest.main()
