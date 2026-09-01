import hashlib
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone
import json

from concert_calendar.automation import (
    PUBLIC_STABLE_ASSETS,
    STALE_PUBLIC_TEST_ASSETS,
    ProductionValidationError,
    publish,
    promote_verified,
    read_pointer,
    stage_candidate,
    validate_count_regression,
    validate_genre_coverage,
    validate_events,
    validate_source_report,
)
from concert_calendar.production_export import build_current_pointer, build_data_asset
from concert_calendar.event_state import (
    EventStateError,
    canonical_event_identity,
    load_state,
    is_new,
    reconcile_state,
    write_state,
)
from concert_calendar.models import ConcertEvent
from concert_calendar.venues import normalize_event_venue
from concert_calendar.sources import load_events_with_report


def valid_event(index=0):
    return {
        "d": "2027-01-01",
        "h": f"Artist {index}",
        "o": [],
        "v": "La CLEF",
        "c": "Saint-Germain-en-Laye",
        "x": ["Hip-hop / Rap"],
        "p": ["Example promoter"],
        "t": "https://example.com/tickets",
        "f": False,
        "so": False,
        "fs": "2026-08-20T00:00:00Z",
        "i": f"{index:016x}",
        "ts": "tickets",
        "st": None,
    }


def write_generated_publication(destination, marker="candidate"):
    destination.mkdir(parents=True, exist_ok=True)
    for stable in PUBLIC_STABLE_ASSETS:
        if stable != "electric-eye-content-current.js":
            (destination / stable).write_text(stable, encoding="utf-8")
    content_body = f"content-{marker}".encode()
    content_digest = hashlib.sha256(content_body).hexdigest()
    content_name = f"electric-eye-content.{content_digest[:16]}.js"
    (destination / content_name).write_bytes(content_body)
    (destination / "electric-eye-content-current.js").write_text(
        "window.ElectricEyeContentManifest=Object.freeze("
        + json.dumps({"data": content_name, "sha256": content_digest})
        + ");\n",
        encoding="utf-8",
    )
    state = {"version": 1, "updated_at": "2026-08-23T10:00:00Z", "events": {}}
    state_digest = write_state(destination / "calendar-state.json", state)
    filename, digest, asset = build_data_asset(
        [valid_event(index) for index in range(100)],
        published_at="2026-08-23T10:00:00Z",
    )
    (destination / filename).write_text(asset, encoding="utf-8")
    (destination / "calendar-current.js").write_text(
        build_current_pointer(
            filename, digest, 100,
            published_at="2026-08-23T10:00:00Z",
            state_sha256=state_digest,
        ),
        encoding="utf-8",
    )

    (destination / "index.html").write_text(
        "<!doctype html><title>Electric Eye Archive</title>",
        encoding="utf-8",
    )
    artist_route = destination / "artist" / "test-artist"
    artist_route.mkdir(parents=True)
    (artist_route / "index.html").write_text(
        "<!doctype html><title>Test Artist</title>",
        encoding="utf-8",
    )
    concert_route = destination / "concert" / "0000000000000000"
    concert_route.mkdir(parents=True)
    (concert_route / "index.html").write_text(
        "<!doctype html><title>Test Concert</title>",
        encoding="utf-8",
    )

    return filename, digest


class AutomationValidationTests(unittest.TestCase):
    def test_genre_coverage_guard_rejects_catastrophic_collapse(self):
        with self.assertRaises(ProductionValidationError):
            validate_genre_coverage({"total": 1000, "populated": 99})
        validate_genre_coverage({"total": 1000, "populated": 100})

    def test_source_loader_retries_zero_result_with_a_bound(self):
        scraper = type(
            "Scraper",
            (),
            {"SOURCE_NAME": "Transient source", "load_events": Mock(return_value=[])},
        )
        with patch(
            "concert_calendar.sources.discover_scrapers_with_issues",
            return_value=([scraper], {}),
        ):
            events, report = load_events_with_report(
                scraper_attempts=3, retry_delay_seconds=0
            )

        self.assertEqual(events, [])
        self.assertEqual(report.source_counts, {"Transient source": 0})
        self.assertEqual(scraper.load_events.call_count, 3)
        self.assertEqual("empty", report.source_health[0]["status"])
        with self.assertRaisesRegex(
            ProductionValidationError, "unexpectedly returned zero"
        ):
            validate_source_report(report)

    def test_source_health_allows_explicitly_legitimate_empty_source(self):
        scraper = type(
            "Scraper",
            (),
            {
                "SOURCE_NAME": "Seasonal source",
                "ALLOW_EMPTY": True,
                "load_events": Mock(return_value=[]),
            },
        )
        healthy = type(
            "HealthyScraper",
            (),
            {
                "SOURCE_NAME": "Healthy source",
                "load_events": Mock(return_value=[ConcertEvent(
                    date="2027-01-01",
                    headliner="Artist",
                    venue="La CLEF",
                    city="Saint-Germain-en-Laye",
                    department="78",
                )]),
            },
        )
        with (
            patch(
                "concert_calendar.sources.discover_scrapers_with_issues",
                return_value=([scraper, healthy], {}),
            ),
            patch("concert_calendar.automation.CORE_SOURCES", set()),
        ):
            _, report = load_events_with_report(
                scraper_attempts=1, retry_delay_seconds=0
            )
            validate_source_report(report)

    def test_source_health_rejects_unregistered_scraper_file(self):
        with patch(
            "concert_calendar.sources.discover_scrapers_with_issues",
            return_value=([], {"broken_source": "load_events() is missing"}),
        ):
            _, report = load_events_with_report(
                scraper_attempts=1, retry_delay_seconds=0
            )
        with self.assertRaisesRegex(
            ProductionValidationError, "Scraper registration failures"
        ):
            validate_source_report(report)

    def test_source_health_rejects_registered_scraper_not_exercised(self):
        scraper = type(
            "Scraper",
            (),
            {
                "SOURCE_NAME": "Healthy source",
                "load_events": Mock(return_value=[ConcertEvent(
                    date="2027-01-01",
                    headliner="Artist",
                    venue="La CLEF",
                    city="Saint-Germain-en-Laye",
                    department="78",
                )]),
            },
        )
        with patch(
            "concert_calendar.sources.discover_scrapers_with_issues",
            return_value=([scraper], {}),
        ):
            _, report = load_events_with_report(
                scraper_attempts=1, retry_delay_seconds=0
            )
        report = replace(
            report,
            configured_sources=report.configured_sources + ["Skipped source"],
        )
        with self.assertRaisesRegex(
            ProductionValidationError, "were not exercised: Skipped source"
        ):
            validate_source_report(report)

    def test_source_health_rejects_crashed_scraper(self):
        scraper = type(
            "Scraper",
            (),
            {
                "SOURCE_NAME": "Broken source",
                "load_events": Mock(side_effect=RuntimeError("upstream failed")),
            },
        )
        with patch(
            "concert_calendar.sources.discover_scrapers_with_issues",
            return_value=([scraper], {}),
        ):
            _, report = load_events_with_report(
                scraper_attempts=1, retry_delay_seconds=0
            )
        self.assertEqual("failed", report.source_health[0]["status"])
        with self.assertRaisesRegex(
            ProductionValidationError, "Scrapers exhausted retries"
        ):
            validate_source_report(report)

    def test_count_regression_guard_allows_normal_drift(self):
        validate_count_regression(1600, 1732)

    def test_count_regression_guard_rejects_large_drop(self):
        with self.assertRaises(ProductionValidationError):
            validate_count_regression(900, 1732)

    def test_explicit_override_allows_large_change(self):
        validate_count_regression(900, 1732, allow_large_change=True)

    def test_event_contract_rejects_duplicate_records(self):
        events = [valid_event(index) for index in range(100)]
        events[-1] = events[0].copy()
        with self.assertRaises(ProductionValidationError):
            validate_events(events)

    def test_event_contract_rejects_raw_public_genre(self):
        events = [valid_event(index) for index in range(100)]
        events[0]["x"] = ["Rap, Hip-Hop"]
        with self.assertRaises(ProductionValidationError):
            validate_events(events)

    def test_event_contract_rejects_descriptive_venue_billing(self):
        events = [valid_event(index) for index in range(100)]
        events[0]["v"] = "En première partie de ARTIST | La Seine Musicale"
        with self.assertRaises(ProductionValidationError):
            validate_events(events)

    def test_event_contract_rejects_relocation_notice_headliner(self):
        events = [valid_event(index) for index in range(100)]
        events[0]["h"] = "CHANGEMENT DE SALLE _ Artist"
        with self.assertRaises(ProductionValidationError):
            validate_events(events)

    def test_event_contract_allows_legitimate_move_title(self):
        events = [valid_event(index) for index in range(100)]
        events[0]["h"] = "The Move"
        validate_events(events)

    def test_event_contract_allows_legitimate_angle_bracket_title(self):
        events = [valid_event(index) for index in range(100)]
        events[0]["h"] = "ALL(H)OURS <RISE UP>"
        validate_events(events)

    def test_publish_stages_data_before_pointer_and_keeps_three_hashes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            generated = root / "generated"
            pages = root / "pages"
            proof = pages / "proof"
            generated.mkdir()
            proof.mkdir(parents=True)

            old_names = []
            for marker in ("oldest", "previous"):
                body = marker.encode()
                digest = hashlib.sha256(body).hexdigest()
                name = f"calendar-data.{digest[:16]}.js"
                (proof / name).write_bytes(body)
                old_names.append((name, digest))
            (proof / "calendar-current.js").write_text(
                build_current_pointer(old_names[-1][0], old_names[-1][1], 100),
                encoding="utf-8",
            )

            subprocess_result = __import__("subprocess").run(
                ["git", "init", "-q"], cwd=pages, check=True
            )
            self.assertEqual(subprocess_result.returncode, 0)
            __import__("subprocess").run(
                ["git", "add", "."], cwd=pages, check=True
            )
            __import__("subprocess").run(
                [
                    "git",
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.com",
                    "commit",
                    "-qm",
                    "fixture",
                ],
                cwd=pages,
                check=True,
            )

            filename, digest = write_generated_publication(generated)
            args = type(
                "Args",
                (),
                {"generated_dir": str(generated), "pages_dir": str(pages)},
            )()

            publish(args)

            self.assertEqual(read_pointer(proof / "calendar-current.js")["data"], filename)
            self.assertEqual(len(list(proof.glob("calendar-data.*.js"))), 3)
            self.assertEqual((proof / "calendar-state.json").read_text(), (generated / "calendar-state.json").read_text())

    def test_candidate_failure_leaves_live_release_and_success_promotes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            generated = root / "generated"
            pages = root / "pages"
            proof = pages / "proof"
            proof.mkdir(parents=True)
            old_body = b"known-good"
            old_digest = hashlib.sha256(old_body).hexdigest()
            old_name = f"calendar-data.{old_digest[:16]}.js"
            (proof / old_name).write_bytes(old_body)
            (proof / "calendar-current.js").write_text(
                build_current_pointer(old_name, old_digest, 99), encoding="utf-8"
            )
            for stale in STALE_PUBLIC_TEST_ASSETS:
                (proof / stale).write_text("test harness", encoding="utf-8")
            __import__("subprocess").run(["git", "init", "-q"], cwd=pages, check=True)
            __import__("subprocess").run(["git", "add", "."], cwd=pages, check=True)
            __import__("subprocess").run(
                ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "baseline"],
                cwd=pages, check=True,
            )
            filename, digest = write_generated_publication(generated)
            candidate_id = digest + "-123"
            stage_candidate(type("Args", (), {
                "generated_dir": str(generated), "pages_dir": str(pages),
                "candidate_id": candidate_id,
            })())
            candidate = proof / "candidates" / candidate_id
            promote_args = type("Args", (), {
                "candidate_dir": str(candidate), "pages_dir": str(pages),
                "base_url": "https://example.invalid/candidate",
                "sha256": digest, "timeout": 1,
            })()

            def fail_verification(_args):
                raise ProductionValidationError("forced hosted verification failure")

            with self.assertRaises(ProductionValidationError):
                promote_verified(promote_args, verifier=fail_verification)
            self.assertEqual(read_pointer(proof / "calendar-current.js")["data"], old_name)

            promote_verified(promote_args, verifier=lambda _args: 0)
            self.assertEqual(read_pointer(proof / "calendar-current.js")["data"], filename)
            self.assertFalse(any((proof / stale).exists() for stale in STALE_PUBLIC_TEST_ASSETS))
            self.assertFalse((proof / "candidates").exists())

    def test_final_verification_rollback_is_a_normal_commit_restoring_baseline(self):
        with tempfile.TemporaryDirectory() as temporary:
            pages = Path(temporary)
            proof = pages / "proof"
            proof.mkdir()
            subprocess = __import__("subprocess")
            subprocess.run(["git", "init", "-q"], cwd=pages, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=pages, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=pages, check=True)
            (proof / "calendar-current.js").write_text("known-good", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=pages, check=True)
            subprocess.run(["git", "commit", "-qm", "baseline"], cwd=pages, check=True)
            baseline = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=pages, text=True).strip()

            (proof / "calendar-current.js").write_text("promoted-candidate", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=pages, check=True)
            subprocess.run(["git", "commit", "-qm", "promotion"], cwd=pages, check=True)
            subprocess.run(
                ["git", "restore", f"--source={baseline}", "--staged", "--worktree", "--", "."],
                cwd=pages, check=True,
            )
            subprocess.run(["git", "commit", "-qm", "rollback"], cwd=pages, check=True)

            self.assertEqual((proof / "calendar-current.js").read_text(), "known-good")
            self.assertEqual(
                subprocess.check_output(["git", "rev-list", "--count", "HEAD"], cwd=pages, text=True).strip(),
                "3",
            )
            subprocess.run(["git", "merge-base", "--is-ancestor", baseline, "HEAD"], cwd=pages, check=True)


class PersistentEventStateTests(unittest.TestCase):
    NOW = datetime(2026, 8, 23, 12, tzinfo=timezone.utc)

    def make_event(self, **changes):
        values = {
            "date": "2026-09-01", "headliner": "The Afghan Whigs",
            "venue": "Le Trabendo", "city": "Paris", "department": "75",
            "ticket_url": "https://example.com/old",
        }
        values.update(changes)
        return ConcertEvent(**values)

    def test_bootstrap_baseline_is_not_new(self):
        event = self.make_event()
        state = reconcile_state([event], None, now=self.NOW)
        self.assertLess(
            datetime.fromisoformat(event.first_seen.replace("Z", "+00:00")),
            self.NOW - timedelta(hours=72),
        )
        self.assertEqual(1, len(state["events"]))

    def test_new_event_gets_first_seen_and_it_survives_metadata_improvements(self):
        baseline = reconcile_state([self.make_event(headliner="Other")], None, now=self.NOW)
        event = self.make_event()
        first = reconcile_state([event], baseline, now=self.NOW)
        self.assertEqual("2026-08-23T12:00:00Z", event.first_seen)
        improved = self.make_event(
            headliner="The Afghan Whigs",
            ticket_url="https://official.example/ticket",
            openers=["Ed Harcourt"],
            genre="Rock",
        )
        second = reconcile_state(
            [improved], first,
            now=datetime(2026, 8, 24, 12, tzinfo=timezone.utc),
        )
        self.assertEqual(event.first_seen, improved.first_seen)
        self.assertEqual(first["events"][canonical_event_identity(event)]["first_seen"], second["events"][canonical_event_identity(improved)]["first_seen"])

    def test_capitalization_improvement_does_not_reset_first_seen(self):
        old = self.make_event(headliner="THE AFGHAN WHIGS")
        state = reconcile_state([old], None, now=self.NOW)
        improved = self.make_event(headliner="The Afghan Whigs")
        reconcile_state([improved], state, now=self.NOW)
        self.assertEqual(old.first_seen, improved.first_seen)

    def test_canonical_venue_spelling_improvement_does_not_reset_first_seen(self):
        old = self.make_event(venue="La Marberie")
        normalize_event_venue(old)
        state = reconcile_state([old], None, now=self.NOW)
        improved = self.make_event(venue="La Marbrerie")
        normalize_event_venue(improved)
        reconcile_state([improved], state, now=self.NOW + timedelta(hours=6))
        self.assertEqual(old.first_seen, improved.first_seen)

    def test_plenitude_rename_does_not_reset_first_seen(self):
        old = self.make_event(
            date="2026-11-27", headliner="Muse",
            venue="Paris La Défense Arena", city="Nanterre", department="92",
        )
        state = reconcile_state([old], None, now=self.NOW)
        current = self.make_event(
            date="2026-11-27", headliner="Muse",
            venue="Plénitude Arena", city="Nanterre", department="92",
        )

        reconcile_state([current], state, now=self.NOW + timedelta(hours=6))

        self.assertEqual(old.first_seen, current.first_seen)

    def test_reviewed_tour_title_does_not_reset_first_seen(self):
        old = self.make_event(
            date="2026-09-09", headliner="KATSEYE",
            venue="Accor Arena",
        )
        state = reconcile_state([old], None, now=self.NOW)
        improved = self.make_event(
            date="2026-09-09",
            headliner="KATSEYE - THE WILDWORLD TOUR",
            venue="Accor Arena",
        )

        reconcile_state([improved], state, now=self.NOW + timedelta(hours=6))

        self.assertEqual(old.first_seen, improved.first_seen)

    def test_reviewed_move_preserves_predecessor_first_seen(self):
        old = self.make_event(headliner="Father of Peace", venue="L'Alhambra")
        old.date = "2026-10-06"
        state = reconcile_state([old], None, now=self.NOW)
        moved = self.make_event(headliner="Father of Peace", venue="La Maroquinerie")
        moved.date = "2026-10-06"

        reconcile_state([moved], state, now=self.NOW + timedelta(hours=6))

        self.assertEqual(old.first_seen, moved.first_seen)

    def test_humanity_last_breath_move_preserves_predecessor_first_seen(self):
        old = self.make_event(
            headliner="HUMANITY'S LAST BREATH", venue="Petit Bain"
        )
        old.date = "2026-10-06"
        state = reconcile_state([old], None, now=self.NOW)
        moved = self.make_event(
            headliner="HUMANITY’S LAST BREATH",
            venue="La Machine du Moulin Rouge",
        )
        moved.date = "2026-10-06"

        reconcile_state([moved], state, now=self.NOW + timedelta(hours=6))

        self.assertEqual(old.first_seen, moved.first_seen)

    def test_malformed_state_fails_without_overwriting_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "calendar-state.json"
            path.write_text('{"broken":true}\n', encoding="utf-8")
            before = path.read_bytes()
            with self.assertRaises(EventStateError):
                load_state(path)
            self.assertEqual(before, path.read_bytes())

    def test_unpublished_candidate_does_not_advance_published_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            published = Path(temporary) / "published-state.json"
            baseline = reconcile_state([self.make_event()], None, now=self.NOW)
            write_state(published, baseline)
            before = published.read_bytes()

            candidate_event = self.make_event(headliner="A Genuinely New Artist")
            reconcile_state(
                [candidate_event], load_state(published),
                now=self.NOW + timedelta(hours=6),
            )

            self.assertEqual(before, published.read_bytes())

    def test_new_window_expires_after_72_hours(self):
        first_seen = "2026-08-23T12:00:00Z"
        self.assertTrue(is_new(first_seen, now=self.NOW + timedelta(hours=72)))
        self.assertFalse(
            is_new(first_seen, now=self.NOW + timedelta(hours=72, seconds=1))
        )


if __name__ == "__main__":
    unittest.main()
