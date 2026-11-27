"""Cross-source venue-branded event collision regression tests."""
import unittest

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent
from concert_calendar.venues import normalize_event_venue


def sample(title, venue, source, *, time=None, lineup=None, ticket=None):
    return ConcertEvent(
        date="2026-11-28",
        headliner=title,
        venue=venue,
        city="Paris",
        department="75",
        source_names=[source],
        start_time=time,
        openers=lineup,
        ticket_url=ticket,
    )


class PopupVenueBrandedDedupTests(unittest.TestCase):
    def test_popup_aliases_identify_one_physical_room(self):
        self.assertEqual(
            "Le Pop-Up du Label",
            normalize_event_venue(
                sample("Singer", "Le POPUP du Label", "DICE")
            ).venue,
        )
        self.assertEqual(
            "Le Pop-Up du Label",
            normalize_event_venue(
                sample("Singer", "Le Pop-Up du Label", "Le Pop-Up du Label")
            ).venue,
        )

    def test_corroborated_event_with_venue_partner_suffix_is_one_row(self):
        official = sample(
            "Mauvaise Ambiance", "Le Pop-Up du Label", "Le Pop-Up du Label",
            lineup=["Enzo Grubert", "Fraga", "Jim Gamberge", "May Bad", "POM"],
            ticket="https://shotgun.live/events/mauvaise-ambiance-x-popup",
        )
        external = sample(
            "MAUVAISE AMBIANCE x POPUP", "Le POPUP du Label", "DICE",
            time="23:00",
            ticket="https://dice.fm/event/6b06aeaa4e70980001c99fac",
        )
        for row in (official, external):
            normalize_event_venue(row)
        result = deduplicate_events([official, external])
        self.assertEqual(1, len(result))
        self.assertEqual("Mauvaise Ambiance", result[0].headliner)
        self.assertEqual(
            ["Enzo Grubert", "Fraga", "Jim Gamberge", "May Bad", "POM"],
            result[0].openers,
        )
        self.assertEqual("Le Pop-Up du Label", result[0].venue)
        self.assertEqual("23:00", result[0].start_time)
        self.assertEqual(
            {"DICE", "Le Pop-Up du Label"},
            set(result[0].source_names or []),
        )

    def test_actual_artist_collaboration_is_not_a_venue_wrapper(self):
        events = [
            sample("Singer", "Le Pop-Up du Label", "Le Pop-Up du Label"),
            sample("Singer x Other Artist", "Le POPUP du Label", "DICE"),
        ]
        for event in events:
            normalize_event_venue(event)
        self.assertEqual(2, len(deduplicate_events(events)))

    def test_distinct_set_times_remain_distinct_even_with_venue_suffix(self):
        events = [
            sample("Singer", "Le Pop-Up du Label", "Le Pop-Up du Label", time="20:00"),
            sample("Singer x POPUP", "Le POPUP du Label", "DICE", time="23:00"),
        ]
        for event in events:
            normalize_event_venue(event)
        self.assertEqual(2, len(deduplicate_events(events)))

    def test_unrelated_venue_suffix_is_not_removed(self):
        events = [
            sample("Singer", "Le Pop-Up du Label", "Le Pop-Up du Label"),
            sample("Singer x Supersonic", "Le POPUP du Label", "DICE"),
        ]
        for event in events:
            normalize_event_venue(event)
        self.assertEqual(2, len(deduplicate_events(events)))


if __name__ == "__main__":
    unittest.main()
