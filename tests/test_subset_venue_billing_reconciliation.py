"""Regression: differing ticket/venue bills for one dated live performance."""
import unittest

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent


def row(title, *, source, day="2026-11-13", time="19:30", marker=None,
        co_headliners=None):
    return ConcertEvent(
        date=day, headliner=title, venue="Bal Chavaux",
        city="Montreuil", department="93",
        start_time=time, source_names=[source],
        performance_marker=marker, co_headliners=co_headliners,
        ticket_url=(
            "https://balchavaux.fr/agenda/baby-berserk-no-sex-last-night-exchpoptrue-nevroses-nocturnes"
            if source == "Bal Chavaux"
            else "https://dice.fm/event/6a21778c6e822400010fe6c2"
        ),
    )


VENUE_BILL = "Baby Berserk + No Sex Last Night + Exchpoptrue + Nevroses Nocturnes"
DICE_BILL = "Baby Berserk + Exchpoptrue + No Sex Last Night"


class SubsetVenueBillTests(unittest.TestCase):
    def test_reordered_shorter_dice_bill_merges_into_authoritative_full_bill(self):
        events = [
            row(DICE_BILL, source="DICE"),
            row(VENUE_BILL, source="Bal Chavaux", co_headliners=["No Sex Last Night"]),
        ]
        audit = {}
        results = deduplicate_events(events, diagnostics=audit)
        self.assertEqual(1, len(results))
        self.assertEqual("Baby Berserk", results[0].headliner)
        self.assertEqual(
            ["No Sex Last Night", "Exchpoptrue", "Nevroses Nocturnes"],
            results[0].co_headliners,
        )
        self.assertEqual(
            ["Baby Berserk", "No Sex Last Night", "Exchpoptrue", "Nevroses Nocturnes"],
            results[0].performers,
        )
        self.assertEqual("19:30", results[0].start_time)
        self.assertEqual(["Bal Chavaux", "DICE"], results[0].source_names)
        self.assertEqual(1, audit["unique_subset_venue_bills_merged"])

    def test_reverse_order_also_merges(self):
        events = [
            row(VENUE_BILL, source="Bal Chavaux"),
            row(DICE_BILL, source="DICE"),
        ]
        self.assertEqual(1, len(deduplicate_events(events)))

    def test_different_times_remain_separate(self):
        events = [
            row(VENUE_BILL, source="Bal Chavaux", time="19:30"),
            row(DICE_BILL, source="DICE", time="21:00"),
        ]
        self.assertEqual(2, len(deduplicate_events(events)))

    def test_different_date_remains_separate(self):
        events = [
            row(VENUE_BILL, source="Bal Chavaux"),
            row(DICE_BILL, source="DICE", day="2026-11-14"),
        ]
        self.assertEqual(2, len(deduplicate_events(events)))

    def test_non_subset_bill_remains_separate(self):
        events = [
            row(VENUE_BILL, source="Bal Chavaux"),
            row("Baby Berserk + A Different Artist + No Sex Last Night", source="DICE"),
        ]
        self.assertEqual(2, len(deduplicate_events(events)))

    def test_two_venue_performances_are_preserved(self):
        events = [
            row(VENUE_BILL, source="Bal Chavaux"),
            row(DICE_BILL, source="Bal Chavaux"),
        ]
        self.assertEqual(2, len(deduplicate_events(events)))

    def test_multiple_candidates_are_not_automatically_collapsed(self):
        events = [
            row(VENUE_BILL, source="Bal Chavaux"),
            row(DICE_BILL, source="DICE"),
            row("Baby Berserk + No Sex Last Night + Exchpoptrue", source="DICE"),
        ]
        self.assertGreaterEqual(len(deduplicate_events(events)), 2)

    def test_separately_marked_set_is_preserved(self):
        events = [
            row(VENUE_BILL, source="Bal Chavaux", marker="early show"),
            row(DICE_BILL, source="DICE", marker="late show"),
        ]
        self.assertEqual(2, len(deduplicate_events(events)))


if __name__ == "__main__":
    unittest.main()
