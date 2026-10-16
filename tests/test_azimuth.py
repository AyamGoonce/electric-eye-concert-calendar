from unittest import TestCase

from bs4 import BeautifulSoup

from concert_calendar.scrapers.azimuth import parse_card


def card(artist: str, venue: str):
    return BeautifulSoup(
        f"""
        <article>
          <a href="https://tickets.example/show">Tickets</a>
          <div class="elementor-inner-section">
            <div class="elementor-container">
              <div class="elementor-inner-column"><h4>{artist}</h4></div>
              <div class="elementor-inner-column">21/10/2026</div>
              <div class="elementor-inner-column">{venue}</div>
              <div class="elementor-inner-column">Paris</div>
            </div>
          </div>
        </article>
        """,
        "html.parser",
    ).select_one("article")


class AzimuthBillingTests(TestCase):
    def test_support_copy_is_promoted_to_billing(self):
        event = parse_card(card(
            "GOODBYE KARELLE",
            "La Maroquinerie – support Zed Yun Pavarotti",
        ))

        self.assertEqual("Zed Yun Pavarotti", event.headliner)
        self.assertEqual(["GOODBYE KARELLE"], event.openers)
        self.assertEqual("La Maroquinerie", event.venue)

    def test_unknown_descriptive_venue_is_preserved(self):
        event = parse_card(card(
            "Artist",
            "Independent Arts Space – rooftop room",
        ))

        self.assertEqual("Artist", event.headliner)
        self.assertIsNone(event.openers)
        self.assertEqual("Independent Arts Space – rooftop room", event.venue)
