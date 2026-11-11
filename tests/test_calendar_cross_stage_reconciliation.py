"""Regress cross-stage title semantics and safe cross-source title merges."""
import unittest

from concert_calendar.billing_semantics import apply_structured_performer_semantics
from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent
from concert_calendar.scrapers.gaite_lyrique import detail_performers


def e(title, *, source="DICE", venue="La Gaîté Lyrique",
      when="2026-11-13", time=None, performers=None):
    return ConcertEvent(
        date=when, headliner=title, venue=venue, city="Paris",
        department="75", start_time=time, source_names=[source],
        performers=performers,
    )


class BillSemanticsIntegrationTests(unittest.TestCase):
    def test_raw_title_performer_does_not_undo_marked_invitees(self):
        title = "ESCAPE MUSIC Invite OMAR C, BOUSTI,IZZY b2b KAPMAN"
        item = e(title, venue="211", performers=[title])
        apply_structured_performer_semantics([item])
        self.assertEqual("OMAR C", item.headliner)
        self.assertEqual(["BOUSTI", "IZZY", "KAPMAN"], item.co_headliners)
        self.assertEqual("ESCAPE MUSIC", item.event_title)
        self.assertEqual(title, item.raw_title)

    def test_artist_invites_others_does_not_get_treated_as_event_brand(self):
        item = e("Sainte Nicole invite Delali", performers=None)
        apply_structured_performer_semantics([item])
        self.assertEqual("Sainte Nicole invite Delali", item.headliner)

    def test_presenter_colon_is_not_part_of_artist_name(self):
        item = e("BSC CONCERT PRÉSENTE : Squelette - Brux - Voiture 27")
        apply_structured_performer_semantics([item])
        self.assertEqual("Squelette - Brux - Voiture 27", item.headliner)
        self.assertEqual("BSC CONCERT", item.event_title)

    def test_open_stage_series_is_separated_but_unproved_artists_stay_opaque(self):
        item = e("Scène Ouverte + LÉVA + LIFE REPORTS + MINETTE")
        apply_structured_performer_semantics([item])
        self.assertEqual("LÉVA + LIFE REPORTS + MINETTE", item.headliner)
        self.assertEqual("Scène Ouverte", item.event_title)
        self.assertIsNone(item.co_headliners)

    def test_tribute_experience_is_separated(self):
        item = e("Strangelove - The Depeche Mode Experience")
        apply_structured_performer_semantics([item])
        self.assertEqual("Strangelove", item.headliner)
        self.assertEqual("The Depeche Mode Experience", item.event_title)

    def test_no_split_of_legitimate_band_project(self):
        item = e("Florence + The Machine")
        apply_structured_performer_semantics([item])
        self.assertEqual("Florence + The Machine", item.headliner)


class SourceReconciliationTests(unittest.TestCase):
    def test_two_artist_names_come_from_explicit_official_venue_prose(self):
        html = ('<main><p>Nosaj Thing et Daito Manabe réunissent leurs univers '
                'artistiques à travers leur live audiovisuel. '
                'Les deux artistes travaillent ensemble depuis 2012.</p></main>')
        self.assertEqual(
            ["Nosaj Thing", "Daito Manabe"],
            detail_performers(html, "Nosaj Thing & Daito Manabe"),
        )

    def test_ampersand_title_alone_is_not_sufficient(self):
        self.assertEqual([], detail_performers(
            "<main><p>Simon & Garfunkel en concert</p></main>",
            "Simon & Garfunkel",
        ))

    def test_cross_source_et_ampersand_variant_is_one_concert(self):
        events = [
            e("Nosaj Thing & Daito Manabe", source="La Gaîté Lyrique",
              time="20:00"),
            e("Nosaj Thing et Daito Manabe", source="AEG Presents"),
        ]
        out = deduplicate_events(events)
        self.assertEqual(1, len(out))

    def test_cross_source_plural_with_support_is_one_concert(self):
        events = [
            e("Westside Cowboys", source="Petit Bain", venue="Petit Bain"),
            e("Westside Cowboy + Wyatt", source="DICE", venue="Petit Bain",
              time="19:00"),
        ]
        out = deduplicate_events(events)
        self.assertEqual(
            1, len(out),
            [(x.headliner, x.co_headliners, x.performers, x.source_names)
             for x in out],
        )
        self.assertEqual("Westside Cowboys", out[0].headliner)

    def test_conflicting_times_are_distinct(self):
        events = [
            e("Nosaj Thing & Daito Manabe", source="La Gaîté Lyrique",
              time="19:00"),
            e("Nosaj Thing et Daito Manabe", source="AEG Presents",
              time="22:30"),
        ]
        self.assertEqual(2, len(deduplicate_events(events)))

    def test_official_programme_artist_headings_supply_independent_roles(self):
        from concert_calendar.scrapers.file7 import (
            enrich_official_detail_billing, explicit_detail_artist_sections,
        )
        html = (
            "<h2>REVNOIR <span>Metalcore</span></h2>"
            "<h2>Solitaris <span>Metalcore</span></h2>"
            "<h2>TRVMA <span>Metalcore</span></h2>"
        )
        parts = explicit_detail_artist_sections(
            html, "REVNOIR + Solitaris + TRVMA",
        )
        self.assertEqual(["REVNOIR", "Solitaris", "TRVMA"], parts)
        event = e("REVNOIR + Solitaris + TRVMA", source="File7", venue="File7")
        self.assertTrue(enrich_official_detail_billing(event, html))
        self.assertEqual("REVNOIR", event.headliner)
        self.assertEqual(["Solitaris", "TRVMA"], event.co_headliners)
        self.assertEqual("REVNOIR + Solitaris + TRVMA", event.raw_title)

    def test_opaque_project_not_split_without_distinct_official_sections(self):
        from concert_calendar.scrapers.file7 import explicit_detail_artist_sections
        self.assertEqual([], explicit_detail_artist_sections(
            "<h2>Florence + The Machine</h2>", "Florence + The Machine",
        ))
        self.assertEqual([], explicit_detail_artist_sections(
            "<h2>REVNOIR Metalcore</h2>", "REVNOIR + Solitaris + TRVMA",
        ))

    def test_no_cross_source_plural_guess_without_explicit_support(self):
        events = [
            e("The Doors", source="Petit Bain", venue="Petit Bain"),
            e("The Door", source="DICE", venue="Petit Bain"),
        ]
        self.assertEqual(2, len(deduplicate_events(events)))


if __name__ == "__main__":
    unittest.main()
