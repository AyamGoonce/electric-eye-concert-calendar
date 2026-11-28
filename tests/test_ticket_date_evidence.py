"""Regression tests for conservative date verification by linked ticket sellers."""
import unittest
from unittest.mock import Mock, patch

from concert_calendar.scrapers.supersonic import (
    parse_event_row, verify_linked_ticket_date,
)
from concert_calendar.ticket_date_evidence import confirmed_ticket_date
from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent
from bs4 import BeautifulSoup

BILL = "The Sha La Lee’s + The Unbelieverz"
SELLER = """
<html><body>
<h1>The Sha La Lee’s + The Unbelieverz</h1>
<div>Sat Jan 30, 2027 from 08:00 PM to 11:00 PM</div>
<p>Supersonic Records, Rue Biscornet, Paris, France</p>
<pre>2027-01-30 20:00:00 Europe/Paris</pre>
</body></html>
"""
DETAIL = """
<html><body><a href="https://www.billetweb.fr/the-sha-la-lee-s-the-unbelieverz">
Réserver</a></body></html>
"""


class SellerEvidenceTests(unittest.TestCase):
    def test_seller_corrects_contradictory_venue_date(self):
        self.assertEqual(
            confirmed_ticket_date(SELLER, BILL, "Supersonic Records"),
            "2027-01-30",
        )

    def test_title_and_venue_must_both_agree(self):
        self.assertIsNone(
            confirmed_ticket_date(SELLER, "Other Band", "Supersonic Records")
        )
        self.assertIsNone(
            confirmed_ticket_date(SELLER, BILL, "Bataclan")
        )

    def test_two_seller_dates_must_not_be_guessed(self):
        html = SELLER.replace(
            "</body>", "<p>Sun Jan 31, 2027 at 20:00</p></body>"
        )
        self.assertIsNone(
            confirmed_ticket_date(html, BILL, "Supersonic Records")
        )

    def test_unrelated_bare_calendar_day_is_not_sufficient(self):
        html = """
        <html><body><h1>The Sha La Lee's + The Unbelieverz</h1>
        <p>Supersonic Records</p><p>2027-01-30</p></body></html>
        """
        self.assertIsNone(
            confirmed_ticket_date(html, BILL, "Supersonic Records")
        )

    def test_ticket_must_be_linked_from_venue_event(self):
        replies = [
            Mock(text=DETAIL, raise_for_status=Mock()),
            Mock(text=SELLER, raise_for_status=Mock()),
        ]
        with patch(
            "concert_calendar.scrapers.supersonic.requests.get",
            side_effect=replies,
        ) as get:
            self.assertEqual(
                verify_linked_ticket_date(
                    "https://supersonic-club.fr/evenement/sha-la-lees/",
                    BILL,
                ),
                "2027-01-30",
            )
            self.assertEqual(get.call_count, 2)

    def test_mismatched_ticket_or_ambiguous_link_preserves_date(self):
        for detail in (
            "<a href='https://www.billetweb.fr/other'>Réserver</a>"
            "<a href='https://www.billetweb.fr/another'>Réserver</a>",
            "<a href='https://www.example.com/other'>Réserver</a>",
        ):
            with self.subTest(detail=detail), patch(
                "concert_calendar.scrapers.supersonic.requests.get",
                return_value=Mock(text=detail, raise_for_status=Mock()),
            ) as get:
                self.assertIsNone(
                    verify_linked_ticket_date(
                        "https://supersonic-club.fr/evenement/foo/", BILL
                    )
                )
                self.assertEqual(get.call_count, 1)

    def test_same_date_structured_venue_and_full_bill_are_one_show(self):
        venue = ConcertEvent(
            date="2027-01-30", headliner="Sha-La-Lee’s",
            co_headliners=["The Unbelieverz"],
            venue="Supersonic Records", city="Paris", department="75",
            ticket_url="https://supersonic-club.fr/evenement/sha-la-lees-the-unbelieverz/",
            source_names=["Supersonic"],
        )
        aggregator = ConcertEvent(
            date="2027-01-30",
            headliner="The Sha La Lee’s + The Unbelieverz",
            venue="Supersonic Records", city="Paris", department="75",
            ticket_url="https://dice.fm/event/6b06a6ad50af5c000134acec",
            source_names=["DICE"],
        )
        results = deduplicate_events([venue, aggregator])
        self.assertEqual(
            len(results), 1,
            [(row.headliner, row.co_headliners, row.source_names) for row in results],
        )
        self.assertIn("Unbelieverz", " ".join(
            [results[0].headliner, *(results[0].co_headliners or []),
             *(results[0].openers or [])]
        ))

    def test_original_card_date_retained_for_non_records_venue(self):
        html = """
        <li class="agenda-item" data-venue="supersonic-2">
          <h3>A Band</h3>
          <a class="agenda-item-link" href="/evenement/band"></a>
          <time datetime="2027-01-25"></time>
          <span class="agenda-item-venue">Supersonic</span>
        </li>
        """
        event = parse_event_row(BeautifulSoup(html, "html.parser").li,
                                "https://supersonic-club.fr/agenda/")
        self.assertEqual(event.date, "2027-01-25")


if __name__ == "__main__":
    unittest.main()
