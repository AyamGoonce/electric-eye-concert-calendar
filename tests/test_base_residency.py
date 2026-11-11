"""Counted residencies retain individual official-venue performance dates."""
import unittest

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent
from concert_calendar.scrapers.base_productions import detail_residency_title

ODEZENNE_DATES = [
    "2027-05-11", "2027-05-12", "2027-05-13", "2027-05-14",
    "2027-05-15", "2027-05-16", "2027-05-18", "2027-05-19",
    "2027-05-20", "2027-05-21", "2027-05-22", "2027-05-23",
    "2027-05-25", "2027-05-26", "2027-05-27", "2027-05-28",
    "2027-05-29", "2027-05-30", "2027-06-01", "2027-06-02",
    "2027-06-03", "2027-06-04", "2027-06-05", "2027-06-06",
]


class BaseResidencyTests(unittest.TestCase):
    def test_promoter_artist_heading_separates_counted_residency(self):
        detail = "<h1>ODEZENNE</h1><p>24 concerts à la Maroquinerie.</p>"
        self.assertEqual(
            ("ODEZENNE", "24 MAROQUINERIES"),
            detail_residency_title(detail, "ODEZENNE – 24 MAROQUINERIES"),
        )

    def test_promotional_title_without_independent_artist_heading_stays_opaque(self):
        self.assertIsNone(detail_residency_title(
            "<h1>Other Artist</h1>", "ODEZENNE – 24 MAROQUINERIES",
        ))
        self.assertIsNone(detail_residency_title(
            "<h1>FLORENCE + THE MACHINE</h1>", "FLORENCE + THE MACHINE",
        ))

    def test_base_single_card_and_24_venue_dates_remain_24_events(self):
        events = [
            ConcertEvent(
                date=day, headliner="ODEZENNE", venue="La Maroquinerie",
                city="Paris", department="75",
                source_names=["La Maroquinerie"],
                ticket_url=f"https://www.lamaroquinerie.fr/fr/agenda/view/{i+2300}/odezenne/",
            )
            for i, day in enumerate(ODEZENNE_DATES)
        ]
        events.append(ConcertEvent(
            date="2027-05-11", headliner="ODEZENNE",
            raw_title="ODEZENNE – 24 MAROQUINERIES",
            event_title="24 MAROQUINERIES",
            venue="La Maroquinerie", city="Paris", department="75",
            source_names=["Base Productions"],
            ticket_url="https://www.base-productions.com/concerts/5923/",
        ))
        result = deduplicate_events(events)
        matching = [event for event in result if event.venue == "La Maroquinerie"]
        self.assertEqual(24, len(matching))
        self.assertEqual(ODEZENNE_DATES, sorted(x.date for x in matching))
        self.assertTrue(all(x.headliner.casefold() == "odezenne" for x in matching))
        self.assertTrue(all(not x.co_headliners for x in matching))


if __name__ == "__main__":
    unittest.main()
