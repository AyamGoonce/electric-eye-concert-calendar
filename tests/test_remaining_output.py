import json
import unittest
from datetime import date

from concert_calendar.models import ConcertEvent
from concert_calendar.scrapers.dice import parse_event
from concert_calendar.deduplication import deduplicate_events
from concert_calendar.venues import normalize_event_venue
from concert_calendar.genres import enrich_event_genres
from concert_calendar.production_export import prepare_upcoming_events, serialize_data


def output(events):
    return json.loads(serialize_data(prepare_upcoming_events(events, date(2026, 1, 1))))


class RemainingOutputTests(unittest.TestCase):
    def test_carpenter_branding_output(self):
        for different_time in (False, True):
            plain = ConcertEvent(date="2027-03-13", headliner="Carpenter Brut",
                                 venue="Le Zénith Paris – La Villette", city="Paris", department="75",
                                 source_names=["Le Zénith Paris – La Villette"],
                                 start_time="18:00" if different_time else None)
            marked = parse_event({"id": "698348ede5b7c200018909ce",
                                  "name": "CARPENTER BRUT - THE END COMPLETE",
                                  "dates": {"event_start_date": "2027-03-13T20:00:00+01:00"},
                                  "venues": [{"name": "Zénith Paris - La Villette", "city": {"name": "Paris"}}]})
            marked.source_names = ["DICE"]
            normalize_event_venue(marked)
            rows = output(deduplicate_events([plain, marked]))
            self.assertEqual(2 if different_time else 1, len(rows))
            if not different_time:
                self.assertEqual("Carpenter Brut", rows[0]["h"])

    def test_heavy_lungs_current_source_preserves_structure(self):
        parsed = parse_event({"id": "6a314dc1e947e50001325e21",
                              "name": "HEAVY LUNGS + JOE & THE SHITBOYS",
                              "dates": {"event_start_date": "2026-10-30T20:00:00+02:00"},
                              "venues": [{"name": "Le Plan", "city": {"name": "Paris"}}]})
        rows = output(deduplicate_events([parsed]))
        self.assertEqual("Heavy Lungs", rows[0]["h"])
        self.assertEqual(["Joe & The Shitboys"], rows[0]["ch"])

    def test_unordered_taxonomy_retains_raw_without_three_public_genres(self):
        for title, raw in (("Keziah Jones Symphonique", "Jazz, Musiques du monde, Soul, Funk"),
                           ("Tout le monde s'appelle clara", "Pop, Rock, Soul, Funk")):
            event = ConcertEvent(date="2026-09-29", headliner=title, venue="La Seine Musicale",
                                 city="Boulogne-Billancourt", department="92", genre=raw,
                                 genre_evidence=[{"raw": raw, "source": "La Seine Musicale"}])
            enrich_event_genres([event])
            self.assertEqual([], output([event])[0]["x"])
            self.assertEqual(raw, event.genre_evidence[0]["raw"])

    def test_unrelated_explicit_multigenre_is_not_capped(self):
        event = ConcertEvent(date="2027-01-01", headliner="Example", venue="Example", city="Paris",
                             department="75", genre="Jazz, Musiques du monde, Soul, Funk")
        enrich_event_genres([event])
        self.assertEqual(3, len(output([event])[0]["x"]))
