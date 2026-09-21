from unittest import TestCase

from bs4 import BeautifulSoup
from tests.clock_helpers import freeze_date

from concert_calendar.billing_semantics import apply_structured_performer_semantics
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
        self.assertIsNone(diagnostic["parsed_openers"])
        self.assertEqual("SHADOW OF INTENT + ABORTED", event.headliner)

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

    def test_elysee_detail_strong_blocks_confirm_compound_artists(self):
        html = '''
          <div class="part css_text">
            <p><strong>Emma Ruth Rundle</strong> présente son nouvel album.</p>
            <p><strong>Cinder Well</strong> est le projet d'Amelia Baker.</p>
          </div>
        '''
        event = elysee_montmartre.parse_card(BeautifulSoup('''
          <div class="bloc_extrait evenement">
            <a class="link" title="Emma Ruth Rundle + Cinder Well"
               href="https://example.test/emma"></a>
            <div class="date">13 avril 2027</div>
          </div>
        ''', "html.parser").select_one("div"))[0]

        event.performers = elysee_montmartre.detail_performers(
            html,
            event.headliner,
        )
        if event.performers:
            event.event_title = event.headliner
        apply_structured_performer_semantics([event])

        self.assertEqual("Emma Ruth Rundle", event.headliner)
        self.assertEqual(["Cinder Well"], event.co_headliners)
        self.assertEqual(
            "Emma Ruth Rundle + Cinder Well",
            event.event_title,
        )

    def test_elysee_plus_title_needs_independent_detail_evidence(self):
        self.assertEqual(
            [],
            elysee_montmartre.detail_performers(
                '''<div class="part css_text">
                  <p><strong>Mike + The Mechanics</strong> return to Paris.</p>
                </div>''',
                "Mike + The Mechanics",
            ),
        )
        self.assertEqual(
            [],
            elysee_montmartre.detail_performers(
                '''<div class="part css_text">
                  <p><strong>The Mission</strong> return to Paris.</p>
                </div>''',
                "The Mission + Guest",
            ),
        )

    def test_machine_diagnostic_is_bounded_and_nonsemantic(self):
        html = '''<article class="evenement-item"><span id="tyevtagenda">Concert</span>
          <time datetime="2027-01-02T20:00:00"></time><h2 class="titevtagenda">Spite + Emmure + Distant + Mauled</h2>
          <a class="lkagenavt" href="https://example.test/spite"></a></article>'''
        machine_moulin_rouge._DIAGNOSTICS.clear()
        events = machine_moulin_rouge.parse_events(BeautifulSoup(html, "html.parser"), today=__import__("datetime").date(2026, 1, 1))
        self.assertEqual("Spite + Emmure + Distant + Mauled", events[0].headliner)
        self.assertEqual(events[0].date, machine_moulin_rouge.get_diagnostics()[0]["final_date"])
        self.assertLessEqual(len(machine_moulin_rouge.get_diagnostics()), 200)
