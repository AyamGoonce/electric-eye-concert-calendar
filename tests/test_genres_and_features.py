from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

from concert_calendar.event_state import (
    build_change_report,
    canonical_event_identity,
    reconcile_state,
)
from concert_calendar.genres import (
    PUBLIC_GENRES,
    enrich_event_genres,
    load_reviewed_mappings,
    map_raw_genre,
)
from concert_calendar.ics import build_ics
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import event_to_data, read_renderer


def event(**changes):
    values = dict(
        date="2026-09-27", headliner="The Afghan Whigs", venue="Le Trabendo",
        city="Paris", department="75", ticket_url="https://example.com/tickets",
    )
    values.update(changes)
    return ConcertEvent(**values)


class GenreEnrichmentTests(unittest.TestCase):
    def test_historical_taxonomy_aliases(self):
        for raw in ("Comedy", "Spoken Word", "Comedy / Spoken Word", "stand-up", "humour"):
            self.assertEqual("Comedy / Spoken Word", map_raw_genre(raw))
        for raw in ("French chanson", "Chanson française", "Variétés", "Variété française", "French Variety", "Chanson Française / Variétés"):
            self.assertEqual("Chanson Française / Variétés", map_raw_genre(raw))
        for raw in ("Pop", "Metal / Hard Rock", "Electronic"):
            self.assertEqual(raw, map_raw_genre(raw))
        for raw in ("Jewish music", "Guitare espagnole"):
            self.assertEqual("World / Latin", map_raw_genre(raw))
        for raw in ("grapefruit", "metallic object", "French artist", "metalcoreography", "hiphopopotamus"):
            self.assertIsNone(map_raw_genre(raw))

    def test_explicit_compounds_preserved_without_unioning_conflicts(self):
        for raw, expected in (
            ("Rock / Metal", {"Rock / Indie / Punk", "Metal / Hard Rock"}),
            ("Jazz / Funk", {"Jazz / Blues", "R&B / Soul / Funk"}),
            ("Pop, Rock", {"Pop", "Rock / Indie / Punk"}),
            ("Jazz funk", {"Jazz / Blues", "R&B / Soul / Funk"}),
        ):
            item = event(headliner="Unmapped artist", genre=raw)
            enrich_event_genres([item])
            self.assertEqual(expected, set(event_to_data(item)["x"]))
            self.assertEqual(len(expected), len(event_to_data(item)["x"]))

    def test_compound_unknown_components_do_not_supply_guessed_genres(self):
        from concert_calendar.genres import map_raw_genres
        self.assertEqual([], map_raw_genres("Pop, unknown style"))
        self.assertEqual(["Pop"], map_raw_genres("Pop, Pop"))
        self.assertEqual([], map_raw_genres("POP ROCK FOLK"))

    def test_reviewed_raw_gap_taxonomies(self):
        from concert_calendar.genres import map_raw_genres

        singles = {
            "Rap, Hip Hop": ["Hip-hop / Rap"],
            "concert rock": ["Rock / Indie / Punk"],
        }
        for raw, expected in singles.items():
            with self.subTest(raw=raw):
                self.assertEqual(expected, map_raw_genres(raw))

        compounds = {
            "Electro Pop": {"Pop", "Electronic"},
            "Afropop, Rumba, Reggae": {"World / Latin", "Reggae / Dub / Ska"},
            "Jazz, Blues, Groove, Funk & Musiques improvisées": {
                "Jazz / Blues", "R&B / Soul / Funk"
            },
            "#rock #postpunk #heavymetal": {
                "Rock / Indie / Punk", "Metal / Hard Rock"
            },
            "##indiepop #pop #electro #house": {
                "Pop", "Electronic"
            },
        }
        for raw, expected in compounds.items():
            with self.subTest(raw=raw):
                self.assertEqual(expected, set(map_raw_genres(raw)))

    def test_public_vocabulary_is_exactly_closed(self):
        self.assertEqual((
            "Comedy / Spoken Word", "Electronic", "Folk / Country", "Chanson Française / Variétés",
            "Hip-hop / Rap", "Jazz / Blues", "Metal / Hard Rock", "Pop",
            "R&B / Soul / Funk", "Reggae / Dub / Ska",
            "Rock / Indie / Punk", "World / Latin",
        ), PUBLIC_GENRES)
        self.assertEqual(len(PUBLIC_GENRES), len(set(PUBLIC_GENRES)))

    def test_source_explicit_and_source_mapping_provenance(self):
        explicit = event(genre="Pop", genre_evidence=[{"raw": "Pop", "source": "Official"}])
        mapped = event(headliner="Other", genre="Rap, Hip-Hop", genre_evidence=[{"raw": "Rap, Hip-Hop", "source": "Official"}])
        report = enrich_event_genres([explicit, mapped])
        self.assertEqual("source_explicit", explicit.genre_method)
        self.assertEqual("source_mapping", mapped.genre_method)
        self.assertEqual("Hip-hop / Rap", mapped.genre_public)
        self.assertEqual(1, report["source_explicit"])
        self.assertEqual(1, report["source_mapping"])

    def test_artist_mapping_is_exact_normalized_not_fuzzy(self):
        matched = event(headliner="THE AFGHAN WHIGS")
        different = event(headliner="The Afghan Whigs Tribute")
        enrich_event_genres([matched, different])
        self.assertEqual("Rock / Indie / Punk", matched.genre_public)
        self.assertEqual("artist_mapping", matched.genre_method)
        self.assertIsNone(different.genre_public)

    def test_reviewed_display_variant_uses_one_canonical_mapping(self):
        item = event(headliner="BLEOOD : Kill Your Idols Europe Tour")
        enrich_event_genres([item])
        self.assertEqual("Hip-hop / Rap", item.genre_public)
        self.assertEqual("artist_mapping", item.genre_method)

    def test_genre_lookup_identity_removes_explicit_session_metadata(self):
        from concert_calendar.genres import genre_lookup_artist_identity

        cases = {
            "David Sauzay + jam – 19h30": "David Sauzay",
            "Laurent Courthaliac + JAM SESSION – 21h30": "Laurent Courthaliac",
            "Fabien Mary + jam – 19h30": "Fabien Mary",
        }

        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(
                    expected,
                    genre_lookup_artist_identity(raw),
                )

    def test_genre_lookup_identity_preserves_arbitrary_billing(self):
        from concert_calendar.genres import genre_lookup_artist_identity

        self.assertEqual(
            "Artist A + Artist B",
            genre_lookup_artist_identity("Artist A + Artist B"),
        )
        self.assertEqual(
            "Coco & Clair Clair",
            genre_lookup_artist_identity("Coco & Clair Clair"),
        )

    def test_artist_mapping_uses_conservative_genre_lookup_identity(self):
        items = [
            event(headliner="David Sauzay + jam – 19h30"),
            event(headliner="Laurent Courthaliac + JAM SESSION – 21h30"),
            event(headliner="Fabien Mary + jam – 19h30"),
        ]

        enrich_event_genres(items)

        self.assertTrue(
            all(item.genre_public == "Jazz / Blues" for item in items)
        )
        self.assertTrue(
            all(item.genre_method == "artist_mapping" for item in items)
        )

    def test_sunset_sunside_venue_is_jazz_fallback(self):
        items = [
            event(
                headliner="Unmapped Sunset Artist",
                venue="Sunset/Sunside — Sunset",
            ),
            event(
                headliner="Unmapped Sunside Artist",
                venue="Sunset/Sunside — Sunside",
            ),
        ]

        enrich_event_genres(items)

        self.assertTrue(
            all(item.genre_public == "Jazz / Blues" for item in items)
        )
        self.assertTrue(
            all(item.genre_method == "event_context" for item in items)
        )
        self.assertTrue(
            all(item.genre_source == "venue" for item in items)
        )

    def test_sunset_sunside_fallback_does_not_override_source_genre(self):
        item = event(
            headliner="Unmapped Artist",
            venue="Sunset/Sunside — Sunside",
            genre="Pop",
            genre_evidence=[{"raw": "Pop", "source": "Official"}],
        )

        enrich_event_genres([item])

        self.assertEqual("Pop", item.genre_public)
        self.assertEqual("source_explicit", item.genre_method)
        self.assertNotEqual("venue", item.genre_source)

    def test_sunset_sunside_jam_taxonomy_is_jazz_fallback(self):
        item = event(
            headliner="Unmapped Jam Artist",
            venue="Sunset/Sunside — Sunside",
            genre="Entrée libre⎥jam session",
            genre_evidence=[
                {"raw": "Entrée libre⎥jam session", "source": "Sunset/Sunside"}
            ],
        )

        enrich_event_genres([item])

        self.assertEqual("Jazz / Blues", item.genre_public)
        self.assertEqual("event_context", item.genre_method)
        self.assertEqual("venue", item.genre_source)

    def test_sunset_sunside_does_not_override_unresolved_specific_raw_genre(self):
        item = event(
            headliner="Unmapped Artist",
            venue="Sunset/Sunside — Sunside",
            genre="Unclassified specialist programme",
            genre_evidence=[
                {"raw": "Unclassified specialist programme", "source": "Sunset/Sunside"}
            ],
        )

        enrich_event_genres([item])

        self.assertIsNone(item.genre_public)

    def test_co_headliners_require_shared_mapped_genre(self):
        shared = event(headliner="The Afghan Whigs", co_headliners=["Drug Church"])
        primary_only = event(
            headliner="The Afghan Whigs", co_headliners=["Unmapped Billing Partner"]
        )
        conflicting = event(
            headliner="Bloc Party", co_headliners=["Thee Sinseers"]
        )
        enrich_event_genres([shared, primary_only, conflicting])
        self.assertEqual("Rock / Indie / Punk", shared.genre_public)
        self.assertEqual("bill_consensus", shared.genre_method)
        self.assertEqual("Rock / Indie / Punk", primary_only.genre_public)
        self.assertEqual("bill_consensus", primary_only.genre_method)
        self.assertIsNone(conflicting.genre_public)

    def test_support_act_does_not_supply_headliner_genre(self):
        item = event(headliner="Unmapped Headliner", openers=["Bloc Party"])
        enrich_event_genres([item])
        self.assertIsNone(item.genre_public)

    def test_known_cross_bucket_identities_remain_blank(self):
        items = [event(headliner=name) for name in (
            "Gildaa", "Alma Rechtman", "Saint Levant", "FFF",
        )]
        enrich_event_genres(items)
        self.assertTrue(all(item.genre_public is None for item in items))

    def test_reviewed_dominant_rock_identities_are_classified(self):
        items = [event(headliner=name) for name in ("Asaf Avidan", "Ben Harper")]
        enrich_event_genres(items)
        self.assertTrue(
            all(item.genre_public == "Rock / Indie / Punk" for item in items)
        )

    def test_ambiguous_raw_genre_and_conflict_remain_blank(self):
        ambiguous = event(headliner="Ambiguous", genre="Pop, Rock", genre_evidence=[{"raw": "Pop, Rock", "source": "Official"}])
        conflict = event(headliner="Conflict", genre="Pop", genre_evidence=[{"raw": "Pop", "source": "A"}, {"raw": "Metal / Hard Rock", "source": "B"}])
        report = enrich_event_genres([ambiguous, conflict])
        self.assertEqual({"Pop", "Rock / Indie / Punk"}, set(event_to_data(ambiguous)["x"]))
        self.assertIsNone(conflict.genre_public)
        self.assertEqual(1, report["conflict_count"])
        self.assertEqual([], event_to_data(conflict)["x"])

    def test_festival_does_not_inherit_headliner_mapping(self):
        festival = event(headliner="The Cure", festival_name="Rock en Seine")
        report = enrich_event_genres([festival])
        self.assertIsNone(festival.genre_public)
        self.assertEqual(1, report["blank_festival"])

    def test_reviewed_mapping_has_evidence_and_valid_genres(self):
        mappings = load_reviewed_mappings()
        for section in mappings.values():
            for record in section.values():
                self.assertIn(record["genre"], PUBLIC_GENRES)
                self.assertTrue(record["evidence_source"])
                self.assertTrue(record["evidence_type"])
                self.assertRegex(record["review_date"], r"^\d{4}-\d{2}-\d{2}$")

    def test_reviewed_override_has_priority_and_provenance(self):
        value = {
            "version": 1, "artists": [],
            "overrides": [{
                "artist": "Conflict", "genre": "Pop",
                "evidence_source": "Reviewed test evidence",
                "evidence_type": "editorial_review", "review_date": "2026-08-23",
            }],
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "genres.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            conflict = event(headliner="CONFLICT", genre_evidence=[
                {"raw": "Pop", "source": "A"},
                {"raw": "Metal / Hard Rock", "source": "B"},
            ])
            report = enrich_event_genres([conflict], path)
        self.assertEqual("Pop", conflict.genre_public)
        self.assertEqual("manual_override", conflict.genre_method)
        self.assertEqual("Reviewed test evidence", conflict.genre_source)
        self.assertEqual(1, report["override"])

    def test_conflicting_duplicate_mapping_cannot_silently_overwrite(self):
        provenance = {
            "evidence_source": "Reviewed test", "evidence_type": "editorial_review",
            "review_date": "2026-08-23",
        }
        value = {"version": 1, "artists": [
            {"artist": "Same Artist", "genre": "Pop", **provenance},
            {"artist": "SAME ARTIST", "genre": "Jazz / Blues", **provenance},
        ], "overrides": []}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "genres.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate reviewed genre identity"):
                load_reviewed_mappings(path)

    def test_malformed_reviewed_mapping_is_rejected(self):
        value = {"version": 1, "artists": [{
            "artist": "Missing Provenance", "genre": "Pop",
        }], "overrides": []}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "genres.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Malformed reviewed genre mapping"):
                load_reviewed_mappings(path)

    def test_event_specific_genre_beats_artist_default(self):
        item = event(headliner="The Afghan Whigs", genre_evidence=[
            {"raw": "Jazz", "source": "Authoritative event source"},
        ])
        enrich_event_genres([item])
        self.assertEqual("Jazz / Blues", item.genre_public)
        self.assertEqual("source_mapping", item.genre_method)

    def test_completeness_report_includes_raw_frequency_and_sources(self):
        item = event(headliner="Unmapped", genre_evidence=[{"raw": "Other", "source": "Official"}])
        report = enrich_event_genres([item])
        self.assertEqual(1, report["blank"])
        self.assertEqual({"Other": 1}, report["raw_inventory"])
        self.assertEqual(["Official"], report["raw_sources"]["Other"])
        self.assertTrue(report["unresolved_artists"])
        self.assertTrue(report["artist_mappings"])

    def test_public_payload_does_not_leak_raw_genre_or_provenance(self):
        item = event(genre="Other", genre_source="Internal source", genre_method="artist_mapping")
        payload = event_to_data(item)
        self.assertNotIn("g", payload)
        self.assertNotIn("genre_source", payload)
        self.assertNotIn("genre_method", payload)

    def test_safe_and_ambiguous_raw_examples(self):
        self.assertEqual("R&B / Soul / Funk", map_raw_genre("#neosoul"))
        self.assertEqual("Metal / Hard Rock", map_raw_genre("metalcore / newcore / metal progressif"))
        self.assertEqual("Pop", map_raw_genre("Other, Pop"))
        self.assertEqual("Pop", map_raw_genre("Pop, Variété Internationale"))
        self.assertEqual("Pop", map_raw_genre("Variété Internationale"))
        self.assertIsNone(map_raw_genre("Pop, Rock"))


class StatusIdentityAndICSTests(unittest.TestCase):
    def test_public_id_survives_metadata_improvements(self):
        first = event()
        improved = event(headliner="THE AFGHAN WHIGS", openers=["Ed Harcourt"], genre="Rock", ticket_url="https://official.example/t")
        self.assertEqual(canonical_event_identity(first), canonical_event_identity(improved))
        self.assertEqual(16, len(event_to_data(first)["i"]))

    def test_ticket_statuses_are_explicit_and_missing_is_unknown(self):
        self.assertEqual("sold_out", event_to_data(event(sold_out=True))["ts"])
        self.assertEqual("free", event_to_data(event(ticket_status="free", ticket_url=None))["ts"])
        self.assertEqual("not_on_sale", event_to_data(event(ticket_status="not_on_sale", ticket_url=None))["ts"])
        self.assertEqual("cancelled", event_to_data(event(ticket_status="cancelled", ticket_url=None))["ts"])
        self.assertEqual("postponed", event_to_data(event(ticket_status="postponed", ticket_url=None))["ts"])
        self.assertIsNone(event_to_data(event(ticket_url=None))["ts"])
        self.assertEqual("tickets", event_to_data(event())["ts"])

    def test_all_day_ics_contains_unicode_suburban_venue_openers_and_ticket(self):
        value = build_ics(event(headliner="Élodie, Live", venue="Le Forum; Grande Salle", city="Vauréal", department="95", openers=["Support\nAct"]))
        self.assertIn("DTSTART;VALUE=DATE:20260927", value)
        self.assertIn("DTEND;VALUE=DATE:20260928", value)
        self.assertIn("SUMMARY:Élodie\\, Live", value)
        self.assertIn("LOCATION:Le Forum\\; Grande Salle\\, Vauréal", value)
        self.assertIn("Support\\nAct", value)
        self.assertIn("https://example.com/tickets", value)

    def test_timed_ics_only_uses_reliable_start_time(self):
        value = build_ics(event(start_time="20:30"))
        self.assertIn("DTSTART;TZID=Europe/Paris:20260927T203000", value)
        self.assertNotIn("VALUE=DATE", value)

    def test_festival_ics_is_one_event_with_full_lineup(self):
        value = build_ics(event(festival_name="Rock en Seine", openers=["One", "Two", "Three"]))
        self.assertEqual(1, value.count("BEGIN:VEVENT"))
        self.assertIn("Festival lineup: The Afghan Whigs\\, One\\, Two\\, Three", value)


class ChangeReportTests(unittest.TestCase):
    NOW = datetime(2026, 8, 23, 12, tzinfo=timezone.utc)

    def test_detects_new_disappeared_support_genre_and_sold_out(self):
        retained = event(headliner="Retained", ticket_url="https://example.com")
        disappeared = event(headliner="Gone", date="2026-10-01")
        enrich_event_genres([retained, disappeared])
        previous = reconcile_state([retained, disappeared], None, now=self.NOW)
        previous["version"] = 2
        changed = event(headliner="Retained", openers=["New Support"], genre_public="Pop", sold_out=True)
        added = event(headliner="New Event", date="2026-10-02")
        current = reconcile_state([changed, added], previous, now=self.NOW)
        report = build_change_report([changed, added], previous, current, now=self.NOW)
        self.assertEqual(1, report["new_events"])
        self.assertEqual(1, report["no_longer_present"])
        self.assertEqual(1, report["new_support_acts"])
        self.assertEqual(1, report["genre_enrichments"])
        self.assertEqual(1, report["newly_sold_out"])


class CoHeadlinerRendererTests(unittest.TestCase):

    def test_renderer_supports_co_headliners_in_display_and_search(self):
        renderer = read_renderer()

        self.assertIn(
            'e.s=normalize([e.h].concat(e.ch,e.o,[e.v,e.c]).join(" "))',
            renderer,
        )
        self.assertIn(
            'e.ch.forEach(function(name){h.append(document.createTextNode(" + "));h.append(artistElement(name,e));});',
            renderer,
        )
        self.assertIn(
            '(e.ch === undefined || validArray(e.ch))',
            renderer,
        )


class RendererFeatureContractTests(unittest.TestCase):
    def test_indexed_artist_links_are_separate_from_event_coverage_and_actions(self):
        renderer = read_renderer()
        self.assertIn('function artistElement(name,e)', renderer)
        self.assertIn('https://archive.electriceyerock.com/artist/', renderer)
        self.assertIn('https://archive.electriceyerock.com/concert/', renderer)
        self.assertIn('className="ee-calendar-coverage"', renderer)
        for action in ('"Tickets"', '"Copy link"', '"Share"', '"Add to calendar"'):
            self.assertIn(action, renderer)

    def test_multi_genre_links_ics_preferences_counts_and_recovery_exist(self):
        renderer = read_renderer()
        for required in (
            'p.getAll("genre")', 'p.append("genre",g)',
            'e.x.includes(g)', 'g==="Unsorted"?!e.x.length',
            '"Copy link"', 'navigator.share', '"Add to calendar"', "buildICS",
            'localStorage.getItem("ee-calendar-sort")', 'venueCounts.get',
            '"Clear genres"', '"Clear date"', '"Clear venue"', '"Show all concerts"',
            '/^#event-[0-9a-f]{16}$/', 'scrollIntoView',
        ):
            self.assertIn(required, renderer)


if __name__ == "__main__":
    unittest.main()
