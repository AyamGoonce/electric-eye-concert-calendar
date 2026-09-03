from datetime import date
from pathlib import Path
from unittest import TestCase

from bs4 import BeautifulSoup

from concert_calendar.scrapers.bellevilloise import parse_events


FIXTURE = Path(__file__).parent / "fixtures" / "bellevilloise" / "programme.html"


class BellevilloiseTests(TestCase):
    def test_filters_mixed_programme_by_explicit_concert_categories(self):
        events = parse_events(BeautifulSoup(FIXTURE.read_text(), "html.parser"), today=date(2026, 9, 1))
        self.assertEqual(["SIX60", "Café-Concert : Radio Cantina"], [event.headliner for event in events])
        self.assertEqual(["2026-10-14", "2026-10-15"], [event.date for event in events])

    def test_rejects_clubbing_brunch_and_non_music(self):
        events = parse_events(BeautifulSoup(FIXTURE.read_text(), "html.parser"), today=date(2026, 9, 1))
        titles = [event.headliner for event in events]
        self.assertNotIn("Club Night", titles)
        self.assertNotIn("Jazz Brunch", titles)
        self.assertNotIn("Workshop", titles)

    def test_extracts_official_artwork_and_detail_url(self):
        event = parse_events(BeautifulSoup(FIXTURE.read_text(), "html.parser"), today=date(2026, 9, 1))[0]
        self.assertEqual("https://www.labellevilloise.com/uploads/six60.jpg", event.image_url)
        self.assertEqual("https://bellevilloise.test/six60", event.ticket_url)
