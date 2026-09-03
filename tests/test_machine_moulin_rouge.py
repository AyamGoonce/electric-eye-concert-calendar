from datetime import date
from pathlib import Path
from unittest import TestCase

from bs4 import BeautifulSoup

from concert_calendar.scrapers.machine_moulin_rouge import parse_events


FIXTURE = Path(__file__).parent / "fixtures" / "machine_moulin_rouge" / "programme.html"


class MachineMoulinRougeTests(TestCase):
    def setUp(self):
        self.events = parse_events(
            BeautifulSoup(FIXTURE.read_text(), "html.parser"),
            today=date(2026, 9, 1),
        )

    def test_accepts_only_explicit_concert_cards(self):
        self.assertEqual(["CORONER", "Artist + Support"], [event.headliner for event in self.events])
        self.assertNotIn("Trendy", [event.headliner for event in self.events])
        self.assertNotIn("Untyped listing", [event.headliner for event in self.events])

    def test_preserves_same_day_performances_and_billing(self):
        self.assertEqual(["19:00", "20:00"], [event.start_time for event in self.events])
        self.assertEqual("Artist + Support", self.events[1].headliner)
        self.assertIsNone(self.events[1].openers)

    def test_extracts_status_detail_link_and_artwork(self):
        event = self.events[0]
        self.assertEqual("sold_out", event.ticket_status)
        self.assertEqual("https://machine.test/coroner", event.ticket_url)
        self.assertEqual("https://www.lamachinedumoulinrouge.com/uploads/coroner.jpg", event.image_url)
