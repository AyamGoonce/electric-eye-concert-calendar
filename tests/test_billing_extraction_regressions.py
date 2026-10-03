import unittest

from bs4 import BeautifulSoup

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent
from concert_calendar.scrapers.supersonic import parse_event_row


class BillingExtractionRegressionTests(unittest.TestCase):

    def test_supersonic_records_agenda_card_is_accepted(self):
        soup = BeautifulSoup("""
        <li class="agenda-item" data-venue="supersonic-records">
          <a class="agenda-item-link"
             href="/evenement/finojet-tom-river-9th-oct-supersonic-records-paris-tickets/">
            <div class="info-event-slider-agenda">
              <div class="evenement-date">
                <time datetime="2026-10-09"></time>
                <span class="agenda-item-venue">Supersonic Records</span>
              </div>
              <h3>Finojet + Tom River</h3>
            </div>
          </a>
        </li>
        """, "html.parser")

        event = parse_event_row(
            soup.select_one("li.agenda-item"),
            "https://supersonic-club.fr/agenda/",
        )

        self.assertIsNotNone(event)
        self.assertEqual("Supersonic Records", event.venue)
        self.assertEqual("2026-10-09", event.date)
        self.assertEqual(
            ["Finojet", "Tom River"],
            event.performers,
        )

    def test_supersonic_plus_bill_becomes_structured_performers(self):
        soup = BeautifulSoup("""
        <li class="agenda-item" data-venue="supersonic-2">
          <a class="agenda-item-link"
             href="/evenement/king-phantom/">
            <div class="info-event-slider-agenda">
              <div class="evenement-date">
                <time datetime="2026-10-01"></time>
                <span class="agenda-item-venue">Supersonic</span>
              </div>
              <h3>King Phantom + Les Caballeros + KIJE</h3>
            </div>
          </a>
        </li>
        """, "html.parser")

        event = parse_event_row(
            soup.select_one("li.agenda-item"),
            "https://supersonic-club.fr/agenda/",
        )

        self.assertEqual(
            ["King Phantom", "Les Caballeros", "KIJE"],
            event.performers,
        )

        result = deduplicate_events([event])

        self.assertEqual(1, len(result))
        self.assertEqual("King Phantom", result[0].headliner)
        self.assertEqual(
            ["Les Caballeros", "KIJE"],
            result[0].co_headliners,
        )

    def test_unnamed_very_special_guest_is_not_part_of_artist_identity(self):
        original = "Emilie Calmé with very special guest"
        event = ConcertEvent(
            date="2026-10-01",
            headliner=original,
            raw_title=original,
            venue="Sunset/Sunside — Sunside",
            city="Paris",
            department="75",
            source_names=["Sunset/Sunside"],
        )

        result = deduplicate_events([event])

        self.assertEqual(1, len(result))
        self.assertEqual("Emilie Calmé", result[0].headliner)
        self.assertEqual(original, result[0].event_title)


class BillingExtractionSafetyTests(unittest.TestCase):

    def _supersonic_event(self, title, lineup_names):
        soup = BeautifulSoup(f"""
        <li class="agenda-item" data-venue="supersonic-2">
          <a class="agenda-item-link" href="/evenement/fixture/">
            <time datetime="2026-10-27"></time>
            <span class="agenda-item-venue">Supersonic</span>
            <h3>{title}</h3>
          </a>
        </li>
        """, "html.parser")
        return parse_event_row(
            soup.select_one("li.agenda-item"),
            "https://supersonic-club.fr/agenda/",
            lineup_names=lineup_names,
        )

    def test_supersonic_lineup_removes_reviewed_tour_title_from_artist(self):
        title = "Camille Jansen : A Slice Of Life Tour + Laelou"
        event = self._supersonic_event(title, ["Laelou", "Camille Jansen"])

        self.assertEqual("Camille Jansen", event.headliner)
        self.assertEqual(["Camille Jansen", "Laelou"], event.performers)
        self.assertEqual(title, event.event_title)
        self.assertEqual(title, event.raw_title)

    def test_supersonic_lineup_removes_tgbb_festival_prefixes(self):
        cases = [
            ("Alien Boy", "Alien Boy", "mry"),
            ("Rejoincein4K", "Rejoicein4K", "Burglar"),
            ("Hungry", "Hungry", "lttl mort"),
        ]
        for artist, lineup_artist, support in cases:
            with self.subTest(artist=artist):
                title = f"TGBB fest : {artist} + {support}"
                event = self._supersonic_event(title, [support, lineup_artist])

                self.assertEqual(artist, event.headliner)
                self.assertEqual([artist, support], event.performers)
                self.assertEqual(title, event.event_title)

    def test_supersonic_punctuated_artist_is_unchanged_without_lineup_proof(self):
        title = "Artist: The Tour + Support"
        event = self._supersonic_event(title, ["Different Artist", "Support"])

        self.assertEqual(title, event.headliner)
        self.assertIsNone(event.performers)
        self.assertIsNone(event.event_title)

    def test_supersonic_does_not_split_other_title_punctuation(self):
        title = "The Devil And The Almighty Blues"

        soup = BeautifulSoup(f"""
        <li class="agenda-item" data-venue="supersonic-2">
          <a class="agenda-item-link"
             href="/evenement/devil/">
            <div class="info-event-slider-agenda">
              <div class="evenement-date">
                <time datetime="2026-10-01"></time>
                <span class="agenda-item-venue">Supersonic</span>
              </div>
              <h3>{title}</h3>
            </div>
          </a>
        </li>
        """, "html.parser")

        event = parse_event_row(
            soup.select_one("li.agenda-item"),
            "https://supersonic-club.fr/agenda/",
        )

        self.assertEqual(title, event.headliner)
        self.assertIsNone(event.performers)

    def test_named_very_special_guest_is_not_stripped(self):
        title = "Emilie Calmé with very special guest Brad Mehldau"

        event = ConcertEvent(
            date="2026-10-01",
            headliner=title,
            raw_title=title,
            venue="Sunset/Sunside — Sunside",
            city="Paris",
            department="75",
            source_names=["Sunset/Sunside"],
        )

        result = deduplicate_events([event])

        self.assertEqual(1, len(result))
        self.assertEqual(title, result[0].headliner)

    def test_garmonbozia_multi_plus_extension_stays_opaque_without_evidence(self):
        short = ConcertEvent(
            date="2026-10-01",
            headliner="The Devil And The Almighty Blues",
            venue="Backstage By The Mill",
            city="Paris",
            department="75",
            source_names=["Backstage By The Mill"],
        )
        rich = ConcertEvent(
            date="2026-10-01",
            headliner=(
                "The Devil And The Almighty Blues "
                "+ Skyjoggers + Third Artist"
            ),
            venue="Backstage By The Mill",
            city="Paris",
            department="75",
            source_names=["Garmonbozia"],
        )

        result = deduplicate_events([short, rich])

        self.assertEqual(1, len(result))
        self.assertEqual(
            "The Devil And The Almighty Blues + Skyjoggers + Third Artist",
            result[0].headliner,
        )
        self.assertIsNone(result[0].co_headliners)


class GarmonboziaStructuredBillingRegressions(unittest.TestCase):
    def test_hidden_artist_metadata_unlocks_explicit_plus_bill(self):
        from bs4 import BeautifulSoup
        from concert_calendar.scrapers import garmonbozia

        html = '''
        <dl>
          <dd>
            <a class="evenementNom">
              <span itemprop="summary">
                I AM MORBID + ATHEIST + CANCER + STELLVRIS
              </span>
            </a>
            <time itemprop="startDate" datetime="2026-12-13T17:30:00"></time>
            <span class="evenementSalleNom">La Machine du Moulin Rouge</span>
            <span class="evenementSalleVille">- Paris</span>

            <div class="evenementInfo">
              GARMONBOZIA présente le MORBIDFEST 2026 :
              I AM MORBID + ATHEIST + CANCER + STELLVRIS
              I AM MORBID jouera un set spécial.
              ATHEIST fera un set spécial.
              CANCER jouera un set spécial.
              L'ouverture de soirée sera assurée par STELLVRIS.
            </div>

            <div class="evenementInfoArtists" style="display:none;">
              Atheist,I AM MORBID,STELLVRIS
            </div>

            <a class="evenementReserver"
               href="https://example.test/i-am-morbid">Tickets</a>
          </dd>
        </dl>
        '''

        event = garmonbozia.parse_card(
            BeautifulSoup(html, "html.parser").select_one("dl")
        )

        self.assertEqual("I AM MORBID", event.headliner)
        self.assertEqual(
            ["I AM MORBID", "ATHEIST", "CANCER"],
            event.performers,
        )
        self.assertEqual(["STELLVRIS"], event.openers)
        self.assertIsNone(event.raw_title)
        self.assertIsNone(event.event_title)
        self.assertIsNone(event.identity_aliases)

    def test_plus_title_without_structured_artist_evidence_stays_opaque(self):
        from bs4 import BeautifulSoup
        from concert_calendar.scrapers import garmonbozia

        html = '''
        <dl>
          <dd>
            <span class="evenementNom">SHADOW OF INTENT + ABORTED</span>
            <time itemprop="startDate" datetime="2027-01-02"></time>
            <span class="evenementSalleNom">Bataclan</span>
            <span class="evenementSalleVille">- Paris</span>
            <a class="evenementReserver"
               href="https://example.test/shadow">Tickets</a>
          </dd>
        </dl>
        '''

        event = garmonbozia.parse_card(
            BeautifulSoup(html, "html.parser").select_one("dl")
        )

        self.assertEqual("SHADOW OF INTENT + ABORTED", event.headliner)
        self.assertIsNone(event.performers)
        self.assertIsNone(event.openers)


class GarmonboziaRoleEvidenceSafetyRegressions(unittest.TestCase):
    def test_hidden_artist_metadata_alone_does_not_unlock_plus_bill(self):
        from bs4 import BeautifulSoup
        from concert_calendar.scrapers import garmonbozia

        html = """
        <dl><dd>
          <span class="evenementNom">
            HAVOK + BLOOD RED THRONE + XONOR + ERADIKATED
          </span>
          <time itemprop="startDate" datetime="2026-09-21"></time>
          <span class="evenementSalleNom">Petit Bain</span>
          <span class="evenementSalleVille">- Paris</span>
          <div class="evenementInfo">
            Four bands appear on the current concert bill.
          </div>
          <div class="evenementInfoArtists">
            Blood Red Throne,Havok
          </div>
          <a class="evenementReserver"
             href="https://example.test/havok">Tickets</a>
        </dd></dl>
        """

        event = garmonbozia.parse_card(
            BeautifulSoup(html, "html.parser").select_one("dl")
        )

        self.assertEqual(
            "HAVOK + BLOOD RED THRONE + XONOR + ERADIKATED",
            event.headliner,
        )
        self.assertIsNone(event.performers)
        self.assertIsNone(event.openers)

    def test_biographical_support_wording_does_not_unlock_current_bill(self):
        from bs4 import BeautifulSoup
        from concert_calendar.scrapers import garmonbozia

        html = """
        <dl><dd>
          <span class="evenementNom">
            AESTHETIC PERFECTION + PRIEST
          </span>
          <time itemprop="startDate" datetime="2026-11-02"></time>
          <span class="evenementSalleNom">Le Backstage by the Mill</span>
          <span class="evenementSalleVille">- Paris</span>
          <div class="evenementInfo">
            PRIEST has performed on several tours en première partie
            de Till Lindemann in Europe and North America.
          </div>
          <div class="evenementInfoArtists">
            AESTHETIC PERFECTION,PRIEST
          </div>
          <a class="evenementReserver"
             href="https://example.test/aesthetic">Tickets</a>
        </dd></dl>
        """

        event = garmonbozia.parse_card(
            BeautifulSoup(html, "html.parser").select_one("dl")
        )

        self.assertEqual(
            "AESTHETIC PERFECTION + PRIEST",
            event.headliner,
        )
        self.assertIsNone(event.performers)
        self.assertIsNone(event.openers)


if __name__ == "__main__":
    unittest.main()
