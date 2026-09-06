import unittest
from unittest.mock import Mock, patch

from concert_calendar.scrapers import olympia


class OlympiaDiagnosticsTests(unittest.TestCase):
    def test_raw_item_diagnostics_do_not_change_parsed_events(self):
        item = {
            "ID": 123,
            "post_title": "Ronnie Wood",
            "permalink": "https://example.test/ronnie-wood",
            "terms": {"genre": [{"name": "Rock"}]},
            "meta": {
                "begin_date_ymd": "2026-09-05",
                "end_date_ymd": "2026-09-06",
                "exclude_dates": "",
                "show_statuses": ["open", "open"],
                "infos_text_status": "",
                "artistes_premiere_partie": "Imelda May",
            },
        }
        response = Mock()
        response.json.return_value = {"items": [item], "nb_pages": 1}
        response.raise_for_status.return_value = None
        session = Mock()
        session.get.return_value = response
        with patch.object(olympia.requests, "Session", return_value=session):
            events = olympia.load_events()

        self.assertEqual(["2026-09-05", "2026-09-06"], [event.date for event in events])
        diagnostic = olympia.get_diagnostics()[0]
        self.assertEqual("Ronnie Wood", diagnostic["raw_event_title"])
        self.assertEqual("2026-09-05", diagnostic["raw_begin_date"])
        self.assertEqual("2026-09-06", diagnostic["raw_end_date"])
        self.assertEqual(["2026-09-05", "2026-09-06"], diagnostic["parsed_dates"])
        self.assertEqual("https://example.test/ronnie-wood", diagnostic["source_url"])


if __name__ == "__main__":
    unittest.main()
