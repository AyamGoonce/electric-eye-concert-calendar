import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from concert_calendar.automation import (
    ProductionValidationError,
    publish,
    read_pointer,
    validate_count_regression,
    validate_events,
)
from concert_calendar.production_export import build_current_pointer, build_data_asset
from concert_calendar.sources import load_events_with_report


def valid_event(index=0):
    return {
        "d": "2027-01-01",
        "h": f"Artist {index}",
        "o": [],
        "v": "La CLEF",
        "c": "Saint-Germain-en-Laye",
        "g": "Rap, Hip-Hop",
        "x": ["Hip-hop / Rap"],
        "p": ["Example promoter"],
        "t": "https://example.com/tickets",
    }


class AutomationValidationTests(unittest.TestCase):
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
                build_current_pointer(filename, digest, 100), encoding="utf-8"
            )
            args = type(
                "Args",
                (),
                {"generated_dir": str(generated), "pages_dir": str(pages)},
            )()

            publish(args)

            self.assertEqual(read_pointer(proof / "calendar-current.js")["data"], filename)
            self.assertEqual(len(list(proof.glob("calendar-data.*.js"))), 3)


if __name__ == "__main__":
    unittest.main()
