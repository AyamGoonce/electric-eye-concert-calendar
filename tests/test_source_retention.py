"""Regressions for bounded, explicitly failed-source publication retention."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import Mock, patch

from concert_calendar.automation import ProductionValidationError, validate_source_report
from concert_calendar.event_state import reconcile_state
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import prepare_upcoming_events
from concert_calendar.source_retention import (
    SOURCE_STATE_FILENAME,
    SOURCE_STATE_VERSION,
    SourceStateError,
    build_source_state,
    load_source_state,
    validate_retained_identities,
    write_source_state,
)
from concert_calendar.sources import load_events_with_report


NOW = datetime(2026, 9, 22, 10, 0, tzinfo=timezone.utc)


def event(name="Meryl Streek", *, date="2027-01-20", venue="La Cigale", **changes):
    row = ConcertEvent(
        date=date, headliner=name, venue=venue, city="Paris", department="75",
        ticket_url="https://dice.fm/event/one", openers=["Original Support"],
        event_title="Original Title", start_time="20:00",
    )
    for key, value in changes.items():
        setattr(row, key, value)
    return row


def scraper(name, response, *, allow_empty=False):
    return SimpleNamespace(
        SOURCE_NAME=name, __name__=name, ALLOW_EMPTY=allow_empty,
        load_events=Mock(side_effect=response) if isinstance(response, Exception)
        else Mock(return_value=deepcopy(response)),
    )


def run(sources, prior=None, *, now=NOW):
    with (
        patch("concert_calendar.sources.discover_scrapers_with_issues", return_value=(sources, {})),
        redirect_stdout(io.StringIO()),
    ):
        return load_events_with_report(
            scraper_attempts=1, retry_delay_seconds=0,
            prior_source_state=prior, now=now,
        )


def source_state(name="DICE", rows=None, *, now=NOW, previous=None):
    rows = [deepcopy(row) for row in (rows if rows is not None else [event()])]
    for row in rows:
        row.source_names = [name]
    reconcile_state(rows, None, now=now)
    state = build_source_state(
        rows, [{"source_name": name, "status": "ok"}],
        previous, now=now, retained_snapshots={},
    )
    return state, rows


class SourceRetentionTests(unittest.TestCase):
    def test_failed_source_restores_future_row_and_keeps_failed_status(self):
        prior, _ = source_state()
        rows, report = run([scraper("DICE", RuntimeError("HTTP 403"))], prior)
        self.assertEqual(["Meryl Streek"], [row.headliner for row in rows])
        health = report.source_health[0]
        self.assertEqual("failed", health["status"])
        self.assertEqual(0, health["fresh_event_count"])
        self.assertEqual(1, health["fallback_event_count"])
        self.assertEqual(prior["sources"]["DICE"]["last_successful_at"], health["last_successful_at"])
        self.assertEqual(SOURCE_STATE_VERSION, health["source_state_version"])
        self.assertEqual(1, len(report.retention_details))
        self.assertEqual("Meryl Streek", report.retention_details[0]["headliner"])

    def test_allowed_empty_never_falls_back_and_clears_inventory(self):
        prior, _ = source_state()
        rows, report = run([scraper("DICE", [], allow_empty=True)], prior)
        self.assertEqual([], rows)
        self.assertEqual("empty", report.source_health[0]["status"])
        self.assertEqual(0, report.source_health[0]["fallback_event_count"])
        candidate = build_source_state(rows, report.source_health, prior, now=NOW,
                                      retained_snapshots=report.retained_snapshots)
        self.assertEqual([], candidate["sources"]["DICE"]["events"])
        self.assertEqual("2026-09-22T10:00:00Z", candidate["sources"]["DICE"]["last_successful_at"])

    def test_unexpected_empty_still_fails_without_fallback(self):
        prior, _ = source_state()
        rows, report = run([scraper("DICE", [])], prior)
        self.assertEqual([], rows)
        self.assertEqual(0, report.source_health[0]["fallback_event_count"])
        with self.assertRaisesRegex(ProductionValidationError, "unexpectedly returned zero"):
            validate_source_report(report)

    def test_recovered_valid_empty_after_exception_is_not_a_failed_source(self):
        prior, _ = source_state()
        module = SimpleNamespace(
            SOURCE_NAME="DICE", __name__="DICE", ALLOW_EMPTY=True,
            load_events=Mock(side_effect=[RuntimeError("transient"), []]),
        )
        with (
            patch("concert_calendar.sources.discover_scrapers_with_issues",
                  return_value=([module], {})),
            redirect_stdout(io.StringIO()),
        ):
            rows, report = load_events_with_report(
                scraper_attempts=2, retry_delay_seconds=0,
                prior_source_state=prior, now=NOW,
            )
        self.assertEqual([], rows)
        self.assertEqual("empty", report.source_health[0]["status"])
        self.assertEqual({}, report.source_failures)
        self.assertEqual(0, report.source_health[0]["fallback_event_count"])

    def test_successful_smaller_inventory_replaces_not_unions(self):
        prior, _ = source_state(rows=[event("Old"), event("Current", ticket_url="https://dice.fm/current")])
        rows, report = run([scraper("DICE", [event("Current", ticket_url="https://dice.fm/current")])], prior)
        reconcile_state(rows, None, now=NOW)
        candidate = build_source_state(rows, report.source_health, prior, now=NOW,
                                      retained_snapshots=report.retained_snapshots)
        self.assertEqual(["Current"], [item["event"]["headliner"] for item in candidate["sources"]["DICE"]["events"]])

    def test_past_rows_are_never_restored(self):
        prior, _ = source_state(rows=[event("Yesterday", date="2026-09-21"), event("Tomorrow", date="2026-09-23")], now=NOW-timedelta(days=2))
        rows, report = run([scraper("DICE", RuntimeError("offline"))], prior)
        self.assertEqual(["Tomorrow"], [row.headliner for row in rows])
        self.assertEqual(1, report.source_health[0]["fallback_excluded_past_count"])

    def test_paris_date_boundary_filters_utc_yesterday(self):
        at_boundary = datetime(2026, 9, 22, 22, 30, tzinfo=timezone.utc)
        prior, _ = source_state(rows=[event("Paris yesterday", date="2026-09-22"), event("Paris today", date="2026-09-23")], now=at_boundary-timedelta(hours=1))
        rows, _ = run([scraper("DICE", RuntimeError("offline"))], prior, now=at_boundary)
        self.assertEqual(["Paris today"], [row.headliner for row in rows])

    def test_exactly_72_hours_is_retained_then_expires(self):
        prior, _ = source_state(now=NOW)
        rows, _ = run([scraper("DICE", RuntimeError("offline"))], prior, now=NOW+timedelta(hours=72))
        self.assertEqual(1, len(rows))
        expired, report = run([scraper("DICE", RuntimeError("offline"))], prior,
                              now=NOW+timedelta(hours=72, microseconds=1))
        self.assertEqual([], expired)
        self.assertEqual(1, report.source_health[0]["fallback_expired_count"])

    def test_repeated_failure_does_not_advance_clock(self):
        prior, _ = source_state(now=NOW)
        rows, report = run([scraper("DICE", RuntimeError("offline"))], prior, now=NOW+timedelta(hours=40))
        candidate = build_source_state(rows, report.source_health, prior,
                                      now=NOW+timedelta(hours=40), retained_snapshots=report.retained_snapshots)
        self.assertEqual(prior["sources"]["DICE"]["last_successful_at"],
                         candidate["sources"]["DICE"]["last_successful_at"])
        rows2, report2 = run([scraper("DICE", RuntimeError("offline"))], candidate,
                             now=NOW+timedelta(hours=73))
        self.assertEqual([], rows2)
        self.assertEqual(1, report2.source_health[0]["fallback_expired_count"])

    def test_healthy_duplicate_suppresses_stale_metadata_without_enrichment(self):
        prior, _ = source_state(rows=[event(openers=["Stale Support"], ticket_url="https://dice.fm/stale")])
        fresh = event(openers=["Fresh Support"], ticket_url="https://official.test/current",
                      event_title="Fresh Title")
        rows, report = run([scraper("Official", [fresh]), scraper("DICE", RuntimeError("403"))], prior)
        self.assertEqual(1, len(rows))
        self.assertEqual(["Fresh Support"], rows[0].openers)
        self.assertEqual("https://official.test/current", rows[0].ticket_url)
        self.assertEqual("Fresh Title", rows[0].event_title)
        self.assertEqual(["Official"], rows[0].source_names)
        health = report.source_health[1]
        self.assertEqual(1, health["fallback_suppressed_count"])
        self.assertEqual(0, health["fallback_event_count"])

    def test_distinct_performance_is_not_suppressed(self):
        prior, _ = source_state(rows=[event(start_time="18:00", performance_marker="early")])
        fresh = event(start_time="21:00", performance_marker="late")
        rows, report = run([scraper("Official", [fresh]), scraper("DICE", RuntimeError("403"))], prior)
        self.assertEqual(2, len(rows))
        self.assertEqual(1, report.source_health[1]["fallback_event_count"])

    def test_reviewed_relocation_is_suppressed_by_authoritative_current_row(self):
        stale = event("South Arcade", date="2027-03-18", venue="Backstage By The Mill",
                      openers=["Stale"], ticket_url="https://dice.fm/old")
        fresh = event("South Arcade", date="2027-03-18", venue="L'Alhambra",
                      openers=["Fresh"], ticket_url="https://official.test/new")
        prior, _ = source_state(rows=[stale])
        rows, report = run([scraper("Official", [fresh]), scraper("DICE", RuntimeError("403"))], prior)
        self.assertEqual(1, len(rows))
        self.assertEqual("L'Alhambra", rows[0].venue)
        self.assertEqual(["Fresh"], rows[0].openers)
        self.assertEqual(1, report.source_health[1]["fallback_suppressed_count"])

    def test_suppressed_row_is_pruned_from_failed_snapshot(self):
        prior, _ = source_state()
        rows, report = run([scraper("Official", [event()]),
                            scraper("DICE", RuntimeError("403"))], prior)
        reconcile_state(rows, None, now=NOW)
        candidate = build_source_state(rows, report.source_health, prior, now=NOW,
                                      retained_snapshots=report.retained_snapshots)
        self.assertEqual([], candidate["sources"]["DICE"]["events"])

    def test_expired_snapshot_is_pruned_but_clock_is_not_refreshed(self):
        prior, _ = source_state(now=NOW)
        rows, report = run([scraper("DICE", RuntimeError("403"))], prior,
                           now=NOW+timedelta(hours=73))
        candidate = build_source_state(rows, report.source_health, prior,
                                      now=NOW+timedelta(hours=73),
                                      retained_snapshots=report.retained_snapshots)
        self.assertEqual([], candidate["sources"]["DICE"]["events"])
        self.assertEqual(prior["sources"]["DICE"]["last_successful_at"],
                         candidate["sources"]["DICE"]["last_successful_at"])

    def test_id_and_first_seen_survive_healthy_failed_healthy_cycle(self):
        first, first_report = run([scraper("DICE", [event()])])
        event_state = reconcile_state(first, None, now=NOW)
        public_id, first_seen = first[0]._public_id, first[0].first_seen
        prior = build_source_state(first, first_report.source_health, None, now=NOW,
                                   retained_snapshots={})
        second, second_report = run([scraper("DICE", RuntimeError("403"))], prior,
                                    now=NOW+timedelta(hours=6))
        second_state = reconcile_state(second, event_state, now=NOW+timedelta(hours=6))
        self.assertEqual((public_id, first_seen), (second[0]._public_id, second[0].first_seen))
        prior2 = build_source_state(second, second_report.source_health, prior,
                                    now=NOW+timedelta(hours=6), retained_snapshots=second_report.retained_snapshots)
        third, _ = run([scraper("DICE", [event()])], prior2, now=NOW+timedelta(hours=12))
        reconcile_state(third, second_state, now=NOW+timedelta(hours=12))
        self.assertEqual((public_id, first_seen), (third[0]._public_id, third[0].first_seen))

    def test_simultaneous_failed_sources_are_deterministic(self):
        left, _ = source_state("A", [event("A", ticket_url="https://a.test")])
        right, _ = source_state("B", [event("B", ticket_url="https://b.test")])
        prior = {"version": SOURCE_STATE_VERSION, "updated_at": left["updated_at"],
                 "sources": {**left["sources"], **right["sources"]}}
        modules = [scraper("A", RuntimeError("down")), scraper("B", RuntimeError("down"))]
        first, report1 = run(modules, prior)
        second, report2 = run(modules, prior)
        self.assertEqual([row.headliner for row in first], [row.headliner for row in second])
        self.assertEqual(report1.retained_snapshots, report2.retained_snapshots)

    def test_missing_prior_snapshot_is_explicit_and_does_not_fabricate_ownership(self):
        rows, report = run([scraper("DICE", RuntimeError("403"))], None)
        self.assertEqual([], rows)
        health = report.source_health[0]
        self.assertTrue(health["fallback_unavailable"])
        self.assertEqual(0, health["fallback_event_count"])

    def test_removed_source_is_pruned_without_resurrection(self):
        prior, _ = source_state("Removed")
        rows, report = run([scraper("Current", [event("Current")])], prior)
        reconcile_state(rows, None, now=NOW)
        candidate = build_source_state(rows, report.source_health, prior, now=NOW,
                                      retained_snapshots=report.retained_snapshots)
        self.assertEqual(["Current"], list(candidate["sources"]))

    def test_round_trip_is_deterministic_validated_and_excludes_derived_links(self):
        row = event(electric_eye_links=[{"url": "https://private.example"}],
                    description="Unrelated rendered metadata")
        state, _ = source_state(rows=[row])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / SOURCE_STATE_FILENAME
            digest1 = write_source_state(path, state)
            self.assertEqual(state, load_source_state(path))
            digest2 = write_source_state(path, state)
            self.assertEqual(digest1, digest2)
            self.assertEqual(digest1, hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertNotIn("electric_eye_links", path.read_text())
            self.assertNotIn("description", path.read_text())

    def test_malformed_sidecar_fails_safely(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / SOURCE_STATE_FILENAME
            path.write_text('{"version":999,"sources":{}}', encoding="utf-8")
            with self.assertRaises(SourceStateError):
                load_source_state(path)

    def test_snapshot_hints_are_not_a_second_id_allocator(self):
        prior, rows = source_state()
        hint = prior["sources"]["DICE"]["events"][0]["public_id"]
        restored, _ = run([scraper("DICE", RuntimeError("403"))], prior)
        self.assertIsNone(getattr(restored[0], "_public_id", None))
        reconcile_state(restored, None, now=NOW+timedelta(hours=1))
        self.assertEqual(hint, restored[0]._public_id)
        self.assertEqual(rows[0].headliner, restored[0].headliner)

    def test_identity_drift_is_detected_instead_of_minting_new_route(self):
        prior, _ = source_state()
        restored, report = run([scraper("DICE", RuntimeError("403"))], prior)
        wrong = event("Different Artist")
        historical = reconcile_state(restored, None, now=NOW)
        candidate_state = reconcile_state([wrong], historical, now=NOW+timedelta(hours=1))
        with self.assertRaises(SourceStateError):
            validate_retained_identities([wrong], candidate_state, report.retained_snapshots)

    def test_snapshot_carries_only_whitelisted_event_fields(self):
        row = event()
        row.scraper_private_token = "do-not-publish"
        state, _ = source_state(rows=[row])
        serialized = json.dumps(state)
        self.assertNotIn("scraper_private_token", serialized)
        self.assertIn("ticket_url", serialized)
        self.assertIn("public_id", serialized)

    def test_healthy_only_public_semantics_are_unchanged(self):
        prior, _ = source_state(rows=[event("Old")])
        fresh = [event("New", openers=["New Support"])]
        with_retention, report = run([scraper("DICE", fresh)], prior)
        without_retention, _ = run([scraper("DICE", fresh)], None)
        self.assertEqual(prepare_upcoming_events(with_retention),
                         prepare_upcoming_events(without_retention))
        self.assertEqual(0, report.source_health[0]["fallback_event_count"])


if __name__ == "__main__":
    unittest.main()
