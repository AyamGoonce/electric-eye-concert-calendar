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

    def test_propagates_structured_eligibility_metadata(self):
        soup = BeautifulSoup(
            '<div class="concerts_mois"><div id="Septembre2026" class="concert mois"></div>'
            '<div class="concert" data-event-type="listening session" data-category="record event" '
            'data-tags="vinyl, listening" data-description="A listening event">'
            '<div class="jour">17.09</div><div class="titre">The Vinyl Hour</div>'
            '<div class="description" data-description="A listening event"></div></div></div>',
            "html.parser",
        )
        event = parse_events(soup, today=date(2026, 9, 1))[0]
        self.assertEqual("listening session", event.event_type)
        self.assertEqual("record event", event.category)
        self.assertEqual(["vinyl", "listening"], event.tags)
        self.assertEqual("A listening event", event.description)
