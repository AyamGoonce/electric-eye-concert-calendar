import unittest

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent
from concert_calendar.venues import normalize_event_venue


def event(headliner, venue, *, co_headliners=None, source="Source"):
    return ConcertEvent(
        date="2030-01-01",
        headliner=headliner,
        venue=venue,
        city="Paris",
        department="75",
        source_names=[source],
        co_headliners=co_headliners,
    )


class WrappedVenueNormalizationTests(unittest.TestCase):

    def test_promotional_prefix_before_known_venue_is_removed(self):
        item = event(
            "Example Artist",
            "Example Festival - Théâtre de Rungis",
        )

        normalize_event_venue(item)

        self.assertEqual(item.venue, "Théâtre de Rungis")

    def test_colon_wrapper_before_known_venue_is_removed(self):
        item = event(
            "Example Artist",
            "Example Series : Pavillon Baltard",
        )

        normalize_event_venue(item)

        self.assertEqual(item.venue, "Pavillon Baltard")

    def test_unknown_wrapped_venue_is_not_guessed(self):
        item = event(
            "Example Artist",
            "Example Festival - Imaginary Hall",
        )

        normalize_event_venue(item)

        self.assertEqual(
            item.venue,
            "Example Festival - Imaginary Hall",
        )

    def test_wrapped_and_plain_known_venues_reconcile(self):
        events = [
            event(
                "Alpha + Beta",
                "Example Festival - Théâtre de Rungis",
                source="Venue",
            ),
            event(
                "Alpha",
                "Théâtre de Rungis",
                co_headliners=["Beta"],
                source="Ticketing",
            ),
        ]

        for item in events:
            normalize_event_venue(item)

        result = deduplicate_events(events)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].headliner, "Alpha")
        self.assertEqual(result[0].co_headliners, ["Beta"])
        self.assertEqual(result[0].venue, "Théâtre de Rungis")


if __name__ == "__main__":
    unittest.main()
