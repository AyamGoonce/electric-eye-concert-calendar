from datetime import date
from pathlib import Path
from unittest import TestCase

from bs4 import BeautifulSoup

from concert_calendar.scrapers.cabaret_sauvage import parse_events


FIXTURE = Path(__file__).parent / "fixtures" / "cabaret_sauvage" / "programme.html"


class CabaretSauvageTests(TestCase):
    def setUp(self):
        self.events = parse_events(BeautifulSoup(FIXTURE.read_text(), "html.parser"), today=date(2026, 9, 1))

    def test_uses_all_pane_once_and_accepts_only_concerts(self):
        self.assertEqual(["Ruggero", "JONY"], [event.headliner for event in self.events])

    def test_extracts_status_artwork_and_detail_url(self):
        event = self.events[0]
        self.assertEqual("2026-09-06", event.date)
        self.assertEqual("sold_out", event.ticket_status)
        self.assertEqual("https://www.cabaretsauvage.com/work/ruggero", event.ticket_url)
        self.assertEqual("https://cdn.test/ruggero.webp", event.image_url)
