"""Protect distinct performances while reconciling unique venue/DICE clocks."""
import unittest

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent


def event(time, source, *, title="Bilal Hassani", venue="La Cigale", marker=None):
    return ConcertEvent(
        date="2026-11-17", headliner=title, venue=venue, city="Paris",
        department="75", start_time=time, source_names=[source],
        performance_marker=marker,
        ticket_url=(
            "https://lacigale.fr/evenements/bilal-hassani/"
            if source == "La Cigale"
            else "https://dice.fm/event/69a58c9d2d2d100001956846"
        ),
        genre="Pop" if source == "La Cigale" else None,
    )


class UniqueVenueDiceClockTests(unittest.TestCase):
    def test_bilal_exact_production_duplicate_keeps_venue_time(self):
        official = event("19:45", "La Cigale")
        dice = event("20:00", "DICE")
        audit = {}
        merged = deduplicate_events([dice, official], diagnostics=audit)
        self.assertEqual(1, len(merged))
        self.assertEqual("19:45", merged[0].start_time)
        self.assertEqual(["DICE", "La Cigale"], merged[0].source_names)
        self.assertEqual("https://lacigale.fr/evenements/bilal-hassani/", merged[0].ticket_url)
        self.assertEqual(1, audit["unique_official_dice_clock_variants_merged"])

    def test_bilal_reverse_source_order(self):
        merged = deduplicate_events([event("19:45", "La Cigale"), event("20:00", "DICE")])
        self.assertEqual(1, len(merged))
        self.assertEqual("19:45", merged[0].start_time)

    def test_unique_venue_and_dice_door_time_discrepancy_90_minutes(self):
        for venue_time, dice_time in (
            ("18:30", "20:00"), ("20:00", "18:30"),
            ("19:00", "20:00"),
        ):
            with self.subTest(venue=venue_time, dice=dice_time):
                merged = deduplicate_events([
                    event(venue_time, "La Cigale"),
                    event(dice_time, "DICE"),
                ])
                self.assertEqual(1, len(merged))
                self.assertEqual(venue_time, merged[0].start_time)

    def test_single_official_missing_clock_and_lone_dice_copy_merge(self):
        merged = deduplicate_events([
            event(None, "La Cigale"), event("20:00", "DICE"),
        ])
        self.assertEqual(1, len(merged))

    def test_distant_clocks_stay_separate(self):
        merged = deduplicate_events([event("19:00", "La Cigale"), event("21:00", "DICE")])
        self.assertEqual(2, len(merged))

    def test_two_official_performances_are_never_collapsed(self):
        merged = deduplicate_events([
            event("19:45", "La Cigale"), event("20:00", "La Cigale")
        ])
        self.assertEqual(2, len(merged))

    def test_three_records_are_not_automatically_collapsed(self):
        merged = deduplicate_events([
            event("19:45", "La Cigale"),
            event("20:00", "DICE"),
            event("20:20", "DICE"),
        ])
        self.assertGreaterEqual(len(merged), 2)

    def test_explicit_set_markers_are_preserved(self):
        merged = deduplicate_events([
            event("19:45", "La Cigale", marker="early show"),
            event("20:00", "DICE", marker="late show"),
        ])
        self.assertEqual(2, len(merged))

    def test_distinct_artist_billings_are_not_merged(self):
        merged = deduplicate_events([
            event("19:45", "La Cigale"),
            event("20:00", "DICE", title="Other Performer"),
        ])
        self.assertEqual(2, len(merged))


if __name__ == "__main__":
    unittest.main()
