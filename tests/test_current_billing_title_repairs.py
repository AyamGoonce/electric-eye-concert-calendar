import unittest
from datetime import date
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from concert_calendar.billing_semantics import (
    apply_structured_performer_semantics,
    normalize_event_semantics,
)
from concert_calendar.event_state import canonical_event_identity, reconcile_state
from concert_calendar.models import ConcertEvent
from concert_calendar.scrapers import (
    accor_arena,
    backstage_btm,
    bataclan,
    bellevilloise,
    dome_de_paris,
    file7,
    garmonbozia,
    petit_bain,
    point_ephemere,
    sunset_sunside,
)
from concert_calendar.sources import classify_event_eligibility


def bataclan_document(title, team_love, description=None):
    return {"attributes": {
        "title": title,
        "date": "2027-01-30T18:00:00.000Z",
        "uid": "fixture_2027-01-30",
        "type": {"data": {"attributes": {"title": "Concert & Festival"}}},
        "teamLove": team_love,
        "description": description,
        "ticketingUrl": "https://billetterie.bataclan.fr/fr/manifestation/fixture",
    }}


def garmonbozia_card(title, artists, info):
    return BeautifulSoup(f"""
    <dl><dd>
      <span class="evenementNom">{title}</span>
      <time itemprop="startDate" datetime="2027-02-23T19:00:00"></time>
      <span class="evenementSalleNom">La Machine du Moulin Rouge</span>
      <span class="evenementSalleVille">- Paris</span>
      <div class="evenementInfo">{info}</div>
      <div class="evenementInfoArtists">{artists}</div>
      <a class="evenementReserver" href="https://example.test/ticket">Tickets</a>
    </dd></dl>
    """, "html.parser").select_one("dl")


def sunset_payload(title, description):
    return {"props": {"pageProps": {"entities": {
        "ticketing": {
            "title": title,
            "description": description,
            "venue": {
                "name": "Sunset Sunside", "seatingName": "Sunside", "city": "Paris",
            },
        },
        "eventDates": {"hydra:totalItems": 1, "hydra:member": [
            {"startDate": "2026-11-25T20:00:00+01:00", "onSale": True},
        ]},
    }}}}


class CurrentBillingTitleRepairTests(unittest.TestCase):
    def test_accor_tour_uses_independent_spotify_artist_metadata(self):
        item = {
            "spotify": "https://open.spotify.com/artist/example",
            "artist_reference": "MACKLEMORE &amp; FRIENDS",
            "room": {"full_name": "Accor Arena"},
            "sessions": [{"date": "2026-10-29 20:00:00"}],
            "translations": [{
                "language": "fr",
                "category": "CONCERT",
                "title": "MACKLEMORE & FRIENDS : FREE PALESTINE TOUR",
                "description": "<p>Macklemore &amp; Friends sera sur scène.</p>",
                "spotify_tiles": [
                    {"title": "This Is Macklemore", "year": "Macklemore"},
                    {"title": "BEN", "year": "Macklemore"},
                ],
            }],
        }
        event = accor_arena.parse_item(item)[0]
        self.assertEqual(["Macklemore"], event.performers)
        apply_structured_performer_semantics([event])
        self.assertEqual("Macklemore", event.headliner)
        self.assertEqual(
            "MACKLEMORE & FRIENDS : FREE PALESTINE TOUR",
            event.event_title,
        )

    def test_accor_spotify_metadata_cannot_collapse_a_tribute_production(self):
        translation = {
            "title": "500 VOIX POUR JOHNNY - TRIBUTE TOUR",
            "spotify_tiles": [{"year": "Johnny Hallyday"}],
        }
        item = {
            "spotify": "https://open.spotify.com/artist/example",
            "artist_reference": "500 VOIX POUR JOHNNY",
        }
        self.assertIsNone(accor_arena.extract_tour_performer(item, translation))

    def test_bataclan_explicit_support_stays_support(self):
        cases = (
            (
                "HEALTH + VOWWS + DOODSESKADER",
                "HEALTH sera de passage au Bataclan avec en support les Australiens de VOWWS et le duo belge Doodseskader.",
                ["VOWWS", "DOODSESKADER"],
            ),
            (
                "ELUVEITIE + PAIN + WOLFHEART",
                "Eluveitie sera en concert au Bataclan. Accompagné de Wolfheart et Pain, la soirée promet d'être inoubliable !",
                ["PAIN", "WOLFHEART"],
            ),
        )
        for title, prose, expected_openers in cases:
            with self.subTest(title=title):
                event = bataclan.parse_document(bataclan_document(title, prose))
                self.assertEqual(title.split(" + ")[0], event.headliner)
                self.assertEqual(expected_openers, event.openers)
                self.assertEqual(title, event.raw_title)

    def test_bataclan_explicit_triple_bill_preserves_all_named_acts(self):
        event = bataclan.parse_document(bataclan_document(
            "KRAV BOCA x POESIE ZERO",
            "Le Bataclan présente une triple affiche avec Krav Boca, Poesie Zero et King Kong Meuf.",
            "<p>KRAV BOCA + POESIE ZERO + KING KONG MEUF</p>",
        ))
        self.assertEqual("KRAV BOCA", event.headliner)
        self.assertEqual(["POESIE ZERO", "KING KONG MEUF"], event.co_headliners)
        self.assertEqual("KRAV BOCA x POESIE ZERO", event.raw_title)

    def test_bataclan_x_and_plus_without_role_evidence_stay_opaque(self):
        for title in ("ACT ONE x ACT TWO", "ACT ONE + ACT TWO"):
            event = bataclan.parse_document(bataclan_document(title, "An evening of music."))
            self.assertEqual(title, event.headliner)
            self.assertIsNone(event.co_headliners)
            self.assertIsNone(event.openers)

    def test_garmonbozia_current_event_sillage_is_support(self):
        cases = (
            (
                "ARKONA + SETH + THE GREAT OLD ONES",
                "Arkona,SETH,THE GREAT OLD ONES",
                "ARKONA embarque dans son sillage deux formations, SETH et THE GREAT OLD ONES.",
                ["SETH", "THE GREAT OLD ONES"],
            ),
            (
                "SIGNS OF THE SWARM + OCEANS ATE ALASKA + FACE YOURSELF",
                "Oceans Ate Alaska,SIGNS OF THE SWARM",
                "SIGNS OF THE SWARM sera à la tête de sa propre tournée et embarqueront dans leur sillage OCEANS ATE ALASKA et FACE YOURSELF.",
                ["OCEANS ATE ALASKA", "FACE YOURSELF"],
            ),
        )
        for title, artists, info, openers in cases:
            with self.subTest(title=title):
                event = garmonbozia.parse_card(garmonbozia_card(title, artists, info))
                self.assertEqual(title.split(" + ")[0], event.headliner)
                self.assertEqual(openers, event.openers)
                self.assertEqual(title, event.raw_title)

    def test_garmonbozia_unresolved_titles_remain_opaque(self):
        for title, artists, info in (
            ("EVERGREY + IGNEA + STELLAR CIRCUITS", "Evergrey", "Evergrey revient à Paris."),
            ("DARVAZA + MERRIMACK + HELLERUIN + DETRESSE", "", "Darvaza s'unit à Merrimack, Helleruin et Detresse."),
            ("The Devil And The Almighty Blues + Skyjoggers", "", "Deux groupes."),
        ):
            event = garmonbozia.parse_card(garmonbozia_card(title, artists, info))
            self.assertEqual(title, event.headliner)
            self.assertIsNone(event.openers)

    def test_point_structured_artist_sections_split_only_corresponding_bill(self):
        document = {"uid": "par.sek-", "data": {
            "name": "PAR.SEK + YOLANDE BASHING", "start_date": "2026-11-19",
            "text": [
                {"type": "paragraph", "text": "PAR.SEK ", "spans": [{"start": 0, "end": 8, "type": "strong"}]},
                {"type": "paragraph", "text": "Biography of PAR.SEK", "spans": []},
                {"type": "paragraph", "text": "YOLANDE BASHING ", "spans": [{"start": 0, "end": 16, "type": "strong"}]},
            ],
        }}
        event = point_ephemere.parse_document(document)
        self.assertEqual("PAR.SEK", event.headliner)
        self.assertEqual(["YOLANDE BASHING"], event.co_headliners)
        self.assertEqual(document["data"]["name"], event.raw_title)
        document["data"]["text"] = []
        self.assertEqual("PAR.SEK + YOLANDE BASHING", point_ephemere.parse_document(document).headliner)

    def test_petit_bain_strips_only_explicit_opener_label(self):
        card = BeautifulSoup("""
        <article class="categorie-concerts">
          <a href="https://petitbain.org/evenement/carlton/"></a>
          <div id="ladatevtmin">19 novembre 2026</div>
          <div class="titevtprog">
            <span class="titartprog">Carlton Jumel Smith &amp; The Soul Seeders</span>
            <span class="titartprog">première partie - Indawa</span>
          </div>
        </article>
        """, "html.parser").select_one("article")
        event = petit_bain.parse_card(card, today=date(2026, 9, 22))
        self.assertEqual("Carlton Jumel Smith & The Soul Seeders", event.headliner)
        self.assertEqual(["Indawa"], event.openers)

    def test_backstage_plus_without_role_evidence_stays_opaque(self):
        card = BeautifulSoup("""
        <li><span class="event-title">DARVAZA + MERRIMACK + HELLERUIN + DETRESSE</span>
        <span class="event-booking">10/12/2026</span><span class="event-type">Concert</span>
        <span class="see-event"><a href="/agenda/darvaza/">Detail</a></span></li>
        """, "html.parser").select_one("li")
        self.assertEqual(
            "DARVAZA + MERRIMACK + HELLERUIN + DETRESSE",
            backstage_btm.parse_card(card, today=date(2026, 9, 22)).headliner,
        )

    def test_dome_uses_authoritative_detail_title_over_status_text(self):
        listing = BeautifulSoup("""
        <div class="spectacle-content"><h4><a href="/fr/mania-the-abba-tribute">bientôt en vente</a></h4>
        <p>Concert<br>09 octobre 2027</p></div>
        """, "html.parser")
        detail = '<title>Mania, The Abba Tribute, Dôme de Paris</title><meta property="og:title" content="Mania, The Abba Tribute, Dôme de Paris"><meta name="description" content="Richard Walter Productions est fier d’accueillir à nouveau ABBA MANIA, le Tribute Band d’ABBA">'
        events = dome_de_paris.parse_events(
            listing, today=date(2026, 9, 22), detail_resolver=lambda url: detail,
        )
        self.assertEqual(1, len(events))
        self.assertEqual("ABBA MANIA", events[0].headliner)
        self.assertIn("Mania, The Abba Tribute", events[0].event_title)
        self.assertEqual("bientôt en vente", events[0].raw_title)
        old = ConcertEvent("2027-10-09", "bientôt en vente", "Le Dôme de Paris", "Paris", "75")
        old_identity = canonical_event_identity(old)
        previous = {"version": 3, "updated_at": "2026-09-22T11:50:12Z", "events": {
            old_identity: {
                "date": old.date, "first_seen": "2026-09-22T11:31:40Z",
                "last_seen": "2026-09-22T11:50:12Z", "openers": [],
                "genre": "", "ticket_status": "tickets",
                "public_id": old_identity[:16], "base_identity": old_identity,
                "performance": "",
            },
        }}
        reconcile_state(events, previous, now=datetime(2026, 9, 22, 12, tzinfo=timezone.utc))
        self.assertEqual(old_identity[:16], events[0]._public_id)
        self.assertEqual("2026-09-22T11:31:40Z", events[0].first_seen)

    def test_dome_detail_prose_separates_artist_from_production_title(self):
        listing = BeautifulSoup("""
        <div class="spectacle-content"><h4><a href="/fr/spectacle/374/khaled">HIER, AUJOURD'HUI, DEMAIN : KHALED</a></h4>
        <p>Concert<br>31 octobre 2026</p></div>
        """, "html.parser")
        detail = """
        <meta property="og:title" content="Hier, Aujourd'hui, Demain : Khaled, Dôme de Paris">
        <div class="col-lg-6 offset-lg-1">
          <h4>HIER, AUJOURD'HUI, DEMAIN : KHALED</h4>
          <p class="float-md-left"><small>Concert / Du 31 octobre au 01 novembre 2026</small></p>
          <div class="clearfix"></div>
          <div>
            <p>Il est des voix que les années n’effacent pas. Elles traversent le temps, habitent les mémoires et continuent d’éclairer les générations.</p>
            <p>Pour célébrer 50 ans de carrière, Khaled revient sur scène pour une date anniversaire exceptionnelle, entre émotion, fête et souvenirs partagés.</p>
            <p>Le 31 octobre et 01 novembre 2026, au Dôme de Paris, Khaled vous donne rendez-vous pour un concert unique, accompagné par le Paris One World Orchestra.</p>
            <p>Réservez vos places dès maintenant.</p>
          </div>
          <div class="mt-4">
            <h6>Horaires et dates des représentations</h6>
            <strong>Samedi 31 octobre 2026 à 20:00</strong>
          </div>
        </div>
        """
        event = dome_de_paris.parse_events(
            listing, today=date(2026, 9, 22), detail_resolver=lambda url: detail,
        )[0]
        self.assertEqual("Khaled", event.headliner)
        self.assertEqual("Hier, Aujourd'hui, Demain", event.event_title)
        self.assertEqual("HIER, AUJOURD'HUI, DEMAIN : KHALED", event.raw_title)

    def test_sunset_detail_evidence_separates_artist_and_context(self):
        cases = (
            (
                "Cinema Italia ft. Luca Zennaro & Michelangelo Scandroglio - Festival Jazzycolors",
                "Le duo formé par deux musiciens. Le projet se distingue par son répertoire. Cinema Italia devient ainsi un espace de rencontre.",
                "Cinema Italia",
            ),
            (
                'Carlton Rara "Universed Live"',
                "La musique de Carlton Rara est un mélange à nul autre pareil et son dernier album Universed est une invitation.",
                "Carlton Rara",
            ),
            (
                'Thierry Peala & Edouard Ferlet - "Any Time !"',
                "Concert exceptionnel en Duo avec Thierry Peala et Edouard Ferlet. Any Time est la promesse que les deux musiciens se sont faite.",
                "Thierry Peala & Edouard Ferlet",
            ),
            (
                "Antoine Boyer Group « The Big Step » - L'élégance de l'anachronisme",
                "Ce nouveau trio insuffle un vent de modernité. Autour d’Antoine Boyer, la guitare devient un orchestre.",
                "Antoine Boyer Group",
            ),
        )
        for title, description, expected in cases:
            with self.subTest(title=title):
                event = sunset_sunside.parse_detail_payload(
                    sunset_payload(title, description), "https://example.test/ticket",
                )[0]
                self.assertEqual(expected, event.headliner)
                self.assertEqual(title, event.event_title)
                self.assertEqual(title, event.raw_title)
                self.assertIsNone(event.co_headliners)

    def test_sunset_punctuation_without_detail_evidence_stays_opaque(self):
        for title in (
            "Antoine Boyer & Rita Payés",
            "Pearl & The Oysters",
            "TC.KYLIE × JOYA — “Somewhere Between”",
        ):
            with self.subTest(title=title):
                event = sunset_sunside.parse_detail_payload(
                    sunset_payload(title, "Un concert de jazz."), "https://example.test/ticket",
                )[0]
                self.assertEqual(title, event.headliner)
                self.assertIsNone(event.raw_title)

    def test_sunset_explicit_programme_grammar_preserves_the_named_performer(self):
        cases = (
            ("Kate Bush Tribute – Claire Nouet Quartet", "Claire Nouet Quartet", "Kate Bush Tribute"),
            (
                'Hommage à John Coltrane "Coltrane\'s Sound" avec Les Blakettes + jam',
                "Les Blakettes",
                'Hommage à John Coltrane "Coltrane\'s Sound" + jam',
            ),
            (
                "Jazz & Goûter fête Queen et George Michael avec Léa Castro",
                "Léa Castro",
                "Jazz & Goûter fête Queen et George Michael",
            ),
            (
                'Jam Session "Django Celebration" avec Alex Swing',
                "Alex Swing",
                'Jam Session "Django Celebration"',
            ),
        )
        for title, expected, event_title in cases:
            with self.subTest(title=title):
                event = sunset_sunside.parse_detail_payload(
                    sunset_payload(title, "Présentation du concert."),
                    "https://example.test/ticket",
                )[0]
                self.assertEqual(expected, event.headliner)
                self.assertEqual(event_title, event.event_title)
                self.assertEqual(title, event.raw_title)

    def test_category_backed_cafe_concert_wrapper_is_presentation(self):
        soup = BeautifulSoup("""
        <article class="c-tile" data-categories="cafe-concert;2026-10">
          <span class="c-tile_date">Mer 14 octobre</span>
          <span class="c-tile_title">Café concert : Milla Leika &amp; Paul Pesty</span>
          <a class="c-link" href="https://example.test/milla"></a>
        </article>
        """, "html.parser")
        event = bellevilloise.parse_events(soup, today=date(2026, 9, 22))[0]
        self.assertEqual("Milla Leika & Paul Pesty", event.headliner)
        self.assertEqual("Café concert : Milla Leika & Paul Pesty", event.raw_title)
        self.assertEqual("Café concert", event.series_name)

    def test_file7_source_wrapper_does_not_authorize_plus_splitting(self):
        card = BeautifulSoup("""
        <div class="bloc_show"><a href="https://file7.com/09-10-2026-20h00-example"></a>
          <span class="artistes">Soirées Fan-Club : Mike + The Mechanics</span>
        </div>
        """, "html.parser").select_one(".bloc_show")
        event = file7.parse_card(card)
        self.assertEqual("Mike + The Mechanics", event.headliner)
        self.assertIsNone(event.co_headliners)
        self.assertEqual("Soirées Fan-Club : Mike + The Mechanics", event.raw_title)
        self.assertEqual("Soirées Fan-Club", event.series_name)
        self.assertEqual(["Soirées Fan-Club : Mike"], event.identity_aliases)

    def test_file7_legacy_primary_is_state_migration_only(self):
        card = BeautifulSoup("""
        <div class="bloc_show"><a href="https://file7.com/03-10-2026-20h00-example"></a>
          <span class="artistes">Les Fatals Picards + La bise</span>
        </div>
        """, "html.parser").select_one(".bloc_show")
        event = file7.parse_card(card)
        self.assertEqual("Les Fatals Picards + La bise", event.headliner)
        self.assertIsNone(event.co_headliners)
        self.assertIsNone(event.performers)
        self.assertEqual(["Les Fatals Picards"], event.identity_aliases)

        old = ConcertEvent(event.date, "Les Fatals Picards", event.venue, event.city, event.department)
        old_identity = canonical_event_identity(old)
        previous = {"version": 3, "updated_at": "2026-09-22T11:50:12Z", "events": {
            old_identity: {
                "date": old.date, "first_seen": "2026-08-20T11:02:59Z",
                "last_seen": "2026-09-22T11:50:12Z", "openers": [],
                "genre": "", "ticket_status": "tickets",
                "public_id": old_identity[:16], "base_identity": old_identity,
                "performance": "",
            },
        }}
        reconcile_state(
            [event], previous,
            now=datetime(2026, 9, 22, 12, tzinfo=timezone.utc),
        )
        self.assertEqual(old_identity[:16], event._public_id)
        self.assertEqual("2026-08-20T11:02:59Z", event.first_seen)

    def test_explicit_tour_and_release_grammars_are_context_not_identity(self):
        cases = (
            ("Gracie Abrams: The Look at My Life Tour", "Gracie Abrams"),
            ("GURL release party", "GURL"),
            ("Malesa release party II", "Malesa"),
        )
        for title, expected in cases:
            with self.subTest(title=title):
                event = ConcertEvent("2027-01-01", title, "Venue", "Paris", "75")
                normalize_event_semantics(event)
                self.assertEqual(expected, event.headliner)
                self.assertEqual(title, event.event_title)
                self.assertIn(title, event.identity_aliases)

    def test_punctuation_and_unlabelled_context_remain_opaque(self):
        for title in (
            "Bigflo & Oli", "Jack & Jack", "Dan & Phil", "Chase & Status",
            "Pearl & The Oysters", "Uncle Acid & The Deadbeats",
            "Mike + The Mechanics", "Artist: Name", "Artist-Name",
            "Tonic Walter II Tour 2026", "GUADAL TEJAZ Release Party + YAR",
        ):
            with self.subTest(title=title):
                event = ConcertEvent("2027-01-01", title, "Venue", "Paris", "75")
                normalize_event_semantics(event)
                self.assertEqual(title, event.headliner)

    def test_unresolved_commerce_placeholders_cannot_be_headliners(self):
        for title in (
            "bientôt en vente", "prochainement", "en vente", "sold out",
            "complet", "tickets", "billetterie", "réserver", "réservation",
        ):
            with self.subTest(title=title):
                record = ConcertEvent("2027-01-01", title, "Venue", "Paris", "75")
                self.assertFalse(classify_event_eligibility(record)[0])
        for title in (
            "Tickets to My Downfall", "Completement fou", "The Devil And The Almighty Blues",
            "Carlton Jumel Smith & The Soul Seeders", "St. Paul and the Broken Bones",
        ):
            with self.subTest(valid=title):
                record = ConcertEvent("2027-01-01", title, "Venue", "Paris", "75")
                self.assertTrue(classify_event_eligibility(record)[0])


if __name__ == "__main__":
    unittest.main()
