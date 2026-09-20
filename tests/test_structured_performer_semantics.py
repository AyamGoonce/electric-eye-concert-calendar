import unittest

from concert_calendar.billing_semantics import (
    apply_structured_performer_semantics,
)
from concert_calendar.models import ConcertEvent
from concert_calendar.scrapers.new_morning import (
    _parse_explicit_byline,
    infer_performers_from_detail_html,
)


def event(headliner, **kwargs):
    return ConcertEvent(
        date="2026-10-01",
        headliner=headliner,
        venue="Venue",
        city="Paris",
        department="75",
        **kwargs,
    )


class StructuredPerformerSemanticsTests(unittest.TestCase):
    def test_explicit_performers_become_structured_bill(self):
        item = event(
            "Named Show",
            performers=["Artist A", "Artist B", "Artist C"],
            event_title="Named Show",
        )

        apply_structured_performer_semantics([item])

        self.assertEqual("Artist A", item.headliner)
        self.assertEqual(["Artist B", "Artist C"], item.co_headliners)
        self.assertEqual("Named Show", item.event_title)
        self.assertIn("Named Show", item.identity_aliases)

    def test_existing_headliner_stays_primary(self):
        item = event(
            "Artist B",
            performers=["Artist A", "Artist B", "Artist C"],
        )

        apply_structured_performer_semantics([item])

        self.assertEqual("Artist B", item.headliner)
        self.assertEqual(["Artist A", "Artist C"], item.co_headliners)

    def test_openers_are_not_promoted_to_coheadliners(self):
        item = event(
            "Artist A",
            performers=["Artist A", "Support"],
            openers=["Support"],
        )

        apply_structured_performer_semantics([item])

        self.assertEqual("Artist A", item.headliner)
        self.assertIsNone(item.co_headliners)

    def test_plus_name_without_performer_evidence_is_untouched(self):
        item = event("Mike + The Mechanics")

        apply_structured_performer_semantics([item])

        self.assertEqual("Mike + The Mechanics", item.headliner)
        self.assertIsNone(item.co_headliners)

    def test_new_morning_explicit_byline(self):
        self.assertEqual(
            ["Tai Allen", "Reg Wyns", "Emanuel Ruffler"],
            _parse_explicit_byline(
                "By Tai Allen, Reg Wyns, Emanuel Ruffler with guests"
            ),
        )

    def test_detail_resolves_surnames_from_explicit_names(self):
        html = """
        <h2>Présentation</h2>
        <strong>Ludivine Issambourg</strong>
        <strong>Brian Jackson</strong>
        <strong>Eric Legnini</strong>
        <strong>Other Musician</strong>
        """

        performers, programme = infer_performers_from_detail_html(
            html,
            "Jackson - Issambourg - Legnini",
        )

        self.assertEqual(
            ["Brian Jackson", "Ludivine Issambourg", "Eric Legnini"],
            performers,
        )
        self.assertFalse(programme)

    def test_detail_resolves_multiword_candidates_from_independent_prose(self):
        html = """
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "Event",
          "name": "Kamilya Jubran & Werner Hasler - Lynn Adib",
          "description": "Kamilya Jubran & Werner Hasler - Lynn Adib : Le duo formé par Kamilya Jubran et Werner Hasler partage la soirée avec le projet de Lynn Adib Quartet."
        }
        </script>
        """

        performers, programme = infer_performers_from_detail_html(
            html,
            "Kamilya Jubran & Werner Hasler - Lynn Adib",
        )

        self.assertEqual(
            ["Kamilya Jubran", "Werner Hasler", "Lynn Adib"],
            performers,
        )
        self.assertFalse(programme)

    def test_show_suffix_does_not_become_artist(self):
        html = """
        <h2>Présentation</h2>
        <strong>Tommy Smith</strong>
        """

        performers, programme = infer_performers_from_detail_html(
            html,
            'Tommy Smith - Coltrane Centenary "Year 1963"',
        )

        self.assertEqual(["Tommy Smith"], performers)
        self.assertTrue(programme)

    def test_legitimate_plus_name_is_not_split_without_independent_evidence(self):
        html = """
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "Event",
          "name": "Mike + The Mechanics",
          "description": "Mike + The Mechanics return to Paris."
        }
        </script>
        """

        performers, programme = infer_performers_from_detail_html(
            html,
            "Mike + The Mechanics",
        )

        self.assertEqual([], performers)
        self.assertFalse(programme)


if __name__ == "__main__":
    unittest.main()
