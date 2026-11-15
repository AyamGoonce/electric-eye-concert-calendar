import unittest
from unittest.mock import Mock, patch

from concert_calendar.scrapers import olympia


class OlympiaDiagnosticsTests(unittest.TestCase):
    def test_official_anniversary_tour_is_programme_not_band_name(self):
        from concert_calendar.deduplication import deduplicate_events
        from concert_calendar.production_export import event_to_data
        item = {
            "ID": 5261,
            "post_title": "ACCEPT 50th Anniversary Tour 2026",
            "permalink": "https://www.olympiahall.com/agenda/accept/",
            "terms": {"genre": [{"name": "Metal / Hard Rock"}]},
            "meta": {
                "begin_date_ymd": "2026-11-22",
                "end_date_ymd": "2026-11-22",
                "show_statuses": ["open"],
                "infos_text_status": "",
                "artistes_premiere_partie": "DYNAZTY + ENFORCER",
            },
        }
        parsed = olympia.parse_item(item)
        self.assertEqual(1, len(parsed))
        self.assertEqual("ACCEPT", parsed[0].headliner)
        self.assertEqual("50th Anniversary Tour 2026", parsed[0].event_title)
        self.assertEqual(["DYNAZTY", "ENFORCER"], parsed[0].openers)
        self.assertEqual(item["post_title"], parsed[0].raw_title)
        self.assertIn(item["post_title"], parsed[0].identity_aliases)
        reconciled = deduplicate_events(parsed)
        self.assertEqual(1, len(reconciled))
        exported = event_to_data(reconciled[0])
        self.assertEqual("Accept", exported["h"])
        self.assertEqual("50th Anniversary Tour 2026", exported["et"])
        self.assertEqual(["Dynazty", "Enforcer"], exported["o"])

    def test_late_source_merge_cannot_restore_full_tour_title_as_artist(self):
        from concert_calendar.models import ConcertEvent
        from concert_calendar.deduplication import deduplicate_events
        from concert_calendar.production_export import event_to_data
        row = ConcertEvent(
            "2026-11-22", "ACCEPT 50th Anniversary Tour 2026",
            "L'Olympia Bruno Coquatrix", "Paris", "75",
            raw_title="ACCEPT 50th Anniversary Tour 2026",
            openers=["DYNAZTY", "ENFORCER"],
            performers=["ACCEPT 50th Anniversary Tour 2026"],
            ticket_url="https://www.olympiahall.com/agenda/accept/",
            source_names=["L’Olympia Bruno Coquatrix"],
        )
        public = event_to_data(deduplicate_events([row])[0])
        self.assertEqual("Accept", public["h"])
        self.assertEqual("50th Anniversary Tour 2026", public["et"])
        self.assertEqual(["Dynazty", "Enforcer"], public["o"])

        unrelated = ConcertEvent(
            "2026-11-22", "ACCEPT 50th Anniversary Tour 2026",
            "L'Olympia Bruno Coquatrix", "Paris", "75",
            ticket_url="https://www.olympiahall.com/agenda/another-artist/",
        )
        self.assertNotEqual(
            "Accept", event_to_data(deduplicate_events([unrelated])[0])["h"]
        )

    def test_anniversary_words_do_not_split_without_venue_artist_evidence(self):
        cases = (
            ("Accept 50th Anniversary Tour 2026",
             "https://www.olympiahall.com/agenda/another-artist/"),
            ("The 50th Anniversary Tour",
             "https://www.olympiahall.com/agenda/the-50th-anniversary-tour/"),
            ("Fifty Years of Metal",
             "https://www.olympiahall.com/agenda/fifty-years-of-metal/"),
        )
        for title, url in cases:
            with self.subTest(title=title):
                self.assertEqual(
                    (title, None), olympia.separate_official_tour_suffix(title, url),
                )

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
