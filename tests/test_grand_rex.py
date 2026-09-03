from datetime import date
from pathlib import Path
from unittest import TestCase

from bs4 import BeautifulSoup

from concert_calendar.scrapers.grand_rex import parse_events


FIXTURE = Path(__file__).parent / "fixtures" / "grand_rex" / "programme.html"


class GrandRexTests(TestCase):
    def setUp(self):
        self.events = parse_events(
            BeautifulSoup(FIXTURE.read_text(), "html.parser"), today=date(2026, 9, 1)
        )

    def test_only_explicit_non_cancelled_concerts_are_accepted(self):
        self.assertEqual(
            ["JAMES BLAKE", "JAMES BLAKE", "SECOND CONCERT", "La Légende de Korra en Concert"],
            [e.headliner for e in self.events],
        )

    def test_multi_date_metadata(self):
        self.assertEqual(["2026-10-12", "2026-10-13"], [e.date for e in self.events[:2]])
        for event in self.events[:2]:
            self.assertEqual("20:00", event.start_time)
            self.assertEqual("sold_out", event.ticket_status)
            self.assertEqual("https://tickets.example/james", event.ticket_url)
            self.assertEqual("https://www.legrandrex.com/images/james.jpg", event.image_url)

    def test_generic_booking_search_uses_event_specific_official_url(self):
        self.assertEqual(
            "https://www.legrandrex.com/evenement/2", self.events[2].ticket_url
        )

    def test_explicit_full_concert_title_in_card_copy_is_preserved(self):
        self.assertEqual("La Légende de Korra en Concert", self.events[3].headliner)
