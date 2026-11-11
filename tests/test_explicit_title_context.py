"""Explicit performer-role and venue-presentation normalization regressions."""
import unittest

from concert_calendar.billing_semantics import normalize_event_semantics
from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent


def event(title, *, venue="Le Pop-Up du Label", source="DICE", date="2026-11-12"):
    return ConcertEvent(
        date=date, headliner=title, venue=venue, city="Paris",
        department="75", source_names=[source],
    )


class ExplicitTitleContextTests(unittest.TestCase):
    def test_support_in_parentheses_becomes_opener(self):
        item = event("namesbliss (première partie : Kadiata)")
        normalize_event_semantics(item)
        self.assertEqual("namesbliss", item.headliner)
        self.assertEqual(["Kadiata"], item.openers)
        self.assertEqual("namesbliss (première partie : Kadiata)", item.raw_title)
        normalize_event_semantics(item)
        self.assertEqual(["Kadiata"], item.openers)

    def test_corroborated_plain_show_and_support_title_reconcile(self):
        a = event("namesbliss (première partie : Kadiata)")
        b = event("namesbliss", source="Le Pop-Up du Label")
        result = deduplicate_events([a, b])
        self.assertEqual(1, len(result))
        self.assertEqual("namesbliss", result[0].headliner)
        self.assertEqual(["Kadiata"], result[0].openers)

    def test_exact_venue_suffix_stripped_and_duplicate_removed(self):
        a = event("Arthur Fu Bandini à La Maroquinerie", venue="La Maroquinerie")
        b = event("Arthur Fu Bandini", venue="La Maroquinerie", source="La Maroquinerie")
        result = deduplicate_events([a, b])
        self.assertEqual(1, len(result))
        self.assertEqual("Arthur Fu Bandini", result[0].headliner)

    def test_unmatched_venue_suffix_is_not_erased(self):
        a = event("Arthur Fu Bandini à La Maroquinerie", venue="Le Trabendo")
        normalize_event_semantics(a)
        self.assertEqual("Arthur Fu Bandini à La Maroquinerie", a.headliner)

    def test_release_party_suffix_keeps_artist_identity(self):
        a = event("MELO XXX – RELEASE PARTY Girly Punk Event", venue="La Marbrerie")
        normalize_event_semantics(a)
        self.assertEqual("MELO XXX", a.headliner)
        self.assertEqual("RELEASE PARTY Girly Punk Event", a.event_title)
        self.assertEqual("MELO XXX – RELEASE PARTY Girly Punk Event", a.raw_title)

    def test_opaque_artist_quoted_title_and_plus_remain_untouched(self):
        for value in ("Florence + The Machine", "Belle et Sebastian",
                      "The (Opening Act)", "La Femme à la Mode"):
            with self.subTest(value=value):
                a = event(value)
                normalize_event_semantics(a)
                self.assertEqual(value, a.headliner)


if __name__ == "__main__":
    unittest.main()
