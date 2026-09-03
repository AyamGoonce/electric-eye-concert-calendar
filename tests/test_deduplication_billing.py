import unittest

from concert_calendar.deduplication import deduplicate_events
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

    def test_high_similarity_presentation_copy_merges(self):
        self.assertEqual(
            1,
            len(deduplicate_events([
                event("Wolfgang Voigt presents GAS live", source="Promoter"),
                event("Wolfgang Voigt présente GAS Live", source="Venue"),
            ])),
        )

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


if __name__ == "__main__":
    unittest.main()
