import unittest
from unittest.mock import Mock, patch

import requests

from concert_calendar.content_index import fetch_entries


def response(entries, total):
    result = Mock()
    result.json.return_value = {"feed": {
        "openSearch$totalResults": {"$t": str(total)}, "entry": entries,
    }}
    return result


class ContentFeedRetryTests(unittest.TestCase):
    @patch("concert_calendar.content_index.time.sleep")
    def test_retries_current_page_without_refetching_completed_page(self, sleep):
        session = Mock()
        session.get.side_effect = [response([{"id": 1}], 2),
                                   requests.ReadTimeout("temporary"),
                                   requests.ConnectionError("temporary"),
                                   response([{"id": 2}], 2)]
        self.assertEqual([{"id": 1}, {"id": 2}], fetch_entries(session))
        self.assertEqual([1, 2, 2, 2], [c.kwargs["params"]["start-index"] for c in session.get.call_args_list])
        self.assertTrue(all(c.kwargs["timeout"] == 30 for c in session.get.call_args_list))
        self.assertEqual([((2,), {}), ((2,), {})], sleep.call_args_list)

    @patch("concert_calendar.content_index.time.sleep")
    def test_exhausted_timeout_raises_original_failure(self, sleep):
        session = Mock()
        error = requests.ReadTimeout("still unavailable")
        session.get.side_effect = error
        with self.assertRaises(requests.ReadTimeout) as caught:
            fetch_entries(session)
        self.assertIs(error, caught.exception)
        self.assertEqual(3, session.get.call_count)
        self.assertEqual(2, sleep.call_count)

    @patch("concert_calendar.content_index.time.sleep")
    def test_http_and_invalid_content_fail_without_retry(self, sleep):
        for failure in (requests.HTTPError("404"), ValueError("invalid JSON")):
            session = Mock()
            result = response([], 1)
            if isinstance(failure, requests.HTTPError):
                result.raise_for_status.side_effect = failure
            else:
                result.json.side_effect = failure
            session.get.return_value = result
            with self.assertRaises(type(failure)):
                fetch_entries(session)
            self.assertEqual(1, session.get.call_count)
        sleep.assert_not_called()

    @patch("concert_calendar.content_index.time.sleep")
    def test_incomplete_content_still_fails(self, sleep):
        session = Mock()
        session.get.side_effect = [response([{"id": 1}], 2), response([], 2)]
        with self.assertRaisesRegex(RuntimeError, "Incomplete Electric Eye feed"):
            fetch_entries(session)
        sleep.assert_not_called()
