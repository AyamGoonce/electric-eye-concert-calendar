import unittest

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent


def event(
    headliner,
    *,
    source,
    start_time,
    co_headliners=None,
    event_title=None,
):
    return ConcertEvent(
        date="2030-01-01",
        headliner=headliner,
        venue="Example Hall",
        city="Paris",
        department="75",
        source_names=[source],
        start_time=start_time,
        co_headliners=co_headliners,
        event_title=event_title,
    )


class CrossSourceTimeReconciliationTests(unittest.TestCase):

    def test_venue_time_resolves_external_source_disagreement(self):
        events = [
            event(
                "Alpha + Beta",
                source="Example Hall",
                start_time="20:00",
            ),
            event(
                "Alpha",
                source="Ticketing Platform",
                start_time="19:00",
                co_headliners=["Beta"],
                event_title="Alpha + Beta",
            ),
        ]

        result = deduplicate_events(events)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].headliner, "Alpha")
        self.assertEqual(result[0].co_headliners, ["Beta"])
        self.assertEqual(result[0].start_time, "20:00")

    def test_two_external_sources_with_different_times_remain_separate(self):
        events = [
            event(
                "Alpha + Beta",
                source="Ticket Source A",
                start_time="20:00",
            ),
            event(
                "Alpha",
                source="Ticket Source B",
                start_time="19:00",
                co_headliners=["Beta"],
                event_title="Alpha + Beta",
            ),
        ]

        self.assertEqual(len(deduplicate_events(events)), 2)

    def test_two_venue_records_with_different_times_remain_separate(self):
        events = [
            event(
                "Alpha + Beta",
                source="Example Hall",
                start_time="20:00",
            ),
            event(
                "Alpha",
                source="Example Hall",
                start_time="19:00",
                co_headliners=["Beta"],
                event_title="Alpha + Beta",
            ),
        ]

        self.assertEqual(len(deduplicate_events(events)), 2)

    def test_explicit_early_late_performances_remain_separate(self):
        events = [
            event(
                "Alpha + Beta",
                source="Example Hall",
                start_time="20:00",
                event_title="Alpha + Beta — Late Show",
            ),
            event(
                "Alpha",
                source="Ticketing Platform",
                start_time="19:00",
                co_headliners=["Beta"],
                event_title="Alpha + Beta — Early Show",
            ),
        ]

        self.assertEqual(len(deduplicate_events(events)), 2)


if __name__ == "__main__":
    unittest.main()
