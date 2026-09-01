import unittest
from unittest.mock import patch

import requests

from concert_calendar.automation import (
    ProductionValidationError,
    validate_source_report,
)
from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent
from concert_calendar.scrapers import zenith_paris
from concert_calendar.sources import load_events_with_report
from concert_calendar.venues import normalize_event_venue


def event(headliner="Artist", venue="Zénith Paris - La Villette"):
    return ConcertEvent(
        date="2027-01-01",
        headliner=headliner,
        venue=venue,
        city="Paris",
        department="75",
        ticket_url="https://tickets.example/artist",
        image_url="https://images.example/artist.jpg",
        image_source="Live Nation",
        promoters=["Live Nation"],
    )


class ZenithFallbackTests(unittest.TestCase):
    def test_primary_success_does_not_call_fallback(self):
        primary = [event()]
        with (
            patch.object(zenith_paris, "load_primary_events", return_value=primary),
            patch.object(zenith_paris, "load_fallback_events") as fallback,
        ):
            self.assertIs(primary, zenith_paris.load_events())
        fallback.assert_not_called()

    def test_primary_timeout_uses_successful_fallback(self):
        recovered = [event()]
        with (
            patch.object(
                zenith_paris,
                "load_primary_events",
                side_effect=requests.Timeout("timed out"),
            ),
            patch.object(
                zenith_paris, "load_fallback_events", return_value=recovered
            ),
        ):
            self.assertEqual(recovered, zenith_paris.load_events())

    def test_primary_and_fallback_failure_remains_unhealthy(self):
        with (
            patch(
                "concert_calendar.sources.discover_scrapers_with_issues",
                return_value=([zenith_paris], {}),
            ),
            patch.object(
                zenith_paris,
                "load_primary_events",
                side_effect=requests.Timeout("timed out"),
            ),
            patch.object(
                zenith_paris,
                "load_fallback_events",
                side_effect=requests.ConnectionError("fallback unavailable"),
            ),
        ):
            _, report = load_events_with_report(
                scraper_attempts=1, retry_delay_seconds=0
            )
        self.assertIn(zenith_paris.SOURCE_NAME, report.source_failures)
        with self.assertRaisesRegex(
            ProductionValidationError, "Scrapers exhausted retries"
        ):
            validate_source_report(report)

    def test_fallback_filters_exactly_to_canonical_zenith_paris(self):
        candidates = [
            event("Paris", "Zénith Paris - La Villette"),
            event("Elsewhere", "Zénith de Strasbourg"),
            event("Dresden Dolls", "Élysée Montmartre"),
        ]
        with patch(
            "concert_calendar.scrapers.livenation.load_events",
            return_value=candidates,
        ):
            recovered = zenith_paris.load_fallback_events()
        self.assertEqual(["Paris"], [item.headliner for item in recovered])
        self.assertTrue(
            all(item.venue == zenith_paris.SOURCE_NAME for item in recovered)
        )

    def test_fallback_and_promoter_duplicate_merge_without_affecting_dresden(self):
        fallback = event("Shared Artist")
        fallback.source_names = [zenith_paris.SOURCE_NAME]
        promoter = event("SHARED ARTIST", "Le Zénith")
        promoter.source_names = ["Live Nation"]
        dresden = ConcertEvent(
            date="2026-09-08",
            headliner="THE DRESDEN DOLLS",
            venue="Élysée Montmartre",
            city="Paris",
            department="75",
            source_names=["Élysée Montmartre"],
        )
        merged = deduplicate_events([
            normalize_event_venue(fallback),
            normalize_event_venue(promoter),
            normalize_event_venue(dresden),
        ])
        self.assertEqual(2, len(merged))
        self.assertEqual(
            1,
            sum(item.headliner.casefold() == "shared artist" for item in merged),
        )
        self.assertEqual(
            1,
            sum("dresden dolls" in item.headliner.casefold() for item in merged),
        )


if __name__ == "__main__":
    unittest.main()
