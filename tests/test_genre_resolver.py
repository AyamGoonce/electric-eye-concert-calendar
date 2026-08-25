import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "resolve_genres.py"
SPEC = importlib.util.spec_from_file_location("genre_resolver_maintenance", SCRIPT)
resolver = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(resolver)


class GenreResolverTests(unittest.TestCase):
    def test_same_name_musicbrainz_candidates_are_rejected(self):
        payload = {"artists": [
            {"name": "LOST", "score": 100, "type": "Group", "id": "one"},
            {"name": "Lost", "score": 98, "type": "Person", "id": "two"},
        ]}
        candidate, status = resolver.select_musicbrainz_candidate(payload, "LOST")
        self.assertIsNone(candidate)
        self.assertEqual("ambiguous_identity", status)

    def test_non_musical_and_substring_identities_are_rejected(self):
        payload = {"artists": [
            {"name": "The Buoys Tribute", "score": 100, "type": "Group"},
            {"name": "The Buoys", "score": 100, "type": "Other"},
        ]}
        candidate, status = resolver.select_musicbrainz_candidate(payload, "The Buoys")
        self.assertIsNone(candidate)
        self.assertEqual("unresolved", status)

    def test_dry_run_does_not_write_cache_or_reviewed_mappings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            asset = root / "calendar-data.js"
            asset.write_text(
                "window.ElectricEyeConcertData = Object.freeze(" +
                json.dumps([{"h": "Blank Artist", "x": [], "f": None}]) + ");",
                encoding="utf-8",
            )
            with patch.object(resolver, "musicbrainz_batch", return_value={
                "blank artist": {
                    "artist": "Blank Artist", "genre": None,
                    "status": "unresolved", "scores": {}, "evidence": [],
                }
            }):
                report = resolver.resolve_calendar_asset(asset)

            self.assertEqual(1, report["blank_rows"])
            self.assertEqual(0, report["resolved_events"])
            self.assertEqual([asset], list(root.iterdir()))

    def test_production_does_not_import_or_execute_maintenance_resolver(self):
        root = SCRIPT.parents[1]
        production_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [*(root / "concert_calendar").glob("*.py"),
                         *(root / ".github" / "workflows").glob("*.yml")]
        )
        self.assertNotIn("resolve_genres", production_text)


if __name__ == "__main__":
    unittest.main()
