import unittest
from unittest.mock import Mock, patch

import requests

from concert_calendar.models import ConcertEvent
from concert_calendar.scrapers import gaite_lyrique


class GaiteLyriquePaginationTests(unittest.TestCase):
    def test_page_one_404_remains_a_source_failure(self):
        response = Mock()
        response.text = ""
        response.status_code = 404
        response.raise_for_status.side_effect = requests.HTTPError(
            "404 Client Error"
        )

        session = Mock()
        session.get.return_value = response

        with patch(
            "concert_calendar.scrapers.gaite_lyrique.requests.Session",
            return_value=session,
        ):
            with self.assertRaises(requests.HTTPError):
                gaite_lyrique.load_events()

        self.assertEqual(1, session.get.call_count)

    def test_terminal_page_seven_404_keeps_events_from_pages_one_through_six(self):
        responses = []

        for _ in range(6):
            response = Mock()
            response.text = '<article class="event"></article>'
            response.status_code = 200
            response.raise_for_status = Mock()
            responses.append(response)

        terminal = Mock()
        terminal.text = ""
        terminal.status_code = 404
        terminal.raise_for_status.side_effect = requests.HTTPError(
            "404 Client Error"
        )
        responses.append(terminal)

        session = Mock()
        session.get.side_effect = responses

        parsed_events = [
            ConcertEvent(
                date=f"2027-01-{day:02d}",
                headliner=f"Artist {day}",
                venue="La Gaîté Lyrique",
                city="Paris",
                department="75",
            )
            for day in range(1, 7)
        ]

        with (
            patch(
                "concert_calendar.scrapers.gaite_lyrique.requests.Session",
                return_value=session,
            ),
            patch(
                "concert_calendar.scrapers.gaite_lyrique.parse_card",
                side_effect=parsed_events,
            ),
        ):
            events = gaite_lyrique.load_events()

        self.assertEqual(6, len(events))
        self.assertEqual(
            [f"Artist {day}" for day in range(1, 7)],
            [event.headliner for event in events],
        )
        self.assertEqual(7, session.get.call_count)


if __name__ == "__main__":
    unittest.main()
