import unittest

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent


def event(
    date,
    headliner,
    *,
    source,
    ticket_url=None,
    co_headliners=None,
    event_title=None,
):
    return ConcertEvent(
        date=date,
        headliner=headliner,
        venue="Example Hall",
        city="Paris",
        department="75",
        source_names=[source],
        ticket_url=ticket_url,
        co_headliners=co_headliners,
        event_title=event_title,
    )


class PostTitleNormalizationReconciliationTests(unittest.TestCase):

    def test_series_wrapper_normalization_exposes_late_bill_match(self):
        events = [
            # Flat source representation: one billed artist, but the
            # event-specific URL explicitly contains the complete bill.
            event(
                "2030-01-01",
                "Beta",
                source="Example Hall",
                ticket_url=(
                    "https://tickets.example.test/"
                    "alpha-beta-example-hall"
                ),
            ),

            # Structured source representation whose primary artist is
            # initially hidden behind a programme/series prefix.
            event(
                "2030-01-01",
                "Example Festival : Alpha",
                source="Ticketing Platform",
                co_headliners=["Beta"],
                event_title="Example Festival : Alpha + Beta",
            ),

            # A second distinct bill from the same source establishes
            # "Example Festival" as recurring contextual programme grammar.
            event(
                "2030-01-02",
                "Example Festival : Gamma",
                source="Ticketing Platform",
            ),
        ]

        result = deduplicate_events(events)

        day_one = [
            item for item in result
            if item.date == "2030-01-01"
        ]

        self.assertEqual(len(day_one), 1)
        self.assertEqual(day_one[0].headliner, "Alpha")
        self.assertEqual(day_one[0].co_headliners, ["Beta"])
        self.assertEqual(
            set(day_one[0].source_names),
            {"Example Hall", "Ticketing Platform"},
        )


if __name__ == "__main__":
    unittest.main()
