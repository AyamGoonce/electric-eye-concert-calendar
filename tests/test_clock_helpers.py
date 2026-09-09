from unittest import TestCase

from bs4 import BeautifulSoup

from concert_calendar.scrapers import elysee_montmartre
from tests.clock_helpers import freeze_date


class FixtureClockTests(TestCase):
    def test_historical_fixture_parses_under_reference_clock_and_restores_cutoff(self):
        card = BeautifulSoup('''<div class="bloc_extrait evenement">
          <a class="link" href="https://example.test/show" title="Historical Artist"></a>
          <div class="date">8 septembre 2026</div>
          <div class="visuel"><img src="https://example.test/show.jpg"></div>
        </div>''', "html.parser").div
        original_date = elysee_montmartre.date
        with freeze_date("concert_calendar.scrapers.elysee_montmartre", "2040-01-01"):
            self.assertEqual([], elysee_montmartre.parse_card(card))
            with freeze_date("concert_calendar.scrapers.elysee_montmartre", "2026-09-01"):
                events = elysee_montmartre.parse_card(card)
                self.assertEqual(1, len(events))
                self.assertEqual("2026-09-08", events[0].date)
                self.assertEqual("https://example.test/show.jpg", events[0].image_url)
            self.assertEqual([], elysee_montmartre.parse_card(card))
        self.assertIs(original_date, elysee_montmartre.date)
