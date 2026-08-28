import unittest
from unittest.mock import Mock

from bs4 import BeautifulSoup

from concert_calendar.deduplication import _unresolved_candidates, deduplicate_events
from concert_calendar.scrapers.sunset_sunside import (
    parse_detail_payload,
    programme_items,
)
from concert_calendar.scrapers.trianon import parse_card


class TrianonScraperTests(unittest.TestCase):
    def test_billy_cobham_card_retains_official_detail_link_and_time(self):
        card = BeautifulSoup(
            """
            <div class="bloc_extrait evenement sell">
              <div class="date">dimanche 22 novembre 2026</div>
              <div class="titre">BILLY COBHAM</div>
              <a class="link" href="https://www.letrianon.fr/fr/programmation/billy-cobham/"></a>
              <img src="https://www.letrianon.fr/uploads/billy.jpg">
            </div>
            """,
            "html.parser",
        ).div
        response = Mock(text="<main>Dimanche 22 novembre 2026, à 19h00</main>")
        response.raise_for_status = Mock()
        session = Mock()
        session.get.return_value = response

        event = parse_card(card, session)

        self.assertEqual(event.date, "2026-11-22")
        self.assertEqual(event.headliner, "BILLY COBHAM")
        self.assertEqual(event.venue, "Le Trianon")
        self.assertEqual(event.start_time, "19:00")
        self.assertEqual(
            event.ticket_url,
            "https://www.letrianon.fr/fr/programmation/billy-cobham/",
        )

    def test_reviewed_hasan_ronny_title_preserves_explicit_co_headliner(self):
        card = BeautifulSoup(
            """
            <div class="bloc_extrait evenement sell">
              <div class="date">dimanche 11 octobre 2026</div>
              <div class="titre">HASAN HATES RONNY | RONNY HATES HASAN</div>
              <a class="link" href="https://www.letrianon.fr/fr/programmation/hasan/"></a>
            </div>
            """, "html.parser",
        ).div
        response = Mock(text="<main>à 17h00</main>")
        response.raise_for_status = Mock()
        session = Mock(); session.get.return_value = response
        event = parse_card(card, session)
        self.assertEqual(event.headliner, "Hasan Minhaj")
        self.assertEqual(event.co_headliners, ["Ronny Chieng"])
        self.assertEqual(event.event_title, "HASAN HATES RONNY | RONNY HATES HASAN")


class SunsetSunsideScraperTests(unittest.TestCase):
    def payload(self, sessions, *, room="Sunset", title="Example Trio"):
        return {
            "props": {"pageProps": {"entities": {
                "ticketing": {
                    "title": title,
                    "venue": {
                        "name": "Sunset Sunside", "seatingName": room,
                        "city": "Paris",
                    },
                    "ticketingCategory": {"name": "Jazz actuel"},
                    "mediaList": [{"path": "2026/8/example.jpeg"}],
                },
                "eventDates": {
                    "hydra:totalItems": len(sessions),
                    "hydra:member": sessions,
                },
            }}}
        }

    def test_programme_requires_complete_structured_listing(self):
        payload = {
            "props": {"pageProps": {"entities": {"ticketings": {
                "hydra:totalItems": 2,
                "hydra:member": [{"type": "dated_events", "slug": "one"}],
            }}}}
        }
        html = f'<script id="__NEXT_DATA__" type="application/json">{__import__("json").dumps(payload)}</script>'
        with self.assertRaises(RuntimeError):
            programme_items(html)

    def test_room_distinction_and_same_day_sets_are_preserved(self):
        sessions = [
            {"startDate": "2026-10-10T19:00:00+02:00", "status": "opened", "onSale": True},
            {"startDate": "2026-10-10T21:30:00+02:00", "status": "opened", "onSale": True},
        ]
        events = parse_detail_payload(
            self.payload(sessions, room="Sunset"),
            "https://billetterie.sunset-sunside.com/event/example",
            {"ticketingCategory": {"name": "Jazz actuel"}},
        )

        self.assertEqual({event.venue for event in events}, {"Sunset/Sunside — Sunset"})
        self.assertEqual({event.start_time for event in events}, {"19:00", "21:30"})
        self.assertEqual(len(deduplicate_events(events)), 2)
        self.assertTrue(all(" – " in event.headliner for event in events))
        self.assertEqual(_unresolved_candidates(events), [])
        self.assertEqual({event.genre for event in events}, {"Jazz actuel"})

    def test_sunside_room_is_not_flattened(self):
        events = parse_detail_payload(
            self.payload([
                {"startDate": "2026-10-11T21:30:00+02:00", "status": "opened", "onSale": True},
            ], room="Sunside"),
            "https://billetterie.sunset-sunside.com/event/example",
        )
        self.assertEqual(events[0].venue, "Sunset/Sunside — Sunside")

    def test_entree_libre_category_is_explicitly_free(self):
        payload = self.payload([
            {"startDate": "2026-10-11T21:30:00+02:00", "status": "opened", "onSale": True},
        ])
        payload["props"]["pageProps"]["entities"]["ticketing"]["ticketingCategory"] = {
            "name": "Jazz actuel (Entrée libre)",
        }
        events = parse_detail_payload(payload, "https://example.test/event")
        self.assertEqual(events[0].ticket_status, "free")

    def test_incomplete_detail_pagination_fails_loudly(self):
        payload = self.payload([
            {"startDate": "2026-10-11T21:30:00+02:00", "status": "opened", "onSale": True},
        ])
        payload["props"]["pageProps"]["entities"]["eventDates"]["hydra:totalItems"] = 2
        with self.assertRaises(RuntimeError):
            parse_detail_payload(payload, "https://example.test/event")


if __name__ == "__main__":
    unittest.main()
