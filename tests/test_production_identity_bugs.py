import json
import unittest
from datetime import date
from unittest.mock import patch

from concert_calendar import content_index
from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import prepare_upcoming_events, serialize_data
from concert_calendar.scrapers import dice, olympia
from tests.test_content_index import entry


def serialized(events):
    return json.loads(serialize_data(prepare_upcoming_events(events, today=date(2027, 1, 1))))


class ProductionIdentityBugsTests(unittest.TestCase):
    def test_exact_support_title_through_parsers_dedup_and_export(self):
        title = "Eivør | 1ère Partie : Rabbitology"
        official = olympia.parse_item({
            "post_title": title, "terms": {"genre": [{"name": "Rock"}]},
            "meta": {"begin_date_ymd": "2027-03-06", "end_date_ymd": "2027-03-06"},
        })[0]
        aggregate = dice.parse_event({
            "id": "test", "name": title,
            "dates": {"event_start_date": "2027-03-06T20:00:00+01:00"},
            "venues": [{"name": official.venue, "city": {"name": "Paris"}}],
        })
        for parsed in (official, aggregate):
            self.assertEqual("Eivør", parsed.headliner)
            self.assertEqual(["Rabbitology"], parsed.openers)
            plain = ConcertEvent(date=parsed.date, headliner="Eivør", venue=parsed.venue, city="Paris", department="75")
            output = serialized(deduplicate_events([plain, parsed]))
            self.assertEqual(1, len(output))
            self.assertEqual("Eivør", output[0]["h"])
            self.assertEqual(["Rabbitology"], output[0]["o"])
        for parser in (dice.parse_explicit_support_title, olympia.parse_explicit_support_title):
            self.assertEqual(("Artist | Live: Session", None), parser("Artist | Live: Session"))

    def test_content_ownership_in_final_data(self):
        for article_artist, concert_artist, matches in (
            ("Ambré", "Ambre", False), ("Ambre", "Ambré", False),
            ("Ambré", "Ambré", True), ("Ambré", "Ambre\u0301", True),
            ("Ambré", "AMBRÉ", True),
        ):
            with self.subTest(article=article_artist, concert=concert_artist):
                index = content_index.build_index([entry(
                    article_artist + " @ Bataclan, Paris - January 1st, 2026", [article_artist, "Concert Review"],
                    image="https://example.com/s100/hero.jpg",
                )])
                event = ConcertEvent(date="2027-03-08", headliner=concert_artist,
                                     venue="Salle Pleyel", city="Paris", department="75")
                content_index.enrich_events([event], index)
                output = serialized([event])[0]
                self.assertEqual(matches, bool(output.get("ee")))
                self.assertEqual(matches, bool(output.get("im")))
                if matches:
                    self.assertEqual(1, event.electric_eye_links[0]["total"])
                else:
                    self.assertIsNone(event.image_source)

    def test_reviewed_alias_remains_valid(self):
        with patch.dict(content_index.EXPLICIT_ALIASES, {"Verified Alias": "Ambré"}):
            index = content_index.build_index([entry("Ambré @ Bataclan, Paris - January 1st, 2026", ["Ambré", "Concert Review"])])
            event = ConcertEvent(date="2027-03-08", headliner="Verified Alias", venue="Salle Pleyel", city="Paris", department="75")
            content_index.enrich_events([event], index)
            self.assertEqual(1, event.electric_eye_links[0]["total"])
            self.assertTrue(serialized([event])[0].get("ee"))
