from datetime import date
from pathlib import Path
from unittest import TestCase

from bs4 import BeautifulSoup

from concert_calendar.scrapers.dome_de_paris import parse_events


FIXTURE = Path(__file__).parent / "fixtures" / "dome_de_paris" / "programme.html"


class DomeDeParisTests(TestCase):
    def setUp(self):
        self.events = parse_events(
            BeautifulSoup(FIXTURE.read_text(), "html.parser"), today=date(2026, 9, 1)
        )

    def test_only_explicit_concerts_with_real_titles_are_accepted(self):
        self.assertEqual(["ARTIST", "ARTIST"], [event.headliner for event in self.events])

    def test_date_range_and_listing_metadata(self):
        self.assertEqual(["2027-09-24", "2027-09-25"], [event.date for event in self.events])
        self.assertEqual("https://www.ledomedeparis.com/fr/spectacle/1/artist", self.events[0].ticket_url)
        self.assertEqual("https://www.ledomedeparis.com/images/artist.jpg", self.events[0].image_url)
