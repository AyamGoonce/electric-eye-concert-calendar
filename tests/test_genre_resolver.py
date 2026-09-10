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

        self.assertEqual(
            "Chanson Française / Variétés",
            resolver.ITUNES_GENRE_MAP["chanson française"],
        )
        self.assertEqual(
            "Chanson Française / Variétés",
            resolver.ITUNES_GENRE_MAP["variété française"],
        )
        self.assertNotIn(
            "French chanson",
            resolver.ITUNES_GENRE_MAP.values(),
        )

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


    def test_explicit_none_disables_provider_cache(self):
        import tempfile

        with tempfile.TemporaryDirectory() as temporary:
            default_cache = Path(temporary) / "default.json"
            old = resolver.PROVIDER_CACHE_PATHS["apple"]
            resolver.PROVIDER_CACHE_PATHS["apple"] = default_cache

            try:
                result = resolver.provider_result(
                    "apple",
                    "Example Artist",
                    lookup=lambda _artist: {
                        "status": "resolved",
                        "genre": "Pop",
                    },
                    cache_path=None,
                )
            finally:
                resolver.PROVIDER_CACHE_PATHS["apple"] = old

            self.assertEqual("resolved", result["status"])
            self.assertFalse(default_cache.exists())

    def test_provider_list_parser(self):
        self.assertEqual(
            ("apple", "wikidata", "bandcamp"),
            resolver.parse_provider_list(
                "apple, wikidata, bandcamp"
            ),
        )

        with self.assertRaises(ValueError):
            resolver.parse_provider_list(
                "apple,definitely-not-a-provider"
            )

    def test_bulk_consensus_ranks_high_impact_identities_first(self):
        import tempfile

        with tempfile.TemporaryDirectory() as temporary:
            asset = Path(temporary) / "calendar.js"

            asset.write_text(
                "window.ElectricEyeConcertData = Object.freeze(" +
                json.dumps([
                    {"h": "One Off", "x": [], "f": None},
                    {"h": "High Impact", "x": [], "f": None},
                    {"h": "High Impact", "x": [], "f": None},
                    {"h": "Already Classified", "x": ["Pop"], "f": None},
                    {"h": "Festival Act", "x": [], "f": "Festival"},
                ]) +
                ");",
                encoding="utf-8",
            )

            with patch(
                "concert_calendar.genres.load_reviewed_mappings",
                return_value={"artists": [], "overrides": []},
            ), patch(
                "concert_calendar.genres.mapping_for_artist",
                return_value=None,
            ), patch.object(
                resolver,
                "resolve_artist_consensus",
                side_effect=lambda artist, **kwargs: {
                    "artist": artist,
                    "status": "review_candidate",
                    "genre": "Pop",
                    "providers": ["apple"],
                    "votes": {"Pop": ["apple"]},
                    "provider_results": {
                        "apple": {
                            "status": "resolved",
                            "genre": "Pop",
                        }
                    },
                },
            ):
                report = resolver.resolve_calendar_consensus(
                    asset,
                    providers=("apple",),
                    cache_dir=None,
                )

            self.assertEqual(2, report["research_identities"])
            self.assertEqual(3, report["research_rows"])

            self.assertEqual(
                ["High Impact", "One Off"],
                [row["artist"] for row in report["review_candidates"]],
            )

            self.assertEqual(
                [2, 1],
                [row["affected_events"] for row in report["review_candidates"]],
            )


if __name__ == "__main__":
    unittest.main()
