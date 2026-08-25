import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone
import json

from concert_calendar.automation import (
    ProductionValidationError,
    publish,
    read_pointer,
    validate_count_regression,
    validate_genre_coverage,
    validate_events,
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
        with patch("concert_calendar.sources.discover_scrapers", return_value=[scraper]):
            events, report = load_events_with_report(
                scraper_attempts=3, retry_delay_seconds=0
            )

        self.assertEqual(events, [])
        self.assertEqual(report.source_counts, {"Transient source": 0})
        self.assertEqual(scraper.load_events.call_count, 3)

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

    def test_publish_stages_data_before_pointer_and_keeps_three_hashes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            generated = root / "generated"
            pages = root / "pages"
            proof = pages / "proof"
            generated.mkdir()
            proof.mkdir(parents=True)

            for stable in ("calendar-renderer.js", "calendar.css"):
                (generated / stable).write_text(stable, encoding="utf-8")

            state = {
                "version": 1,
                "updated_at": "2026-08-23T10:00:00Z",
                "events": {},
            }
            state_digest = write_state(generated / "calendar-state.json", state)

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

            filename, digest, asset = build_data_asset(
                [valid_event(index) for index in range(100)]
            )
            (generated / filename).write_text(asset, encoding="utf-8")
            (generated / "calendar-current.js").write_text(
                build_current_pointer(
                    filename,
                    digest,
                    100,
                    published_at="2026-08-23T10:00:00Z",
                    state_sha256=state_digest,
                ), encoding="utf-8"
            )
            args = type(
                "Args",
                (),
                {"generated_dir": str(generated), "pages_dir": str(pages)},
            )()

            publish(args)

            self.assertEqual(read_pointer(proof / "calendar-current.js")["data"], filename)
            self.assertEqual(len(list(proof.glob("calendar-data.*.js"))), 3)
            self.assertEqual((proof / "calendar-state.json").read_text(), (generated / "calendar-state.json").read_text())


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

    def test_reviewed_move_preserves_predecessor_first_seen(self):
        old = self.make_event(headliner="Father of Peace", venue="L'Alhambra")
        old.date = "2026-10-06"
        state = reconcile_state([old], None, now=self.NOW)
        moved = self.make_event(headliner="Father of Peace", venue="La Maroquinerie")
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
