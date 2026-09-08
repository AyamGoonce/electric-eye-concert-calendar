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

    def test_whole_source_title_reconstructs_without_splitting_artist_name(self):
        for records in (self.records(), tuple(reversed(self.records()))):
            events = deduplicate_events(copy.deepcopy(records))
            self.assertEqual(1, len(events))
            event = events[0]
            self.assertEqual("Example Band", event.headliner)
            self.assertEqual(["Another & The Others"], event.co_headliners)
            self.assertFalse(event.openers)
            self.assertEqual({"DICE", "Le Plan"}, set(event.source_names))
            self.assertEqual("2026-08-20T11:02:59Z", event.first_seen)
            self.assertEqual("https://venue.example/event.jpg", event.image_url)
            self.assertEqual(["Example promoter"], event.promoters)
            self.assertEqual("Rock,Punk", event.genre)
            self.assertEqual("https://dice.fm/event/example", event.ticket_url)

    def test_heavy_lungs_captured_billing(self):
        events = deduplicate_events(list(self.records("HEAVY LUNGS", "JOE & THE SHITBOYS")))
        self.assertEqual(1, len(events))
        self.assertEqual("HEAVY LUNGS", events[0].headliner)
        self.assertEqual(["JOE & THE SHITBOYS"], events[0].co_headliners)
        self.assertFalse(events[0].openers)

    def test_new_reconstruction_requires_complete_matching_raw_title_and_time(self):
        for change in ("title", "missing_time", "different_time", "same_source", "different_venue"):
            structured, full = self.records()
            if change == "title": structured.event_title = "Different event"
            if change == "missing_time": full.start_time = None
            if change == "different_time": full.start_time = "22:00"
            if change == "same_source": full.source_names = ["DICE"]
            if change == "different_venue": full.venue = "Another venue"
            with self.subTest(change=change):
                self.assertEqual(2, len(deduplicate_events([structured, full])))

    def test_distinct_set_markers_remain_separate(self):
        structured, full = self.records()
        full.headliner += " - 2e set"
        self.assertEqual(2, len(deduplicate_events([structured, full])))

    def test_single_artist_name_is_not_parsed(self):
        event = self.records()[0]
        event.headliner = "An Artist + An Orchestra"
        event.event_title = event.headliner
        event.co_headliners = None
        result = deduplicate_events([event])[0]
        self.assertEqual(event.headliner, result.headliner)
        self.assertFalse(result.co_headliners)
