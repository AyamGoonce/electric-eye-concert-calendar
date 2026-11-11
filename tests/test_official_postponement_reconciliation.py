"""Officially postponed dates must not survive as stale external listings."""
import unittest
from datetime import date
from bs4 import BeautifulSoup

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent
from concert_calendar.scrapers.nouveau_casino import parse_items


def record(title="Levara", *, source="Nouveau Casino",
           date_value="2026-11-11", status=None, time="19:00"):
    return ConcertEvent(
        date=date_value, headliner=title, venue="Nouveau Casino",
        city="Paris", department="75", source_names=[source],
        start_time=time, ticket_status=status,
        ticket_url="https://nouveaucasino.fr/" if source == "Nouveau Casino" else None,
    )


class OfficialPostponementTests(unittest.TestCase):
    def test_venue_parser_extracts_postponement_as_status(self):
        html = """
        <li class="day_item">
          <time><span class="date">11.11</span></time>
          <li class="event_item" data-type="concert">
            <div class="event_header">
              <h3>Levara [reporté]</h3>
              <p><span>19:00</span></p>
            </div>
          </li>
        </li>
        """
        events = parse_items(BeautifulSoup(html, "html.parser"), today=date(2026, 11, 1))
        self.assertEqual(1, len(events))
        self.assertEqual("Levara", events[0].headliner)
        self.assertEqual("postponed", events[0].ticket_status)

    def test_postponed_venue_entry_and_old_external_copy_disappear(self):
        official = record(status="postponed")
        promoter = record(source="Gérard Drouot Productions", time=None)
        diagnostics = {}
        result = deduplicate_events([official, promoter], diagnostics=diagnostics)
        self.assertEqual([], result)
        self.assertEqual(2, diagnostics["officially_postponed_date_rows_excluded"])

    def test_unrelated_concert_and_rescheduled_date_are_preserved(self):
        official = record(status="postponed")
        unrelated = record("Other Artist", source="DICE")
        replacement = record(
            source="Gérard Drouot Productions", date_value="2027-01-10",
        )
        result = deduplicate_events([official, unrelated, replacement])
        self.assertEqual(2, len(result))
        self.assertEqual({"Other Artist", "Levara"}, {x.headliner for x in result})
        self.assertEqual({"2026-11-11", "2027-01-10"}, {x.date for x in result})

    def test_external_postponement_alone_cannot_remove_official_venue_record(self):
        venue = record(status="tickets")
        external = record(source="DICE", status="postponed")
        result = deduplicate_events([venue, external])
        self.assertTrue(result)

    def test_other_performance_same_date_is_not_removed(self):
        official = record(status="postponed", time="19:00")
        distinct = record(source="DICE", time="22:00")
        result = deduplicate_events([official, distinct])
        self.assertEqual(1, len(result))
        self.assertEqual("22:00", result[0].start_time)


if __name__ == "__main__":
    unittest.main()
