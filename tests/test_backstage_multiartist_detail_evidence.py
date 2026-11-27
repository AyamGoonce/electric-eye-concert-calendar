from unittest import TestCase

from concert_calendar.scrapers.backstage_btm import parse_detail_performers


class BackstageIndependentDetailEvidenceTests(TestCase):
    def test_independent_artist_headings_and_support_label(self):
        detail = """
        <h1>EMPLOYED TO SERVE + CABAL + Cold Culture</h1>
        <div class="details"><p>EMPLOYED TO SERVE</p>
        <p>The headliner biography.</p><p>CABAL</p>
        <p>Support biography.</p>
        <p>PREMIÈRE PARTIE: COLD CULTURE</p>
        <p>Another biography.</p></div>
        """
        artists, openers = parse_detail_performers(
            detail, "EMPLOYED TO SERVE + CABAL + Cold Culture"
        )
        self.assertEqual(["EMPLOYED TO SERVE", "CABAL", "Cold Culture"], artists)
        self.assertEqual(["Cold Culture"], openers)

    def test_headline_only_is_not_separate_performer_evidence(self):
        artists, openers = parse_detail_performers(
            "<h1>BLACKGOLD + SUMO CYCO + HYRO THE HERO</h1><p>BLACKGOLD</p>",
            "BLACKGOLD + SUMO CYCO + HYRO THE HERO"
        )
        self.assertEqual(([], []), (artists, openers))

    def test_protected_guest_placeholder_is_not_a_named_artist(self):
        self.assertEqual(
            ([], []),
            parse_detail_performers(
                "<h1>GREENLEAF + GUEST</h1><p>GREENLEAF</p><p>GUEST</p>",
                "GREENLEAF + GUEST"
            ),
        )
