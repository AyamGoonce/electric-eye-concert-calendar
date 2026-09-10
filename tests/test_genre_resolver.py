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

    def test_resolver_uses_current_public_taxonomy(self):
        self.assertIn(
            "Chanson Française / Variétés",
            resolver.GENRE_RULES,
        )
        self.assertIn(
            "Comedy / Spoken Word",
            resolver.GENRE_RULES,
        )
        self.assertNotIn("French chanson", resolver.GENRE_RULES)
        self.assertNotIn("Comedy", resolver.GENRE_RULES)

    def test_genre_terms_use_token_boundaries(self):
        self.assertFalse(
            resolver._genre_term_matches(
                "biographical film",
                "rap",
            )
        )
        self.assertTrue(
            resolver._genre_term_matches(
                "French hip-hop",
                "hip-hop",
            )
        )
        self.assertTrue(
            resolver._genre_term_matches(
                "synth-pop",
                "pop",
            )
        )


    def test_two_independent_sources_can_resolve_genre(self):
        result = resolver.combine_provider_results({
            "musicbrainz": {
                "status": "resolved",
                "genre": "R&B / Soul / Funk",
            },
            "apple": {
                "status": "resolved",
                "genre": "R&B / Soul / Funk",
            },
        })
        self.assertEqual("resolved", result["status"])
        self.assertEqual("R&B / Soul / Funk", result["genre"])
        self.assertEqual(["apple", "musicbrainz"], result["providers"])

    def test_single_source_requires_review(self):
        result = resolver.combine_provider_results({
            "apple": {
                "status": "resolved",
                "genre": "Pop",
            },
        })
        self.assertEqual("review_candidate", result["status"])
        self.assertEqual("Pop", result["genre"])

    def test_conflicting_sources_remain_ambiguous(self):
        result = resolver.combine_provider_results({
            "musicbrainz": {
                "status": "resolved",
                "genre": "Rock / Indie / Punk",
            },
            "apple": {
                "status": "resolved",
                "genre": "Pop",
            },
        })
        self.assertEqual("ambiguous", result["status"])
        self.assertIsNone(result["genre"])
        self.assertEqual(
            {
                "Pop": ["apple"],
                "Rock / Indie / Punk": ["musicbrainz"],
            },
            result["votes"],
        )

    def test_unresolved_provider_does_not_block_consensus(self):
        result = resolver.combine_provider_results({
            "musicbrainz": {
                "status": "resolved",
                "genre": "Jazz / Blues",
            },
            "apple": {
                "status": "resolved",
                "genre": "Jazz / Blues",
            },
            "bandcamp": {
                "status": "unresolved",
                "genre": None,
            },
        })
        self.assertEqual("resolved", result["status"])
        self.assertEqual("Jazz / Blues", result["genre"])


    def test_provider_transport_failure_is_not_cached(self):
        import requests
        import tempfile

        with tempfile.TemporaryDirectory() as temporary:
            cache = Path(temporary) / "provider.json"

            def broken(_artist):
                raise requests.RequestException("503")

            result = resolver.provider_result(
                "apple",
                "Example Artist",
                lookup=broken,
                cache_path=cache,
            )

            self.assertEqual("unavailable", result["status"])
            self.assertFalse(cache.exists())

    def test_genuine_unresolved_provider_result_can_be_cached(self):
        import tempfile

        with tempfile.TemporaryDirectory() as temporary:
            cache = Path(temporary) / "provider.json"

            result = resolver.provider_result(
                "apple",
                "Unknown Artist",
                lookup=lambda _artist: None,
                cache_path=cache,
            )

            self.assertEqual("unresolved", result["status"])
            self.assertTrue(cache.exists())

            stored = json.loads(cache.read_text(encoding="utf-8"))
            self.assertEqual(
                "unresolved",
                stored["unknown artist"]["status"],
            )

    def test_artist_consensus_combines_independent_provider_results(self):
        lookups = {
            "musicbrainz": lambda _artist: {
                "status": "resolved",
                "genre": "R&B / Soul / Funk",
            },
            "apple": lambda _artist: {
                "status": "resolved",
                "genre": "R&B / Soul / Funk",
            },
            "bandcamp": lambda _artist: {
                "status": "unresolved",
                "genre": None,
            },
            "wikidata": lambda _artist: {
                "status": "resolved",
                "genre": "R&B / Soul / Funk",
            },
        }

        result = resolver.resolve_artist_consensus(
            "Lee Fields",
            lookups=lookups,
            cache_paths={
                "musicbrainz": None,
                "apple": None,
                "bandcamp": None,
                "wikidata": None,
            },
        )

        self.assertEqual("resolved", result["status"])
        self.assertEqual("R&B / Soul / Funk", result["genre"])
        self.assertEqual(
            ["apple", "musicbrainz", "wikidata"],
            result["providers"],
        )

    def test_artist_consensus_preserves_provider_conflict(self):
        lookups = {
            "musicbrainz": lambda _artist: {
                "status": "resolved",
                "genre": "Rock / Indie / Punk",
            },
            "apple": lambda _artist: {
                "status": "resolved",
                "genre": "Pop",
            },
        }

        result = resolver.resolve_artist_consensus(
            "Example",
            providers=("musicbrainz", "apple"),
            lookups=lookups,
            cache_paths={
                "musicbrainz": None,
                "apple": None,
            },
        )

        self.assertEqual("ambiguous", result["status"])
        self.assertIsNone(result["genre"])



if __name__ == "__main__":
    unittest.main()
