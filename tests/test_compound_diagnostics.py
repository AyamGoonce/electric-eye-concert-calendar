from unittest import TestCase

from bs4 import BeautifulSoup
from tests.clock_helpers import freeze_date

from concert_calendar.scrapers import elysee_montmartre, garmonbozia, machine_moulin_rouge


class CompoundDiagnosticsTests(TestCase):
    def test_garmonbozia_diagnostic_retains_join_fields(self):
        html = '''<dl><dd><span class="evenementNom">SHADOW OF INTENT + ABORTED</span>
          <time itemprop="startDate" datetime="2027-01-02"></time>
          <span class="evenementSalleNom">Bataclan</span><span class="evenementSalleVille">- Paris</span>
          <a class="evenementReserver" href="https://example.test/event/1">Tickets</a></dd></dl>'''
        garmonbozia._DIAGNOSTICS.clear()
        event = garmonbozia.parse_card(BeautifulSoup(html, "html.parser").select_one("dl"))
        diagnostic = garmonbozia.get_diagnostics()[0]
        self.assertEqual(event.date, diagnostic["final_date"])
        self.assertEqual(event.venue, diagnostic["final_venue"])
        self.assertEqual(event.ticket_url, diagnostic["detail_url"])
        self.assertEqual(["ABORTED"], diagnostic["parsed_openers"])

    @freeze_date("concert_calendar.scrapers.elysee_montmartre")
    def test_elysee_compound_diagnostic_does_not_change_event(self):
        html = '''<div class="bloc_extrait evenement"><a class="link" title="Emma Ruth Rundle + Cinder Well" href="https://example.test/emma"></a>
          <div class="date">13 avril 2027</div></div>'''
        elysee_montmartre._DIAGNOSTICS.clear()
        events = elysee_montmartre.parse_card(BeautifulSoup(html, "html.parser").select_one("div"))
        self.assertEqual("Emma Ruth Rundle + Cinder Well", events[0].headliner)
        diagnostic = elysee_montmartre.get_diagnostics()[0]
        self.assertEqual(events[0].date, diagnostic["final_date"])
        self.assertEqual("Élysée Montmartre", diagnostic["final_venue"])

    def test_machine_diagnostic_is_bounded_and_nonsemantic(self):
        html = '''<article class="evenement-item"><span id="tyevtagenda">Concert</span>
          <time datetime="2027-01-02T20:00:00"></time><h2 class="titevtagenda">Spite + Emmure + Distant + Mauled</h2>
          <a class="lkagenavt" href="https://example.test/spite"></a></article>'''
        machine_moulin_rouge._DIAGNOSTICS.clear()
        events = machine_moulin_rouge.parse_events(BeautifulSoup(html, "html.parser"), today=__import__("datetime").date(2026, 1, 1))
        self.assertEqual("Spite + Emmure + Distant + Mauled", events[0].headliner)
        self.assertEqual(events[0].date, machine_moulin_rouge.get_diagnostics()[0]["final_date"])
        self.assertLessEqual(len(machine_moulin_rouge.get_diagnostics()), 200)
