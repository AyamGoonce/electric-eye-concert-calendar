"""Verified official multi-act billing against live programme variants."""
import unittest

from concert_calendar.artist_billings import resolve_artist_billings
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import event_to_data


def event(title, date, venue, **kwargs):
    return ConcertEvent(
        date=date, headliner=title, venue=venue,
        city="Paris", department="75", source_names=[venue], **kwargs
    )


class CurrentVerifiedMultiActRegressions(unittest.TestCase):
    def test_elysee_three_distinct_acts(self):
        item = event("The Halo Effect + Lacuna Coil + Omnium Gatherum",
                     "2027-02-27", "Élysée Montmartre")
        resolve_artist_billings([item])
        self.assertEqual("The Halo Effect", item.headliner)
        self.assertEqual(["Lacuna Coil", "Omnium Gatherum"], item.co_headliners)
        self.assertEqual(["Lacuna Coil", "Omnium Gatherum"], event_to_data(item)["ch"])

    def test_olympia_three_distinct_acts(self):
        item = event("Anthrax + Kerry King & Sacred Reich",
                     "2027-03-19", "L'Olympia Bruno Coquatrix")
        resolve_artist_billings([item])
        self.assertEqual("Anthrax", item.headliner)
        self.assertEqual(["Kerry King", "Sacred Reich"], item.co_headliners)

    def test_glazart_review_catches_missing_artist_on_existing_structured_bill(self):
        item = event("Sunami", "2026-11-28", "Glazart",
                     event_title="Sunami + Missing Link + Extinguish",
                     performers=["Sunami", "Missing Link", "Extinguish"],
                     co_headliners=["Missing Link", "Extinguish"])
        resolve_artist_billings([item])
        self.assertEqual("Sunami", item.headliner)
        self.assertEqual(["Desolated", "Missing Link", "Extinguish"],
                         item.co_headliners)
        self.assertEqual(4, len(item.performers))

    def test_scoped_bill_does_not_apply_to_other_event_dates(self):
        item = event("Anthrax + Kerry King & Sacred Reich",
                     "2027-03-20", "L'Olympia Bruno Coquatrix")
        resolve_artist_billings([item], identity_catalog={})
        self.assertEqual("Anthrax + Kerry King & Sacred Reich", item.headliner)
        self.assertIsNone(item.co_headliners)


if __name__ == "__main__":
    unittest.main()
