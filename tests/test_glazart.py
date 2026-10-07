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

    def test_multi_artist_bill_resolves_and_corrects_confirmed_headliner_typo(self):
        html = """
        <div class="portfolio-item" data-terms="concert">
          <a class="item-link" href="https://www.glazart.com/09-10-26-concert-predition-temple-force-of-darkness-hexekration-rites/">
            09.10.26 – Concert : Predition Temple + Force of Darkness + Hexekration Rites
          </a>
          <img src="https://example.com/poster.jpg">
        </div>
        """

        detail_html = """
        <p>Perdition Temple (Death Metal, Etats-Unis)</p>
        <p>Force of Darkness (Black/Death/Thrash Metal, Chili)</p>
        <p>Hexekration Rites (Black/Death Metal, France)</p>
        """

        response = Mock(text=detail_html)
        response.raise_for_status = Mock()
        session = Mock()
        session.get.return_value = response

        soup = BeautifulSoup(html, "html.parser")
        event = glazart.parse_card(
            soup.select_one(".portfolio-item"),
            today=date(2026, 10, 7),
            session=session,
        )

        self.assertEqual("Perdition Temple", event.headliner)
        self.assertEqual(
            ["Force of Darkness", "Hexekration Rites"],
            event.co_headliners,
        )
        self.assertEqual(
            ["Perdition Temple", "Force of Darkness", "Hexekration Rites"],
            event.performers,
        )

    def test_load_uses_official_concert_taxonomy_only(self):
        response = Mock(text=FIXTURE.read_text())
        response.raise_for_status = Mock()
        session = Mock()
        session.get.return_value = response
        with patch("concert_calendar.scrapers.glazart.requests.Session", return_value=session):
            events = glazart.load_events(today=date(2026, 9, 1))
        self.assertEqual(2, len(events))
        self.assertNotIn("DJ NAME", [event.headliner for event in events])
