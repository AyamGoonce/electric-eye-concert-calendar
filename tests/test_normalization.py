import unittest

from concert_calendar.deduplication import (
    deduplicate_events,
    normalize_headliner,
)
from concert_calendar.models import ConcertEvent
from concert_calendar.scrapers.gdp import normalize_date as normalize_gdp_date
from concert_calendar.scrapers.dice import parse_event as parse_dice_event
from concert_calendar.scrapers.livenation import document_to_event
from concert_calendar.scrapers.cigale import parse_detail_metadata
from concert_calendar.scrapers.maroquinerie import parse_card
from concert_calendar.scraper_loader import discover_scrapers
from concert_calendar.sources import is_supported_event
from concert_calendar.venues import normalize_event_venue
from concert_calendar.scrapers.olympia import parse_item as parse_olympia_item


def make_event(headliner, venue="La Boule Noire"):
    return ConcertEvent(
        date="2026-09-27",
        headliner=headliner,
        venue=venue,
        city="Paris",
        department="75",
    )


class ArtistNormalizationTests(unittest.TestCase):
    def test_known_joined_artist_alias_merges(self):
        events = deduplicate_events(
            [make_event("Day We Ran"), make_event("DAYWERAN")]
        )

        self.assertEqual(1, len(events))

    def test_known_diacritic_variant_merges(self):
        events = deduplicate_events(
            [make_event("GAËLLE JOLY"), make_event("GAELLE JOLY")]
        )

        self.assertEqual(1, len(events))

    def test_known_source_punctuation_variants_merge(self):
        pairs = [
            ("LA P’TITÉ FUMÉE", "LA P’TITE FUMÉE"),
            (
                "ZOH AMBA (LES FEMMES S’EN MÊLENT)",
                "Zoh Amba (Les Femmes s'en Mêlent)",
            ),
        ]

        for left, right in pairs:
            with self.subTest(left=left, right=right):
                self.assertEqual(
                    1,
                    len(deduplicate_events([make_event(left), make_event(right)])),
                )

    def test_quality_audit_artist_variants_merge(self):
        pairs = [
            ("F.F.F.", "FFF"),
            ("Sebastien Tellier", "Sébastien Tellier"),
            ("GREGOIRE JOKIC", "Grégoire Jokic"),
            ("LA SECURITE", "La Sécurité"),
            ("Howlin’ Jaws", "Howlin' Jaws"),
            ("Alison’s Halo", "Alison's Halo"),
            ("NOE PRESZOW", "NOÉ PRESZOW"),
        ]

        for left, right in pairs:
            with self.subTest(left=left, right=right):
                self.assertEqual(
                    1,
                    len(
                        deduplicate_events(
                            [make_event(left), make_event(right)]
                        )
                    ),
                )

    def test_unlisted_spacing_difference_does_not_merge(self):
        events = deduplicate_events(
            [make_event("AB CD"), make_event("ABCD")]
        )

        self.assertEqual(2, len(events))

    def test_meaningful_punctuation_is_preserved(self):
        self.assertNotEqual(
            normalize_headliner("Artist + Guest"),
            normalize_headliner("Artist Guest"),
        )

    def test_distinct_time_suffixes_do_not_merge(self):
        events = deduplicate_events(
            [make_event("TIGERCUB – 16H"), make_event("TIGERCUB – 20H")]
        )

        self.assertEqual(2, len(events))

    def test_duplicate_metadata_is_merged(self):
        first = make_event("Day We Ran")
        first.promoters = ["AEG Presents France"]
        second = make_event("DAYWERAN")
        second.openers = ["Support Act"]
        second.genre = "Rock"
        second.ticket_url = "https://example.com/tickets"

        merged = deduplicate_events([first, second])[0]

        self.assertEqual(["AEG Presents France"], merged.promoters)
        self.assertEqual(["Support Act"], merged.openers)
        self.assertEqual("Rock", merged.genre)
        self.assertEqual("https://example.com/tickets", merged.ticket_url)

    def test_corroborated_mixed_case_spelling_is_used_for_display(self):
        uppercase = make_event("HOLLYWOOD VAMPIRES")
        mixed_case = make_event("Hollywood Vampires")

        merged = deduplicate_events([uppercase, mixed_case])

        self.assertEqual("Hollywood Vampires", merged[0].headliner)

    def test_uncorroborated_uppercase_spelling_is_preserved(self):
        merged = deduplicate_events([make_event("CHVRCHES")])

        self.assertEqual("CHVRCHES", merged[0].headliner)


class BillingReconciliationTests(unittest.TestCase):
    def test_structured_bill_merges_full_bill_and_inherits_ticket(self):
        structured = make_event("Michael Cera Palin", "Supersonic")
        structured.date = "2026-08-25"
        structured.openers = ["Club Bombardier", "Handbrace"]
        structured.promoters = ["Supersonic"]
        full_bill = make_event(
            "Michael Cera Palin + Club Bombardier + Handbrace",
            "Supersonic",
        )
        full_bill.date = "2026-08-25"
        full_bill.ticket_url = "https://dice.fm/event/michael-cera-palin"

        merged = deduplicate_events([structured, full_bill])

        self.assertEqual(1, len(merged))
        self.assertEqual("Michael Cera Palin", merged[0].headliner)
        self.assertEqual(["Club Bombardier", "Handbrace"], merged[0].openers)
        self.assertEqual(
            "https://dice.fm/event/michael-cera-palin",
            merged[0].ticket_url,
        )

    def test_structured_bill_keeps_official_ticket(self):
        structured = make_event("Headliner", "Supersonic")
        structured.openers = ["Support"]
        structured.ticket_url = "https://official.example/event"
        full_bill = make_event("Headliner + Support", "Supersonic")
        full_bill.ticket_url = "https://dice.fm/event/duplicate"

        merged = deduplicate_events([structured, full_bill])

        self.assertEqual("https://official.example/event", merged[0].ticket_url)

    def test_ambiguous_co_headliner_bill_does_not_merge(self):
        first = make_event("Artist A + Artist B")
        second = make_event("Artist A")

        self.assertEqual(2, len(deduplicate_events([first, second])))

    def test_unrelated_same_date_and_venue_artist_does_not_merge(self):
        structured = make_event("Headliner")
        structured.openers = ["Support"]
        unrelated = make_event("Different Artist")

        self.assertEqual(2, len(deduplicate_events([structured, unrelated])))

    def test_explicit_support_card_requires_shared_event_evidence(self):
        parent = make_event("Headliner")
        parent.openers = ["Support"]
        support = make_event("Support")

        self.assertEqual(2, len(deduplicate_events([parent, support])))

        parent.promoters = ["Official Promoter"]
        support.promoters = ["Official Promoter"]
        merged = deduplicate_events([parent, support])

        self.assertEqual(1, len(merged))
        self.assertEqual("Headliner", merged[0].headliner)
        self.assertEqual(["Support"], merged[0].openers)

    def test_hollywood_vampires_verified_support_is_one_concert(self):
        ticket = (
            "https://www.gdp.fr/fr/catalogue/"
            "hollywood-vampires-paris-2026-08-26-1"
        )
        headliner = make_event("HOLLYWOOD VAMPIRES", "Adidas Arena")
        headliner.date = "2026-08-26"
        headliner.promoters = ["Gérard Drouot Productions"]
        headliner.ticket_url = ticket
        support = make_event("THE LAST INTERNATIONALE", "Adidas Arena")
        support.date = "2026-08-26"
        support.promoters = ["Gérard Drouot Productions"]
        support.ticket_url = ticket

        merged = deduplicate_events([headliner, support])

        self.assertEqual(1, len(merged))
        self.assertEqual("Hollywood Vampires", merged[0].headliner)
        self.assertEqual(["The Last Internationale"], merged[0].openers)
        self.assertEqual(ticket, merged[0].ticket_url)


class VenueNormalizationTests(unittest.TestCase):
    def test_final_clear_venue_aliases_normalize(self):
        examples = {
            "La Marberie": "La Marbrerie",
            "La Marbrerie": "La Marbrerie",
            "Backstage": "Backstage By The Mill",
            "Backstage by the Mill": "Backstage By The Mill",
            "Backstage By The Mill": "Backstage By The Mill",
            "Le Backstage by the Mill": "Backstage By The Mill",
        }
        for source, expected in examples.items():
            item = ConcertEvent("2026-09-01", "Artist", source, "Paris", "75")
            normalize_event_venue(item)
            self.assertEqual(expected, item.venue)

    def test_article_variant_normalizes_to_point_ephemere(self):
        event = normalize_event_venue(
            make_event("MERYL STREEK", "LE POINT ÉPHÉMÈRE")
        )

        self.assertEqual("Point Éphémère", event.venue)

    def test_distinct_neighboring_venues_remain_distinct(self):
        cigale = normalize_event_venue(make_event("Artist", "La Cigale"))
        boule_noire = normalize_event_venue(
            make_event("Artist", "La Boule Noire")
        )

        self.assertNotEqual(cigale.venue, boule_noire.venue)

    def test_distinct_rooms_remain_distinct(self):
        sunset = normalize_event_venue(make_event("Artist", "Sunset"))
        sunside = normalize_event_venue(make_event("Artist", "Sunside"))

        self.assertNotEqual(sunset.venue, sunside.venue)

    def test_safe_spelling_and_article_variants_normalize(self):
        aliases = {
            "Babour Sauvage": "Cabaret Sauvage",
            "CIRQUE D'HIVER": "Cirque d'Hiver Bouglione",
            "Le Café de la Danse": "Café de la Danse",
            "L'ÉLYSÉE MONTMARTRE": "Élysée Montmartre",
            "NEW MORNING": "New Morning",
            "Le Nouveau Casino": "Nouveau Casino",
            "POPUP!": "Le Pop-Up du Label",
        }

        for source, expected in aliases.items():
            with self.subTest(source=source):
                event = normalize_event_venue(make_event("Artist", source))
                self.assertEqual(expected, event.venue)

    def test_distinct_seine_musicale_room_remains_named(self):
        event = normalize_event_venue(
            make_event("Artist", "SEINE MUSICALE - GRANDE SEINE")
        )

        self.assertEqual("La Seine Musicale – Grande Seine", event.venue)

    def test_clear_venue_capitalization_variants_share_canonical_labels(self):
        groups = {
            "La Batterie": ["LA BATTERIE", "La Batterie"],
            "La CLEF": ["La clef", "La CLEF", "LA CLEF"],
            "Le POC": ["Le Poc", "Le POC"],
            "Théâtre de Rungis": ["THEATRE DE RUNGIS", "Théâtre de Rungis"],
        }

        for expected, variants in groups.items():
            with self.subTest(expected=expected):
                normalized = {
                    normalize_event_venue(make_event("Artist", variant)).venue
                    for variant in variants
                }
                self.assertEqual({expected}, normalized)


class EventScopeTests(unittest.TestCase):
    def test_release_party_concert_is_supported(self):
        self.assertTrue(
            is_supported_event(make_event("Artist – Album Release Party"))
        )

    def test_dice_style_release_party_cobill_is_supported(self):
        self.assertTrue(
            is_supported_event(
                make_event("ARTIST (RELEASE PARTY) + GUEST")
            )
        )

    def test_bloc_party_artist_is_supported(self):
        self.assertTrue(
            is_supported_event(make_event("Bloc Party + Interpol"))
        )

    def test_bloc_party_night_is_not_artist_exception(self):
        self.assertFalse(
            is_supported_event(make_event("Bloc Party Night"))
        )

    def test_generic_party_remains_excluded(self):
        self.assertFalse(is_supported_event(make_event("Friday Party")))

    def test_dj_release_party_remains_excluded(self):
        self.assertFalse(
            is_supported_event(
                make_event("Album Release Party – DJ Set")
            )
        )

    def test_viewing_party_remains_excluded(self):
        self.assertFalse(
            is_supported_event(make_event("Finale Viewing Party"))
        )


class SourcePriorityTests(unittest.TestCase):
    def test_aggregator_loads_after_official_sources(self):
        scrapers = discover_scrapers()
        dice_index = next(
            index
            for index, scraper in enumerate(scrapers)
            if scraper.SOURCE_NAME == "DICE"
        )

        self.assertEqual(len(scrapers) - 1, dice_index)
        self.assertTrue(
            all(
                getattr(scraper, "SOURCE_PRIORITY", 0)
                < getattr(scrapers[dice_index], "SOURCE_PRIORITY", 0)
                for scraper in scrapers[:dice_index]
            )
        )

    def test_aggregator_merge_preserves_official_base_metadata(self):
        official = make_event("Artist")
        official.city = "Paris"
        official.promoters = ["Official Promoter"]
        official.ticket_url = "https://official.example/event"
        aggregator = make_event("Artist")
        aggregator.city = "Wrong City"
        aggregator.promoters = None
        aggregator.ticket_url = "https://aggregator.example/event"

        merged = deduplicate_events([official, aggregator])[0]

        self.assertEqual("Paris", merged.city)
        self.assertEqual(["Official Promoter"], merged.promoters)
        self.assertEqual("https://official.example/event", merged.ticket_url)


class MetadataMergeTests(unittest.TestCase):

    def test_merge_preserves_new_optional_metadata(self):
        from concert_calendar.deduplication import merge_events

        existing = ConcertEvent(
            date="2026-09-08",
            headliner="Slow Pilot",
            venue="La Cigale",
            city="Paris",
            department="75",
        )

        incoming = ConcertEvent(
            date="2026-09-08",
            headliner="Slow Pilot",
            venue="La Cigale",
            city="Paris",
            department="75",
            co_headliners=["Co-Headliner"],
            event_title="The Songs of Jeff Buckley",
            series_name="Special Presentation",
            image_url="https://lacigale.fr/example.jpg",
            image_source="La Cigale",
            electric_eye_links=[
                {
                    "label": "Review",
                    "url": "https://www.electriceyerock.com/example",
                    "kind": "artist",
                }
            ],
        )

        merged = merge_events(existing, incoming)

        self.assertEqual("The Songs of Jeff Buckley", merged.event_title)
        self.assertEqual("Special Presentation", merged.series_name)
        self.assertEqual("https://lacigale.fr/example.jpg", merged.image_url)
        self.assertEqual("La Cigale", merged.image_source)
        self.assertEqual(
            "https://www.electriceyerock.com/example",
            merged.electric_eye_links[0]["url"],
        )


class SourceQualityTests(unittest.TestCase):
    def test_olympia_explicit_complet_status_is_sold_out(self):
        item = {
            "post_title": "Sold Out Artist",
            "permalink": "https://www.olympiahall.com/agenda/sold-out-artist/",
            "terms": {"genre": [{"name": "Rock"}]},
            "meta": {
                "begin_date_ymd": "2027-01-02",
                "end_date_ymd": "2027-01-02",
                "infos_text_status": "Complet",
            },
        }
        parsed = parse_olympia_item(item)
        self.assertEqual(1, len(parsed))
        self.assertTrue(parsed[0].sold_out)

    def test_dice_release_party_has_no_invented_promoter_or_openers(self):
        event = parse_dice_event(
            {
                "id": "event-id",
                "name": "Artist – Release Party",
                "dates": {"event_start_date": "2026-10-12T20:00:00+02:00"},
                "venues": [
                    {"name": "Point Éphémère", "city": {"name": "Paris"}}
                ],
            }
        )

        self.assertEqual("Artist – Release Party", event.headliner)
        self.assertEqual("2026-10-12", event.date)
        self.assertIsNone(event.promoters)
        self.assertIsNone(event.openers)

    def test_dice_named_cobill_uses_co_headliners_not_openers(self):
        event = parse_dice_event(
            {
                "id": "automatic-test",
                "name": "AUTOMATIC (US) + LEO VINCENT",
                "status": "sold-out",
                "images": {
                    "square": "https://dice-media.imgix.net/automatic.jpg"
                },
                "dates": {
                    "event_start_date": "2026-09-01T19:30:00+02:00"
                },
                "venues": [
                    {"name": "Le Chinois", "city": {"name": "Paris"}}
                ],
            }
        )

        self.assertEqual("AUTOMATIC (US)", event.headliner)
        self.assertEqual(["LEO VINCENT"], event.co_headliners)
        self.assertIsNone(event.openers)
        self.assertEqual(
            "AUTOMATIC (US) + LEO VINCENT",
            event.event_title,
        )
        self.assertEqual("19:30", event.start_time)
        self.assertEqual("sold_out", event.ticket_status)
        self.assertTrue(event.sold_out)
        self.assertEqual(
            "https://dice-media.imgix.net/automatic.jpg",
            event.image_url,
        )
        self.assertEqual("DICE", event.image_source)

    def test_dice_placeholder_support_is_not_promoted_to_artist(self):
        event = parse_dice_event(
            {
                "id": "placeholder-test",
                "name": "JOE YORKE + 1ère partie",
                "dates": {
                    "event_start_date": "2026-09-02T20:00:00+02:00"
                },
                "venues": [
                    {"name": "Test Venue", "city": {"name": "Paris"}}
                ],
            }
        )

        self.assertEqual("JOE YORKE + 1ère partie", event.headliner)
        self.assertIsNone(event.co_headliners)
        self.assertIsNone(event.openers)

    def test_dice_mardi_jazz_uses_series_and_real_musicians(self):
        from unittest.mock import patch

        description = """Tous les mardis...

Dmitry Boevsky • Saxophone Alto
Sandro Zerafa • Guitare
Tom Guillois • Contrebasse
Stéphane Chandelier • Batterie
"""

        with patch(
            "concert_calendar.scrapers.dice.fetch_dice_detail_description",
            return_value=description,
        ):
            event = parse_dice_event(
                {
                    "id": "mardi-jazz-test",
                    "name": "Mardi Jazz!",
                    "status": "on-sale",
                    "images": {
                        "square": "https://dice-media.imgix.net/mardi-jazz.jpg"
                    },
                    "dates": {
                        "event_start_date": "2026-08-25T20:00:00+02:00"
                    },
                    "venues": [
                        {"name": "POPUP!", "city": {"name": "Paris"}}
                    ],
                }
            )

        self.assertEqual("Dmitry Boevsky", event.headliner)
        self.assertEqual(
            ["Sandro Zerafa", "Tom Guillois", "Stéphane Chandelier"],
            event.openers,
        )
        self.assertEqual("Mardi Jazz!", event.series_name)
        self.assertEqual("Mardi Jazz!", event.event_title)

    def test_cigale_structured_detail_exposes_real_performer_and_metadata(self):
        class FakeResponse:
            def __init__(self, text):
                self.text = text

            def raise_for_status(self):
                return None

        class FakeSession:
            def get(self, url, headers=None, timeout=None):
                return FakeResponse(
                    """
                    <html>
                    <head>
                    <script type="application/ld+json">
                    {
                      "@context": "https://schema.org",
                      "@type": "Event",
                      "name": "THE SONGS OF JEFF BUCKLEY",
                      "performer": [
                        {
                          "@type": "MusicGroup",
                          "name": "SLOW PILOT"
                        }
                      ],
                      "startDate": "2026-09-08T20:00:00+02:00",
                      "image": "https://lacigale.fr/wp-content/uploads/slow-pilot.png"
                    }
                    </script>
                    </head>
                    </html>
                    """
                )

        result = parse_detail_metadata(
            FakeSession(),
            "https://lacigale.fr/evenements/slow-pilot-tribute-jeff-buckley/",
        )

        self.assertEqual("THE SONGS OF JEFF BUCKLEY", result["event_title"])
        self.assertEqual(["SLOW PILOT"], result["performers"])
        self.assertEqual("2026-09-08T20:00:00+02:00", result["start_date"])
        self.assertEqual(
            "https://lacigale.fr/wp-content/uploads/slow-pilot.png",
            result["image_url"],
        )

    def test_gdp_normalizes_datetime_to_calendar_date(self):
        self.assertEqual(
            "2026-10-12",
            normalize_gdp_date("2026-10-12T20:00:00+02:00"),
        )

    def test_gdp_reviewed_festival_day_keeps_festival_as_venue_and_full_bill(self):
        from bs4 import BeautifulSoup
        from concert_calendar.scrapers.gdp import parse_card as parse_gdp_card

        card = BeautifulSoup(
            """
            <div class="gdpEvtCardCtnt">
              <span class="gdpEvtCardGenre">Hard / Metal</span>
              <h3 class="gdpEvtCardName">
                <a href="https://mmfestival.mapado.com/event/672126-mennecy-metal-fest">
                  SAXON
                </a>
              </h3>
              <time class="gdpEvtCardDate" datetime="2026-09-04T20:00:00+02:00"></time>
              <div class="gdpEvtCardLoc">
                <span class="gdpEvtCardCity">MENNECY</span>
                <span class="gdpEvtCardVenue">Mennecy Metal Fest</span>
              </div>
            </div>
            """,
            "html.parser",
        )

        event = parse_gdp_card(card)

        self.assertEqual("Saxon", event.headliner)
        self.assertEqual("Mennecy Metal Fest", event.venue)
        self.assertEqual("Mennecy Metal Fest", event.festival_name)
        self.assertTrue(event.authoritative_billing)
        self.assertEqual(
            [
                "Amon Sethis",
                "Oomph!",
                "No One Is Innocent",
                "Prophecy 23",
                "Titan",
                "TrollHeart",
                "USQUAM",
                "Ghost Anthem",
            ],
            event.openers,
        )

    def test_livenation_normalizes_date_and_relative_event_url(self):
        event = document_to_event(
            {
                "name": "Artist",
                "eventDate": "2027-01-22T00:00:00Z",
                "venue": {"name": "Bataclan", "city": "Paris"},
                "localizations": [
                    {
                        "cultureName": "fr-FR",
                        "url": "/event/artist-paris-tickets-edp1",
                    }
                ],
            }
        )

        self.assertEqual("2027-01-22", event.date)
        self.assertEqual(
            "https://www.livenation.fr/event/artist-paris-tickets-edp1",
            event.ticket_url,
        )

    def test_maroquinerie_keeps_facebook_out_of_ticket_url(self):
        from bs4 import BeautifulSoup

        card = BeautifulSoup(
            """
            <article>
              <a href="/fr/agenda/view/artist/"></a>
              <div class="thumbnail"><h2>Artist</h2></div>
              <h3 class="date">10 octobre</h3>
              <div class="booking">
                <a href="https://www.facebook.com/events/123/">Facebook</a>
              </div>
            </article>
            """,
            "html.parser",
        )

        event = parse_card(card, 2026)

        self.assertEqual(
            "https://www.facebook.com/events/123/",
            event.facebook_event_url,
        )
        self.assertEqual(
            "https://www.lamaroquinerie.fr/fr/agenda/view/artist/",
            event.ticket_url,
        )


if __name__ == "__main__":
    unittest.main()
