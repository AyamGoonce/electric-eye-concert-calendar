"""Regressions for performer billing, programme concepts, and retained inventory."""
import unittest
from datetime import date

from bs4 import BeautifulSoup

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.event_titles import is_non_music_quiz_title
from concert_calendar.models import ConcertEvent
from concert_calendar.scrapers import dice, popup_label
from concert_calendar.sources import (
    classify_event_eligibility,
    filter_eligible_retained_events,
)


def item(title, venue="Le Chinois", day="2026-11-22", **kwargs):
    return ConcertEvent(
        date=day, headliner=title, venue=venue,
        city="Montreuil" if venue == "Le Chinois" else "Paris",
        department="93" if venue == "Le Chinois" else "75",
        **kwargs,
    )


class NonMusicalQuizTests(unittest.TestCase):
    def test_nonperforming_blindtests_and_music_quizzes(self):
        for name in (
            "Blindtest with Dr Wax",
            "Blind Test avec DJ Marcel",
            "Blind-test : spécial rock",
            "Quiz musical du vendredi",
            "Music trivia with a host",
        ):
            with self.subTest(name=name):
                self.assertTrue(is_non_music_quiz_title(name))
                self.assertEqual(
                    (False, "non_music_quiz_event"),
                    classify_event_eligibility(item(name)),
                )
                self.assertIsNone(dice.parse_event({
                    "id": "quiz-1", "name": name,
                    "dates": {"event_start_date": "2026-11-22T20:00:00+01:00"},
                    "venues": [{"name": "Le Chinois", "city": {"name": "Montreuil"}}],
                }))

    def test_concert_bills_and_music_named_artists_remain_eligible(self):
        for title in (
            "Blind Guardian", "The Blind Test Orchestra",
            "DJ Shadow", "The Quiz", "The Music",
            "Florence + The Machine", "Immatures + P.o Box + Solitone + Lundi Brûle",
        ):
            with self.subTest(title=title):
                self.assertFalse(is_non_music_quiz_title(title))
                self.assertTrue(classify_event_eligibility(item(title))[0])

    def test_popup_calendar_discards_blindtest_but_retains_real_concert(self):
        html = """
        <div id="Novembre2026" class="concert mois"></div>
        <div class="concert"><div class="jour">11.11</div>
            <div class="titre">Blindtest with Dr Wax</div></div>
        <div class="concert"><div class="jour">12.11</div>
            <div class="titre">Blind Guardian</div></div>
        """
        records = popup_label.parse_events(
            BeautifulSoup(html, "html.parser"), today=date(2026, 11, 1),
        )
        self.assertEqual(["Blind Guardian"], [record.headliner for record in records])

    def test_prior_retention_cannot_reintroduce_quiz(self):
        records = [
            item("Blindtest with Dr Wax", venue="Le Pop-Up du Label"),
            item("Real Concert", venue="Le Pop-Up du Label"),
        ]
        self.assertEqual(
            ["Real Concert"],
            [record.headliner for record in filter_eligible_retained_events(records)],
        )


class ReviewedTheatricalCabaretTests(unittest.TestCase):
    def test_bad_biches_ticket_is_not_a_concert_even_with_music_language(self):
        title = "Cabaret Bad Biches : Qui a tué Constance Palmer ?"
        event = dice.parse_event({
            "id": "6ace08ea4bb69200019f0926",
            "name": title,
            "dates": {"event_start_date": "2026-11-21T20:00:00+01:00"},
            "venues": [{"name": "Les Trois Baudets",
                        "city": {"name": "Paris"}}],
        })
        self.assertIsNotNone(event)
        self.assertEqual(
            (False, "non_music_theatrical_cabaret"),
            classify_event_eligibility(event),
        )
        # Both the initial and post-dedup gates must enforce this.
        event.headliner = "Bad Biches"
        event.raw_title = title
        event.performers = ["Bad Biches"]
        event.event_type = "live performance"
        self.assertEqual(
            (False, "non_music_theatrical_cabaret"),
            classify_event_eligibility(event),
        )
        self.assertEqual([], filter_eligible_retained_events([event]))

    def test_bad_biches_exception_does_not_exclude_real_music_cabarets(self):
        for title, venue, day in (
            ("Cabaret Bad Biches : Qui a tué Constance Palmer ?",
             "Les Trois Baudets", "2026-11-22"),
            ("Cabaret Bad Biches : Qui a tué Constance Palmer ?",
             "Le Trianon", "2026-11-21"),
            ("Cabaret Concert: Les Voix du Jazz",
             "Les Trois Baudets", "2026-11-21"),
            ("Bad Biches", "Les Trois Baudets", "2026-11-21"),
        ):
            with self.subTest(title=title, venue=venue, day=day):
                self.assertTrue(classify_event_eligibility(
                    item(title, venue=venue, day=day)
                )[0])


class AmbiguousTicketingEditionTests(unittest.TestCase):
    def test_unbilled_late_night_dice_edition_is_not_a_concert(self):
        for title in ("INFRRD Ep02", "INFRRD Ep03", "New Signal Edition 4"):
            with self.subTest(title=title):
                record = item(
                    title, venue="Vogue", day="2026-11-20",
                    start_time="23:45", source_names=["DICE"],
                    raw_title=title,
                )
                self.assertEqual(
                    (False, "unverified_late_night_edition"),
                    classify_event_eligibility(record),
                )
                self.assertEqual([], filter_eligible_retained_events([record]))
                self.assertEqual(
                    (False, "unverified_late_night_edition"),
                    classify_event_eligibility(deduplicate_events([record])[0]),
                )

    def test_proven_performance_and_other_sources_survive(self):
        cases = (
            dict(performers=["The Musician"]),
            dict(genre="Electronic"),
            dict(event_type="live performance"),
            dict(start_time="19:00"),
            dict(source_names=["Official venue"]),
        )
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                params = dict(start_time="23:45", source_names=["DICE"])
                params.update(kwargs)
                record = item("Signal Ep03", venue="Vogue", **params)
                self.assertTrue(classify_event_eligibility(record)[0])

    def test_non_series_band_names_are_not_rejected(self):
        for title in ("Episode 4", "The Ep 3", "Ep 02 and the Bad Seeds"):
            with self.subTest(title=title):
                record = item(title, venue="Vogue", start_time="23:45",
                              source_names=["DICE"])
                self.assertTrue(classify_event_eligibility(record)[0])


class SourceCreditedStagePerformanceTests(unittest.TestCase):
    def test_named_work_uses_structured_artist_credit(self):
        work = "A long music and movement performance with an evocative narrative title"
        result = dice.parse_event({
            "id": "source-credited-work",
            "name": work,
            "artists": [{"name": "Performing Musician"}],
            "dates": {"event_start_date": "2027-01-13T20:30:00+01:00"},
            "venues": [{"name": "Maison des Métallos", "city": {"name": "Paris"}}],
        })
        self.assertEqual(result.headliner, "Performing Musician")
        self.assertEqual(result.event_title, work)
        self.assertEqual(result.raw_title, work)
        self.assertEqual(result.performers, ["Performing Musician"])
        self.assertTrue(classify_event_eligibility(result)[0])

    def test_uncredited_or_multi_artist_titles_not_guessed(self):
        work = "A long music and movement performance with an evocative narrative title"
        for artists in ([], [{"name": "One"}, {"name": "Two"}]):
            with self.subTest(artists=artists):
                result = dice.parse_event({
                    "id": "unresolved-stage-work",
                    "name": work,
                    "artists": artists,
                    "dates": {"event_start_date": "2027-01-13T20:30:00+01:00"},
                    "venues": [{"name": "Maison des Métallos", "city": {"name": "Paris"}}],
                })
                self.assertEqual(result.headliner, work)


class ProgrammeBillingTests(unittest.TestCase):
    def test_reviewed_city_presentation_is_not_the_artist(self):
        raw = "Athènes débarque à la Méca : THEODORE + SOMA"
        event = item(
            raw, "La Mécanique Ondulatoire", "2026-11-20",
            source_names=["DICE"],
        )
        result = deduplicate_events([event])[0]
        self.assertEqual("THEODORE", result.headliner)
        self.assertEqual(["SOMA"], result.co_headliners)
        self.assertEqual(["THEODORE", "SOMA"], result.performers)
        self.assertEqual("Athènes débarque à la Méca", result.event_title)
        self.assertEqual(raw, result.raw_title)

    def test_scoped_review_corrects_incomplete_structured_lineup(self):
        raw = "Athènes débarque à la Méca : THEODORE + SOMA"
        event = item(
            "THEODORE", "La Mécanique Ondulatoire", "2026-11-20",
            raw_title=raw, performers=["THEODORE"],
            event_title=raw, source_names=["DICE"],
        )
        result = deduplicate_events([event])[0]
        self.assertEqual("THEODORE", result.headliner)
        self.assertEqual(["SOMA"], result.co_headliners)
        self.assertEqual("Athènes débarque à la Méca", result.event_title)

    def test_series_name_is_not_invented_as_performer(self):
        raw = "Immatures + P.o Box + Solitone + Lundi Brûle"
        event = item(raw, source_names=["DICE"])
        result = deduplicate_events([event])[0]
        self.assertEqual("P.o Box", result.headliner)
        self.assertEqual(["Solitone", "Lundi Brûle"], result.co_headliners)
        self.assertEqual("Immatures", result.event_title)
        self.assertEqual(raw, result.raw_title)

    def test_scoped_review_never_rewrites_different_show(self):
        raw = "Immatures + P.o Box + Solitone + Lundi Brûle"
        event = item(raw, day="2027-11-22", source_names=["DICE"])
        result = deduplicate_events([event])[0]
        self.assertEqual(raw, result.headliner)
        self.assertIsNone(result.co_headliners)

    def test_other_ambiguous_separator_titles_are_not_guessed(self):
        raw = "Artist: Album Tour + Special Project"
        event = item(raw, source_names=["DICE"])
        result = deduplicate_events([event])[0]
        self.assertEqual(raw, result.headliner)
        self.assertIsNone(result.co_headliners)


if __name__ == "__main__":
    unittest.main()
