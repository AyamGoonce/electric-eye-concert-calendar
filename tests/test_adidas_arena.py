from datetime import date
import requests
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
from concert_calendar.scrapers.adidas_arena import parse_events, load_events, PROGRAMME_URL, CONCERT_PROGRAMME_URL

FIXTURE = Path(__file__).parent / "fixtures" / "adidas_arena" / "programme.html"

class AdidasArenaTests(TestCase):
    def setUp(self):
        self.events = parse_events(BeautifulSoup(FIXTURE.read_text(), "html.parser"), today=date(2026, 9, 1))

    def test_explicit_concert_filter_and_exact_advertised_dates(self):
        self.assertEqual(["2026-10-02", "2026-10-03", "2026-10-30", "2026-11-21"], [e.date for e in self.events])
        self.assertNotIn("SPORT", [e.headliner for e in self.events])

    def test_newly_announced_concert_appears_with_french_uppercase_date(self):
        sample = """
        <div class="app-programmation-card">
            <h3 class="type">concert</h3>
            <h3 class="date">3 DÉCEMBRE 2027 à 19h00</h3>
            <h2>WITHIN TEMPTATION</h2>
            <a class="app-programmation-card__cta"
               href="/programmation/within-temptation--1628">Réserver</a>
        </div>
        """
        parsed = parse_events(
            BeautifulSoup(sample, "html.parser"), today=date(2026, 11, 27)
        )
        self.assertEqual(1, len(parsed))
        self.assertEqual("2027-12-03", parsed[0].date)
        self.assertEqual("WITHIN TEMPTATION", parsed[0].headliner)
        self.assertEqual(
            "https://www.adidasarena.com/programmation/within-temptation--1628",
            parsed[0].ticket_url,
        )

    def test_concert_view_recovers_new_listing_missing_from_stale_all_events(self):
        old = """
        <div class="app-programmation-card concert">
          <h3 class="type">concert</h3>
          <h3 class="date">1 DÉCEMBRE 2027 à 19h00</h3>
          <h2>OLDER BAND</h2>
          <a class="app-programmation-card__cta"
             href="/programmation/older-band--123">Réserver</a>
        </div>
        """
        added = old + """
        <div class="app-programmation-card">
          <h3 class="type">concert</h3>
          <h3 class="date">3 DÉCEMBRE 2027 à 19h00</h3>
          <h2>WITHIN TEMPTATION</h2>
          <a href="/programmation/within-temptation--1628">Réserver</a>
        </div>
        """
        def response(html):
            item = Mock()
            item.text = html
            item.raise_for_status = Mock()
            return item

        session = Mock()
        session.get.side_effect = [response(old), response(added)]
        with patch(
            "concert_calendar.scrapers.adidas_arena.requests.Session",
            return_value=session,
        ):
            events = load_events()
        self.assertEqual(
            ["OLDER BAND", "WITHIN TEMPTATION"],
            [item.headliner for item in events],
        )
        self.assertEqual(2, session.get.call_count)
        self.assertEqual(
            [PROGRAMME_URL, CONCERT_PROGRAMME_URL],
            [call.args[0] for call in session.get.call_args_list],
        )

    def test_real_http_latin1_default_is_overridden_for_french_months(self):
        page = """
        <div class="app-programmation-card concert">
          <h3 class="type">concert</h3>
          <h3 class="date">3 DÉCEMBRE 2027 à 19h00</h3>
          <h2>WITHIN TEMPTATION</h2>
          <a class="app-programmation-card__cta"
             href="/programmation/within-temptation--1628">Réserver</a>
        </div>
        <div class="app-programmation-card concert">
          <h3 class="type">concert</h3>
          <h3 class="date">21 FÉVRIER 2027 à 19h00</h3>
          <h2>JAMES BLUNT</h2>
          <a class="app-programmation-card__cta"
             href="/programmation/james-blunt--1497">Réserver</a>
        </div>
        """
        def mislabelled_response():
            response = requests.Response()
            response.status_code = 200
            response._content = page.encode("utf-8")
            response.encoding = "ISO-8859-1"
            return response

        session = Mock()
        session.get.side_effect = [
            mislabelled_response(), mislabelled_response()
        ]
        with patch(
            "concert_calendar.scrapers.adidas_arena.requests.Session",
            return_value=session,
        ):
            events = load_events()
        self.assertEqual(
            [("2027-02-21", "JAMES BLUNT"),
             ("2027-12-03", "WITHIN TEMPTATION")],
            sorted((item.date, item.headliner) for item in events),
        )

    def test_metadata(self):
        self.assertEqual("20:30", self.events[0].start_time)
        self.assertEqual("https://www.adidasarena.com/images/music.jpg", self.events[0].image_url)
        self.assertEqual("https://www.adidasarena.com/programmation/artist--1", self.events[0].ticket_url)
        self.assertEqual("sold_out", self.events[-1].ticket_status)
