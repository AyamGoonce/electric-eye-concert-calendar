from datetime import date
from pathlib import Path
from unittest import TestCase

from bs4 import BeautifulSoup

from concert_calendar.scrapers.casino_de_paris import parse_events


FIXTURE = Path(__file__).parent / "fixtures" / "casino_de_paris" / "programme.html"


class CasinoDeParisTests(TestCase):
    def setUp(self):
        self.events = parse_events(BeautifulSoup(FIXTURE.read_text(), "html.parser"), today=date(2026, 9, 1))

    def test_accepts_only_explicit_non_cancelled_concerts(self):
        self.assertEqual(["ARTIST", "ARTIST LATE"], [event.headliner for event in self.events])

    def test_parses_time_ticket_image_and_status(self):
        first, second = self.events
        self.assertEqual(("2026-09-10", "20:00"), (first.date, first.start_time))
        self.assertEqual("https://www.casinodeparis.fr/img/artist.jpg", first.image_url)
        self.assertEqual("https://www.casinodeparis.fr/fr/artist", first.ticket_url)
        self.assertEqual("sold_out", second.ticket_status)

    def test_preserves_distinct_same_day_performances(self):
        self.assertEqual(["20:00", "22:00"], [event.start_time for event in self.events])
