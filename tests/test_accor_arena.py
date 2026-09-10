import unittest

from concert_calendar.scrapers.accor_arena import parse_item


def accor_item(*, status_code="D"):
    return {
        "status": "published",
        "status_code": status_code,
        "room": {"full_name": "Accor Arena"},
        "sessions": [{"date": "2026-09-15 20:00:00"}],
        "translations": [{
            "language": "fr",
            "category": "Concert",
            "title": "Example Artist",
            "sub_category": "Pop",
            "url_event": "https://example.test/tickets",
            "description": "",
        }],
    }


class AccorArenaStatusTests(unittest.TestCase):

    def test_status_code_h_is_cancelled(self):
        events = parse_item(accor_item(status_code="H"))

        self.assertEqual(1, len(events))
        self.assertEqual("cancelled", events[0].ticket_status)
        self.assertFalse(events[0].sold_out)

    def test_normal_published_event_is_not_marked_cancelled(self):
        events = parse_item(accor_item(status_code="D"))

        self.assertEqual(1, len(events))
        self.assertIsNone(events[0].ticket_status)


if __name__ == "__main__":
    unittest.main()
