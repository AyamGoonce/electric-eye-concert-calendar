from datetime import date
from pathlib import Path
from unittest import TestCase
from bs4 import BeautifulSoup
from concert_calendar.scrapers.adidas_arena import parse_events

FIXTURE = Path(__file__).parent / "fixtures" / "adidas_arena" / "programme.html"

class AdidasArenaTests(TestCase):
    def setUp(self):
        self.events = parse_events(BeautifulSoup(FIXTURE.read_text(), "html.parser"), today=date(2026, 9, 1))

    def test_explicit_concert_filter_and_exact_advertised_dates(self):
        self.assertEqual(["2026-10-02", "2026-10-03", "2026-10-30", "2026-11-21"], [e.date for e in self.events])
        self.assertNotIn("SPORT", [e.headliner for e in self.events])

    def test_metadata(self):
        self.assertEqual("20:30", self.events[0].start_time)
        self.assertEqual("https://www.adidasarena.com/images/music.jpg", self.events[0].image_url)
        self.assertEqual("https://www.adidasarena.com/programmation/artist--1", self.events[0].ticket_url)
        self.assertEqual("sold_out", self.events[-1].ticket_status)
