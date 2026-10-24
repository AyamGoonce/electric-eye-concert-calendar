import unittest
from unittest.mock import patch, Mock
from concert_calendar.scrapers import file7

class File7EmptyInventoryTests(unittest.TestCase):
    def response(self, html):
        result = Mock()
        result.text = html
        return result

    def test_empty_http_200_must_fail(self):
        session = Mock()
        session.get.return_value = self.response('<html><title>Maintenance</title></html>')
        with patch.object(file7.requests, 'Session', return_value=session):
            with self.assertRaisesRegex(RuntimeError, 'no parsable concert listings'):
                file7.load_events()

    def test_unrecognized_cards_must_fail(self):
        session = Mock()
        session.get.return_value = self.response('<div class="zone_grille"><div class="bloc_show">Changed format</div></div>')
        with patch.object(file7.requests, 'Session', return_value=session):
            with self.assertRaisesRegex(RuntimeError, 'no parsable concert listings'):
                file7.load_events()

    def test_valid_card_still_produces_one_event(self):
        html = ('<div class="zone_grille"><div class="bloc_show">'
                '<a href="https://file7.com/fr/programme/13-11-2026-20h00-revnoir.html">Tickets</a>'
                '<div class="artistes">REVNOIR</div></div></div>')
        session = Mock()
        session.get.return_value = self.response(html)
        with patch.object(file7.requests, 'Session', return_value=session):
            events = file7.load_events()
        self.assertEqual(1, len(events))
        self.assertEqual('2026-11-13', events[0].date)
        self.assertEqual('REVNOIR', events[0].headliner)

if __name__ == '__main__':
    unittest.main()
