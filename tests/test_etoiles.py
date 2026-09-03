from datetime import date
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
from concert_calendar.scrapers import etoiles

FIX=Path(__file__).parent/"fixtures"/"etoiles"
class EtoilesTests(TestCase):
    def test_concert_card_and_club_filter(self):
        soup=BeautifulSoup((FIX/"programme.html").read_text(),"html.parser")
        event=etoiles.parse_card(soup.select("a")[0],today=date(2026,9,1))
        self.assertEqual(("2026-09-05","SAMARA CYN","19:00"),(event.date,event.headliner,event.start_time))
        self.assertIsNone(etoiles.parse_card(soup.select("a")[1],today=date(2026,9,1)))
    def test_bounded_pagination(self):
        responses=[]
        for name in ("programme.html","page-2.html"):
            response=Mock(text=(FIX/name).read_text()); response.raise_for_status=Mock(); responses.append(response)
        session=Mock(); session.get.side_effect=responses
        with patch("concert_calendar.scrapers.etoiles.requests.Session",return_value=session): events=etoiles.load_events()
        self.assertEqual(2,len(events)); self.assertEqual(2,session.get.call_count)
