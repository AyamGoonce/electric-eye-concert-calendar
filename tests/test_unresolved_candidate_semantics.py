import unittest

from concert_calendar.deduplication import _unresolved_candidates
from concert_calendar.models import ConcertEvent


def event(
    headliner,
    venue,
    *,
    source,
    ticket_url=None,
):
    return ConcertEvent(
        date="2030-01-01",
        headliner=headliner,
        venue=venue,
        city="Paris",
        department="75",
        source_names=[source],
        ticket_url=ticket_url,
    )


class UnresolvedCandidateSemanticsTests(unittest.TestCase):

    def test_two_official_venues_are_not_automatically_a_conflict(self):
        events = [
            event(
                "Example Artist",
                "Example Hall A",
                source="Example Hall A",
            ),
            event(
                "Example Artist",
                "Example Hall B",
                source="Example Hall B",
            ),
        ]

        result = _unresolved_candidates(events)

        self.assertFalse(
            any(item["kind"] == "venue_conflict" for item in result)
        )

    def test_external_source_disagreement_still_flags_venue_conflict(self):
        events = [
            event(
                "Example Artist",
                "Example Hall A",
                source="Example Hall A",
            ),
            event(
                "Example Artist",
                "Example Hall B",
                source="Ticketing Platform",
            ),
        ]

        result = _unresolved_candidates(events)

        self.assertTrue(
            any(item["kind"] == "venue_conflict" for item in result)
        )

    def test_generic_ticket_page_with_language_parameter_is_not_event_specific(self):
        url = (
            "https://tickets.example.test/content/billetterie"
            "?lang=fr-fr"
        )

        events = [
            event(
                "Artist Alpha",
                "Example Festival",
                source="Promoter",
                ticket_url=url,
            ),
            event(
                "Artist Beta",
                "Example Festival",
                source="Promoter",
                ticket_url=url,
            ),
        ]

        result = _unresolved_candidates(events)

        self.assertFalse(
            any(item["kind"] == "shared_event_ticket" for item in result)
        )

    def test_event_identifier_on_generic_ticket_path_remains_specific(self):
        url = (
            "https://tickets.example.test/billetterie"
            "?event=12345&lang=fr-fr"
        )

        events = [
            event(
                "Artist Alpha",
                "Example Hall",
                source="Promoter",
                ticket_url=url,
            ),
            event(
                "Artist Beta",
                "Example Hall",
                source="Promoter",
                ticket_url=url,
            ),
        ]

        result = _unresolved_candidates(events)

        self.assertTrue(
            any(item["kind"] == "shared_event_ticket" for item in result)
        )


if __name__ == "__main__":
    unittest.main()
