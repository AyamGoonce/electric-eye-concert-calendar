"""Phase 3 hardening: identity collision, provenance and release accounting."""
import unittest

from concert_calendar.genre_editorial import (
    build_editorial_artist_genre_evidence,
)
from concert_calendar.genre_release_audit import genre_release_audit
from concert_calendar.genres import enrich_event_genres
from concert_calendar.models import ConcertEvent


def event(name="Lambrini Girls", **kwargs):
    fields = dict(date="2027-01-11", headliner=name, venue="Le Trabendo",
                  city="Paris", department="75")
    fields.update(kwargs)
    return ConcertEvent(**fields)


def report_for(events):
    total = len(events)
    populated = sum(bool(e.genre_public) for e in events)
    return dict(total=total, populated=populated, blank=total-populated,
                blank_no_raw=total-populated, blank_unresolved_raw=0,
                blank_festival=0, blank_unresolved_taxonomy=0,
                conflict_count=0)


class GenreReleaseHardeningTests(unittest.TestCase):
    def test_homonym_index_collision_is_never_authoritative(self):
        index = {"artists": {
            "artist-one": {"n": "Same Name", "identity": {"genres": ["Punk"]}},
            "artist-two": {"n": "Same Name", "identity": {"genres": ["Jazz"]}},
        }, "articles": []}
        self.assertEqual({}, build_editorial_artist_genre_evidence(index))

    def test_article_must_credit_the_indexed_artist_not_another_slug(self):
        index = {"artists": {
            "lambrini-girls": {"n": "Lambrini Girls", "da": [0, 1]},
        }, "articles": [
            {"t": "Lambrini Girls live", "a": ["unrelated"], "l": ["Punk"]},
            {"t": "Lambrini Girls interview", "a": ["unrelated"], "l": ["Punk"]},
        ]}
        self.assertEqual({}, build_editorial_artist_genre_evidence(index))

    def test_bill_collaboration_cannot_inherit_same_run_artist_consensus(self):
        events = [
            event("Lambrini Girls et Guest", genre="Punk", venue="Le Trabendo"),
            event("Lambrini Girls et Guest", genre="Punk", venue="Le Bataclan",
                  date="2027-01-12"),
            event("Lambrini Girls et Guest"),
        ]
        enrich_event_genres(events)
        self.assertIsNone(events[-1].genre_public)

    def test_inconsistent_blank_accounting_rejected(self):
        e = event()
        diagnostics = report_for([e])
        diagnostics["blank_no_raw"] = 0
        with self.assertRaisesRegex(ValueError, "accounting mismatch"):
            genre_release_audit([e], diagnostics, [])

    def test_valid_source_provenance_and_baseline_change_report(self):
        e = event(genre="Punk", genre_source="Official venue")
        diagnostics = enrich_event_genres([e])
        before = [{"i": "id1", "h": "Old Artist", "x": ["Electronic"],
                   "ch": ["Guest"], "o": []}]
        after = [{"i": "id1", "h": "Lambrini Girls", "x": [],
                  "ch": [], "o": []}]
        audit = genre_release_audit([e], diagnostics, after, before)
        self.assertEqual([], audit["provenance_defects"])
        self.assertEqual(1, len(audit["genre_losses_on_retained_ids"]))
        self.assertEqual(1, len(audit["billing_changes_on_retained_ids"]))
        self.assertEqual(1, audit["baseline_comparable_ids"])

    def test_provenance_defect_is_visible(self):
        e = event()
        e.genre_public = "Pop"
        e.genre_method = "source_explicit"
        audit = genre_release_audit(
            [e], dict(total=1, populated=1, blank=0), [])
        self.assertEqual(1, len(audit["provenance_defects"]))


if __name__ == "__main__":
    unittest.main()
