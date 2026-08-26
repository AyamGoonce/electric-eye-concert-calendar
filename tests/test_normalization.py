import unittest
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

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
from concert_calendar.scrapers.seine_musicale import parse_detail as parse_seine_detail
from concert_calendar.scrapers.veryshow import post_to_event as parse_veryshow_post
from concert_calendar.scrapers.accor_arena import (
    extract_explicit_support as extract_accor_support,
    parse_item as parse_accor_item,
)
from concert_calendar.scrapers.aeg import parse_detail_page as parse_aeg_detail
from concert_calendar.scrapers.petit_bain import (
    find_relocated_venue,
    strip_relocation_notice,
)


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

    def test_unlisted_diacritic_variant_merges(self):
        events = deduplicate_events(
            [make_event("Etran de l'Aïr"), make_event("Étran de l'Aïr")]
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

    def test_reviewed_identity_variants_merge_without_global_fuzziness(self):
        pairs = [
            ("Flamin' Groovies", "The Flamin' Groovies"),
            ("Kiwi JR", "Kiwi Jr."),
            ("Westside Cowboy", "Westside Cowboys"),
            ("LA 808E NUIT", "La 808ème Nuit"),
        ]
        for left, right in pairs:
            with self.subTest(left=left, right=right):
                self.assertEqual(
                    1, len(deduplicate_events([make_event(left), make_event(right)]))
                )

    def test_html_entities_decode_before_identity_and_display(self):
        variants = [
            "LA P&amp;TITE FUMÉE",
            "LA P&rsquo;TITE FUMÉE",
            "LA P'TITE FUMÉE",
            "LA P’TITÉ FUMÉE",
        ]
        ampersand = deduplicate_events([make_event(variants[0])])[0]
        apostrophes = deduplicate_events([make_event(value) for value in variants[1:]])

        self.assertEqual("LA P&TITE FUMÉE", ampersand.headliner)
        self.assertEqual(1, len(apostrophes))
        self.assertNotIn("&rsquo;", apostrophes[0].headliner)

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
    def test_four_reviewed_shared_ticket_bills_are_event_scoped(self):
        cases = [
            (
                "2026-11-16", "Le Zénith Paris – La Villette",
                "Bloc Party", "Interpol", "Bloc Party", None, ["Interpol"],
            ),
            (
                "2026-12-02", "Paul B – Massy", "Gildaa", "Alma Rechtman",
                "Alma Rechtman", None, ["Gildaa"],
            ),
            (
                "2026-12-07", "Le Zénith Paris – La Villette",
                "Electric Pyramid", "The Dire Straits Experience",
                "The Dire Straits Experience", ["Electric Pyramid"], None,
            ),
            (
                "2027-02-16", "La Maroquinerie", "Escape The Internet", "BERNTH",
                "Escape The Internet (feat. Bernth)", None, None,
            ),
        ]
        for date, venue, left_name, right_name, headliner, openers, coheads in cases:
            with self.subTest(headliner=headliner):
                left, right = make_event(left_name, venue), make_event(right_name, venue)
                left.date = right.date = date
                left.ticket_url = right.ticket_url = "https://tickets.example/reviewed"
                left.source_names, right.source_names = ["Official"], ["DICE"]

                result = deduplicate_events([left, right])

                self.assertEqual(1, len(result))
                self.assertEqual(headliner, result[0].headliner)
                self.assertEqual(openers, result[0].openers)
                self.assertEqual(coheads, result[0].co_headliners)
                searchable = " ".join([
                    result[0].headliner, *(result[0].openers or []),
                    *(result[0].co_headliners or []),
                ]).casefold()
                self.assertIn(left_name.casefold(), searchable)
                self.assertIn(right_name.casefold(), searchable)

    def test_escape_the_internet_override_does_not_apply_elsewhere(self):
        escape, bernth = make_event("Escape The Internet"), make_event("BERNTH")
        escape.date = bernth.date = "2027-02-17"
        result = deduplicate_events([escape, bernth])
        self.assertEqual(2, len(result))
        self.assertNotIn("feat.", " ".join(event.headliner for event in result))

    def test_reviewed_paris_jackson_move_merges_stale_dice_venue(self):
        stale = make_event("Paris Jackson", "L'Alhambra")
        official = make_event("Paris Jackson", "La Bellevilloise")
        stale.date = official.date = "2026-10-10"
        stale.source_names = ["DICE"]
        official.source_names = ["AEG Presents France"]

        result = deduplicate_events([stale, official])

        self.assertEqual(1, len(result))
        self.assertEqual("La Bellevilloise", result[0].venue)
        self.assertEqual(
            ["AEG Presents France", "DICE"], sorted(result[0].source_names)
        )

    def test_status_difference_does_not_split_same_event(self):
        available = make_event("Same Artist")
        sold_out = make_event("Same Artist")
        sold_out.sold_out = True
        sold_out.ticket_status = "sold_out"

        result = deduplicate_events([available, sold_out])

        self.assertEqual(1, len(result))
        self.assertTrue(result[0].sold_out)
        self.assertEqual("sold_out", result[0].ticket_status)

    def test_reviewed_wolfgang_voigt_project_titles_merge(self):
        plain = make_event("Wolfgang Voigt", "La Gaîté Lyrique")
        project = make_event("WOLFGANG VOIGT presents GAS live", "La Gaîté Lyrique")
        plain.date = project.date = "2026-09-23"

        result = deduplicate_events([plain, project])

        self.assertEqual(1, len(result))
        self.assertEqual("WOLFGANG VOIGT presents GAS live", result[0].headliner)

    def test_reviewed_augusta_full_band_titles_merge_and_keep_sold_out(self):
        plain = make_event("Augusta", "Le Hasard Ludique")
        full_band = make_event("Augusta (full band)", "Le Hasard Ludique")
        plain.date = full_band.date = "2026-09-30"
        full_band.sold_out = True
        full_band.ticket_status = "sold_out"

        result = deduplicate_events([plain, full_band])

        self.assertEqual(1, len(result))
        self.assertEqual("Augusta (full band)", result[0].headliner)
        self.assertTrue(result[0].sold_out)
        self.assertEqual("sold_out", result[0].ticket_status)

    def test_additional_reviewed_descriptive_titles_merge(self):
        cases = [
            (
                "2026-09-19", "Accor Arena", "The Pussycat Dolls",
                "THE PUSSYCAT DOLLS - PCD FOREVER TOUR",
            ),
            (
                "2026-10-28", "La Boule Noire", "Crenoka",
                "CRENOKA (RELEASE PARTY)",
            ),
            (
                "2026-11-02", "Accor Arena", "The World of Hans Zimmer",
                "THE WORLD OF HANS ZIMMER - A NEW DIMENSION",
            ),
            (
                "2027-03-18", "L'Olympia Bruno Coquatrix", "Chloé",
                "CHLOÉ (Live)",
            ),
        ]
        for event_date, venue, left_title, right_title in cases:
            with self.subTest(title=left_title):
                left = make_event(left_title, venue)
                right = make_event(right_title, venue)
                left.date = right.date = event_date
                self.assertEqual(1, len(deduplicate_events([left, right])))

    def test_reviewed_five_finger_bill_keeps_official_special_guests(self):
        official = make_event("FIVE FINGER DEATH PUNCH", "Accor Arena")
        promoter = make_event(
            "Five Finger Death Punch et Lamb Of God", "Accor Arena"
        )
        official.date = promoter.date = "2027-02-10"
        official.openers = ["Lamb of God", "Bleed From Within"]
        official.authoritative_billing = True

        result = deduplicate_events([official, promoter])

        self.assertEqual(1, len(result))
        self.assertEqual("FIVE FINGER DEATH PUNCH", result[0].headliner)
        self.assertEqual(["Lamb of God", "Bleed From Within"], result[0].openers)

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

    def test_structured_co_headliner_reconciles_with_full_bill(self):
        structured = make_event("Bedouine", "La Marbrerie (Montreuil)")
        structured.date = "2026-09-07"
        structured.co_headliners = ["Barbara Forstner"]
        full = make_event("Bedouine + Barbara Forstner", "La Marbrerie")
        full.date = "2026-09-07"
        for item in (structured, full):
            normalize_event_venue(item)

        merged = deduplicate_events([structured, full])

        self.assertEqual(1, len(merged))
        self.assertEqual(["Barbara Forstner"], merged[0].co_headliners)
        self.assertEqual("La Marbrerie", merged[0].venue)
        self.assertEqual("Montreuil", merged[0].city)

    def test_moved_structured_co_headliner_keeps_role(self):
        stale = make_event("My New Band Believe", "Point Éphémère")
        stale.date = "2026-10-19"
        stale.co_headliners = ["Jasper Llewellyn"]
        current = make_event(
            "MY NEW BAND BELIEVE + Jasper Llewellyn", "La Maroquinerie"
        )
        current.date = "2026-10-19"
        for item in (stale, current):
            normalize_event_venue(item)

        merged = deduplicate_events([stale, current])

        self.assertEqual(1, len(merged))
        self.assertEqual("La Maroquinerie", merged[0].venue)
        self.assertEqual(["Jasper Llewellyn"], merged[0].co_headliners)

    def test_terminal_generic_guest_requires_strong_evidence(self):
        plain = make_event("The Dear Hunter", "Petit Bain")
        marked = make_event("The Dear Hunter + Guest", "Petit Bain")
        self.assertEqual(2, len(deduplicate_events([plain, marked])))

        plain.promoters = ["Official Promoter"]
        marked.promoters = ["Official Promoter"]
        self.assertEqual(1, len(deduplicate_events([plain, marked])))

    def test_terminal_generic_guest_known_pairs_merge_with_shared_promoter(self):
        for plain_name, marked_name in [
            ("Boris", "Boris + Guest"),
            ("NERLOV", "NERLOV + Guest"),
            ("Fragile", "Fragile + Guest"),
            ("7 WEEKS", "7 Weeks + Guest"),
            ("BURNING HEADS", "Burning Heads + Guest"),
        ]:
            with self.subTest(plain=plain_name):
                plain, marked = make_event(plain_name), make_event(marked_name)
                plain.promoters = marked.promoters = ["Official Promoter"]
                self.assertEqual(1, len(deduplicate_events([plain, marked])))

    def test_terminal_guest_uses_official_plus_dice_corroboration(self):
        plain = make_event("NERLOV", "Point Éphémère")
        marked = make_event("NERLOV + Guest", "Point Éphémère")
        plain.source_names = ["Point Éphémère"]
        marked.source_names = ["DICE"]
        self.assertEqual(1, len(deduplicate_events([plain, marked])))

    def test_generic_ticket_page_is_not_shared_event_evidence(self):
        plain = make_event("Artist")
        marked = make_event("Artist + Guest")
        plain.ticket_url = marked.ticket_url = "https://tickets.example/events/"
        self.assertEqual(2, len(deduplicate_events([plain, marked])))

    def test_event_ticket_normalization_ignores_tracking_and_trailing_slash(self):
        plain = make_event("Metro Verlaine", "Point Éphémère")
        marked = make_event("Metro Verlaine + Guest", "Point Éphémère")
        plain.ticket_url = "https://dice.fm/event/metro-verlaine/?utm_source=venue"
        marked.ticket_url = "https://dice.fm/event/metro-verlaine"
        self.assertEqual(1, len(deduplicate_events([plain, marked])))

    def test_reviewed_descriptive_title_and_ronnie_wood_collapse(self):
        ftv = [
            make_event("FTV UNPLUGGED : carte blanche à GRANDMA'S ASHES", "Point Éphémère"),
            make_event("FTV UNPLUGGED : GRANDMA'S ASHES", "Point Éphémère"),
        ]
        for item in ftv:
            item.date = "2026-09-12"
        self.assertEqual(1, len(deduplicate_events(ftv)))

        ronnie = [
            make_event("RONNIE WOOD", "L'Olympia Bruno Coquatrix"),
            make_event("Ronnie Wood and His Band featuring Imelda May", "L'Olympia Bruno Coquatrix"),
        ]
        for item in ronnie:
            item.date = "2026-09-05"
            item.ticket_url = "https://www.olympiahall.com/agenda/ronnie-wood/"
        merged = deduplicate_events(ronnie)
        self.assertEqual(1, len(merged))
        self.assertEqual("Ronnie Wood and His Band featuring Imelda May", merged[0].headliner)

    def test_distinct_performance_titles_and_times_remain_separate(self):
        early = make_event("TIGERCUB – 16H")
        late = make_event("TIGERCUB – 20H")
        early.start_time, late.start_time = "16:00", "20:00"
        self.assertEqual(2, len(deduplicate_events([early, late])))

    def test_plain_timed_card_reconciles_only_matching_labeled_show(self):
        plain = make_event("TIGERCUB", "La Boule Noire")
        plain.start_time = "16:00"
        early = make_event("TIGERCUB – 16H", "La Boule Noire")
        late = make_event("TIGERCUB – 20H", "La Boule Noire")
        result = deduplicate_events([plain, early, late])
        self.assertEqual(2, len(result))
        self.assertEqual({"TIGERCUB – 16H", "TIGERCUB – 20H"}, {x.headliner for x in result})

    def test_generic_parent_does_not_create_third_multi_set_performance(self):
        parent = make_event("Mark Guiliana", "New Morning")
        parent.ticket_url = "https://official.example/mark-guiliana"
        first = make_event("Mark Guiliana - 1er set", "New Morning")
        second = make_event("Mark Guiliana - 2e set", "New Morning")
        first.start_time, second.start_time = "19:30", "21:30"

        result = deduplicate_events([parent, first, second])

        self.assertEqual(2, len(result))
        self.assertEqual({"19:30", "21:30"}, {item.start_time for item in result})
        self.assertTrue(all(item.ticket_url for item in result))

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
            "ESPACE CARPEAUX": "Espace Carpeaux",
            "LA SCALA PARIS": "La Scala Paris",
            "Le Zénith": "Le Zénith Paris – La Villette",
            "THÉÂTRE ALEXANDRE DUMAS": "Théâtre Alexandre Dumas",
            "Théâtre de L’Européen": "L'Européen",
        }

        for source, expected in aliases.items():
            with self.subTest(source=source):
                event = normalize_event_venue(make_event("Artist", source))
                self.assertEqual(expected, event.venue)

    def test_reviewed_philharmonie_variants_canonicalize(self):
        for venue in (
            "Philarmonie de Paris",
            "Philharmonie",
            "Philharmonie de Paris",
        ):
            with self.subTest(venue=venue):
                event = normalize_event_venue(make_event("Artist", venue))
                self.assertEqual("Philharmonie de Paris", event.venue)

    def test_festival_wrapper_canonicalizes_to_salle_gaveau(self):
        event = normalize_event_venue(
            make_event("Artist", "FESTIVAL CLASH (SALLE GAVEAU)")
        )
        self.assertEqual("Salle Gaveau", event.venue)

    def test_seine_musicale_rooms_share_canonical_public_venue(self):
        for venue in (
            "SEINE MUSICALE - GRANDE SEINE",
            "La Seine Musicale – Grande Seine (Boulogne-Billancourt)",
            "Grande Seine",
            "Auditorium Patrick Devedjian",
            "Petite Seine",
        ):
            with self.subTest(venue=venue):
                event = normalize_event_venue(make_event("Artist", venue))
                self.assertEqual("La Seine Musicale", event.venue)
                self.assertEqual("Boulogne-Billancourt", event.city)
                self.assertEqual("92", event.department)

    def test_seine_room_normalization_does_not_touch_unrelated_venue(self):
        event = normalize_event_venue(make_event("Artist", "Grande Salle"))
        self.assertEqual("Grande Salle", event.venue)

    def test_veryshow_support_copy_is_not_used_as_a_venue(self):
        event = parse_veryshow_post({
            "artists_titles": ["JINJER"],
            "date": "09/10/2026",
            "city": "PARIS (75)",
            "concert_hall": "En première partie de SPIRITBOX | La Seine Musicale",
            "link": "https://example.test/tickets",
        })
        self.assertEqual("SPIRITBOX", event.headliner)
        self.assertEqual(["JINJER"], event.openers)
        self.assertEqual("La Seine Musicale", event.venue)
        self.assertTrue(event.authoritative_billing)

    def test_seine_detail_parses_bireli_and_spiritbox_billing(self):
        bireli = parse_seine_detail(
            '<script type="application/ld+json">'
            '{"@type":"Event","name":"Biréli Lagrène",'
            '"startDate":"2026-11-04T20:30",'
            '"offers":{"url":"https://tickets.test/bireli"}}'
            '</script>',
            "https://example.test/bireli",
            {"Jazz, Musiques du monde"},
        )
        self.assertEqual(1, len(bireli))
        self.assertEqual("2026-11-04", bireli[0].date)
        self.assertEqual("20:30", bireli[0].start_time)
        self.assertEqual("La Seine Musicale", bireli[0].venue)
        self.assertEqual("Boulogne-Billancourt", bireli[0].city)
        self.assertEqual("92", bireli[0].department)

        spiritbox = parse_seine_detail(
            '<script type="application/ld+json">'
            '{"@type":"Event","name":"Spiritbox",'
            '"startDate":"2026-10-09T19:00"}'
            '</script><p>avec <strong>Jinjer</strong> et '
            '<strong>Dying Wish</strong> en invités spéciaux.</p>',
            "https://example.test/spiritbox",
            {"Hard Rock, Metal"},
        )
        self.assertEqual(["Jinjer", "Dying Wish"], spiritbox[0].openers)
        self.assertTrue(spiritbox[0].authoritative_billing)

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

    def test_accord_parfait_aliases_and_verified_geography(self):
        normalized = []
        for venue in ("L’Accord Parfait", "Studio L'Accord Parfait"):
            item = make_event("Joseph Schiano di Lombo", venue)
            item.city, item.department = "Unknown", ""
            normalized.append(normalize_event_venue(item))
        self.assertEqual({"L’Accord Parfait"}, {item.venue for item in normalized})
        self.assertEqual({"Paris"}, {item.city for item in normalized})
        self.assertEqual({"75"}, {item.department for item in normalized})

    def test_marbrerie_suffix_is_display_name_plus_structured_city(self):
        item = make_event("Bedouine", "La Marbrerie (Montreuil)")
        item.city, item.department = "Paris", "75"
        normalize_event_venue(item)
        self.assertEqual("La Marbrerie", item.venue)
        self.assertEqual("Montreuil", item.city)
        self.assertEqual("93", item.department)


class ReviewedMoveTests(unittest.TestCase):
    def test_confirmed_moves_resolve_only_reviewed_date_artist_pairs(self):
        cases = [
            ("2026-10-06", "Father of Peace", "L'Alhambra", "La Maroquinerie"),
            (
                "2026-10-06", "Humanity's Last Breath", "Petit Bain",
                "La Machine du Moulin Rouge",
            ),
            ("2026-10-19", "My New Band Believe", "Point Éphémère", "La Maroquinerie"),
            ("2026-11-20", "ZEBRAHEAD", "La Maroquinerie", "L'Alhambra"),
            ("2026-12-10", "Blondshell", "La Gaîté Lyrique", "Élysée Montmartre"),
        ]
        for date, artist, old, new in cases:
            with self.subTest(artist=artist):
                stale, current = make_event(artist, old), make_event(artist, new)
                stale.date = current.date = date
                for item in (stale, current):
                    normalize_event_venue(item)
                merged = deduplicate_events([stale, current])
                self.assertEqual(1, len(merged))
                self.assertEqual(new, merged[0].venue)

    def test_different_venues_without_reviewed_move_remain_separate(self):
        left = make_event("Unrelated Move Candidate", "Petit Bain")
        right = make_event("Unrelated Move Candidate", "La Maroquinerie")
        self.assertEqual(2, len(deduplicate_events([left, right])))


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

    def test_named_party_live_tour_is_supported(self):
        self.assertTrue(
            is_supported_event(make_event("Niall Horan - Dinner Party Live On Tour"))
        )

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

    def test_merge_preserves_provenance_status_time_and_announcement(self):
        from concert_calendar.deduplication import merge_events

        existing = make_event("Metadata Artist")
        existing.promoters = ["Official Promoter"]
        existing.ticket_url = "https://official.example/event"
        incoming = make_event("Metadata Artist")
        incoming.genre_public = "Rock / Indie / Punk"
        incoming.genre_source = "Official source"
        incoming.genre_method = "source_explicit"
        incoming.genre_evidence = [{"raw": "Rock", "source": "Official source"}]
        incoming.ticket_status = "postponed"
        incoming.start_time = "20:30"
        incoming.announced_at = "2026-08-01T10:00:00Z"

        merged = merge_events(existing, incoming)

        self.assertEqual("Rock / Indie / Punk", merged.genre_public)
        self.assertEqual("Official source", merged.genre_source)
        self.assertEqual("source_explicit", merged.genre_method)
        self.assertEqual("postponed", merged.ticket_status)
        self.assertEqual("20:30", merged.start_time)
        self.assertEqual("2026-08-01T10:00:00Z", merged.announced_at)
        self.assertEqual("https://official.example/event", merged.ticket_url)


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


class DiscoveryAndDetailEnrichmentTests(unittest.TestCase):
    def test_aeg_json_ld_locality_recovers_cityless_montell_row(self):
        html = """
        <script type="application/ld+json">{
          "@type":"Event", "startDate":"2026-11-15",
          "location":{"name":"Casino de Paris","address":{"addressLocality":"Paris"}}
        }</script>
        <div class="event-details">
          <p class="event-date">15 nov.</p>
          <p class="event-venue">Casino de Paris</p>
          <a href="https://tickets.example/montell">Réserver</a>
        </div>
        """
        response = Mock(text=html)
        response.raise_for_status = Mock()

        with patch("concert_calendar.scrapers.aeg.requests.get", return_value=response):
            events = parse_aeg_detail(
                "https://www.aegpresents.fr/event/montell-fish/", "Montell Fish"
            )

        self.assertEqual(1, len(events))
        self.assertEqual("2026-11-15", events[0].date)
        self.assertEqual("Casino de Paris", events[0].venue)
        self.assertEqual("Paris", events[0].city)

    def test_accor_explicit_support_sentence_extracts_wet_leg(self):
        self.assertEqual(
            ["Wet Leg"],
            extract_accor_support(
                "<p><strong>Wet Leg</strong> en assurera la première partie.</p>",
                "Tame Impala",
            ),
        )

    def test_accor_explicit_special_guests_are_structured_support(self):
        description = (
            "<p>Five Finger Death Punch, accompagnés de Lamb of God et "
            "Bleed From Within en invités spéciaux.</p>"
        )
        self.assertEqual(
            ["Lamb of God", "Bleed From Within"],
            extract_accor_support(description, "Five Finger Death Punch"),
        )

    def test_accor_tame_impala_sessions_both_receive_wet_leg(self):
        item = {
            "room": {"full_name": "Accor Arena"},
            "spotify": "https://open.spotify.com/artist/example",
            "sessions": [
                {"date": "2027-06-12 19:45:00"},
                {"date": "2027-06-13 19:45:00"},
            ],
            "translations": [{
                "language": "fr", "title": "TAME IMPALA",
                "category": "CONCERT", "sub_category": "POP ROCK FOLK",
                "url_event": "https://tickets.example/tame-impala",
                "description": (
                    "<p><strong>Wet Leg</strong> en assurera la première partie.</p>"
                ),
            }],
        }

        events = parse_accor_item(item)

        self.assertEqual(["2027-06-12", "2027-06-13"], [event.date for event in events])
        self.assertTrue(all(event.openers == ["Wet Leg"] for event in events))
        self.assertTrue(all(event.authoritative_billing for event in events))
        self.assertFalse(any(event.headliner == "Wet Leg" for event in events))

    def test_accor_sports_subcategory_is_not_treated_as_music(self):
        item = {
            "room": {"full_name": "Accor Arena"},
            "sessions": [{"date": "2027-01-01 20:00:00"}],
            "translations": [{
                "language": "fr", "title": "UFC Fight Night",
                "category": "SPORT", "sub_category": "MMA",
                "description": "",
            }],
        }
        self.assertEqual([], parse_accor_item(item))

    def test_petit_bain_relocation_notice_has_structured_artist_and_venue(self):
        self.assertEqual(
            "HUMANITY’S LAST BREATH",
            strip_relocation_notice("CHANGEMENT DE SALLE _ HUMANITY’S LAST BREATH"),
        )
        soup = BeautifulSoup(
            """
            <div id="compinfotar"><p>CHANGEMENT DE SALLE : le concert
            initialement prévu à Petit Bain aura finalement lieu à
            La Machine du Moulin Rouge.</p></div>
            """,
            "html.parser",
        )
        self.assertEqual("La Machine du Moulin Rouge", find_relocated_venue(soup))

    def test_legitimate_title_with_move_word_is_unchanged(self):
        self.assertEqual("The Move", strip_relocation_notice("The Move"))


if __name__ == "__main__":
    unittest.main()
