from datetime import date
from pathlib import Path
from unittest import TestCase

from bs4 import BeautifulSoup

from concert_calendar.scrapers.stade_de_france import parse_events


FIXTURE = Path(__file__).parent / "fixtures" / "stade_de_france" / "concerts.html"


class StadeDeFranceTests(TestCase):
    def setUp(self):
        self.events = parse_events(
            BeautifulSoup(FIXTURE.read_text(), "html.parser"),
            today=date(2026, 9, 1),
        )

    def test_preserves_each_explicit_concert_date(self):
        self.assertEqual(
            ["2026-09-04", "2026-09-05", "2027-04-09", "2027-04-10", "2027-04-11"],
            [event.date for event in self.events],
        )
        self.assertEqual({"Stade de France"}, {event.venue for event in self.events})
        self.assertEqual({"Saint-Denis"}, {event.city for event in self.events})

    def test_official_metadata_and_sold_out_state(self):
        self.assertEqual("https://tickets.example/plk", self.events[0].ticket_url)
        self.assertEqual("https://www.stadefrance.com/images/plk.jpg", self.events[0].image_url)
        self.assertEqual("tickets", self.events[0].ticket_status)
        self.assertTrue(self.events[-1].sold_out)
        self.assertEqual("sold_out", self.events[-1].ticket_status)
