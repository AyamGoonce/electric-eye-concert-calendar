from datetime import date
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

from concert_calendar.scrapers import glazart


FIXTURE = Path(__file__).parent / "fixtures" / "glazart" / "programme.html"


class GlazartTests(TestCase):
    def test_parses_concert_only_card_and_rejects_placeholder(self):
        soup = BeautifulSoup(FIXTURE.read_text(), "html.parser")
        first, second = soup.select("[data-terms='concert']")
        event = glazart.parse_card(first, today=date(2026, 9, 1))
        self.assertEqual("2026-09-15", event.date)
        self.assertEqual("FUNEBRARUM", event.headliner)
        self.assertEqual("Glazart", event.venue)
        self.assertEqual("https://www.glazart.com/15-09-26-concert-funebrarum/", event.ticket_url)
        placeholder = glazart.parse_card(second, today=date(2026, 9, 1))
        self.assertIsNone(placeholder.image_url)

    def test_load_uses_official_concert_taxonomy_only(self):
        response = Mock(text=FIXTURE.read_text())
        response.raise_for_status = Mock()
        session = Mock()
        session.get.return_value = response
        with patch("concert_calendar.scrapers.glazart.requests.Session", return_value=session):
            events = glazart.load_events()
        self.assertEqual(2, len(events))
        self.assertNotIn("DJ NAME", [event.headliner for event in events])
