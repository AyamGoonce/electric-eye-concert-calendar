from bs4 import BeautifulSoup
import unittest

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent
from concert_calendar.scrapers.dice import parse_explicit_billing
from concert_calendar.scrapers.radical import parse_card as parse_radical_card
from concert_calendar.scrapers.rock_en_seine import parse_lineup
from concert_calendar.sources import is_supported_event, is_ticket_product_title
from concert_calendar.venues import normalize_event_venue


def event(headliner, *, venue="Rock en Seine", openers=None, authoritative=False):
    return ConcertEvent(
        date="2026-08-28",
        headliner=headliner,
        venue=venue,
        city="Saint-Cloud",
        department="92",
        openers=openers,
        ticket_url="https://example.com/ticket",
        festival_name="Rock en Seine" if authoritative else None,
        authoritative_billing=authoritative,
    )


class FestivalSemanticsTests(unittest.TestCase):
    LINEUP_HTML = """
    <h1>Programmation 2026</h1>
    <div class="card-artist"><div class="item-date">Ven 28 Août
      <div class="item-stage">19:55 / Grande Scène</div></div><h3>The Black Keys</h3></div>
    <div class="card-artist"><div class="item-date">Ven 28 Août
      <div class="item-stage">22:15 / Grande Scène</div></div><h3>Nick Cave &amp; The Bad Seeds</h3></div>
    <div class="card-artist"><div class="item-date">Ven 28 Août
      <div class="item-stage">21:05 / Scène BoursoBank</div></div><h3>Franz Ferdinand</h3></div>
    """

    def test_official_lineup_selects_main_stage_closing_headliner(self):
        result = parse_lineup(self.LINEUP_HTML)

        self.assertEqual(1, len(result))
        self.assertEqual("Nick Cave & The Bad Seeds", result[0].headliner)
        self.assertEqual(
            ["The Black Keys", "Franz Ferdinand"],
            result[0].openers,
        )
        self.assertEqual("Rock en Seine", result[0].venue)
        self.assertTrue(result[0].authoritative_billing)

    def test_one_authoritative_festival_row_replaces_artist_products(self):
        official = event(
            "Nick Cave & The Bad Seeds",
            openers=["The Black Keys", "Franz Ferdinand"],
            authoritative=True,
        )
        products = [
            event("Nick Cave and The Bad Seeds"),
            event("The Black Keys", venue="Festival Rock en Seine"),
            event("Franz Ferdinand"),
        ]
        for item in [official, *products]:
            normalize_event_venue(item)

        diagnostics = {}
        result = deduplicate_events([official, *products], diagnostics=diagnostics)

        self.assertEqual(1, len(result))
        self.assertEqual("Nick Cave & The Bad Seeds", result[0].headliner)
        self.assertEqual(["The Black Keys", "Franz Ferdinand"], result[0].openers)
        self.assertEqual("Rock en Seine", result[0].venue)
        self.assertEqual(3, diagnostics["festival_artist_rows_collapsed"])

    def test_ambiguous_festival_without_authoritative_bill_is_not_collapsed(self):
        result = deduplicate_events([event("Artist A"), event("Artist B")])
        self.assertEqual(2, len(result))


class SpecialBillingTests(unittest.TestCase):
    def test_le_beau_dimanche_uses_explicit_performer_bill(self):
        headliner, openers = parse_explicit_billing(
            "Le Beau Dimanche : Sahel Ménilmontant + Dj La Bise"
        )
        self.assertEqual("Sahel Ménilmontant", headliner)
        self.assertEqual(["Dj La Bise"], openers)

    def test_afters_suffix_is_metadata_not_artist_identity(self):
        headliner, openers = parse_explicit_billing(
            "KNATS • TUKAN [OPENING DES AFTERS JAZZ À LA VILLETTE #01]"
        )
        self.assertEqual("KNATS", headliner)
        self.assertEqual(["TUKAN"], openers)

    def test_ordinary_dice_cobill_is_not_reinterpreted_as_support(self):
        headliner, openers = parse_explicit_billing("Artist A + Artist B")
        self.assertEqual("Artist A + Artist B", headliner)
        self.assertIsNone(openers)

    def test_radical_explicit_first_part_is_retained(self):
        card = BeautifulSoup(
            """
            <div class="concert-card">
              <div class="concert-card__date">27 <span>sept. 2026</span></div>
              <div class="concert-card__place_m">PARIS</div>
              <div class="concert-card__event">Trabendo</div>
              <a class="concert-card__title">The Afghan Whigs</a>
              <div class="concert-card__infos">Première partie : Ed Harcourt</div>
              <a class="concert-card__link" href="https://tickets.example/afghan">Réserver</a>
            </div>
            """,
            "html.parser",
        ).select_one(".concert-card")

        parsed = parse_radical_card(card)
        self.assertEqual("The Afghan Whigs", parsed.headliner)
        self.assertEqual(["Ed Harcourt"], parsed.openers)


class TicketProductTests(unittest.TestCase):
    def test_pass_and_package_products_are_excluded(self):
        titles = [
            "DO YOU REMEMBER - PASS 2 JOURS - SAMEDI/DIMANCHE",
            "DO YOU REMEMBER FESTIVAL - PASS 1 JOUR - SAMEDI",
            "Festival weekend pass",
            "Artist VIP package",
            "PACKAGE HOLLYWOOD VAMPIRES",
            "URIAH HEEP UPGRADE",
            "THOMAS BERGERSEN LIVE VIP UPGRADE",
            "Artist meet-and-greet package",
            "Artist parking pass",
        ]
        self.assertTrue(all(is_ticket_product_title(title) for title in titles))
        self.assertTrue(
            all(not is_supported_event(event(title, venue="Le Trabendo")) for title in titles)
        )

    def test_artist_name_containing_package_token_is_not_excluded(self):
        self.assertFalse(is_ticket_product_title("The Package"))
        self.assertTrue(is_supported_event(event("The Package", venue="Le Trabendo")))


class WeakRawGenrePrecedenceTests(unittest.TestCase):

    def test_reviewed_artist_mapping_overrides_weak_rock_source_genre(self):
        from concert_calendar.genres import enrich_event_genres

        events = [
            event("DEEP PURPLE", venue="Adidas Arena"),
            event("URIAH HEEP", venue="Casino de Paris"),
        ]

        for item in events:
            item.genre = "Rock"

        enrich_event_genres(events)

        self.assertEqual(
            ["Metal / Hard Rock", "Metal / Hard Rock"],
            [item.genre_public for item in events],
        )
        self.assertEqual(
            ["artist_mapping", "artist_mapping"],
            [item.genre_method for item in events],
        )

    def test_unreviewed_artist_still_uses_weak_rock_source_genre(self):
        from concert_calendar.genres import enrich_event_genres

        item = event(
            "Definitely Not A Reviewed Artist XYZ",
            venue="Le Trabendo",
        )
        item.genre = "Rock"

        enrich_event_genres([item])

        self.assertEqual("Rock / Indie / Punk", item.genre_public)
        self.assertEqual("source_mapping", item.genre_method)


class EditorialGenreOverrideTests(unittest.TestCase):

    def test_editorial_override_resolves_cross_bucket_conflict(self):
        from concert_calendar.genres import enrich_event_genres

        events = [
            event("Hollywood Vampires", venue="Adidas Arena"),
            event("EAGLES OF DEATH METAL", venue="Le Trianon"),
        ]

        events[0].genre_evidence = [
            {"raw": "Rock", "source": "GDP"},
            {"raw": "Metal / Hard Rock", "source": "Other"},
        ]
        events[1].genre_evidence = [
            {"raw": "Rock", "source": "Source 1"},
            {"raw": "Metal / Hard Rock", "source": "Source 2"},
        ]

        enrich_event_genres(events)

        self.assertEqual(
            ["Metal / Hard Rock", "Metal / Hard Rock"],
            [item.genre_public for item in events],
        )
        self.assertEqual(
            ["manual_override", "manual_override"],
            [item.genre_method for item in events],
        )


class VerifiedDisplayNameTests(unittest.TestCase):

    def test_verified_all_caps_artist_names_are_canonicalized(self):
        from concert_calendar.deduplication import deduplicate_events

        events = [
            event("DEEP PURPLE", venue="Adidas Arena"),
            event("URIAH HEEP", venue="Casino de Paris"),
            event("HOLLYWOOD VAMPIRES", venue="Adidas Arena"),
            event("EAGLES OF DEATH METAL", venue="Le Trianon"),
            event("CHVRCHES", venue="Le Zénith Paris – La Villette"),
        ]

        result = deduplicate_events(events)

        self.assertEqual(
            [
                "Deep Purple",
                "Uriah Heep",
                "Hollywood Vampires",
                "Eagles of Death Metal",
                "CHVRCHES",
            ],
            [item.headliner for item in result],
        )


if __name__ == "__main__":
    unittest.main()
