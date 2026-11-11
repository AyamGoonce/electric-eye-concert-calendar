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
