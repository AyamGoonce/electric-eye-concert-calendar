import unittest

from concert_calendar.models import ConcertEvent
from concert_calendar.sources import classify_event_eligibility


def event(**kwargs):
    return ConcertEvent("2027-01-01", "Example", "Venue", "Paris", "75", **kwargs)


class EventEligibilityTests(unittest.TestCase):
    def test_speed_dating_social_listing_is_not_a_concert(self):
        for title in (
            "Le plus grand speed-dating de Paris #3",
            "Speed dating à Paris",
            "Speed-dating social evening",
        ):
            with self.subTest(title=title):
                item = event()
                item.headliner = title
                eligible, reason = classify_event_eligibility(item)
                self.assertFalse(eligible)
                self.assertEqual("non_music_social_event", reason)

    def test_legitimate_music_billings_are_not_broadly_rejected(self):
        for title in (
            "Speedy Ortiz",
            "The Dating Game",
            "Speed of Sound",
            "Love Songs Live",
            "Evil Invaders + Exhorder + Heathen",
        ):
            with self.subTest(title=title):
                item = event()
                item.headliner = title
                self.assertTrue(classify_event_eligibility(item)[0])

    def test_structured_listening_event_without_performer_is_rejected(self):
        eligible, reason = classify_event_eligibility(event(category="Listening session"))
        self.assertFalse(eligible)
        self.assertEqual("non_concert_category", reason)

    def test_structured_screening_with_live_performer_survives(self):
        eligible, reason = classify_event_eligibility(event(event_type="screening", performers=["Live Score"]))
        self.assertTrue(eligible)
        self.assertIsNone(reason)

    def test_dj_and_vinyl_words_are_not_generic_exclusions(self):
        for title in ("DJ Night", "Vinyl Release Party", "Electronic Session"):
            record = event()
            record.headliner = title
            record.event_type = "live performance"
            record.performers = [title]
            self.assertTrue(classify_event_eligibility(record)[0])

    def test_structured_workshop_without_performer_is_rejected(self):
        eligible, reason = classify_event_eligibility(event(event_type="workshop"))
        self.assertFalse(eligible)
        self.assertEqual("non_performance_event_type", reason)
