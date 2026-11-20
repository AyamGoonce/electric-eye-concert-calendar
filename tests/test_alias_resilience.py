from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import Mock, patch

import requests

from concert_calendar.alias_coverage import alias_official_overlap
from concert_calendar.models import ConcertEvent
from concert_calendar.scrapers import alias


class AliasAccessTests(TestCase):
    def test_403_captures_bounded_non_sensitive_response_fingerprint(self):
        response = requests.Response()
        response.status_code = 403
        response.url = alias.EVENTS_URL
        response._content = b"Forbidden - request blocked"
        response.headers["Server"] = "cloudflare"
        response.headers["CF-Ray"] = "abc123-CDG"
        response.headers["Set-Cookie"] = "SECRET"
        session = Mock()
        session.get.return_value = response
        alias._ACCESS_DIAGNOSTICS.clear()
        with self.assertRaises(requests.HTTPError):
            alias._fetch(session, alias.EVENTS_URL, headers=alias.HEADERS, timeout=30)
        diagnostic = alias.get_diagnostics()[0]
        self.assertEqual("http_access_denied", diagnostic["kind"])
        self.assertEqual(403, diagnostic["status_code"])
        self.assertEqual("/billetterie/", diagnostic["path"])
        self.assertEqual("abc123-CDG", diagnostic["cf_ray"])
        self.assertNotIn("SECRET", str(diagnostic))
        self.assertNotIn("Forbidden", str(diagnostic))
        self.assertEqual(8.0, alias.retry_delay_for_error(requests.HTTPError(response=response), 1, 2.0))
        self.assertEqual(16.0, alias.retry_delay_for_error(requests.HTTPError(response=response), 2, 2.0))

    def test_non_403_retains_normal_retry_policy(self):
        self.assertEqual(4.0, alias.retry_delay_for_error(ValueError("other error"), 2, 2.0))

    def test_healthy_response_has_no_diagnostic(self):
        response = requests.Response()
        response.status_code = 200
        response._content = b"OK"
        session = Mock()
        session.get.return_value = response
        alias._ACCESS_DIAGNOSTICS.clear()
        self.assertIs(alias._fetch(session, alias.EVENTS_URL), response)
        self.assertEqual([], alias.get_diagnostics())


class AliasVenueCoverageTests(TestCase):
    NOW = datetime(2026, 11, 20, 13, 0, tzinfo=timezone.utc)

    @staticmethod
    def old_row(date, artist, venue, time=None):
        return {"event": {"date": date, "headliner": artist, "venue": venue,
                          "city": "Paris", "department": "75", "start_time": time}}

    def test_exact_official_venue_overlap_and_unverified_inventory(self):
        state = {"sources": {"Alias Production": {"events": [
            self.old_row("2026-11-24", "Example Band", "Bataclan"),
            self.old_row("2026-11-25", "Another Band", "Bataclan"),
            self.old_row("2026-11-19", "Past Band", "Bataclan"),
        ]}}}
        health = [{"source_name": "Alias Production", "status": "failed"}]
        event = ConcertEvent(date="2026-11-24", headliner="EXAMPLE BAND", venue="Bataclan",
                             city="Paris", department="75", source_names=["Bataclan"])
        records = alias_official_overlap(state, health, [event], now=self.NOW)
        summary = records[0]
        self.assertEqual(2, summary["prior_future_events"])
        self.assertEqual(1, summary["independently_covered"])
        self.assertEqual(1, summary["not_independently_verified"])
        self.assertEqual(["Bataclan"], records[1]["official_sources"])
        self.assertNotIn("Alias Production", event.source_names or [])
        self.assertIsNone(event.promoters)

    def test_aggregator_and_mismatched_time_never_count_as_venue_evidence(self):
        state = {"sources": {"Alias Production": {"events": [
            self.old_row("2026-11-24", "Example Band", "Bataclan", "20:00"),
        ]}}}
        health = [{"source_name": "Alias Production", "status": "failed"}]
        aggregator = ConcertEvent(date="2026-11-24", headliner="Example Band", venue="Bataclan",
                                  city="Paris", department="75", source_names=["DICE"])
        venue = ConcertEvent(date="2026-11-24", headliner="Example Band", venue="Bataclan",
                             city="Paris", department="75", source_names=["Bataclan"],
                             start_time="22:00")
        records = alias_official_overlap(state, health, [aggregator, venue], now=self.NOW)
        self.assertEqual(0, records[0]["independently_covered"])

    def test_no_recovery_claim_when_alias_is_healthy(self):
        self.assertEqual([], alias_official_overlap(
            {}, [{"source_name": "Alias Production", "status": "ok"}], [], now=self.NOW
        ))
