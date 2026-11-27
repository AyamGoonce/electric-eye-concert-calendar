"""Multi-page acquisition and explicit performer billing regressions."""
import unittest
from unittest import mock

from concert_calendar.artist_billings import resolve_artist_billings
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import event_to_data
from concert_calendar.scrapers import veryshow


def post(identity, title, date):
    return {
        "id": identity, "title": title, "artists_titles": [title],
        "date": date, "city": "PARIS (75)",
        "concert_hall": "La Cigale",
        "link": f"https://verygroup.fr/concerts/{identity}",
    }


class VeryShowPaginationRegressions(unittest.TestCase):
    def test_all_page_snapshots_contribute_events_without_duplicate_ids(self):
        snapshots = [
            {"data": {"currentPage": 1, "totalPages": 3, "posts": [
                post(1, "First Artist", "04/03/2027")
            ]}},
            {"data": {"currentPage": 2, "totalPages": 3, "posts": [
                post(2, "Middle Artist", "05/03/2027")
            ]}},
            {"data": {"currentPage": 3, "totalPages": 3, "posts": [
                post(2, "Middle Artist", "05/03/2027"),
                post(3, "Last Artist", "06/03/2027")
            ]}},
        ]
        with mock.patch.object(veryshow, "get_initial_state", return_value=(
            "csrf", "first", snapshots[0]
        )), mock.patch.object(
            veryshow, "go_to_next_page",
            side_effect=[("second", snapshots[1]), ("third", snapshots[2])],
        ) as next_page:
            result = veryshow.load_events()
        self.assertEqual(["First Artist", "Middle Artist", "Last Artist"],
                         [item.headliner for item in result])
        self.assertEqual(2, next_page.call_count)


class StructuredBillingDisplayRegressions(unittest.TestCase):
    @staticmethod
    def event(title, artists, *, openers=None):
        return ConcertEvent(
            date="2027-03-04", headliner=title,
            venue="La Cigale", city="Paris", department="75",
            source_names=["Source A"], performers=artists,
            openers=openers,
        )

    def test_three_performers_are_displayed_as_three_artists(self):
        item = self.event("First Artist + Second Artist + Third Artist",
                          ["First Artist", "Second Artist", "Third Artist"])
        resolve_artist_billings([item], identity_catalog={})
        self.assertEqual("First Artist", item.headliner)
        self.assertEqual(["Second Artist", "Third Artist"], item.co_headliners)
        self.assertEqual("First Artist + Second Artist + Third Artist",
                         item.raw_title)
        self.assertEqual(["Second Artist", "Third Artist"],
                         event_to_data(item)["ch"])

    def test_openers_remain_openers(self):
        item = self.event("First Artist x Second Artist avec Third Artist",
                          ["First Artist", "Second Artist", "Third Artist"],
                          openers=["Third Artist"])
        resolve_artist_billings([item], identity_catalog={})
        self.assertEqual("First Artist", item.headliner)
        self.assertEqual(["Second Artist"], item.co_headliners)
        self.assertEqual(["Third Artist"], item.openers)

    def test_unmatched_roster_never_overwrites_contextual_show_title(self):
        item = self.event("A Tribute to Rock",
                          ["First Artist", "Second Artist"])
        resolve_artist_billings([item], identity_catalog={})
        self.assertEqual("A Tribute to Rock", item.headliner)
        self.assertIsNone(item.co_headliners)

    def test_complete_collaboration_name_is_protected(self):
        item = self.event("Mike + The Mechanics", ["Mike", "The Mechanics"])
        resolve_artist_billings([item], identity_catalog={})
        self.assertEqual("Mike + The Mechanics", item.headliner)
        self.assertIsNone(item.co_headliners)


if __name__ == "__main__":
    unittest.main()
