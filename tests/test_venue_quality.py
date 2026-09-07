from unittest import TestCase

from concert_calendar.event_state import canonical_event_identity
from concert_calendar.models import ConcertEvent
from concert_calendar.venues import normalize_event_venue


class VenueQualityTests(TestCase):
    def test_official_stadium_geography_preserves_identity_and_metadata(self):
        event = ConcertEvent("2027-01-01", "Artist", "Stade de France", "Paris", "75",
                             start_time="20:00", first_seen="2026-01-01T00:00:00Z")
        identity = canonical_event_identity(event)
        normalize_event_venue(event)
        self.assertEqual(("Saint-Denis", "93"), (event.city, event.department))
        self.assertEqual(identity, canonical_event_identity(event))
        self.assertEqual("20:00", event.start_time)
        self.assertEqual("2026-01-01T00:00:00Z", event.first_seen)

    def test_generic_rooms_are_not_assigned_an_inferred_parent(self):
        for venue in ("Main Room", "Club", "Hall", "Room 1", "Pitchfork Music Festival"):
            event = ConcertEvent("2027-01-01", "Artist", venue, "Paris", "75")
            normalize_event_venue(event)
            self.assertEqual(venue, event.venue)
