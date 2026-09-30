import unittest
from unittest.mock import patch

from concert_calendar.scrapers import livenation


def document(document_id):
    return {
        "id": document_id,
        "name": f"Artist {document_id}",
        "eventDate": "2027-12-03T00:00:00Z",
        "venue": {"name": "Example Venue", "city": "Paris"},
        "url": f"/event/artist-{document_id}",
    }


class LiveNationInventoryTests(unittest.TestCase):
    def test_transient_incomplete_inventory_selects_fuller_snapshot(self):
        missing = [document(value) for value in range(1, 393)]
        complete = [document(value) for value in range(1, 394)]
        complete.append(document(1652222))
        # A repeated page-boundary document must not inflate completeness.
        complete.append(document(393))
        third = [document(value) for value in range(1, 394)]

        with patch.object(
            livenation,
            "fetch_inventory_snapshot",
            side_effect=[missing, complete, third],
        ) as fetch:
            events = livenation.load_events()

        self.assertEqual(394, len(events))
        self.assertTrue(any(event.headliner == "Artist 1652222" for event in events))
        self.assertEqual(3, fetch.call_count)
        self.assertEqual(
            {
                "kind": "inventory_stability",
                "snapshot_disagreement": True,
                "snapshots_fetched": 3,
                "snapshot_distinct_counts": [392, 394, 393],
                "snapshot_unidentified_counts": [0, 0, 0],
                "selected_snapshot": 2,
                "selected_distinct_count": 394,
            },
            livenation.get_diagnostics()[0],
        )

    def test_stable_inventory_uses_only_two_snapshots(self):
        first = [document(1), document(2)]
        second = [document(2), document(1)]

        with patch.object(
            livenation,
            "fetch_inventory_snapshot",
            side_effect=[first, second],
        ) as fetch:
            events = livenation.load_events()

        self.assertEqual(2, len(events))
        self.assertEqual(2, fetch.call_count)
        diagnostic = livenation.get_diagnostics()[0]
        self.assertFalse(diagnostic["snapshot_disagreement"])
        self.assertEqual([2, 2], diagnostic["snapshot_distinct_counts"])
        self.assertEqual(2, diagnostic["selected_snapshot"])

    def test_three_differing_snapshots_select_most_complete_deterministically(self):
        snapshots = [
            [document(1), document(2)],
            [document(1), document(2), document(3), document(3)],
            [document(1), document(4), document(5)],
        ]

        with patch.object(
            livenation,
            "fetch_inventory_snapshot",
            side_effect=snapshots,
        ) as fetch:
            events = livenation.load_events()

        self.assertEqual(
            {"Artist 1", "Artist 2", "Artist 3"},
            {event.headliner for event in events},
        )
        self.assertEqual(3, fetch.call_count)
        diagnostic = livenation.get_diagnostics()[0]
        self.assertEqual([2, 3, 3], diagnostic["snapshot_distinct_counts"])
        self.assertEqual(2, diagnostic["selected_snapshot"])


if __name__ == "__main__":
    unittest.main()
