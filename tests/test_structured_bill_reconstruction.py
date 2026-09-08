import copy
import unittest

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent


class StructuredBillReconstructionTests(unittest.TestCase):
    def records(self, primary="Example Band", other="Another & The Others"):
        title = f"{primary} + {other}"
        structured = ConcertEvent(
            date="2026-10-30", headliner=primary, venue="Le Plan",
            city="Ris-Orangis", department="91", start_time="20:00",
            co_headliners=[other], event_title=title, source_names=["DICE"],
            ticket_url="https://dice.fm/event/example",
            first_seen="2026-08-23T21:52:57Z",
        )
        full = ConcertEvent(
            date=structured.date, headliner=title, venue=structured.venue,
            city=structured.city, department="91", start_time="20:00",
            source_names=["Le Plan"], genre="Rock,Punk",
            image_url="https://venue.example/event.jpg", image_source="Le Plan",
            ticket_url="https://venue.example/event",
            promoters=["Example promoter"], first_seen="2026-08-20T11:02:59Z",
        )
        return structured, full

    def test_heavy_lungs_captured_billing(self):
        events = deduplicate_events(list(self.records("HEAVY LUNGS", "JOE & THE SHITBOYS")))
        self.assertEqual(1, len(events))
        self.assertEqual("HEAVY LUNGS", events[0].headliner)
        self.assertEqual(["JOE & THE SHITBOYS"], events[0].co_headliners)

    def test_reconstruction_requires_matching_time_and_title(self):
        structured, full = self.records()
        full.start_time = "22:00"
        self.assertEqual(2, len(deduplicate_events([structured, full])))

