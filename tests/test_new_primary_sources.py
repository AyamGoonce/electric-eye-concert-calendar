import json
from datetime import date
from unittest import TestCase
from unittest.mock import Mock, patch

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.geography import is_ile_de_france_event, normalize_event_geography
from concert_calendar.models import ConcertEvent
from concert_calendar.scraper_loader import discover_scrapers
from concert_calendar.scrapers import (
    bal_chavaux,
    los_production,
    orda,
    persona_grata,
    u_turn_touring,
)
from concert_calendar.venues import normalize_event_venue


class Response:
    def __init__(self, text="", payload=None, headers=None, url=""):
        self.text = text
        self._payload = payload
        self.headers = headers or {}
        self.url = url

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


PERSONA_HTML = """
<section class="all-events">
  <div class="block-artist-list">
    <div class="first"><span class="date">24 November 2026</span>
      <h2 class="band">L.A. GUNS</h2><span class="venue">Bal Chavaux</span>
      <span class="place">Montreuil, France</span></div>
    <div class="second ticket"><a href="https://www.facebook.com/events/1467918094982117/"></a>
      <a href="https://dice.fm/event/69a168d589c7830001a0e8eb">Ticket</a></div>
  </div>
</section>
<section><div class="block-artist-list-paris"><h2 class="band">L.A. GUNS</h2></div></section>
"""

BAL_LISTING = """
<div class="views-row"><article><a class="block font-alt" href="/agenda/la-guns">
  <div class="evt-date" data-day="24" data-month="Novembre" data-year="2026">
    <span class="evt-date-hour">• 19:30 23:00</span></div>
  <div class="agenda--evt-categories">Rock</div><h2>L.A. GUNS</h2>
</a></article></div>
"""


def bal_detail():
    payload = {
        "@context": "https://schema.org", "@type": "Event", "name": "L.A. GUNS",
        "startDate": "2026-11-24T19:30:00+01:00", "keywords": "Rock",
        "location": {"@type": "Place", "name": "Bal Chavaux", "address": {
            "addressLocality": "Montreuil", "postalCode": "93100",
        }},
        "organizer": [{"@type": "Organization", "name": "La Marbrerie"}],
        "offers": [{"@type": "Offer", "url": "https://balchavaux.fr/agenda/la-guns"}],
    }
    return f'<script type="application/ld+json">{json.dumps(payload)}</script>'


def los_card(title, when, location, ticket):
    return f"""<div class="bloc_extrait evenement"><a class="wrap" href="{ticket}"></a>
      <div class="titre">{title}</div><div class="date">{when}</div>
      <div class="lieu">{location}</div></div>"""


LOS_AGENDA = f"""
<form><label><em>MILANO</em><input name="show[]" value="1868"></label></form>
{los_card('Milano', 'mercredi 11 novembre 2026', 'Bataclan - Paris', 'https://tickets.example/milano')}
{los_card('Cirque du Soleil – OVO', 'jeudi 12 novembre 2026', 'Adidas Arena - Paris', 'https://tickets.example/ovo')}
{los_card('Unknown Production', 'vendredi 13 novembre 2026', 'Salle Pleyel - Paris', 'https://tickets.example/unknown')}
"""
LOS_SITEMAP_INDEX = """<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://www.losproduction.com/wp-sitemap-posts-artistes-1.xml</loc></sitemap>
</sitemapindex>"""
LOS_ARTISTS_SITEMAP = """<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://www.losproduction.com/artistes/milano/</loc></url>
</urlset>"""
LOS_SHOWS = '<a href="https://www.losproduction.com/spectacles/cirque-du-soleil-ovo/" title="CIRQUE DU SOLEIL – OVO">OVO</a>'
LOS_MILANO = los_card(
    "Milano", "mercredi 11 novembre 2026", "Bataclan - Paris",
    "https://tickets.example/milano",
)


UTURN_HTML = """
<div class="show-full-row"><div class="show-full-date">03 Oct 2026</div>
  <div class="show-full-name">GYASI</div><div class="show-full-venue">Paris — Petit Bain</div>
  <div class="show-full-country">FR</div><a class="ticket-btn" href="https://tickets.example/gyasi">TICKETS</a></div>
<div class="show-full-row"><div class="show-full-date">04 Oct 2026</div>
  <div class="show-full-name">GYASI</div><div class="show-full-venue">Berlin — Lido</div>
  <div class="show-full-country">DE</div></div>
"""


ORDA_HTML = """
<article class="production-card"><a href="https://ontheroad-again.eu/event/dk-harrell-paris/">
  <time datetime="2026-10-05T20:00:00+02:00"></time><h3>D.K. HARRELL + DD REY</h3>
  <div class="production-card__body"><p>Café de la Danse · Paris</p></div></a></article>
<article class="event-tile"><a href="https://ontheroad-again.eu/event/dk-harrell-paris/">
  <time datetime="2026-10-05T20:00:00+02:00"></time><span class="production-badge">Production ORDA</span>
  <div class="event-tile__info"><p>D.K. HARRELL</p><h2>Café de la Danse</h2><span>Café de la Danse · Paris</span></div></a></article>
<article class="event-tile"><a href="https://ontheroad-again.eu/event/dd-rey-paris/">
  <time datetime="2026-10-05T20:00:00+02:00"></time><span class="production-badge">Production ORDA</span>
  <div class="event-tile__info"><p>DD REY</p><h2>Café de la Danse</h2><span>Café de la Danse · Paris</span></div></a></article>
"""


class NewPrimarySourceTests(TestCase):
    def test_new_sources_are_discovered(self):
        names = {module.SOURCE_NAME for module in discover_scrapers()}
        self.assertTrue({
            "Persona Grata", "Bal Chavaux", "Los Production",
            "U-Turn Touring", "On the RoaD Again / ORDA",
        }.issubset(names))

    def test_persona_grata_parses_la_guns_without_promoter_inference(self):
        events = persona_grata.parse_events(PERSONA_HTML, today=date(2026, 9, 1))
        self.assertEqual(1, len(events))
        event = events[0]
        self.assertEqual(("2026-11-24", "L.A. GUNS", "Bal Chavaux", "Montreuil"), (
            event.date, event.headliner, event.venue, event.city,
        ))
        self.assertIsNone(event.promoters)
        self.assertEqual("https://www.facebook.com/events/1467918094982117/", event.facebook_event_url)

    def test_persona_grata_resolves_bounded_dice_short_link_identity(self):
        short_url = "https://link.dice.fm/x1e1dca52de8"
        canonical_url = "https://dice.fm/event/69a168d589c7830001a0e8eb"
        html = PERSONA_HTML.replace(canonical_url, short_url)
        dice_html = """
        <head>
          <link rel="canonical"
            href="https://dice.fm/event/wwep5p-la-guns-24th-nov-bal-chavaux-montreuil-tickets">
          <meta property="product:retailer_item_id"
            content="69a168d589c7830001a0e8eb">
        </head>
        """
        with patch(
            "concert_calendar.scrapers.persona_grata.requests.get",
            side_effect=[
                Response(html, url=persona_grata.EVENTS_URL),
                persona_grata.requests.ConnectionError("transient redirect failure"),
                Response(
                    dice_html,
                    url=(
                        "https://dice.fm/partner/tickets/event/"
                        "wwep5p-la-guns-24th-nov-bal-chavaux-montreuil-tickets"
                    ),
                ),
            ],
        ) as get:
            events = persona_grata.load_events(today=date(2026, 9, 1))

        self.assertEqual(canonical_url, events[0].ticket_url)
        self.assertEqual(3, get.call_count)

    def test_persona_dice_resolution_failure_is_non_fatal(self):
        short_url = "https://link.dice.fm/x1e1dca52de8"
        current = ConcertEvent(
            date="2026-11-24", headliner="L.A. GUNS",
            venue="Bal Chavaux", city="Montreuil", department="93",
            ticket_url=short_url,
        )
        with patch(
            "concert_calendar.scrapers.persona_grata.requests.get",
            side_effect=persona_grata.requests.ConnectionError("offline"),
        ) as get:
            result = persona_grata.resolve_dice_short_links([current])

        self.assertIs(current, result[0])
        self.assertEqual(short_url, current.ticket_url)
        self.assertEqual(persona_grata.DICE_SHORT_LINK_ATTEMPTS, get.call_count)

    def test_persona_dice_extractor_accepts_structured_canonical_fallback(self):
        html = """
        <link rel="canonical"
          href="https://dice.fm/event/abc123-example-event?utm_source=test">
        """
        self.assertEqual(
            "https://dice.fm/event/abc123-example-event",
            persona_grata.extract_dice_event_url(html),
        )

    def test_bal_chavaux_follows_real_terminal_pager_and_explicit_production(self):
        page_zero = BAL_LISTING + '<nav class="pager"><a rel="next" href="?page=1">Afficher plus</a></nav>'
        page_one = BAL_LISTING
        session = Mock()
        session.get.side_effect = [Response(page_zero), Response(page_one)]
        listings = bal_chavaux.fetch_listing_rows(session)
        self.assertEqual(1, len(listings))
        self.assertEqual(2, session.get.call_count)
        event = bal_chavaux.parse_detail_page(
            bal_detail(), listings[0], today=date(2026, 9, 1),
        )
        self.assertEqual("L.A. GUNS", event.headliner)
        self.assertEqual("19:30", event.start_time)
        self.assertEqual(["La Marbrerie"], event.promoters)

    def test_persona_and_bal_chavaux_reconcile_to_one_la_guns_event(self):
        persona = persona_grata.parse_events(PERSONA_HTML, today=date(2026, 9, 1))[0]
        listing = bal_chavaux.parse_listing_row(
            __import__("bs4").BeautifulSoup(BAL_LISTING, "html.parser").select_one(".views-row")
        )
        bal = bal_chavaux.parse_detail_page(bal_detail(), listing, today=date(2026, 9, 1))
        result = deduplicate_events([persona, bal])
        self.assertEqual(1, len(result))
        self.assertEqual("L.A. GUNS", result[0].headliner)
        self.assertEqual("Bal Chavaux", result[0].venue)

    def test_transitive_time_bridge_uses_official_venue_time(self):
        persona = persona_grata.parse_events(
            PERSONA_HTML, today=date(2026, 9, 1),
        )[0]
        persona.source_names = ["Persona Grata"]

        listing = bal_chavaux.parse_listing_row(
            __import__("bs4").BeautifulSoup(
                BAL_LISTING, "html.parser"
            ).select_one(".views-row")
        )
        bal = bal_chavaux.parse_detail_page(
            bal_detail(), listing, today=date(2026, 9, 1),
        )
        bal.source_names = ["Bal Chavaux"]
        bal.facebook_event_url = persona.facebook_event_url

        dice = ConcertEvent(
            date="2026-11-24",
            headliner="L.A. Guns",
            venue="Bal Chavaux",
            city="Montreuil",
            department="93",
            start_time="19:00",
            ticket_url="https://dice.fm/event/69a168d589c7830001a0e8eb",
            source_names=["DICE"],
        )

        result = deduplicate_events([bal, persona, dice])

        self.assertEqual(1, len(result))
        event = result[0]
        self.assertEqual("L.A. GUNS", event.headliner)
        self.assertEqual("Bal Chavaux", event.venue)
        self.assertEqual("19:30", event.start_time)
        self.assertEqual(["La Marbrerie"], event.promoters)
        self.assertEqual(
            {"Bal Chavaux", "Persona Grata", "DICE"},
            set(event.source_names or []),
        )

    def test_transitive_time_bridge_does_not_merge_labeled_performances(self):
        facebook_url = "https://www.facebook.com/events/123456789/"
        dice_url = "https://dice.fm/event/distinct-shows"
        early = ConcertEvent(
            date="2026-11-24", headliner="Example Artist",
            venue="Bal Chavaux", city="Montreuil", department="93",
            start_time="19:00", performance_marker="early show",
            facebook_event_url=facebook_url, source_names=["Bal Chavaux"],
        )
        bridge = ConcertEvent(
            date="2026-11-24", headliner="Example Artist",
            venue="Bal Chavaux", city="Montreuil", department="93",
            facebook_event_url=facebook_url, ticket_url=dice_url,
            source_names=["Persona Grata"],
        )
        late = ConcertEvent(
            date="2026-11-24", headliner="Example Artist",
            venue="Bal Chavaux", city="Montreuil", department="93",
            start_time="21:00", performance_marker="late show",
            ticket_url=dice_url, source_names=["DICE"],
        )

        result = deduplicate_events([early, bridge, late])

        self.assertEqual(2, len(result))
        self.assertEqual({"19:00", "21:00"}, {event.start_time for event in result})

    def test_authoritative_time_consensus_uses_bal_chavaux_time(self):
        official = ConcertEvent(
            date="2026-10-01", headliner="THE OLLLAM",
            venue="Bal Chavaux", city="Montreuil", department="93",
            start_time="19:30",
            ticket_url="https://balchavaux.fr/agenda/olllam",
            source_names=["Bal Chavaux"],
        )
        promoter = ConcertEvent(
            date="2026-10-01", headliner="The olllam",
            venue="Bal Chavaux", city="Montreuil", department="93",
            ticket_url="https://bit.ly/TheOlllam-AEG26",
            promoters=["AEG Presents France"],
            source_names=["AEG Presents France"],
        )
        dice = ConcertEvent(
            date="2026-10-01", headliner="The Olllam",
            venue="Bal Chavaux", city="Montreuil", department="93",
            start_time="20:00",
            ticket_url="https://dice.fm/event/6a0c6d030857e7000146f411",
            source_names=["DICE"],
        )

        result = deduplicate_events([official, promoter, dice])

        self.assertEqual(1, len(result))
        self.assertEqual("19:30", result[0].start_time)
        self.assertEqual(
            {"Bal Chavaux", "AEG Presents France", "DICE"},
            set(result[0].source_names or []),
        )

    def test_authoritative_time_consensus_preserves_labeled_shows(self):
        early = ConcertEvent(
            date="2030-01-01", headliner="Example Artist",
            venue="Example Venue", city="Paris", department="75",
            start_time="19:00", performance_marker="early show",
            ticket_url="https://venue.example/events/early",
            source_names=["Example Venue"],
        )
        promoter = ConcertEvent(
            date="2030-01-01", headliner="Example Artist",
            venue="Example Venue", city="Paris", department="75",
            ticket_url="https://promoter.example/events/example-artist",
            source_names=["Example Promoter"],
        )
        late = ConcertEvent(
            date="2030-01-01", headliner="Example Artist",
            venue="Example Venue", city="Paris", department="75",
            start_time="21:00", performance_marker="late show",
            ticket_url="https://tickets.example/events/late",
            source_names=["DICE"],
        )

        result = deduplicate_events([early, promoter, late])

        self.assertEqual(2, len(result))
        self.assertEqual({"19:00", "21:00"}, {event.start_time for event in result})

    def test_authoritative_time_consensus_rejects_implausible_clock_gap(self):
        records = [
            ConcertEvent(
                date="2030-01-01", headliner="Example Artist",
                venue="Example Venue", city="Paris", department="75",
                start_time=time, source_names=[source],
            )
            for time, source in (
                ("18:00", "Example Venue"),
                (None, "Example Promoter"),
                ("22:00", "DICE"),
            )
        ]

        result = deduplicate_events(records)

        self.assertEqual(2, len(result))
        self.assertEqual({"18:00", "22:00"}, {event.start_time for event in result})

    def test_persona_reviewed_venue_typo_reconciles_exact_dice_ticket(self):
        persona = ConcertEvent(
            date="2026-10-06",
            headliner="Bleib Modern + Konstantin Unwohl",
            venue="GQ Oberkampf",
            city="Paris",
            department="75",
            ticket_url="https://dice.fm/event/69b084f158a0750001c9b510",
            source_names=["Persona Grata"],
        )
        dice = ConcertEvent(
            date="2026-10-06",
            headliner="Bleib Modern + Konstantin Unwohl",
            venue="QG Oberkampf",
            city="Paris",
            department="75",
            start_time="19:00",
            ticket_url="https://dice.fm/event/69b084f158a0750001c9b510",
            source_names=["DICE"],
        )

        result = deduplicate_events([
            normalize_event_venue(persona),
            normalize_event_venue(dice),
        ])

        self.assertEqual(1, len(result))
        self.assertEqual("QG Oberkampf", result[0].venue)
        self.assertEqual("19:00", result[0].start_time)

    def test_persona_reviewed_exact_ticket_title_variants_reconcile(self):
        cases = (
            (
                "2026-10-16", "La Marbrerie", "QUAL & PSYCHE",
                "Qual , Psyche", "QUAL & PSYCHE",
                "https://dice.fm/event/69adf539843ff10001ff387c",
            ),
            (
                "2026-11-23", "Le Chinois", "Litvrgy", "Liturgy",
                "Liturgy", "https://dice.fm/event/6a576036b9493200019c759b",
            ),
            (
                "2027-02-20", "Bal Chavaux",
                "Das Ich + Diary of Dreams", "Diary of Dreams + Das Ich",
                "Das Ich + Diary of Dreams",
                "https://dice.fm/event/6a1c65b4b5ca1400014c602b",
            ),
        )
        for event_date, venue, persona_title, dice_title, expected, ticket in cases:
            with self.subTest(persona_title=persona_title):
                persona = ConcertEvent(
                    date=event_date, headliner=persona_title, venue=venue,
                    city="Paris", department="75", ticket_url=ticket,
                    performers=[persona_title],
                    source_names=["Persona Grata"],
                )
                dice = ConcertEvent(
                    date=event_date, headliner=dice_title, venue=venue,
                    city="Paris", department="75", start_time="19:00",
                    ticket_url=ticket, source_names=["DICE"],
                    performers=(
                        ["Das Ich", "Diary of Dreams"]
                        if persona_title == "Das Ich + Diary of Dreams"
                        else None
                    ),
                )

                result = deduplicate_events([persona, dice])

                self.assertEqual(1, len(result))
                expected_headliner = (
                    "Das Ich" if persona_title == "Das Ich + Diary of Dreams"
                    else expected
                )
                self.assertEqual(expected_headliner, result[0].headliner)
                if persona_title == "Das Ich + Diary of Dreams":
                    self.assertEqual(["Diary of Dreams"], result[0].co_headliners)
                self.assertEqual("19:00", result[0].start_time)

    def test_persona_constituent_cards_collapse_into_exact_ticket_bill(self):
        ticket = (
            "https://dice.fm/event/mx7xdw-ultra-sunn-sydney-valette-"
            "et-sad-madona-7th-nov-la-marbrerie-paris-tickets"
        )
        full_bill = ConcertEvent(
            date="2026-11-07",
            headliner="Ultra Sunn",
            venue="La Marbrerie",
            city="Montreuil",
            department="93",
            start_time="19:00",
            ticket_url=ticket,
            event_title="Ultra Sunn, Sydney Valette et Sad Madona",
            raw_title="Ultra Sunn, Sydney Valette et Sad Madona",
            performers=["Ultra Sunn"],
            source_names=["DICE"],
        )
        components = [
            ConcertEvent(
                date="2026-11-07", headliner=artist,
                venue="La Marbrerie", city="Montreuil", department="93",
                ticket_url=ticket, performers=[artist],
                source_names=["Persona Grata"],
            )
            for artist in ("Ultra Sunn", "Sydney Valette", "Sad Madona")
        ]

        result = deduplicate_events([full_bill, *components])

        self.assertEqual(1, len(result))
        self.assertEqual("Ultra Sunn", result[0].headliner)
        self.assertEqual(
            "Ultra Sunn, Sydney Valette et Sad Madona",
            result[0].event_title,
        )
        self.assertIsNone(result[0].openers)
        self.assertIsNone(result[0].co_headliners)
        self.assertEqual("19:00", result[0].start_time)

    def test_persona_constituent_cards_collapse_after_late_ticket_reconciliation(self):
        persona_ticket = (
            "https://dice.fm/event/mx7xdw-ultra-sunn-sydney-valette-"
            "et-sad-madona-7th-nov-la-marbrerie-paris-tickets"
        )
        components = [
            ConcertEvent(
                date="2026-11-07", headliner=artist,
                venue="La Marbrerie", city="Montreuil", department="93",
                ticket_url=persona_ticket, performers=[artist],
                source_names=["Persona Grata"],
            )
            for artist in ("Ultra Sunn", "Sydney Valette", "Sad Madona")
        ]
        full_bill = ConcertEvent(
            date="2026-11-07",
            headliner="Ultra Sunn, Sydney Valette et Sad Madona",
            venue="La Marbrerie",
            city="Montreuil",
            department="93",
            start_time="19:00",
            ticket_url="https://dice.fm/event/6b0000000000000000000000",
            raw_title="Ultra Sunn, Sydney Valette et Sad Madona",
            source_names=["DICE"],
        )
        diagnostics = {}

        # Persona cards precede the complete DICE bill, matching the live
        # ordering: the Ultra Sunn identity/title merge occurs only after the
        # first exact-ticket constituent scan has already examined the cards.
        result = deduplicate_events(
            [*components, full_bill],
            diagnostics=diagnostics,
        )

        self.assertEqual(1, len(result))
        self.assertEqual("Ultra Sunn", result[0].headliner)
        self.assertEqual(
            "Ultra Sunn, Sydney Valette et Sad Madona",
            result[0].event_title,
        )
        self.assertEqual("19:00", result[0].start_time)
        self.assertEqual(
            {"DICE", "Persona Grata"},
            set(result[0].source_names or []),
        )
        self.assertEqual(2, diagnostics["late_ticket_constituents_merged"])

    def test_shared_ticket_without_complete_constituent_bill_stays_separate(self):
        ticket = "https://tickets.example.test/event/shared"
        events = [
            ConcertEvent(
                date="2030-01-01", headliner=artist,
                venue="Example Venue", city="Paris", department="75",
                ticket_url=ticket, source_names=[source],
            )
            for artist, source in (
                ("Alpha + Beta", "Venue"),
                ("Alpha", "Agency"),
                ("Gamma", "Agency"),
            )
        ]

        result = deduplicate_events(events)

        self.assertEqual(2, len(result))
        self.assertIn("Gamma", {event.headliner for event in result})

    def test_bad_lila_may_ticket_does_not_merge_jovin_webb(self):
        bad_ticket = "https://lodeonscenejrc.soticket.net/agenda/152-JOVIN-WEBB"
        lila_may = ConcertEvent(
            date="2026-10-17", headliner="LILA-MAY",
            venue="L'Odéon", city="Tremblay-en-France", department="93",
            ticket_url=bad_ticket,
            source_names=["Gérard Drouot Productions"],
        )
        jovin_webb = ConcertEvent(
            date="2026-10-17", headliner="JOVIN WEBB",
            venue="L'Odéon de Tremblay", city="Tremblay-en-France",
            department="93", ticket_url=bad_ticket,
            source_names=["On the RoaD Again / ORDA"],
        )

        result = deduplicate_events([lila_may, jovin_webb])

        self.assertEqual(2, len(result))
        self.assertEqual(
            {"LILA-MAY", "JOVIN WEBB"},
            {event.headliner for event in result},
        )

    def test_los_classification_subject_does_not_collapse_fuller_venue_bill(self):
        venue = ConcertEvent(
            date="2026-10-22",
            headliner="SANANDA MAITREYA & The Sugar Plum Pharaohs",
            venue="Café de la Danse",
            city="Paris",
            department="75",
            source_names=["Café de la Danse"],
        )
        los = ConcertEvent(
            date="2026-10-22",
            headliner="Sananda Maitreya",
            venue="Café de la Danse",
            city="Paris",
            department="75",
            performers=["Sananda Maitreya"],
            source_names=["Los Production"],
        )

        result = deduplicate_events([los, venue])

        self.assertEqual(1, len(result))
        self.assertEqual(
            "SANANDA MAITREYA & The Sugar Plum Pharaohs",
            result[0].headliner,
        )
        self.assertEqual(
            {"Los Production", "Café de la Danse"},
            set(result[0].source_names or []),
        )

    def test_los_subject_does_not_merge_an_ordinary_longer_artist_name(self):
        los = ConcertEvent(
            date="2026-10-22", headliner="Example Artist",
            venue="Café de la Danse", city="Paris", department="75",
            performers=["Example Artist"], source_names=["Los Production"],
        )
        other = ConcertEvent(
            date="2026-10-22", headliner="Example Artist Orchestra",
            venue="Café de la Danse", city="Paris", department="75",
            source_names=["Café de la Danse"],
        )

        self.assertEqual(2, len(deduplicate_events([los, other])))

    def test_los_uses_canonical_artist_relationship_and_diagnoses_skips(self):
        session = Mock()

        def get(url, **kwargs):
            if url == los_production.AGENDA_URL:
                return Response(LOS_AGENDA)
            if url == los_production.SITEMAP_INDEX_URL:
                return Response(LOS_SITEMAP_INDEX)
            if url == "https://www.losproduction.com/wp-sitemap-posts-artistes-1.xml":
                return Response(LOS_ARTISTS_SITEMAP)
            if url == los_production.SHOWS_INDEX_URL:
                return Response(LOS_SHOWS)
            if url == los_production.filtered_agenda_url("1868"):
                return Response(LOS_MILANO)
            raise AssertionError(url)

        session.get.side_effect = get
        with patch("concert_calendar.scrapers.los_production.requests.Session", return_value=session):
            events = los_production.load_events(today=date(2026, 9, 1))
        self.assertEqual(1, len(events))
        self.assertEqual(("Milano", "2026-11-11", "Bataclan", "Paris"), (
            events[0].headliner, events[0].date, events[0].venue, events[0].city,
        ))
        self.assertIsNone(events[0].promoters)
        reasons = {item["reason"] for item in los_production.get_diagnostics()}
        self.assertIn("included_canonical_artist", reasons)
        self.assertIn("excluded_canonical_spectacle", reasons)
        self.assertIn("unclassified_agenda_row", reasons)

    def test_los_milano_reconciles_with_equivalent_existing_row(self):
        los = ConcertEvent(
            date="2026-11-11", headliner="Milano", venue="Bataclan",
            city="Paris", department="75", source_names=["Los Production"],
        )
        existing = ConcertEvent(
            date="2026-11-11", headliner="MILANO", venue="Bataclan",
            city="Paris", department="75", source_names=["Official venue"],
        )
        self.assertEqual(1, len(deduplicate_events([existing, los])))

    def test_u_turn_emits_nationwide_rows_for_central_idf_filtering(self):
        events = u_turn_touring.parse_events(UTURN_HTML, today=date(2026, 9, 1))
        self.assertEqual(2, len(events))
        for event in events:
            normalize_event_geography(event)
        idf = [event for event in events if is_ile_de_france_event(event)]
        self.assertEqual(["Petit Bain"], [event.venue for event in idf])
        self.assertTrue(all(event.promoters is None for event in events))

    def test_orda_production_bill_and_component_rows_become_one_event(self):
        metadata = {
            "https://ontheroad-again.eu/event/dk-harrell-paris/": {
                "ticket_url": "https://tickets.example/orda", "is_production": True,
            },
            "https://ontheroad-again.eu/event/dd-rey-paris/": {
                "ticket_url": "https://tickets.example/orda", "is_production": True,
            },
        }
        events = orda.parse_events(ORDA_HTML, metadata, today=date(2026, 9, 1))
        self.assertEqual(1, len(events))
        self.assertEqual("D.K. HARRELL", events[0].headliner)
        self.assertEqual(["DD REY"], events[0].co_headliners)
        self.assertEqual("D.K. HARRELL + DD REY", events[0].event_title)
        self.assertEqual(["ORDA"], events[0].promoters)
