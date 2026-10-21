import unittest
from datetime import datetime, timezone

from concert_calendar.event_state import (
    _published_continuity_keys, _published_continuity_score,
    canonical_event_identity, reconcile_state,
)
from concert_calendar.models import ConcertEvent


TICKET = "https://web.digitick.com/evil-invaders-exhorder-heathen-concert-dark-metal-css5-garmonbozia-pg51-ei1131957.html"


def event(day, title="Evil Invaders", ticket=TICKET):
    return ConcertEvent(
        date=day, headliner=title, venue="Petit Bain", city="Paris",
        department="75", ticket_url=ticket, start_time="18:00",
        co_headliners=["Exhorder", "Heathen"] if title == "Evil Invaders" else None,
        openers=["Warfield"] if title == "Evil Invaders" else None,
    )


def old_public():
    return {"d": "2027-03-21", "h": "Evil Invaders",
            "ch": ["Exhorder", "Heathen"], "o": ["Warfield"],
            "v": "Petit Bain", "c": "Paris", "st": "18:00",
            "t": TICKET, "i": "7bd7c107f37ed43b"}


class ConcertRescheduleContinuity(unittest.TestCase):
    def test_exact_ticket_bill_and_venue_accept_earlier_date(self):
        self.assertIsNotNone(_published_continuity_score(event("2027-03-01"), old_public()))

    def test_changed_bill_or_venue_or_ticket_rejected(self):
        for item in (
            event("2027-03-01", "Different Artist"),
            event("2027-03-01", ticket="https://tickets.example/other"),
        ):
            self.assertIsNone(_published_continuity_score(item, old_public()))
        item = event("2027-03-01")
        item.venue = "Le Trianon"
        self.assertIsNone(_published_continuity_score(item, old_public()))

    def test_shared_ticket_cannot_move_another_performance(self):
        old = old_public()
        key = canonical_event_identity(event("2027-03-21"))
        previous = {key: {"first_seen": "2026-09-07T16:24:12Z",
                          "last_seen": "2026-10-20T10:00:00Z",
                          "public_id": old["i"]}}
        first = event("2027-03-01")
        second = event("2027-03-02")
        self.assertEqual({}, _published_continuity_keys([first, second], previous, [old]))

    def test_unique_reschedule_retains_public_id_and_first_seen(self):
        old = old_public()
        previous_event = event("2027-03-21")
        key = canonical_event_identity(previous_event)
        first_seen = "2026-09-07T16:24:12Z"
        previous = {key: {"date": "2027-03-21", "first_seen": first_seen,
                          "last_seen": "2026-10-20T10:00:00Z",
                          "public_id": old["i"]}}
        current = event("2027-03-01")
        matches = _published_continuity_keys([current], previous, [old])
        self.assertEqual(key, matches[id(current)])


if __name__ == "__main__":
    unittest.main()
