import unittest

from concert_calendar.deduplication import deduplicate_events, _reconcile_final_identity_collisions
from concert_calendar.models import ConcertEvent
from concert_calendar.venues import normalize_event_venue


def event(
    headliner,
    *,
    venue="Le Zénith Paris – La Villette",
    source="Official venue",
    date="2026-10-16",
):
    item = ConcertEvent(
        date=date,
        headliner=headliner,
        venue=venue,
        city="Paris",
        department="75",
        source_names=[source],
    )
    return normalize_event_venue(item)


class CrossSourceBillingDeduplicationTests(unittest.TestCase):
    def test_reviewed_graveyard_bill_roles(self):
        item = event("GRAVEYARD & BLUES PILLS", venue="Élysée Montmartre", date="2027-03-09")
        result = deduplicate_events([item])
        self.assertEqual(1, len(result))
        self.assertEqual("GRAVEYARD", result[0].headliner)
        self.assertEqual(["BLUES PILLS"], result[0].co_headliners)
        self.assertEqual(["SPIDERS"], result[0].openers)

    def test_reviewed_evil_invaders_bill_roles(self):
        item = event("EVIL INVADERS & EXHORDER & HEATHEN", venue="Petit Bain", date="2027-03-21")
        result = deduplicate_events([item])
        self.assertEqual(1, len(result))
        self.assertEqual("EVIL INVADERS", result[0].headliner)
        self.assertEqual(["EXHORDER", "HEATHEN"], result[0].co_headliners)
        self.assertEqual(["WARFIELD"], result[0].openers)

    def test_reviewed_jay_z_event_branding_preserves_metadata(self):
        plain = event("JAŸ-Z", date="2026-09-10", venue="Stade de France", source="Live Nation")
        branded = event("JAŸ-Z 30", date="2026-09-10", venue="Stade de France", source="Stade de France")
        plain.first_seen = "2026-08-20T11:02:59Z"
        branded.first_seen = "2026-09-03T12:50:16Z"
        plain.promoters = ["Live Nation"]
        plain.ticket_url = "https://tickets.example/jay-z"
        branded.image_url = "https://venue.example/jay-z.jpg"
        branded.image_source = "Stade de France"
        branded.openers = ["Explicit support"]
        result = deduplicate_events([plain, branded])
        self.assertEqual(1, len(result))
        merged = result[0]
        self.assertEqual("JAŸ-Z", merged.headliner)
        self.assertEqual({"Live Nation", "Stade de France"}, set(merged.source_names))
        self.assertEqual(plain.first_seen, merged.first_seen)
        self.assertEqual(plain.ticket_url, merged.ticket_url)
        self.assertEqual(["Live Nation"], merged.promoters)
        self.assertEqual(branded.image_url, merged.image_url)
        self.assertEqual(["Explicit support"], merged.openers)

    def test_reviewed_branding_does_not_strip_numeric_artist_identities(self):
        names = ["Blink-182", "Sum 41", "U2", "UB40", "30 Seconds to Mars"]
        result = deduplicate_events([event(name) for name in names])
        self.assertEqual({name.casefold() for name in names}, {e.headliner.casefold() for e in result})
        unreviewed = event("JAŸ-Z 30", date="2027-09-10", venue="Stade de France")
        self.assertEqual("JAŸ-Z 30", deduplicate_events([unreviewed])[0].headliner)

    def test_behemoth_separator_variant_merges_and_keeps_dark_funeral(self):
        rich = event("Behemoth & Dimmu Borgir", source="Live Nation")
        rich.openers = ["Behemoth", "Dimmu Borgir", "Dark Funeral"]
        rich.genre = "Hard / Metal"
        rich.genre_public = "Metal / Hard Rock"
        rich.image_url = "https://images.example/behemoth.jpg"
        rich.image_source = "Live Nation"
        rich.promoters = ["Live Nation"]
        poor = event("Behemoth x Dimmu Borgir")
        poor.ticket_url = "https://venue.example/behemoth"

        result = deduplicate_events([poor, rich])

        self.assertEqual(1, len(result))
        self.assertEqual("Behemoth & Dimmu Borgir", result[0].headliner)
        self.assertEqual(["Dark Funeral"], result[0].openers)
        self.assertEqual("Metal / Hard Rock", result[0].genre_public)
        self.assertEqual(["Live Nation"], result[0].promoters)
        self.assertEqual(
            {"Official venue", "Live Nation"}, set(result[0].source_names)
        )

    def test_equivalent_explicit_billing_separators_merge(self):
        for separator in ("x", "×", "+", "/", "and", "avec"):
            with self.subTest(separator=separator):
                left = event("Artist A & Artist B", source="Venue")
                right = event(
                    f"Artist A {separator} Artist B", source="Promoter"
                )
                self.assertEqual(1, len(deduplicate_events([left, right])))

    def test_structured_opener_and_with_bill_merge(self):
        structured = event("Headliner", source="Venue")
        structured.openers = ["Support"]
        full = event("Headliner with Support", source="Aggregator")
        result = deduplicate_events([structured, full])
        self.assertEqual(1, len(result))
        self.assertEqual(["Support"], result[0].openers)

    def test_special_guest_marker_requires_and_uses_source_evidence(self):
        plain = event("Headliner", source="Venue")
        marked = event("Headliner + Special Guest", source="DICE")
        result = deduplicate_events([plain, marked])
        self.assertEqual(1, len(result))

    def test_cross_source_tour_suffix_merges_but_single_source_does_not(self):
        plain = event("Artist", source="Venue")
        tour = event("Artist – The Final World Tour", source="Promoter")
        self.assertEqual(1, len(deduplicate_events([plain, tour])))

        first = event("Artist", source="Same source")
        second = event("Artist – The Final World Tour", source="Same source")
        self.assertEqual(2, len(deduplicate_events([first, second])))

    def test_tour_artist_cleanup_is_not_single_source_merge_evidence(self):
        from itertools import permutations
        for titles in permutations(('Artist', 'Artist – Northern Tour', 'Artist – Southern Tour')):
            records = [event(title, source='Same source') for title in titles]
            result = deduplicate_events(records)
            self.assertEqual(3, len(result))
            self.assertEqual({'Artist'}, {item.headliner for item in result})
            self.assertEqual({None, 'Artist – Northern Tour', 'Artist – Southern Tour'},
                             {item.event_title for item in result})

    def test_different_tour_programmes_are_not_cross_source_corroboration(self):
        first = event('Artist – Northern Tour', source='Venue')
        second = event('Artist – Southern Tour', source='Promoter')
        self.assertEqual(2, len(deduplicate_events([first, second])))

    def test_shared_event_ticket_can_corroborate_tour_but_not_different_times(self):
        for different_times in (False, True):
            first = event('Artist', source='Same source')
            second = event('Artist – Northern Tour', source='Same source')
            first.ticket_url = 'https://tickets.example/concert/unique-product?utm_source=one'
            second.ticket_url = 'https://tickets.example/concert/unique-product'
            first.start_time = '19:00'
            second.start_time = '21:00' if different_times else '19:00'
            self.assertEqual(2 if different_times else 1, len(deduplicate_events([first, second])))

    def test_exact_source_tour_representations_still_collapse(self):
        first = event('Artist – Northern Tour', source='Same source')
        second = event('Artist – Northern Tour', source='Same source')
        result = deduplicate_events([first, second])
        self.assertEqual(1, len(result))
        self.assertEqual('Artist', result[0].headliner)
        self.assertEqual('Artist – Northern Tour', result[0].event_title)

    def test_reviewed_tour_equivalence_precedes_guard_but_not_time_safety(self):
        from unittest.mock import patch
        from concert_calendar.deduplication import REVIEWED_EVENT_TITLES
        from concert_calendar.venues import normalize_venue_key
        reviewed_date = '2027-01-10'
        venue = normalize_venue_key(event('Artist').venue)
        rule = {(reviewed_date, venue, 'artist – northern tour'): 'Artist'}
        with patch.dict(REVIEWED_EVENT_TITLES, rule):
            for day, times, expected in (
                (reviewed_date, (None, None), 1),
                ('2027-01-11', (None, None), 2),
                (reviewed_date, ('19:00', '21:00'), 2),
            ):
                with self.subTest(day=day, times=times):
                    plain = event('Artist', source='Same source', date=day)
                    marked = event('Artist – Northern Tour', source='Same source', date=day)
                    plain.start_time, marked.start_time = times
                    self.assertEqual(expected, len(deduplicate_events([plain, marked])))

    def test_punctuation_accent_and_case_variants_merge_cross_source(self):
        left = event("Beyoncé!", source="Venue")
        right = event("BEYONCE", source="Promoter")
        self.assertEqual(1, len(deduplicate_events([left, right])))

    def test_listing_qualifiers_do_not_create_duplicates(self):
        variants = (
            ("EsDeeKid", "EsDeeKid : 2026"),
            ("Hip Hop Talents", "Hip Hop Talents 2026"),
            ("Moreish Idols", "MOREISH IDOLS (UK)"),
            ("DJ Seinfeld", "DJ Seinfeld (live)"),
        )
        for plain, qualified in variants:
            with self.subTest(qualified=qualified):
                self.assertEqual(
                    1,
                    len(deduplicate_events([
                        event(plain, source="Venue"),
                        event(qualified, source="Promoter"),
                    ])),
                )

    def test_city_year_promotional_suffix_merges_same_concert(self):
        for date in ("2026-09-12", "2026-09-16"):
            with self.subTest(date=date):
                clean = event("Celine Dion", source="Venue", date=date, venue="Plénitude Arena")
                decorated = event("Céline Dion Paris 2026", source="Promoter", date=date, venue="Plénitude Arena")
                result = deduplicate_events([clean, decorated])
                self.assertEqual(1, len(result))
                self.assertEqual("Céline Dion", result[0].headliner)
                self.assertEqual({"Venue", "Promoter"}, set(result[0].source_names))

    def test_distinct_explicit_times_never_merge_after_title_normalization(self):
        early = event("Hommage à Ernestine Anderson avec Cecil L. Recchia + Jam Vocale – 19h00", venue="Sunset/Sunside — Sunside", date="2026-09-06", source="Sunset")
        late = event("Hommage à Ernestine Anderson avec Cecil L. Recchia + Jam Vocale – 21h00", venue="Sunset/Sunside — Sunside", date="2026-09-06", source="Venue")
        early.start_time = "19:00"
        late.start_time = "21:00"
        self.assertEqual(2, len(deduplicate_events([early, late])))

    def test_time_only_on_one_title_does_not_block_duplicate_merge(self):
        timed = event("Artist – 19h00", source="Venue")
        plain = event("Artist", source="Promoter")
        self.assertEqual(1, len(deduplicate_events([timed, plain])))

    def test_time_only_on_one_record_does_not_block_duplicate_merge(self):
        timed = event("Artist", source="Venue")
        timed.start_time = "19:00"
        plain = event("Artist", source="Promoter")
        self.assertEqual(1, len(deduplicate_events([timed, plain])))

    def test_equal_explicit_times_merge(self):
        left = event("Artist – 19h00", source="Venue")
        left.start_time = "19:00"
        right = event("Artist – 19h00", source="Promoter")
        right.start_time = "19:00"
        self.assertEqual(1, len(deduplicate_events([left, right])))

    def test_reviewed_truncation_and_typo_variants_merge(self):
        variants = (
            ("The Afghan Wigs", "The Afghan Whigs"),
            ("Two Door Cinema", "Two Door Cinema Club"),
        )
        for left_name, right_name in variants:
            with self.subTest(left_name=left_name):
                self.assertEqual(
                    1,
                    len(deduplicate_events([
                        event(left_name, source="Venue"),
                        event(right_name, source="Promoter"),
                    ])),
                )

    def test_single_artist_card_merges_with_fuller_cobill(self):
        result = deduplicate_events([
            event("Tramhaus", source="Promoter"),
            event("Tramhaus & Leroy Se Meurt", source="Venue"),
        ])
        self.assertEqual(1, len(result))
        self.assertEqual("Tramhaus & Leroy Se Meurt", result[0].headliner)

    def test_word_conjunction_inside_artist_name_is_not_bill_extension(self):
        short = event(
            "The Devil",
            source="Promoter",
            venue="Backstage By The Mill",
            date="2026-10-01",
        )
        full_name = event(
            "The Devil And The Almighty Blues",
            source="Backstage By The Mill",
            venue="Backstage By The Mill",
            date="2026-10-01",
        )

        result = deduplicate_events([short, full_name])

        self.assertEqual(2, len(result))
        self.assertEqual(
            {
                "The Devil",
                "The Devil And The Almighty Blues",
            },
            {item.headliner for item in result},
        )

    def test_complete_artist_name_extends_to_richer_flat_bill_without_splitting(self):
        short = event(
            "The Devil And The Almighty Blues",
            source="Backstage By The Mill",
            venue="Backstage By The Mill",
            date="2026-10-01",
        )
        rich = event(
            "The Devil And The Almighty Blues + Skyjoggers",
            source="Garmonbozia",
            venue="Backstage By The Mill",
            date="2026-10-01",
        )

        result = deduplicate_events([short, rich])

        self.assertEqual(1, len(result))
        self.assertEqual(
            "The Devil And The Almighty Blues + Skyjoggers",
            result[0].headliner,
        )
        self.assertIsNone(result[0].co_headliners)
        self.assertEqual(
            {"Backstage By The Mill", "Garmonbozia"},
            set(result[0].source_names),
        )

    def test_generic_guest_placeholder_yields_to_correlated_named_bill(self):
        placeholder = event(
            "Bad Situation + Guests",
            source="Le Trabendo",
            venue="Le Trabendo",
            date="2026-10-02",
        )
        rich = event(
            "Bad Situation + Moonball + Monnekyn + Coal Noir",
            source="Promoter",
            venue="Le Trabendo",
            date="2026-10-02",
        )

        result = deduplicate_events([placeholder, rich])

        self.assertEqual(1, len(result))
        self.assertEqual(rich.headliner, result[0].headliner)
        self.assertIsNone(result[0].co_headliners)
        self.assertIsNone(result[0].openers)

    def test_flat_punctuation_names_remain_opaque_without_evidence(self):
        names = (
            "River & Mountain Collective",
            "Fire And Memory Orchestra",
            "Alpha + Beta Company",
        )
        for name in names:
            with self.subTest(name=name):
                result = deduplicate_events([event(name)])
                self.assertEqual(name, result[0].headliner)
                self.assertIsNone(result[0].co_headliners)
                self.assertIsNone(result[0].openers)

    def test_structured_semantics_do_not_cross_contaminate_same_day_venues(self):
        duo = event(
            "Simon & Garfunkel + Guests",
            venue="Venue A",
            source="Promoter A",
        )
        duo.performers = ["Simon & Garfunkel", "Guests"]
        duo_flat = event(
            "Simon & Garfunkel + Guests",
            venue="Venue A",
            source="DICE",
        )

        separate = event(
            "Simon and Garfunkel + Guests",
            venue="Venue B",
            source="Promoter B",
        )
        separate.performers = ["Simon", "Garfunkel"]
        separate_flat = event(
            "Simon & Garfunkel + Guests",
            venue="Venue B",
            source="DICE",
        )

        result = deduplicate_events([duo, duo_flat, separate, separate_flat])

        self.assertEqual(2, len(result))
        by_venue = {item.venue: item for item in result}
        self.assertEqual("Simon & Garfunkel", by_venue["Venue A"].headliner)
        self.assertEqual(["Guests"], by_venue["Venue A"].co_headliners)
        self.assertEqual("Simon", by_venue["Venue B"].headliner)
        self.assertEqual(["Garfunkel"], by_venue["Venue B"].co_headliners)

    def test_structured_artist_named_guests_is_not_treated_as_placeholder(self):
        structured = event("Band + Guests", source="Venue")
        structured.performers = ["Band", "Guests"]
        flat = event("Band + Guests", source="Promoter")

        result = deduplicate_events([structured, flat])

        self.assertEqual(1, len(result))
        self.assertEqual("Band", result[0].headliner)
        self.assertEqual(["Guests"], result[0].co_headliners)

    def test_high_similarity_presentation_copy_merges(self):
        self.assertEqual(
            1,
            len(deduplicate_events([
                event("Wolfgang Voigt presents GAS live", source="Promoter"),
                event("Wolfgang Voigt présente GAS Live", source="Venue"),
            ])),
        )

    def test_reviewed_presentation_language_variant_preserves_canonical_title(self):
        promoter = event(
            "Wolfgang Voigt presents GAS live",
            source="Promoter",
        )
        venue = event(
            "Wolfgang Voigt présente GAS Live",
            source="Venue",
        )

        for item in (promoter, venue):
            item.date = "2026-09-23"
            item.venue = "La Gaîté Lyrique"

        result = deduplicate_events([promoter, venue])

        self.assertEqual(1, len(result))
        self.assertEqual(
            "WOLFGANG VOIGT presents GAS live",
            result[0].headliner,
        )
        self.assertIsNone(result[0].event_title)

    def test_reordered_festival_wrapper_merges_same_artist_bill(self):
        rich = event(
            "Pitchfork Music Festival: Ear + Guests", source="Venue"
        )
        rich.electric_eye_links = [{
            "url": "https://www.electriceyerock.com/ear",
            "name": "Ear",
        }]
        poor = event(
            "Ear + guests — Pitchfork Music Festival 2026",
            source="Promoter",
        )

        result = deduplicate_events([poor, rich])

        self.assertEqual(1, len(result))
        self.assertEqual(rich.headliner, result[0].headliner)
        self.assertEqual(rich.electric_eye_links, result[0].electric_eye_links)

    def test_plain_artist_card_merges_with_matching_festival_wrapper(self):
        plain = event("ear", source="Promoter")
        plain.event_title = "ear + guests — Pitchfork Music Festival 2026"
        plain.co_headliners = ["guests — Pitchfork Music Festival 2026"]
        plain.image_url = "https://dice.example/ear.jpg"
        plain.image_source = "DICE"
        wrapped = event(
            "Pitchfork Music Festival: Ear + Guests", source="Venue"
        )
        wrapped.image_url = "https://venue.example/ear.jpg"
        wrapped.image_source = "Le Trabendo"
        result = deduplicate_events([plain, wrapped])
        self.assertEqual(1, len(result))
        self.assertEqual("ear", result[0].headliner)
        self.assertIsNone(result[0].co_headliners)
        self.assertEqual("https://venue.example/ear.jpg", result[0].image_url)
        self.assertEqual("Le Trabendo", result[0].image_source)

    def test_same_artist_at_different_festivals_stays_separate(self):
        first = event("Festival One: Ear + Guests", source="Venue")
        second = event("Ear + Guests — Festival Two", source="Promoter")
        self.assertEqual(2, len(deduplicate_events([first, second])))

    def test_different_artist_bills_at_same_festival_stay_separate(self):
        ear = event("Pitchfork Music Festival: Ear + Guests", source="Venue")
        other = event(
            "Other Artist + guests — Pitchfork Music Festival 2026",
            source="Promoter",
        )
        self.assertEqual(2, len(deduplicate_events([ear, other])))

    def test_richer_survivor_merges_metadata_and_keeps_oldest_first_seen(self):
        poor = event("Artist A x Artist B", source="Aggregator")
        poor.first_seen = "2026-08-20T10:00:00Z"
        poor.ticket_url = "https://tickets.example/poor"
        rich = event("Artist A & Artist B", source="Official venue")
        rich.first_seen = "2026-08-21T10:00:00Z"
        rich.openers = ["Support"]
        rich.genre_public = "Rock / Indie / Punk"
        rich.image_url = "https://images.example/show.jpg"
        rich.image_source = "Official venue"
        rich.promoters = ["Promoter"]
        rich.electric_eye_links = [{
            "url": "https://www.electriceyerock.com/artist-a",
            "name": "Artist A",
        }]

        result = deduplicate_events([poor, rich])

        self.assertEqual(1, len(result))
        self.assertIs(rich, result[0])
        self.assertEqual("2026-08-20T10:00:00Z", result[0].first_seen)
        self.assertEqual(["Support"], result[0].openers)
        self.assertEqual("Rock / Indie / Punk", result[0].genre_public)
        self.assertEqual(["Promoter"], result[0].promoters)

    def test_same_artist_date_at_different_venues_stays_separate(self):
        left = event("Artist", venue="Le Zénith", source="Promoter")
        right = event("ARTIST", venue="Accor Arena", source="Aggregator")
        self.assertEqual(2, len(deduplicate_events([left, right])))

    def test_reviewed_clawfinger_move_keeps_trabendo(self):
        stale = event(
            "Clawfinger", venue="Élysée Montmartre",
            source="Élysée Montmartre", date="2026-10-30",
        )
        current = event(
            "Clawfinger", venue="Le Trabendo",
            source="AEG Presents France", date="2026-10-30",
        )
        current.start_time = "20:00"

        result = deduplicate_events([stale, current])

        self.assertEqual(1, len(result))
        self.assertEqual("Le Trabendo", result[0].venue)
        self.assertEqual("20:00", result[0].start_time)
        self.assertEqual(
            {"AEG Presents France", "Élysée Montmartre"},
            set(result[0].source_names),
        )

    def test_reviewed_os_garotin_move_keeps_new_morning(self):
        stale = event(
            "Os Garotin", venue="Cabaret Sauvage",
            source="Cabaret Sauvage", date="2026-09-13",
        )
        current = event(
            "Os Garotin", venue="New Morning",
            source="New Morning", date="2026-09-13",
        )

        result = deduplicate_events([stale, current])

        self.assertEqual(1, len(result))
        self.assertEqual("New Morning", result[0].venue)

    def test_reviewed_south_arcade_move_keeps_alhambra(self):
        stale = event(
            "South Arcade", venue="Backstage By The Mill",
            source="Backstage By The Mill", date="2027-03-18",
        )
        current = event(
            "South Arcade", venue="L'Alhambra",
            source="AEG Presents France", date="2027-03-18",
        )

        result = deduplicate_events([stale, current])

        self.assertEqual(1, len(result))
        self.assertEqual("L'Alhambra", result[0].venue)

    def test_bagshow_multi_venue_structure_is_not_collapsed(self):
        trianon = event(
            "BAG’SHOW 2026", venue="Le Trianon",
            source="Le Trianon", date="2026-10-24",
        )
        elysee = event(
            "BAG’SHOW 2026", venue="Élysée Montmartre",
            source="Élysée Montmartre", date="2026-10-24",
        )

        result = deduplicate_events([trianon, elysee])

        self.assertEqual(2, len(result))
        self.assertEqual(
            {"Le Trianon", "Élysée Montmartre"},
            {item.venue for item in result},
        )

    def test_same_venue_date_different_performance_times_stay_separate(self):
        early = event("Artist – 16H", source="Venue")
        late = event("ARTIST – 20H", source="Promoter")
        early.start_time = "16:00"
        late.start_time = "20:00"
        self.assertEqual(2, len(deduplicate_events([early, late])))

    def test_festival_pass_and_individual_concert_stay_separate(self):
        festival = event("Festival Pass – Artist", source="Festival")
        festival.festival_name = "Festival Pass"
        festival.authoritative_billing = True
        concert = event("ARTIST", source="Promoter")
        self.assertEqual(2, len(deduplicate_events([festival, concert])))

    def test_venue_promoter_and_aggregator_collapse_to_one(self):
        venue = event("Artist A & Artist B", source="Venue")
        promoter = event("Artist A x Artist B", source="Promoter")
        promoter.openers = ["Support"]
        aggregator = event("Artist A + Artist B", source="DICE")
        result = deduplicate_events([venue, promoter, aggregator])
        self.assertEqual(1, len(result))
        self.assertEqual(["Support"], result[0].openers)

    def test_post_deduplication_diagnostic_reports_intentional_near_pair(self):
        early = event("Artist – 16H", source="Venue")
        late = event("Artist – 20H", source="Promoter")
        diagnostics = {}

        result = deduplicate_events([early, late], diagnostics=diagnostics)

        self.assertEqual(2, len(result))
        self.assertEqual(1, len(diagnostics["suspicious_near_duplicates"]))
        self.assertTrue(
            diagnostics["suspicious_near_duplicates"][0][
                "distinct_performance"
            ]
        )

    def test_merged_billing_variant_is_not_reported_as_suspicious(self):
        diagnostics = {}
        result = deduplicate_events(
            [
                event("Artist A & Artist B", source="Venue"),
                event("Artist A x Artist B", source="Promoter"),
            ],
            diagnostics=diagnostics,
        )
        self.assertEqual(1, len(result))
        self.assertEqual([], diagnostics["suspicious_near_duplicates"])

    def test_final_cross_source_identical_untimed_rows_merge(self):
        left = event("In Flames x Trivium")
        right = event("In Flames x Trivium")
        left.source_names = ["Le Zénith Paris – La Villette"]
        right.source_names = ["Live Nation"]
        left.ticket_url = "https://venue.example/in-flames-trivium"
        right.ticket_url = "https://promoter.example/in-flames-trivium"

        result = deduplicate_events([left, right])

        self.assertEqual(1, len(result))

    def test_final_identity_collision_merges_after_source_metadata_converges(self):
        left = event("Example Artist")
        right = event("Example Artist")

        # Earlier merges may leave both residual rows carrying the same
        # combined provenance. That must not prevent final state-identity
        # reconciliation.
        shared_sources = ["Venue", "Promoter"]
        left.source_names = list(shared_sources)
        right.source_names = list(shared_sources)

        result = _reconcile_final_identity_collisions([left, right])

        self.assertEqual(1, len(result))

    def test_final_identity_collision_preserves_distinct_programmes(self):
        left = event("Example Artist")
        right = event("Example Artist")
        left.source_names = ["Venue"]
        right.source_names = ["Promoter"]
        left.event_title = "Programme One"
        right.event_title = "Programme Two"

        result = _reconcile_final_identity_collisions([left, right])

        self.assertEqual(2, len(result))


if __name__ == "__main__":
    unittest.main()
