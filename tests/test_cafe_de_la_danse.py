from pathlib import Path
from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from concert_calendar.deduplication import (
    deduplicate_events,
    image_source_priority,
    merge_events,
)
from concert_calendar.event_state import (
    canonical_event_identity,
    is_new,
    reconcile_state,
)
from concert_calendar.models import ConcertEvent
from concert_calendar.scraper_loader import discover_scrapers
from concert_calendar.scrapers.cafe_de_la_danse import (
    PROGRAMME_URL,
    clean_headliner,
    load_events,
    parse_card,
)
from concert_calendar.sources import is_supported_event
from concert_calendar.venues import normalize_event_venue


FIXTURES = Path(__file__).with_name("fixtures") / "cafe_de_la_danse"


def fixture(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


class Response:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        return None


class CafeDeLaDanseTests(unittest.TestCase):
    def test_scraper_is_discovered(self):
        names = {module.SOURCE_NAME for module in discover_scrapers()}
        self.assertIn("Café de la Danse", names)

    def test_representative_card_fields_and_explicit_billing(self):
        soup = BeautifulSoup(fixture("programme.html"), "html.parser")
        event = parse_card(soup.select_one(".gt-event-style-4"))
        self.assertEqual("2027-09-10", event.date)
        self.assertEqual("20:00", event.start_time)
        self.assertEqual("RAMON PIPIN – Une folle envie de bisser", event.headliner)
        self.assertEqual("Café de la Danse", event.venue)
        self.assertEqual("Paris", event.city)
        self.assertEqual("75", event.department)
        self.assertEqual("Chanson", event.genre)
        self.assertEqual("tickets", event.ticket_status)
        self.assertEqual("https://tickets.example/ramon", event.ticket_url)
        self.assertEqual(
            "https://www.cafedeladanse.com/uploads/ramon.jpg",
            event.image_url,
        )
        self.assertIsNone(event.openers)

    def test_sold_out_and_placeholder_image(self):
        soup = BeautifulSoup(fixture("programme.html"), "html.parser")
        event = parse_card(soup.select(".gt-event-style-4")[1])
        self.assertEqual("THE EVERMINDS – special guest TSUJI", event.headliner)
        self.assertTrue(event.sold_out)
        self.assertEqual("sold_out", event.ticket_status)
        self.assertIsNone(event.image_url)
        self.assertIsNone(event.openers)

    def test_optional_fields_may_be_missing_and_detail_link_is_retained(self):
        soup = BeautifulSoup(fixture("programme.html"), "html.parser")
        event = parse_card(soup.select(".gt-event-style-4")[2])
        self.assertEqual("VALERIA CASTRO", event.headliner)
        self.assertIsNone(event.genre)
        self.assertIsNone(event.start_time)
        self.assertIsNone(event.ticket_status)
        self.assertEqual(
            "https://www.cafedeladanse.com/event/valeria-castro/",
            event.ticket_url,
        )

    def test_non_music_malformed_and_past_cards_are_rejected(self):
        cards = BeautifulSoup(
            fixture("programme.html"), "html.parser"
        ).select(".gt-event-style-4")
        self.assertIsNone(parse_card(cards[3]))
        self.assertIsNone(parse_card(cards[4]))
        self.assertIsNone(parse_card(cards[5]))

    def test_hyphenated_release_party_remains_a_supported_concert(self):
        self.assertEqual(
            "ELVETT « Release Party »",
            clean_headliner("ELVETT « Release-Party »"),
        )
        event = ConcertEvent(
            date="2027-02-26", headliner=clean_headliner(
                "ELVETT « Release-Party »"
            ),
            venue="Café de la Danse", city="Paris", department="75",
        )
        self.assertTrue(is_supported_event(event))

    def test_bounded_pagination_and_internal_duplicate_protection(self):
        responses = [Response(fixture("programme.html")), Response(fixture("page-2.html"))]
        with patch(
            "concert_calendar.scrapers.cafe_de_la_danse.requests.Session.get",
            side_effect=responses,
        ) as get:
            events = load_events()
        self.assertEqual(2, get.call_count)
        self.assertEqual(4, len(events))
        self.assertEqual(
            {"RAMON PIPIN – Une folle envie de bisser", "THE EVERMINDS – special guest TSUJI", "VALERIA CASTRO", "D.K. HARRELL"},
            {event.headliner for event in events},
        )

    def test_unique_cafe_event_survives_deduplication(self):
        event = ConcertEvent(
            date="2027-10-05", headliner="D.K. HARRELL",
            venue="Café de la Danse", city="Paris", department="75",
            source_names=["Café de la Danse"],
        )
        self.assertEqual([event], deduplicate_events([event]))

    def test_overlap_merges_and_preserves_richer_metadata(self):
        venue = ConcertEvent(
            date="2027-10-05", headliner="D.K. HARRELL",
            venue="Café de la Danse", city="Paris", department="75",
            genre="Jazz", ticket_url="https://venue.example/dk",
            image_url="https://venue.example/dk.jpg",
            image_source="Café de la Danse",
            source_names=["Café de la Danse"],
        )
        promoter = ConcertEvent(
            date="2027-10-05", headliner="D.K. Harrell",
            venue="Le Café de la Danse", city="Paris", department="75",
            openers=["Support Act"], promoters=["Example Promoter"],
            ticket_url="https://promoter.example/dk",
            image_url="https://promoter.example/dk.jpg",
            image_source="Example Promoter",
            source_names=["Example Promoter"],
        )
        merged = deduplicate_events([
            normalize_event_venue(venue), normalize_event_venue(promoter)
        ])
        self.assertEqual(1, len(merged))
        event = merged[0]
        self.assertEqual("Jazz", event.genre)
        self.assertEqual(["Support Act"], event.openers)
        self.assertEqual(["Example Promoter"], event.promoters)
        self.assertEqual("https://promoter.example/dk.jpg", event.image_url)
        self.assertEqual("https://venue.example/dk", event.ticket_url)
        self.assertEqual(
            {"Café de la Danse", "Example Promoter"}, set(event.source_names)
        )

    def test_overlap_with_dice_is_one_event(self):
        cafe = ConcertEvent(
            date="2027-12-03", headliner="MAZINGO", venue="Café de la Danse",
            city="Paris", department="75", source_names=["Café de la Danse"],
        )
        dice = ConcertEvent(
            date="2027-12-03", headliner="Mazingo", venue="Le Café de la Danse",
            city="Paris", department="75", source_names=["DICE"],
        )
        merged = deduplicate_events([
            normalize_event_venue(cafe), normalize_event_venue(dice)
        ])
        self.assertEqual(1, len(merged))
        self.assertEqual({"Café de la Danse", "DICE"}, set(merged[0].source_names))

    def test_reviewed_the_brooks_titles_collapse_for_verified_event(self):
        events = [
            ConcertEvent(
                date="2026-10-13", headliner="THE BROOKS",
                venue="Café de la Danse", city="Paris", department="75",
                source_names=["Café de la Danse"],
            ),
            ConcertEvent(
                date="2026-10-13",
                headliner="THE BROOKS au Café de la Danse",
                venue="Le Café de la Danse", city="Paris", department="75",
                source_names=["DICE"],
            ),
        ]
        merged = deduplicate_events([
            normalize_event_venue(event) for event in events
        ])
        self.assertEqual(1, len(merged))
        self.assertEqual("The Brooks", merged[0].headliner)
        self.assertEqual(
            {"Café de la Danse", "DICE"}, set(merged[0].source_names)
        )

    def test_reviewed_the_brooks_title_is_not_global(self):
        events = [
            ConcertEvent(
                date="2027-10-13", headliner="THE BROOKS",
                venue="Café de la Danse", city="Paris", department="75",
                source_names=["Café de la Danse"],
            ),
            ConcertEvent(
                date="2027-10-13",
                headliner="THE BROOKS au Café de la Danse",
                venue="Café de la Danse", city="Paris", department="75",
                source_names=["DICE"],
            ),
        ]
        self.assertEqual(2, len(deduplicate_events(events)))

    def test_reviewed_title_retains_first_seen_through_identity_alias(self):
        published_at = datetime(2026, 8, 31, 10, 23, 18, tzinfo=timezone.utc)
        previous_event = ConcertEvent(
            date="2026-10-13",
            headliner="THE BROOKS au Café de la Danse",
            venue="Café de la Danse", city="Paris", department="75",
        )
        previous = reconcile_state([previous_event], None, now=published_at)
        self.assertEqual("2026-08-28T10:23:17Z", previous_event.first_seen)
        previous_identity = canonical_event_identity(previous_event)

        current = deduplicate_events([
            ConcertEvent(
                date="2026-10-13", headliner="THE BROOKS",
                venue="Café de la Danse", city="Paris", department="75",
                source_names=["Café de la Danse"],
            ),
            ConcertEvent(
                date="2026-10-13",
                headliner="THE BROOKS au Café de la Danse",
                venue="Café de la Danse", city="Paris", department="75",
                source_names=["DICE"],
            ),
        ])[0]
        self.assertEqual("The Brooks", current.headliner)
        self.assertIn(
            "THE BROOKS au Café de la Danse", current.identity_aliases
        )

        now = published_at + timedelta(days=5)
        reconcile_state([current], previous, now=now)
        self.assertEqual("2026-08-28T10:23:17Z", current.first_seen)
        self.assertFalse(is_new(current.first_seen, now=now))
        self.assertNotEqual(previous_identity, canonical_event_identity(current))

    def test_unreviewed_event_does_not_gain_identity_aliases(self):
        event = ConcertEvent(
            date="2027-10-05", headliner="D.K. HARRELL",
            venue="Café de la Danse", city="Paris", department="75",
        )
        self.assertIsNone(deduplicate_events([event])[0].identity_aliases)

    def test_reviewed_identity_does_not_transfer_first_seen_to_other_date(self):
        now = datetime(2026, 9, 3, 10, 0, tzinfo=timezone.utc)
        old = ConcertEvent(
            date="2026-10-13",
            headliner="THE BROOKS au Café de la Danse",
            venue="Café de la Danse", city="Paris", department="75",
        )
        previous = reconcile_state([old], None, now=now - timedelta(days=6))
        unrelated = deduplicate_events([
            ConcertEvent(
                date="2027-10-13", headliner="THE BROOKS",
                venue="Café de la Danse", city="Paris", department="75",
            )
        ])[0]
        reconcile_state([unrelated], previous, now=now)
        self.assertEqual("2026-09-03T10:00:00Z", unrelated.first_seen)
        self.assertTrue(is_new(unrelated.first_seen, now=now))

    def test_cafe_image_priority_fills_only_when_appropriate(self):
        self.assertEqual(1, image_source_priority("Café de la Danse"))
        self.assertEqual(2, image_source_priority("Live Nation"))
        self.assertEqual(2, image_source_priority("Unrelated Official Source"))

        blank = ConcertEvent(
            date="2027-10-05", headliner="Artist",
            venue="Café de la Danse", city="Paris", department="75",
        )
        cafe = ConcertEvent(
            date="2027-10-05", headliner="Artist",
            venue="Café de la Danse", city="Paris", department="75",
            image_url="https://cafe.example/artist.jpg",
            image_source="Café de la Danse",
        )
        self.assertEqual(
            "https://cafe.example/artist.jpg", merge_events(blank, cafe).image_url
        )

        higher = ConcertEvent(
            date="2027-10-05", headliner="Artist",
            venue="Café de la Danse", city="Paris", department="75",
            image_url="https://promoter.example/artist.jpg",
            image_source="Live Nation",
        )
        merge_events(higher, cafe)
        self.assertEqual("https://promoter.example/artist.jpg", higher.image_url)
        self.assertEqual("Live Nation", higher.image_source)


if __name__ == "__main__":
    unittest.main()
