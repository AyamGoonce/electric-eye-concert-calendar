from datetime import date
from pathlib import Path
from unittest import TestCase
from bs4 import BeautifulSoup
from concert_calendar.scrapers.nouveau_casino import parse_items
FIX=Path(__file__).parent/"fixtures"/"nouveau_casino"/"programme.html"
class NouveauCasinoTests(TestCase):
    def test_concert_filter_metadata_and_year_rollover(self):
        events=parse_items(BeautifulSoup(FIX.read_text(),"html.parser"),today=date(2026,9,1))
        self.assertEqual(2,len(events)); first,second=events
        self.assertEqual(("2026-09-05","Ruggero","19:30","sold_out","Pop"),(first.date,first.headliner,first.start_time,first.ticket_status,first.genre))
        self.assertEqual("2027-01-08",second.date)
