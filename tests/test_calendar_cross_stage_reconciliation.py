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

    def test_source_date_stamp_is_removed_only_when_exact_date_matches(self):
        item = e("Thiefs + Papatef I 13.11.26")
        apply_structured_performer_semantics([item])
        self.assertEqual("Thiefs + Papatef", item.headliner)
        incorrect = e("Thiefs + Papatef I 14.11.26")
        apply_structured_performer_semantics([incorrect])
        self.assertEqual("Thiefs + Papatef I 14.11.26", incorrect.headliner)

    def test_bold_labeled_artist_sections_in_venue_prose_are_supported(self):
        from concert_calendar.scrapers.point_ephemere import structured_bill
        text = [
            {"type": "paragraph", "text": "KOJEY RADICAL writes music...",
             "spans": [{"type": "strong", "start": 0, "end": 13}]},
            {"type": "paragraph", "text": "Claudia Isaki joins the tour...",
             "spans": [{"type": "strong", "start": 0, "end": 13}]},
        ]
        self.assertEqual(
            ["KOJEY RADICAL", "Claudia Isaki"],
            structured_bill("KOJEY RADICAL + Claudia Isaki", text),
        )

    def test_bal_chavaux_jsonld_billing_is_independently_structured(self):
        from concert_calendar.scrapers.bal_chavaux import independent_performer_names
        payload = {"performer": [
            {"@type": "MusicGroup", "name": "Baby Berserk"},
            {"@type": "MusicGroup", "name": "No Sex Last Night"},
        ]}
        self.assertEqual(
            ["Baby Berserk", "No Sex Last Night"],
            independent_performer_names(payload),
        )
        self.assertIsNone(independent_performer_names(
            {"performer": {"name": "Baby Berserk + No Sex Last Night"}},
        ))

    def test_bal_chavaux_full_official_lineup_overrides_partial_jsonld(self):
        from concert_calendar.scrapers.bal_chavaux import (
            corroborated_official_lineup, parse_detail_page,
        )
        complete = (
            "BABY BERSERK + NO SEX LAST NIGHT + EXCHPOPTRUE + NEVROSES NOCTURNES"
        )
        partial = ["Baby Berserk", "No Sex Last Night"]
        self.assertEqual(
            ["BABY BERSERK", "NO SEX LAST NIGHT", "EXCHPOPTRUE",
             "NEVROSES NOCTURNES"],
            corroborated_official_lineup(complete, partial),
        )
        # No splitting from an unsupported opaque artist title.
        self.assertEqual(
            ["Singer", "Band"], corroborated_official_lineup(
                "Florence + The Machine + Other", ["Singer", "Band"]
            ),
        )
        listing = {
            "date": "2026-11-13",
            "headliner": complete,
            "start_time": "19:30",
            "category": "Concert",
            "detail_url": "https://balchavaux.fr/agenda/baby-berserk-no-sex-last-night-exchpoptrue-nevroses-nocturnes",
        }
        html = (
            '<script type="application/ld+json">'
            '{"@type":"Event","name":"No Sex Last Night",'
            '"startDate":"2026-11-13T19:30:00+01:00",'
            '"performer":[{"name":"Baby Berserk"},{"name":"No Sex Last Night"}]}'
            "</script>"
        )
        from datetime import date
        record = parse_detail_page(html, listing, today=date(2026, 11, 11))
        self.assertEqual("BABY BERSERK", record.headliner)
        self.assertEqual(
            ["NO SEX LAST NIGHT", "EXCHPOPTRUE", "NEVROSES NOCTURNES"],
            record.co_headliners,
        )
        self.assertEqual(4, len(record.performers))

    def test_bal_chavaux_presenter_prefix_and_partial_source_names(self):
        from concert_calendar.scrapers.bal_chavaux import (
            corroborated_official_lineup, parse_detail_page,
        )
        from datetime import date
        title = (
            "Les Femmes s’en Mêlent, Persona Grata et Le Bal Chavaux présentent "
            "BABY BERSERK + NO SEX LAST NIGHT + EXCHPOPTRUE + NEVROSES NOCTURNES"
        )
        expected = [
            "BABY BERSERK", "NO SEX LAST NIGHT", "EXCHPOPTRUE",
            "NEVROSES NOCTURNES",
        ]
        self.assertEqual(
            expected,
            corroborated_official_lineup(
                title, ["Baby Berserk", "No Sex Last Night"]
            ),
        )
        listing = {
            "date": "2026-11-13", "headliner": title,
            "start_time": "19:30", "category": "Concert",
            "detail_url": (
                "https://balchavaux.fr/agenda/"
                "baby-berserk-no-sex-last-night-exchpoptrue-nevroses-nocturnes"
            ),
        }
        html = (
            '<script type="application/ld+json">'
            '{"@type":"Event","name":"No Sex Last Night",'
            '"startDate":"2026-11-13T19:30:00+01:00",'
            '"performer":[{"name":"Baby Berserk"},{"name":"No Sex Last Night"}]}'
            "</script>"
        )
        parsed = parse_detail_page(html, listing, today=date(2026, 11, 11))
        self.assertEqual("BABY BERSERK", parsed.headliner)
        self.assertEqual(expected, parsed.performers)
        self.assertEqual(expected[1:], parsed.co_headliners)
        self.assertEqual(title, parsed.raw_title)
        published = deduplicate_events([parsed])
        self.assertEqual("Baby Berserk", published[0].headliner)
        self.assertEqual(4, len(published[0].performers))

    def test_baby_berserk_recovered_from_partial_current_source(self):
        url = (
            "https://balchavaux.fr/agenda/"
            "baby-berserk-no-sex-last-night-exchpoptrue-nevroses-nocturnes"
        )
        complete = (
            "BABY BERSERK + NO SEX LAST NIGHT + "
            "EXCHPOPTRUE + NEVROSES NOCTURNES"
        )
        from concert_calendar.models import ConcertEvent
        partial = ConcertEvent(
            date="2026-11-13", headliner="No Sex Last Night",
            venue="Bal Chavaux", city="Montreuil", department="93",
            ticket_url=url, source_names=["Bal Chavaux"],
            performers=["Baby Berserk", "No Sex Last Night"],
            event_title=complete, raw_title=complete, start_time="19:30",
        )
        result = deduplicate_events([partial])
        self.assertEqual(1, len(result))
        self.assertEqual("Baby Berserk", result[0].headliner)
        self.assertEqual(
            ["No Sex Last Night", "Exchpoptrue", "Nevroses Nocturnes"],
            result[0].co_headliners,
        )
        self.assertEqual(4, len(result[0].performers))
        self.assertIsNone(result[0].event_title)
        # Event-scoped evidence must never rewrite a different ticket.
        other = ConcertEvent(
            date="2026-11-13", headliner="No Sex Last Night",
            venue="Bal Chavaux", city="Montreuil", department="93",
            ticket_url="https://balchavaux.fr/agenda/a-different-event",
            raw_title=complete,
        )
        self.assertEqual("No Sex Last Night", deduplicate_events([other])[0].headliner)

    def test_actual_osees_avec_billing_converges_to_official_headliner(self):
        records = [
            e("Osees Avec Brigid Dawson + Dmbq", source="DICE",
              venue="Cabaret Sauvage", when="2027-06-12"),
            e("OSEES with Brigid Dawson", source="Cabaret Sauvage",
              venue="Cabaret Sauvage", when="2027-06-12", time="19:30"),
        ]
        records[1].openers = ["DMBQ"]
        combined = deduplicate_events(records)
        self.assertEqual(
            1, len(combined),
            [(v.headliner, v.event_title, v.start_time) for v in combined],
        )
        self.assertEqual("Osees with Brigid Dawson", combined[0].headliner)
        self.assertEqual(["DMBQ"], combined[0].openers)
        self.assertEqual("19:30", combined[0].start_time)

    def test_additional_corroborated_real_world_duplicate_variants(self):
        candidates = [
            ("2027-02-22", "L'Alhambra", "Yendry", "Yeиdry", "YENDRY"),
            ("2027-01-24", "Le Grand Rex", "Metaphor: Re Fantazio",
             "Metaphor: ReFantazio Orchestra Concert",
             "Metaphor: ReFantazio Orchestra Concert"),
            ("2027-08-20", "Bal Chavaux", "John Bush",
             "John Bush “Celebrating The Songs Of Anthrax 1993-2003",
             "John Bush"),
        ]
        for when, venue, first, second, expected in candidates:
            with self.subTest(when=when, venue=venue):
                a = e(first, source=venue, venue=venue, when=when)
                b = e(second, source="DICE", venue=venue, when=when)
                if when == "2027-08-20":
                    a.start_time = b.start_time = "19:00"
                result = deduplicate_events([a, b])
                self.assertEqual(
                    1, len(result),
                    [(record.headliner, record.event_title) for record in result],
                )
                self.assertEqual(expected, result[0].headliner)

    def test_afterhours_agreed_performance_clock_and_artist_survive(self):
        records = [
            e("Afterhours", source="DICE",
              venue="Bal Chavaux", when="2027-01-17", time="19:00"),
            e("Afterhours tour 2027 - quello che non c'è",
              source="Bal Chavaux",
              venue="Bal Chavaux", when="2027-01-17", time="19:30"),
        ]
        reconciled = deduplicate_events(records)
        self.assertEqual(
            1, len(reconciled),
            [(row.headliner, row.start_time) for row in reconciled],
        )
        self.assertEqual("Afterhours", reconciled[0].headliner)
        self.assertEqual("19:30", reconciled[0].start_time)

    def test_nonmusic_immersive_listening_concept_excluded(self):
        from concert_calendar.event_titles import is_non_artist_event_title
        self.assertTrue(is_non_artist_event_title(
            "Écoute immersive de disque - THE DARK SIDE OF THE MOON DE PINK FLOYD",
        ))
        self.assertFalse(is_non_artist_event_title("Dark Side of the Moon Band"))

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

    def test_verified_same_concert_title_variations_collapse(self):
        pairs = [
            ("2027-02-05", "La Machine du Moulin Rouge",
             "Lewis Ofman", "Lewis OfMan Tour", "Lewis Ofman"),
            ("2027-03-06", "Bal Chavaux",
             "Daniele Silvestri", "Silvestri", "Daniele Silvestri"),
            ("2027-03-13", "Élysée Montmartre",
             "The Dead Daisies", "The Dead Daisies ft. Kelly Hansen",
             "The Dead Daisies"),
            ("2027-04-11", "La Maroquinerie",
             "Jack Kays", "Jack Kays And His Band", "Jack Kays"),
            ("2027-06-15", "Café de la Danse",
             "Dirty Projectors", "Dirty Projectors (solo)",
             "Dirty Projectors (solo)"),
        ]
        for when, venue, plain, decorated, expected in pairs:
            with self.subTest(when=when, decorated=decorated):
                records = [
                    e(plain, source=venue, venue=venue, when=when),
                    e(decorated, source="DICE", venue=venue, when=when),
                ]
                outcome = deduplicate_events(records)
                self.assertEqual(1, len(outcome),
                                 [(r.headliner, r.event_title) for r in outcome])
                self.assertEqual(expected, outcome[0].headliner)

    def test_osees_dmbq_opener_preserved_during_title_merge(self):
        records = [
            e("Osees with Brigid Dawson",
              source="Cabaret Sauvage", venue="Cabaret Sauvage",
              when="2027-06-12"),
            e("Osees with Brigid Dawson + DMBQ",
              source="DICE", venue="Cabaret Sauvage",
              when="2027-06-12"),
        ]
        outcome = deduplicate_events(records)
        self.assertEqual(1, len(outcome))
        self.assertEqual("Osees with Brigid Dawson", outcome[0].headliner)
        self.assertIn("DMBQ", outcome[0].openers or [])

    def test_venue_scoped_aliases_do_not_merge_unrelated_day(self):
        records = [
            e("Dirty Projectors", source="Cabaret Sauvage",
              venue="Café de la Danse", when="2027-06-16"),
            e("Dirty Projectors (solo)", source="DICE",
              venue="Café de la Danse", when="2027-06-16"),
        ]
        outcome = deduplicate_events(records)
        self.assertEqual(2, len(outcome))

    def test_cross_source_et_ampersand_variant_is_one_concert(self):
        events = [
            e("Nosaj Thing & Daito Manabe", source="La Gaîté Lyrique",
              time="20:00"),
            e("Nosaj Thing et Daito Manabe", source="AEG Presents"),
        ]
        out = deduplicate_events(events)
        self.assertEqual(1, len(out))

    def test_official_lineup_wins_one_conflicting_support_name(self):
        official = e(
            "Darvaza + Merrimack + Helleruin + Detresse",
            source="Backstage By The Mill", venue="Backstage By The Mill",
            when="2026-12-10",
        )
        old_tour = e(
            "Darvaza + Merrimack + Wrang + Detresse",
            source="Garmonbozia", venue="Backstage By The Mill",
            when="2026-12-10",
        )
        merged = deduplicate_events([official, old_tour])
        self.assertEqual(1, len(merged))
        self.assertEqual("Darvaza", merged[0].headliner)
        self.assertEqual(
            ["Merrimack", "Helleruin", "Detresse"],
            merged[0].co_headliners,
        )
        self.assertNotIn("Wrang", merged[0].performers)

    def test_competing_structured_lineups_require_review(self):
        official = e(
            "Darvaza + Merrimack + Helleruin + Detresse",
            source="Backstage By The Mill", venue="Backstage By The Mill",
            when="2026-12-10",
            performers=["Darvaza", "Merrimack", "Helleruin", "Detresse"],
        )
        conflicting = e(
            "Darvaza + Merrimack + Wrang + Detresse",
            source="Garmonbozia", venue="Backstage By The Mill",
            when="2026-12-10",
            performers=["Darvaza", "Merrimack", "Wrang", "Detresse"],
        )
        # Do not discard independently structured conflicting artist evidence.
        merged = deduplicate_events([official, conflicting])
        self.assertEqual(2, len(merged))

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
        # Validate the new source-variant stage itself. Older canonical
        # identity reconciliation has its own artist alias handling.
        from concert_calendar.deduplication import (
            _reconcile_unique_cross_source_name_variants,
        )
        self.assertEqual(
            2, len(_reconcile_unique_cross_source_name_variants(events)),
        )


if __name__ == "__main__":
    unittest.main()
