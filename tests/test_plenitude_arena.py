from datetime import date
from pathlib import Path
from unittest import TestCase

from bs4 import BeautifulSoup

from concert_calendar.scrapers.plenitude_arena import parse_detail, parse_programme


FIXTURES = Path(__file__).parent / "fixtures" / "plenitude_arena"


class PlenitudeArenaTests(TestCase):
    def test_programme_uses_explicit_concert_taxonomy(self):
        cards = parse_programme(BeautifulSoup((FIXTURES / "programme.html").read_text(), "html.parser"))
        self.assertEqual(["ARTIST"], [card["title"] for card in cards])
        self.assertEqual("https://www.plenitudearena.com/images/artist.jpg", cards[0]["image_url"])

    def test_detail_uses_exact_performance_calendar_not_date_range(self):
        card = parse_programme(BeautifulSoup((FIXTURES / "programme.html").read_text(), "html.parser"))[0]
        events = parse_detail(
            BeautifulSoup((FIXTURES / "detail.html").read_text(), "html.parser"),
            card,
            today=date(2026, 9, 1),
        )
        self.assertEqual(["2026-09-12", "2026-09-16"], [event.date for event in events])
        self.assertEqual("Plénitude Arena", events[0].venue)
        self.assertEqual("Nanterre", events[0].city)
        self.assertEqual("19:30", events[0].start_time)
        self.assertEqual("sold_out", events[1].ticket_status)

    def test_single_date_json_ld_fallback(self):
        card = {"title": "MUSE", "url": "https://example.test/muse", "image_url": None}
        events = parse_detail(
            BeautifulSoup((FIXTURES / "detail-single.html").read_text(), "html.parser"),
            card,
            today=date(2026, 9, 1),
        )
        self.assertEqual(1, len(events))
        self.assertEqual("2026-11-27", events[0].date)
        self.assertEqual("20:00", events[0].start_time)
        self.assertEqual("https://tickets.example/single", events[0].ticket_url)

    def test_json_ld_date_without_time(self):
        card = {"title": "RUSH", "url": "https://example.test/rush", "image_url": None}
        events = parse_detail(
            BeautifulSoup((FIXTURES / "detail-date-only.html").read_text(), "html.parser"),
            card,
            today=date(2026, 9, 1),
        )
        self.assertEqual("2027-02-19", events[0].date)
        self.assertIsNone(events[0].start_time)
