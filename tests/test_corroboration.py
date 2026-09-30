from unittest import TestCase
from unittest.mock import Mock

from concert_calendar.corroboration import (
    corroborate_bandsintown_event,
    corroborate_facebook_event,
)
from concert_calendar.models import ConcertEvent


class Response:
    def __init__(self, text="", payload=None):
        self.text = text
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def event():
    return ConcertEvent(
        date="2026-11-24", headliner="L.A. GUNS", venue="Bal Chavaux",
        city="Montreuil", department="93",
        facebook_event_url="https://www.facebook.com/events/1467918094982117/",
        ticket_url="https://official.example/tickets",
    )


class CorroborationTests(TestCase):
    def test_facebook_cannot_overwrite_stronger_canonical_evidence(self):
        html = """<script type="application/ld+json">{
          "@type":"Event","name":"L.A. GUNS plus a longer title",
          "startDate":"2026-11-24T21:00:00+01:00",
          "location":{"name":"Different Venue","address":{"addressLocality":"Paris"}}
        }</script>"""
        session = Mock()
        session.get.return_value = Response(html)
        current = event()
        result = corroborate_facebook_event(current, session=session, enabled=True)
        self.assertEqual("not_applied", result["status"])
        self.assertEqual("L.A. GUNS", current.headliner)
        self.assertEqual("Bal Chavaux", current.venue)
        self.assertIsNone(current.start_time)
        self.assertEqual("https://official.example/tickets", current.ticket_url)

    def test_facebook_failure_is_non_fatal(self):
        session = Mock()
        session.get.side_effect = RuntimeError("login wall")
        current = event()
        result = corroborate_facebook_event(current, session=session, enabled=True)
        self.assertEqual("unavailable", result["status"])
        self.assertEqual("L.A. GUNS", current.headliner)

    def test_bandsintown_exact_match_only_fills_blank_time(self):
        session = Mock()
        session.get.return_value = Response(payload=[{
            "datetime": "2026-11-24T19:30:00+01:00",
            "venue": {"name": "Bal Chavaux", "city": "Montreuil"},
            "url": "https://bandsintown.example/event",
        }])
        current = event()
        result = corroborate_bandsintown_event(
            current, session=session, app_id="authorized-test-app",
        )
        self.assertEqual("applied", result["status"])
        self.assertEqual("19:30", current.start_time)
        self.assertEqual("https://official.example/tickets", current.ticket_url)
        self.assertEqual("L.A. GUNS", current.headliner)

    def test_bandsintown_unavailable_or_uncredentialed_is_non_fatal(self):
        current = event()
        self.assertEqual(
            "disabled", corroborate_bandsintown_event(current, app_id=None)["status"],
        )
        session = Mock()
        session.get.side_effect = TimeoutError("offline")
        result = corroborate_bandsintown_event(
            current, session=session, app_id="authorized-test-app",
        )
        self.assertEqual("unavailable", result["status"])
        self.assertEqual("L.A. GUNS", current.headliner)
