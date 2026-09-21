import unittest

from bs4 import BeautifulSoup

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent
from concert_calendar.scrapers.supersonic import parse_event_row


class BillingExtractionRegressionTests(unittest.TestCase):

    def test_supersonic_bullet_bill_becomes_structured_performers(self):
        soup = BeautifulSoup("""
        <div class="tribe-events-calendar-list__event-row">
          <a class="tribe-events-calendar-list__event-title-link"
             href="/event/king-phantom/">
            King Phantom • Les Caballeros • KIJE
          </a>
          <time class="tribe-events-calendar-list__event-datetime"
                datetime="2026-10-01"></time>
          <span class="tribe-events-calendar-list__event-venue-title">
            Supersonic
          </span>
        </div>
        """, "html.parser")

        event = parse_event_row(
            soup.select_one(".tribe-events-calendar-list__event-row"),
            "https://supersonic-club.fr/events/",
        )

        self.assertEqual(
            ["King Phantom", "Les Caballeros", "KIJE"],
            event.performers,
        )

        result = deduplicate_events([event])

        self.assertEqual(1, len(result))
        self.assertEqual("King Phantom", result[0].headliner)
        self.assertEqual(
            ["Les Caballeros", "KIJE"],
            result[0].co_headliners,
        )

    def test_unnamed_very_special_guest_is_not_part_of_artist_identity(self):
        original = "Emilie Calmé with very special guest"
        event = ConcertEvent(
            date="2026-10-01",
            headliner=original,
            raw_title=original,
            venue="Sunset/Sunside — Sunside",
            city="Paris",
            department="75",
            source_names=["Sunset/Sunside"],
        )

        result = deduplicate_events([event])

        self.assertEqual(1, len(result))
        self.assertEqual("Emilie Calmé", result[0].headliner)
        self.assertEqual(original, result[0].event_title)


class BillingExtractionSafetyTests(unittest.TestCase):

    def test_supersonic_does_not_split_other_title_punctuation(self):
        title = "The Devil And The Almighty Blues"

        soup = BeautifulSoup(f"""
        <div class="tribe-events-calendar-list__event-row">
          <a class="tribe-events-calendar-list__event-title-link"
             href="/event/devil/">
            {title}
          </a>
          <time class="tribe-events-calendar-list__event-datetime"
                datetime="2026-10-01"></time>
          <span class="tribe-events-calendar-list__event-venue-title">
            Supersonic
          </span>
        </div>
        """, "html.parser")

        event = parse_event_row(
            soup.select_one(".tribe-events-calendar-list__event-row"),
            "https://supersonic-club.fr/events/",
        )

        self.assertEqual(title, event.headliner)
        self.assertIsNone(event.performers)

    def test_named_very_special_guest_is_not_stripped(self):
        title = "Emilie Calmé with very special guest Brad Mehldau"

        event = ConcertEvent(
            date="2026-10-01",
            headliner=title,
            raw_title=title,
            venue="Sunset/Sunside — Sunside",
            city="Paris",
            department="75",
            source_names=["Sunset/Sunside"],
        )

        result = deduplicate_events([event])

        self.assertEqual(1, len(result))
        self.assertEqual(title, result[0].headliner)

    def test_multi_plus_extension_is_not_promoted_as_one_artist(self):
        short = ConcertEvent(
            date="2026-10-01",
            headliner="The Devil And The Almighty Blues",
            venue="Backstage By The Mill",
            city="Paris",
            department="75",
            source_names=["Backstage By The Mill"],
        )
        rich = ConcertEvent(
            date="2026-10-01",
            headliner=(
                "The Devil And The Almighty Blues "
                "+ Skyjoggers + Third Artist"
            ),
            venue="Backstage By The Mill",
            city="Paris",
            department="75",
            source_names=["Garmonbozia"],
        )

        result = deduplicate_events([short, rich])

        self.assertEqual(1, len(result))
        self.assertEqual(
            "The Devil And The Almighty Blues + Skyjoggers + Third Artist",
            result[0].headliner,
        )
        self.assertIsNone(result[0].co_headliners)

if __name__ == "__main__":
    unittest.main()
