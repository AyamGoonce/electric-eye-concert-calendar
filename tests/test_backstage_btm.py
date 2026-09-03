from datetime import date
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

from concert_calendar.scrapers import backstage_btm


FIXTURES = Path(__file__).parent / "fixtures" / "backstage_btm"


class BackstageByTheMillTests(TestCase):
    def test_parses_official_card_metadata(self):
        soup = BeautifulSoup(
            (FIXTURES / "programme.html").read_text(), "html.parser"
        )
        event = backstage_btm.parse_card(
            soup.select_one("li"), today=date(2026, 9, 1)
        )
        self.assertEqual("2027-03-18", event.date)
        self.assertEqual("SOUTH ARCADE", event.headliner)
        self.assertEqual("Backstage By The Mill", event.venue)
        self.assertEqual("Alternative", event.genre)
        self.assertEqual("sold_out", event.ticket_status)
        self.assertEqual(
            "https://www.backstage-btm.com/agenda/south-arcade/",
            event.ticket_url,
        )
        self.assertEqual(
            "https://www.backstage-btm.com/wp-content/uploads/south-arcade.jpg",
            event.image_url,
        )

    def test_rejects_explicit_dj_only_card(self):
        soup = BeautifulSoup(
            (FIXTURES / "programme.html").read_text(), "html.parser"
        )
        self.assertIsNone(
            backstage_btm.parse_card(
                soup.select("li")[2], today=date(2026, 9, 1)
            )
        )

    def test_load_events_follows_bounded_pagination(self):
        responses = []
        for filename in ("programme.html", "page-2.html"):
            response = Mock()
            response.text = (FIXTURES / filename).read_text()
            response.raise_for_status = Mock()
            responses.append(response)
        session = Mock()
        session.get.side_effect = responses
        with patch("concert_calendar.scrapers.backstage_btm.requests.Session", return_value=session):
            events = backstage_btm.load_events()
        self.assertEqual(3, len(events))
        self.assertEqual(2, session.get.call_count)
        session.get.assert_any_call(
            backstage_btm.PROGRAMME_URL,
            headers=backstage_btm.HEADERS,
            timeout=backstage_btm.REQUEST_TIMEOUT,
        )
