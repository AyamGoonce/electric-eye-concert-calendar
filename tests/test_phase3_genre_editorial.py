"""Phase 3 conservative genre evidence tests: no speculative genre inheritance."""
import unittest

from concert_calendar.genre_editorial import (
    build_editorial_artist_genre_evidence,
    enrich_unclassified_with_editorial_genres,
)
from concert_calendar.genres import map_raw_genres
from concert_calendar.models import ConcertEvent


def concert(name="Lambrini Girls", **kwargs):
    values = {
        "date": "2027-01-11", "headliner": name,
        "venue": "Le Trabendo", "city": "Paris", "department": "75",
    }
    values.update(kwargs)
    return ConcertEvent(**values)


def article(title, label="Punk", *, slug="lambrini-girls"):
    return {
        "t": title, "a": [slug], "l": [label],
        "u": "https://www.electriceyerock.com/" + title.replace(" ", "-"),
    }


def index(*, reviewed=None, articles=None, direct=None, name="Lambrini Girls"):
    return {
        "artists": {
            "lambrini-girls": {
                "n": name,
                "identity": {"genres": reviewed or []},
                "da": direct if direct is not None else list(range(len(articles or []))),
            },
        },
        "articles": articles or [],
    }


def baseline_report(count=1):
    return {
        "total": count, "populated": 0, "blank": count,
        "blank_no_raw": count, "coverage_percentage": 0,
        "unresolved_artists": [
            {"artist": "Lambrini Girls", "affected_events": count,
             "raw_genres": [], "sources": [], "reason": "no_raw_evidence"},
        ],
    }


class EditorialGenreTests(unittest.TestCase):
    def test_manually_reviewed_identity_fills_no_raw_event(self):
        event = concert()
        report = enrich_unclassified_with_editorial_genres(
            [event], index(reviewed=["Punk"]), baseline_report(),
        )
        self.assertEqual(event.genre_public, "Rock / Indie / Punk")
        self.assertEqual(event.genre_method, "editorial_reviewed_identity")
        self.assertEqual(report["blank"], 0)
        self.assertEqual(report["populated"], 1)
        self.assertEqual(report["blank_no_raw"], 0)
        self.assertEqual(report["unresolved_artists"], [])

    def test_two_direct_artist_articles_support_consensus(self):
        content = index(articles=[
            article("Lambrini Girls interview", "Punk"),
            article("Lambrini Girls live at Trabendo", "Punk"),
        ])
        event = concert()
        report = enrich_unclassified_with_editorial_genres(
            [event], content, baseline_report(),
        )
        self.assertEqual(event.genre_public, "Rock / Indie / Punk")
        self.assertEqual(event.genre_method, "editorial_article_consensus")
        self.assertEqual(report["editorial_genre_evidence"]["assigned_events"], 1)

    def test_one_article_or_conflicting_genre_remains_blank(self):
        for content in (
            index(articles=[article("Lambrini Girls at Trabendo")]),
            index(articles=[
                article("Lambrini Girls at Trabendo", "Punk"),
                article("Lambrini Girls tour", "Electronic"),
            ]),
            index(articles=[
                article("Lambrini Girls gig", "Punk"),
                article("Lambrini Girls review", "Pop"),
            ]),
            index(reviewed=["Punk", "Electronic"], articles=[
                article("Lambrini Girls gig", "Punk"),
                article("Lambrini Girls review", "Punk"),
            ]),
        ):
            with self.subTest(content=content):
                event = concert()
                report = enrich_unclassified_with_editorial_genres(
                    [event], content, baseline_report(),
                )
                self.assertIsNone(event.genre_public)
                self.assertEqual(report["blank"], 1)

    def test_multi_artist_article_is_not_artist_specific(self):
        first = article("Lambrini Girls review")
        first["a"] = ["lambrini-girls", "other-act"]
        content = index(articles=[
            first, article("Lambrini Girls show", "Punk"),
        ])
        self.assertEqual(build_editorial_artist_genre_evidence(content), {})

    def test_direct_subject_and_exact_title_are_both_required(self):
        content = index(articles=[
            article("Lambrini Girls review"),
            article("An unrelated pop festival", "Punk"),
        ])
        self.assertEqual(build_editorial_artist_genre_evidence(content), {})
        content["artists"]["lambrini-girls"]["da"] = [0]
        self.assertEqual(build_editorial_artist_genre_evidence(content), {})

    def test_manual_identity_cannot_override_source_or_festival_roles(self):
        cases = [
            {"genre": "Metal", "genre_evidence": [{"raw": "Metal", "source": "Venue"}]},
            {"genre_evidence": [{"raw": "Other", "source": "Venue"}]},
            {"festival_name": "Festival"},
            {"co_headliners": ["Another Artist"]},
            {"openers": ["Support Act"]},
            {"event_title": "Unrelated stage production"},
        ]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                event = concert(**kwargs)
                report = enrich_unclassified_with_editorial_genres(
                    [event], index(reviewed=["Punk"]), baseline_report(),
                )
                self.assertIsNone(event.genre_public)
                self.assertEqual(report["editorial_genre_evidence"]["assigned_events"], 0)

    def test_billing_strings_and_ambiguous_identities_never_qualify(self):
        for name in ("One + Two", "One et Two", "One — Two", "One / Two"):
            with self.subTest(name=name):
                content = index(reviewed=["Punk"], name=name)
                self.assertEqual(build_editorial_artist_genre_evidence(content), {})
        content = index(reviewed=["Punk"])
        content["artists"]["lambrini-girls"]["identity"]["ambiguityClass"] = "ambiguous"
        self.assertEqual(build_editorial_artist_genre_evidence(content), {})

    def test_source_mapping_is_never_overridden(self):
        event = concert(genre_public="Metal / Hard Rock")
        report = enrich_unclassified_with_editorial_genres(
            [event], index(reviewed=["Punk"]),
            {"total": 1, "populated": 1, "blank": 0, "blank_no_raw": 0,
             "coverage_percentage": 100, "unresolved_artists": []},
        )
        self.assertEqual(event.genre_public, "Metal / Hard Rock")
        self.assertEqual(report["blank"], 0)

    def test_observed_atomic_source_genres(self):
        values = {
            "Deathcore": "Metal / Hard Rock",
            "Groove metal": "Metal / Hard Rock",
            "Industrial Metal": "Metal / Hard Rock",
            "MELODIC DEATH METAL": "Metal / Hard Rock",
            "Thrash Metal": "Metal / Hard Rock",
            "post-hardcore": "Rock / Indie / Punk",
            "punk-hardcore": "Rock / Indie / Punk",
            "prog rock": "Rock / Indie / Punk",
            "house": "Electronic",
            "drum-and-bass": "Electronic",
            "synth-pop": "Pop",
            "Pop indé": "Pop",
            "concert indie folk": "Folk / Country",
            "##rap": "Hip-hop / Rap",
            "#rnb": "R&B / Soul / Funk",
            "#alt #rock #indie": "Rock / Indie / Punk",
            "#noise #rock": "Rock / Indie / Punk",
            "#psychrock #rock": "Rock / Indie / Punk",
        }
        for raw, target in values.items():
            with self.subTest(raw=raw):
                self.assertEqual(map_raw_genres(raw), [target])

    def test_non_genre_and_cross_bucket_labels_still_unresolved(self):
        for raw in (
            "Ciné concert", "Conférence", "Tribute", "Danse",
            "MUSIQUE CLASSIQUE", "POP ROCK FOLK",
            "#folk #rock", "Indie / Folk",
        ):
            with self.subTest(raw=raw):
                self.assertEqual(map_raw_genres(raw), [])


if __name__ == "__main__":
    unittest.main()
