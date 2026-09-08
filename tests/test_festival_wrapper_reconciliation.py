import unittest
import json
from datetime import date
from concert_calendar.models import ConcertEvent
from concert_calendar.deduplication import deduplicate_events
from concert_calendar.production_export import prepare_upcoming_events, serialize_data


class FestivalWrapperTests(unittest.TestCase):
    def records(self, day=6):
        parent = ConcertEvent(date=f"2026-11-{day:02}", headliner=f"JOUR {day-4} - Pitchfork Avant-Garde 2026",
            venue="Multi-lieux : Badaboum, Le Café de la Danse, Les Disquaires, La Mécanique Ondulatoire, POPUP!, Supersonic, Supersonic Records",
            city="Paris", department="75", start_time="19:00", source_names=["DICE"],
            ticket_url="https://dice.fm/event/" + ("6a22cbe921f0160001cd4d5e" if day == 6 else "6a22cf9162c86a0001694560"))
        child = ConcertEvent(date=parent.date, headliner="Pitchfork Avant-Garde", venue="Le Pop-Up du Label",
            city="Paris", department="75", source_names=["Le Pop-Up du Label"],
            ticket_url="https://link.dice.fm/c84a00420511", facebook_event_url="https://www.facebook.com/events/1977130456499809/",
            first_seen="2026-08-01T00:00:00Z")
        return parent, child

    def test_captured_days_serialized(self):
        for day in (6, 7):
            parent, child = self.records(day)
            rows = deduplicate_events([parent, child])
            output = json.loads(serialize_data(prepare_upcoming_events(rows, date(2026, 1, 1))))
            self.assertEqual(1, len(output))
            self.assertEqual(parent.headliner, output[0]["h"])
            self.assertEqual(parent.venue, output[0]["v"])
            self.assertEqual({"DICE", "Le Pop-Up du Label"}, set(rows[0].source_names))
            self.assertEqual(child.first_seen, rows[0].first_seen)
            self.assertEqual(child.facebook_event_url, rows[0].facebook_event_url)
            self.assertTrue(output[0]["t"])

    def test_safety(self):
        for change in ("date", "venue", "artist", "bill", "time", "multi_day_pass"):
            parent, child = self.records()
            if change == "date": child.date = "2026-11-08"
            if change == "venue": child.venue = "La Cigale"
            if change == "artist": child.headliner = "Artist — Pitchfork Avant-Garde"
            if change == "bill": child.co_headliners = ["Artist"]
            if change == "time": child.start_time = "21:00"
            if change == "multi_day_pass": parent.headliner = "PASS 3 JOURS - Pitchfork Avant-Garde 2026"
            with self.subTest(change=change):
                self.assertEqual(2, len(deduplicate_events([parent, child])))
