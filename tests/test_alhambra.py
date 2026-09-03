from datetime import date
from pathlib import Path
from unittest import TestCase
from bs4 import BeautifulSoup
from concert_calendar.scrapers.alhambra import parse_events

FIXTURE = Path(__file__).parent / "fixtures" / "alhambra" / "programme.html"

class AlhambraTests(TestCase):
    def setUp(self):
        self.events = parse_events(BeautifulSoup(FIXTURE.read_text(), "html.parser"), today=date(2026, 9, 1))

    def test_conservative_category_filter(self):
        self.assertEqual(["ROCK BAND", "JAZZ ARTIST"], [event.headliner for event in self.events])

    def test_metadata_and_same_day_events(self):
        first, second = self.events
        self.assertEqual("2026-09-23", first.date)
        self.assertEqual("Rock", first.genre)
        self.assertEqual("https://www.alhambra-paris.com/files/rock.jpg", first.image_url)
        self.assertEqual("https://www.alhambra-paris.com/rock-lo1.html", first.ticket_url)
        self.assertEqual("sold_out", second.ticket_status)
