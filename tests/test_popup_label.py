from datetime import date
from pathlib import Path
from unittest import TestCase

from bs4 import BeautifulSoup

from concert_calendar.scrapers.popup_label import parse_events


FIXTURE = Path(__file__).parent / "fixtures" / "popup_label" / "programme.html"


class PopupLabelTests(TestCase):
    def test_parses_concerts_and_explicit_support(self):
        events = parse_events(
            BeautifulSoup(FIXTURE.read_text(), "html.parser"),
            today=date(2026, 9, 1),
        )

        self.assertEqual(["Lamb", "She's Green", "Tia Gordon"], [event.headliner for event in events])
        self.assertEqual(["BARE MINIMUM", "Second Support"], events[0].openers)
        self.assertEqual("https://facebook.test/lamb", events[0].facebook_event_url)
        self.assertEqual("https://www.popup.paris/uploads/lamb.jpg", events[0].image_url)
        self.assertEqual("sold_out", events[1].ticket_status)
        self.assertEqual("2027-01-20", events[2].date)

    def test_excludes_explicit_late_night_club_sessions(self):
        events = parse_events(
            BeautifulSoup(FIXTURE.read_text(), "html.parser"),
            today=date(2026, 9, 1),
        )
        self.assertNotIn("Club Night", [event.headliner for event in events])
