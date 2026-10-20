import unittest
from concert_calendar.models import ConcertEvent
from concert_calendar.historical_billing import restore_published_billing

URL = "https://tickets.example/events/123"
def make(title, *, date="2027-03-11", venue="Petit Bain", url=URL):
    return ConcertEvent(date=date, headliner=title, venue=venue, city="Paris",
                        department="75", ticket_url=url)

def published():
    return [{"d":"2027-03-11", "v":"Petit Bain", "t":URL,
             "h":"King Buffalo", "ch":["Spirit Mother"], "o":[]}]

class HistoricalBillingTest(unittest.TestCase):
    def test_reuses_verified_two_artist_bill(self):
        e = make("King Buffalo + Spirit Mother")
        report = restore_published_billing([e], published())
        self.assertEqual("King Buffalo", e.headliner)
        self.assertEqual(["Spirit Mother"], e.co_headliners)
        self.assertEqual(["King Buffalo", "Spirit Mother"], e.performers)
        self.assertEqual(1, len(report["restored"]))

    def test_cannot_invent_removed_artist(self):
        e = make("King Buffalo")
        report = restore_published_billing([e], published())
        self.assertEqual("King Buffalo", e.headliner)
        self.assertFalse(e.co_headliners)
        self.assertEqual(1, len(report["conflicts"]))

    def test_never_overrides_structured_new_roster(self):
        e = make("King Buffalo + Spirit Mother")
        e.performers = ["King Buffalo", "New Band"]
        report = restore_published_billing([e], published())
        self.assertEqual(["King Buffalo", "New Band"], e.performers)
        self.assertEqual(1, len(report["conflicts"]))

    def test_requires_exact_venue_date_and_ticket(self):
        for changes in ({"date":"2027-03-12"}, {"venue":"Le Trabendo"},
                        {"url":"https://tickets.example/events/999"}):
            e = make("King Buffalo + Spirit Mother", **changes)
            restore_published_billing([e], published())
            self.assertEqual("King Buffalo + Spirit Mother", e.headliner)

    def test_cannot_use_shared_ticket_for_multiple_events(self):
        a = make("King Buffalo + Spirit Mother")
        b = make("King Buffalo + Spirit Mother")
        report = restore_published_billing([a,b], published())
        self.assertFalse(report["restored"])
        self.assertEqual(1, len(report["ambiguous"]))

    def test_no_split_for_legitimate_plus_named_act(self):
        e = make("Mike + The Mechanics")
        restore_published_billing([e], published())
        self.assertEqual("Mike + The Mechanics", e.headliner)

    def test_new_source_opener_is_not_overwritten(self):
        e = make("King Buffalo + Spirit Mother")
        e.openers = ["Other Support"]
        restore_published_billing([e], published())
        self.assertEqual(["Other Support"], e.openers)

if __name__ == "__main__":
    unittest.main()
