import unittest
from datetime import date, datetime, timezone, timedelta
from bs4 import BeautifulSoup

from concert_calendar.billing_semantics import (
    apply_structured_performer_semantics,
)
from concert_calendar.event_state import canonical_event_identity, reconcile_state, build_change_report
from concert_calendar.deduplication import deduplicate_events, merge_events
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import prepare_upcoming_events
from concert_calendar.production_export import event_to_data
from concert_calendar.scrapers.gaite_lyrique import detail_performers
from concert_calendar.scrapers.nouveau_casino import parse_items
from concert_calendar.scrapers.machine_moulin_rouge import detail_performers as machine_performers
from concert_calendar.content_index import build_index, enrich_events
from concert_calendar.scrapers.sunset_sunside import parse_detail_payload
from concert_calendar.scrapers.new_morning import infer_performers_from_detail_html
from tests.clock_helpers import freeze_date
from tests.test_content_index import entry
from tests import test_trianon_sunset


def event(
    headliner,
    *,
    start_time=None,
    performers=None,
    event_title=None,
):
    return ConcertEvent(
        date="2027-01-01",
        headliner=headliner,
        venue="Example Venue",
        city="Paris",
        department="75",
        start_time=start_time,
        performers=performers,
        event_title=event_title,
    )


class CalendarBillingHardeningTests(unittest.TestCase):
    @staticmethod
    def resolver_reviews(**profiles):
        return {
            "schemaVersion": 1,
            "canonicalIdentities": {},
            "reviewedBillings": {},
            "reviewedDescriptions": {},
            "sourceProfiles": profiles,
        }

    def finish_pipeline(self, events, names):
        index = build_index([entry(name + ' @ Example Hall, Paris - August 10th, 2026', ['Concert Review', name],
                                   '2026-08-' + str(10 + i),
                                   image='https://example.test/' + str(i) + '.jpg')
                             for i, name in enumerate(names)], generated_at='2026-09-20T00:00:00Z')
        events = deduplicate_events(events)
        enrich_events(events, index)
        state = reconcile_state(events, None, now=datetime(2026, 9, 20, tzinfo=timezone.utc))
        rows = prepare_upcoming_events(events, today=date(2026, 9, 20))
        return events, state, rows

    @freeze_date('concert_calendar.scrapers.sunset_sunside')
    def test_bruna_programme_source_to_content_state_and_export(self):
        title = 'Hommage à Chico Buarque avec Bruna Hetzel + jam Brésil'
        payload = test_trianon_sunset.SunsetSunsideScraperTests().payload([
            {'startDate': '2026-10-10T19:00:00+02:00'},
            {'startDate': '2026-10-10T21:00:00+02:00'},
        ], room='Sunside', title=title)
        payload['props']['pageProps']['entities']['ticketing']['description'] = 'La jam est animée par Bruna Hetzel.'
        parsed = parse_detail_payload(payload, 'https://example.test/bruna')
        events, state, rows = self.finish_pipeline(parsed, ['Bruna Hetzel', 'Chico Buarque'])
        # Sunset/Sunside exposes one ticket page for both sessions. Keep both
        # internal performance identities, but publish one calendar card.
        self.assertEqual(1, len(rows))
        self.assertEqual(2, len(state['events']))
        self.assertIsNone(rows[0]['st'])
        self.assertEqual('Bruna Hetzel', rows[0]['h'])
        self.assertEqual('Hommage à Chico Buarque + jam Brésil', rows[0]['et'])
        for item in events:
            self.assertEqual(['Bruna Hetzel'], [link['name'] for link in item.electric_eye_links])
            self.assertEqual('Electric Eye concert review', item.image_source)

    def test_gaite_named_programme_individual_links(self):
        names = detail_performers('<h1>ARTE Dans le club So La Lune, Moha MMZ &amp; Surprise sont dans le club</h1>', 'ARTE Dans le club')
        item = event(
            'ARTE Dans le club',
            performers=names,
            event_title='ARTE Dans le club',
        )
        events, _, rows = self.finish_pipeline([item], ['So La Lune', 'Moha MMZ', 'Surprise'])
        self.assertEqual('So La Lune', rows[0]['h'])
        self.assertEqual(['Moha MMZ', 'Surprise'], rows[0]['ch'])
        self.assertEqual('ARTE Dans le club', rows[0]['et'])
        self.assertEqual(3, len(events[0].electric_eye_links))

    def test_new_morning_independent_names_survive_complete_pipeline(self):
        names, _ = infer_performers_from_detail_html(
            '<h2>Présentation</h2><strong>Ludivine Issambourg</strong><strong>Brian Jackson</strong><strong>Eric Legnini</strong>',
            'Jackson - Issambourg - Legnini')
        events, _, rows = self.finish_pipeline([event('Jackson - Issambourg - Legnini', performers=names)], names)
        self.assertEqual('Brian Jackson', rows[0]['h'])
        self.assertEqual(['Ludivine Issambourg', 'Eric Legnini'], rows[0]['ch'])
        self.assertEqual(3, len(events[0].electric_eye_links))

    def test_legacy_time_labelled_rows_migrate_without_new_or_removed(self):
        now = datetime(2026, 9, 20, tzinfo=timezone.utc)
        legacy = [event('Example Artist – 19h00', start_time='19:00'), event('Example Artist – 21h00', start_time='21:00')]
        state = reconcile_state(legacy, None, now=now)
        expected = {item.start_time: item._public_id for item in legacy}
        current = [event('Example Artist', start_time='21:00'), event('Example Artist', start_time='19:00')]
        new_state = reconcile_state(current, state, now=now + timedelta(days=1))
        self.assertEqual(expected, {item.start_time: item._public_id for item in current})
        self.assertEqual(2, len(new_state['events']))
        report = build_change_report(current, state, new_state, now=now + timedelta(days=1))
        self.assertEqual((0, 0), (report['new_events'], report['no_longer_present']))

    def test_performance_state_survives_reordering_and_disappearance(self):
        now = datetime(2026, 9, 20, tzinfo=timezone.utc)
        early, late = event('Bruna Hetzel', start_time='19:00'), event('Bruna Hetzel', start_time='21:00')
        events = deduplicate_events([early, late])
        self.assertEqual(2, len(events))
        baseline = reconcile_state(events, None, now=now)
        self.assertEqual(2, len(baseline['events']))
        rows = prepare_upcoming_events(events, today=now.date())
        ids = {row['st']: row['i'] for row in rows}
        self.assertEqual(2, len(set(ids.values())))
        age = early.first_seen
        newer = [event('Bruna Hetzel', start_time='21:00'), event('Bruna Hetzel', start_time='19:00')]
        state = reconcile_state(newer, baseline, now=now + timedelta(days=1))
        self.assertEqual(ids, {row['st']: row['i'] for row in prepare_upcoming_events(newer, today=now.date())})
        self.assertTrue(all(item.first_seen == age for item in newer))
        report = build_change_report(newer, baseline, state, now=now + timedelta(days=1))
        self.assertEqual(0, report['new_events'])
        self.assertEqual(0, report['no_longer_present'])
        only_late = [event('Bruna Hetzel', start_time='21:00')]
        reconcile_state(only_late, state, now=now + timedelta(days=2))
        self.assertEqual(ids['21:00'], prepare_upcoming_events(only_late, today=now.date())[0]['i'])

    def test_legacy_single_row_migration_preserves_route_and_age(self):
        now = datetime(2026, 9, 20, tzinfo=timezone.utc)
        original = event('Example Artist')
        state = reconcile_state([original], None, now=now)
        state['version'] = 2
        for record in state['events'].values():
            record.pop('base_identity')
            record.pop('performance')
        performances = [event('Example Artist', start_time='19:00'), event('Example Artist', start_time='21:00')]
        reconcile_state(performances, state, now=now + timedelta(days=1))
        self.assertEqual(canonical_event_identity(original)[:16], performances[0]._public_id)
        self.assertNotEqual(performances[0]._public_id, performances[1]._public_id)
        self.assertTrue(all(item.first_seen == original.first_seen for item in performances))

    def test_nouveau_source_billing_lines_are_individual_neutral_artists(self):
        html = '''<li class="day_item"><time><span class="date">01.10</span></time>
        <li class="event_item" data-type="concert"><div class="event_header">
        <h3><span class="grey">Xandria</span><br/>Seven Spires<br/>Tulip</h3>
        </div></li></li>'''
        events = parse_items(BeautifulSoup(html, 'html.parser'), today=date(2026, 9, 20))
        apply_structured_performer_semantics(events)
        row = prepare_upcoming_events(events, today=date(2026, 9, 20))[0]
        self.assertEqual('Xandria', row['h'])
        self.assertEqual(['Seven Spires', 'Tulip'], row['ch'])
        self.assertFalse(row.get('o'))
        self.assertFalse(row.get('et'))

    def test_machine_artist_headings_not_title_punctuation(self):
        names = ["HUMANITY’S LAST BREATH", 'VILDHJARTA', 'ENTERPRISE EARTH', 'KARMANJAKAH']
        html = ''.join('<h2 class="nomartiste">' + name + '</h2>' for name in names)
        item = event(' + '.join(names), performers=machine_performers(html))
        events, _, rows = self.finish_pipeline([item], ["Humanity’s Last Breath", 'Vildhjarta', 'Enterprise Earth', 'Karmanjakah'])
        row = rows[0]
        self.assertEqual("Humanity’s Last Breath", row['h'])
        self.assertEqual(3, len(row['ch']))
        self.assertFalse(row.get('et'))
        self.assertEqual(4, len(events[0].electric_eye_links))
        self.assertEqual('Electric Eye concert review', events[0].image_source)
        self.assertEqual([], machine_performers('<h1>Artist + Project</h1>'))

    def test_reviewed_flat_bill_resolves_constituents_and_content_links(self):
        item = event("SONGHOY BLUES + Julien Ledru")
        item.source_names = ["DICE", "Vedettes"]
        events, _, rows = self.finish_pipeline([item], ["Songhoy Blues"])

        self.assertEqual("Songhoy Blues", events[0].headliner)
        self.assertEqual(["Julien Ledru"], events[0].co_headliners)
        self.assertEqual(
            ["Songhoy Blues", "Julien Ledru"], events[0].performers
        )
        self.assertEqual("Songhoy Blues", rows[0]["h"])
        self.assertEqual(["Julien Ledru"], rows[0]["ch"])
        self.assertEqual(
            ["Songhoy Blues"],
            [link["name"] for link in events[0].electric_eye_links],
        )
        self.assertNotIn("SONGHOY BLUES + Julien Ledru", [
            rows[0]["h"], *rows[0].get("ch", [])
        ])

    def test_structured_source_performers_are_definitive(self):
        item = event("Unknown A + Unknown B", performers=["Unknown A", "Unknown B"])
        diagnostics = {}
        result = deduplicate_events([item], diagnostics=diagnostics)

        self.assertEqual("Unknown A", result[0].headliner)
        self.assertEqual(["Unknown B"], result[0].co_headliners)
        record = diagnostics["artist_billing_resolution"]["records"][0]
        self.assertEqual(("structured_source", 100), (record["method"], record["confidence"]))

    def test_unseen_known_plus_known_resolves_without_registry_entry(self):
        item = event("Trivium + In Flames")
        diagnostics = {}
        result = deduplicate_events([item], diagnostics=diagnostics)

        self.assertEqual("Trivium", result[0].headliner)
        self.assertEqual(["In Flames"], result[0].co_headliners)
        self.assertEqual("canonical_identity", diagnostics["artist_billing_resolution"]["records"][0]["method"])

    def test_known_plus_unknown_source_hint_remains_unresolved(self):
        item = event("Known Artist + New Support")
        item.source_names = ["Fixture Venue"]
        diagnostics = {}
        result = deduplicate_events(
            [item], diagnostics=diagnostics,
            billing_reviews=self.resolver_reviews(**{
                "Fixture Venue": {"candidateSpacedPlus": True},
            }),
            billing_identity_catalog={"known artist": "Known Artist"},
        )

        self.assertEqual("Known Artist + New Support", result[0].headliner)
        self.assertIsNone(result[0].co_headliners)
        self.assertEqual(1, diagnostics["artist_billing_resolution"]["stillUnresolved"])

    def test_structured_constituents_link_articles_independently(self):
        item = event(
            "Known Artist + New Support",
            performers=["Known Artist", "New Support"],
        )
        item.source_names = ["Fixture Venue"]
        result = deduplicate_events(
            [item],
            billing_reviews=self.resolver_reviews(**{
                "Fixture Venue": {"candidateSpacedPlus": True},
            }),
            billing_identity_catalog={"known artist": "Known Artist"},
        )
        index = build_index([
            entry(
                "Known Artist @ Example Hall, Paris - August 10th, 2026",
                ["Concert Review", "Known Artist"],
                "2026-08-10",
            )
        ], generated_at="2026-09-20T00:00:00Z")
        enrich_events(result, index)

        self.assertEqual(
            ["Known Artist"],
            [link["name"] for link in result[0].electric_eye_links],
        )

    def test_unknown_plus_unknown_with_source_grammar_stays_unresolved(self):
        item = event("Unknown Artist A + Unknown Artist B")
        item.source_names = ["Fixture Venue"]
        diagnostics = {}
        result = deduplicate_events(
            [item], diagnostics=diagnostics,
            billing_reviews=self.resolver_reviews(**{
                "Fixture Venue": {"candidateSpacedPlus": True},
            }),
            billing_identity_catalog={},
        )

        self.assertEqual("Unknown Artist A + Unknown Artist B", result[0].headliner)
        self.assertIsNone(result[0].co_headliners)
        audit = diagnostics["artist_billing_resolution"]
        self.assertEqual(0, audit["sourceProfileOnlyResolutions"])
        self.assertEqual(1, audit["stillUnresolved"])

    def test_unknown_plus_unknown_with_punctuation_only_stays_opaque(self):
        item = event("Unknown Artist A + Unknown Artist B")
        diagnostics = {}
        result = deduplicate_events(
            [item], diagnostics=diagnostics,
            billing_reviews=self.resolver_reviews(),
            billing_identity_catalog={},
        )

        self.assertEqual("Unknown Artist A + Unknown Artist B", result[0].headliner)
        self.assertIsNone(result[0].co_headliners)
        self.assertEqual(1, diagnostics["artist_billing_resolution"]["stillUnresolved"])

    def test_presenter_acts_and_show_title_are_separate_concepts(self):
        item = event(
            "Alex Goody presents: Jon Baddie & the Mediocre Kids + "
            "Nico Jumpface HALLOWEEN SHINDIG"
        )
        item.source_names = ["Fixture Venue"]
        result = deduplicate_events(
            [item],
            billing_reviews=self.resolver_reviews(**{
                "Fixture Venue": {
                    "candidateSpacedPlus": True,
                    "presenterPrefix": True,
                    "showTitleSuffixPatterns": [r"\s+HALLOWEEN SHINDIG$"],
                },
            }),
            billing_identity_catalog={},
        )

        self.assertEqual(
            "Jon Baddie & the Mediocre Kids + Nico Jumpface",
            result[0].headliner,
        )
        self.assertIsNone(result[0].co_headliners)
        self.assertEqual(["Alex Goody"], result[0].promoters)
        self.assertEqual("HALLOWEEN SHINDIG", result[0].event_title)

    def test_source_profile_does_not_split_reviewed_plus_project(self):
        item = event("Mike + The Mechanics")
        item.source_names = ["Fixture Venue"]
        reviews = self.resolver_reviews(**{"Fixture Venue": {"candidateSpacedPlus": True}})
        reviews["canonicalIdentities"] = {"Mike + The Mechanics": {"aliases": []}}
        result = deduplicate_events([item], billing_reviews=reviews, billing_identity_catalog={})

        self.assertEqual("Mike + The Mechanics", result[0].headliner)
        self.assertIsNone(result[0].co_headliners)

    def test_source_profile_preserves_ampersand_project_and_parenthesized_artist(self):
        item = event("Earth, Wind & Fire + (Hed) P.E.")
        item.source_names = ["Fixture Venue"]
        result = deduplicate_events(
            [item],
            billing_reviews=self.resolver_reviews(**{"Fixture Venue": {"candidateSpacedPlus": True}}),
            billing_identity_catalog={
                "earth wind fire": "Earth, Wind & Fire",
                "hed p e": "(Hed) P.E.",
            },
        )

        self.assertEqual("Earth, Wind & Fire", result[0].headliner)
        self.assertEqual(["(Hed) P.E."], result[0].co_headliners)

    def test_cross_source_structured_performers_inform_flat_winner(self):
        flat = event("Unknown A + Unknown B")
        flat.source_names = ["Listing"]
        structured = event("Unknown A", performers=["Unknown A", "Unknown B"])
        structured.source_names = ["Official Venue"]
        diagnostics = {}
        result = deduplicate_events(
            [flat, structured], diagnostics=diagnostics,
            billing_reviews=self.resolver_reviews(),
            billing_identity_catalog={},
        )

        self.assertEqual(1, len(result))
        self.assertEqual(["Unknown B"], result[0].co_headliners)
        methods = {record["method"] for record in diagnostics["artist_billing_resolution"]["records"]}
        self.assertIn("cross_source", methods)

    def test_same_source_current_event_roles_resolve_unknown_bill(self):
        item = event("Unknown A + Unknown B")
        item.source_names = ["Official Venue"]
        item.openers = ["Unknown B"]
        diagnostics = {}

        result = deduplicate_events(
            [item], diagnostics=diagnostics,
            billing_reviews=self.resolver_reviews(), billing_identity_catalog={},
        )

        self.assertEqual("Unknown A", result[0].headliner)
        self.assertEqual(["Unknown B"], result[0].openers)
        self.assertIsNone(result[0].co_headliners)
        record = diagnostics["artist_billing_resolution"]["records"][0]
        self.assertEqual(("same_source", 95), (record["method"], record["confidence"]))

    def test_unknown_legitimate_plus_project_is_not_split_by_source_hint(self):
        item = event("Artist + The Something")
        item.source_names = ["Fixture Venue"]

        result = deduplicate_events(
            [item],
            billing_reviews=self.resolver_reviews(**{
                "Fixture Venue": {"candidateSpacedPlus": True},
            }),
            billing_identity_catalog={},
        )

        self.assertEqual("Artist + The Something", result[0].headliner)
        self.assertIsNone(result[0].co_headliners)

    def test_contextual_wrappers_and_generic_guests_do_not_create_artists(self):
        titles = [
            "SHRED FEST - OBSCURA + PESTILENCE + CRYPTIC SHIFT + THUS + DVRK",
            "Les Femmes s'en mêlent : Metro Verlaine + Tessina",
            "JETLAG : RELEASE PARTY DE BAOZI + CUMULUS. + ILO NAVAHY",
            "Festival de Marne : Artist + Another Artist",
            "Johnny Mafia + Guest",
            "World brain + invités",
            "MONKEYS ON MARS (Mars Red Sky + Monkey3) + Guest",
        ]
        items = [event(title, start_time=f"{index + 10:02d}:00") for index, title in enumerate(titles)]
        for item in items:
            item.source_names = ["Fixture Venue"]

        result = deduplicate_events(
            items,
            billing_reviews=self.resolver_reviews(**{
                "Fixture Venue": {"candidateSpacedPlus": True},
            }),
            billing_identity_catalog={},
        )

        self.assertEqual(titles, [item.headliner for item in result])
        self.assertTrue(all(item.co_headliners is None for item in result))

    def test_external_evidence_abstraction_honors_confidence_threshold(self):
        evidence = {
            "Unknown A + Unknown B": {
                "artists": ["Unknown A", "Unknown B"],
                "confidence": 89,
                "evidence": ["fixture"],
            }
        }
        low = deduplicate_events(
            [event("Unknown A + Unknown B")],
            billing_reviews=self.resolver_reviews(), billing_identity_catalog={},
            billing_external_evidence=evidence,
        )[0]
        self.assertEqual("Unknown A + Unknown B", low.headliner)

        evidence["Unknown A + Unknown B"]["confidence"] = 95
        high = deduplicate_events(
            [event("Unknown A + Unknown B")],
            billing_reviews=self.resolver_reviews(), billing_identity_catalog={},
            billing_external_evidence=evidence,
        )[0]
        self.assertEqual("Unknown A", high.headliner)
        self.assertEqual(["Unknown B"], high.co_headliners)

    def test_reviewed_flat_bill_preserves_parenthesized_artist_name(self):
        item = deduplicate_events([event("SPINESHANK + (Hed) P.E.")])[0]
        row = event_to_data(item)

        self.assertEqual("Spineshank", item.headliner)
        self.assertEqual(["(Hed) P.E."], item.co_headliners)
        self.assertEqual(["(Hed) P.E."], row["ch"])

    def test_existing_structured_plus_bill_remains_structured(self):
        item = event(
            "D'Accord Simon + Gizmo + Eliah",
            performers=["D'Accord Simon", "Gizmo", "Eliah"],
        )
        item = deduplicate_events([item])[0]

        self.assertEqual("D'Accord Simon", item.headliner)
        self.assertEqual(["Gizmo", "Eliah"], item.co_headliners)

    def test_reviewed_project_identity_and_show_description_deduplicate(self):
        plain = event("Jon Anderson And The Band Geeks")
        decorated = event(
            "JON ANDERSON and THE BAND GEEKS "
            "(performing YES Epics, Classics & More)"
        )
        plain.source_names = ["Bataclan"]
        decorated.source_names = ["Persona Grata"]

        result = deduplicate_events([plain, decorated])

        self.assertEqual(1, len(result))
        self.assertEqual(
            "Jon Anderson and The Band Geeks", result[0].headliner
        )
        self.assertIsNone(result[0].co_headliners)
        self.assertEqual(
            "performing YES Epics, Classics & More",
            result[0].event_title,
        )

    def test_structured_and_reviewed_flat_bill_deduplicate(self):
        flat = event("Songhoy Blues + Julien Ledru")
        structured = event(
            "Songhoy Blues",
            performers=["Songhoy Blues", "Julien Ledru"],
        )
        flat.source_names = ["DICE"]
        structured.source_names = ["Venue"]

        result = deduplicate_events([flat, structured])

        self.assertEqual(1, len(result))
        self.assertEqual("Songhoy Blues", result[0].headliner)
        self.assertEqual(["Julien Ledru"], result[0].co_headliners)

    def test_reviewed_billing_normalization_preserves_public_id(self):
        now = datetime(2026, 10, 1, tzinfo=timezone.utc)
        previous = event("SONGHOY BLUES + Julien Ledru")
        previous_state = reconcile_state([previous], None, now=now)

        current = deduplicate_events([
            event("SONGHOY BLUES + Julien Ledru")
        ])[0]
        reconcile_state(
            [current], previous_state, now=now + timedelta(days=1)
        )

        self.assertEqual(previous._public_id, current._public_id)

    def test_cross_source_normalization_preserves_public_id(self):
        now = datetime(2026, 10, 1, tzinfo=timezone.utc)
        previous = event("Unknown A + Unknown B")
        previous_state = reconcile_state([previous], None, now=now)
        current = event("Unknown A + Unknown B")
        current.source_names = ["Listing"]
        structured = event("Unknown A", performers=["Unknown A", "Unknown B"])
        structured.source_names = ["Official Venue"]
        current = deduplicate_events(
            [current, structured],
            billing_reviews=self.resolver_reviews(),
            billing_identity_catalog={},
        )[0]
        reconcile_state([current], previous_state, now=now + timedelta(days=1))

        self.assertEqual(previous._public_id, current._public_id)

    def test_legitimate_compound_artist_names_remain_opaque(self):
        names = [
            "Mike + The Mechanics",
            "Earth, Wind & Fire",
            "Of Monsters and Men",
            "(Hed) P.E.",
        ]

        result = deduplicate_events([event(name) for name in names])

        self.assertEqual(names, [item.headliner for item in result])
        self.assertTrue(all(item.co_headliners is None for item in result))

    def test_merge_retains_semantic_evidence(self):
        left = event('Artist'); right = event('Artist', performers=['Artist', 'Peer'])
        right.tags = ['live']; right.description = 'Authoritative artist description'
        right.raw_title = 'Series: Artist + Peer'
        merged = merge_events(left, right)
        apply_structured_performer_semantics([merged])
        self.assertEqual(['Peer'], merged.co_headliners)
        self.assertEqual(right.description, merged.description)
        self.assertEqual(['live'], merged.tags)
        self.assertEqual(right.raw_title, merged.raw_title)

    def test_richer_structured_bill_wins_in_either_source_order(self):
        for reverse in (False, True):
            flat = event('Alpha + Beta & Company', start_time='20:00')
            structured = event('Alpha', start_time='20:00', performers=['Alpha', 'Beta & Company'])
            flat.source_names = ['Venue']; structured.source_names = ['Promoter']
            records = [flat, structured]
            result = deduplicate_events(list(reversed(records)) if reverse else records)
            self.assertEqual(1, len(result))
            self.assertEqual('Alpha', result[0].headliner)
            self.assertEqual(['Beta & Company'], result[0].co_headliners)
            self.assertEqual({'Venue', 'Promoter'}, set(result[0].source_names))

    def test_apostrophes_acronyms_and_mixed_case(self):
        from concert_calendar.production_export import event_to_data
        for raw, display in [("HUMANITY'S LAST BREATH", "Humanity's Last Breath"),
                             ("HUMANITY’S LAST BREATH", "Humanity’s Last Breath"),
                             ("O'CONNOR", "O'Connor"), ('AC/DC', 'AC/DC'), ('LiSA', 'LiSA')]:
            self.assertEqual(display, event_to_data(event(raw))['h'])

    def test_time_label_is_not_public_artist_identity(self):
        cases = [
            ("Example Artist – 19h00", "19:00"),
            ("Example Artist – 19h30", "19:30"),
            ("Example Artist – 19h", "19:00"),
            ("Example Artist – 16H", "16:00"),
        ]

        for raw, start_time in cases:
            with self.subTest(raw=raw):
                item = event(raw, start_time=start_time)
                apply_structured_performer_semantics([item])

                self.assertEqual("Example Artist", item.headliner)
                self.assertIsNone(item.event_title)

    def test_explicit_description_performer_becomes_public_artist(self):
        item = event(
            "Tribute programme avec Example Artist – 19h00",
            start_time="19:00",
        )
        item.event_title = "Tribute programme avec Example Artist"
        item.description = (
            "Après le concert, la jam est animée par Example Artist."
        )

        apply_structured_performer_semantics([item])
        self.assertEqual(
            "Example Artist",
            item.headliner,
        )

        # Canonical semantics are established before export.
        self.assertEqual(
            "Example Artist",
            item.headliner,
        )

    def test_description_cannot_invent_artist_absent_from_title(self):
        item = event(
            "Named Programme – 19h00",
            start_time="19:00",
        )
        item.description = (
            "La soirée est animée par Example Artist."
        )

        apply_structured_performer_semantics([item])
        self.assertEqual(
            "Named Programme",
            item.headliner,
        )

    def test_mismatched_time_suffix_is_not_removed(self):
        cases = [
            ("Example Artist – 19h00", "21:00"),
            ("Example Artist – 19h", "21:00"),
            ("Example Artist – 16H", "18:00"),
        ]

        for raw, start_time in cases:
            with self.subTest(raw=raw):
                item = event(raw, start_time=start_time)
                apply_structured_performer_semantics([item])
                self.assertEqual(raw, item.headliner)

    def test_two_performances_share_artist_but_keep_distinct_ids(self):
        early = event(
            "Example Artist – 19h00",
            start_time="19:00",
        )
        late = event(
            "Example Artist – 21h00",
            start_time="21:00",
        )

        self.assertNotEqual(
            canonical_event_identity(early),
            canonical_event_identity(late),
        )

        apply_structured_performer_semantics([early, late])
        rows = prepare_upcoming_events(
            [early, late],
            today=date(2026, 9, 20),
        )

        self.assertEqual(
            ["Example Artist", "Example Artist"],
            [row["h"] for row in rows],
        )
        self.assertEqual(
            {"19:00", "21:00"},
            {row["st"] for row in rows},
        )
        self.assertEqual(
            2,
            len({row["i"] for row in rows}),
        )

    def test_flattened_artist_bill_is_not_promoted_to_event_title(self):
        item = event(
            "Artist One + Artist Two",
            performers=["Artist One", "Artist Two"],
        )

        apply_structured_performer_semantics([item])

        self.assertEqual("Artist One", item.headliner)
        self.assertEqual(["Artist Two"], item.co_headliners)
        self.assertIsNone(item.event_title)

    def test_programme_title_is_retained_with_explicit_performers(self):
        item = event(
            "Named Programme",
            performers=[
                "Artist One",
                "Artist Two",
                "Artist Three",
            ],
        )
        # Programme context must be supplied explicitly by source semantics;
        # a generic flattened artist heading must never be promoted here.
        item.event_title = "Named Programme"

        apply_structured_performer_semantics([item])

        self.assertEqual(
            "Artist One",
            item.headliner,
        )
        self.assertEqual(
            ["Artist Two", "Artist Three"],
            item.co_headliners,
        )
        apply_structured_performer_semantics([item])
        self.assertEqual(
            "Named Programme",
            item.event_title,
        )

    def test_gaite_heading_provides_multi_artist_evidence(self):
        html = """
        <h1>
          Named Programme
          Artist One, Artist Two & Artist Three
          sont dans le rendez-vous
        </h1>
        """

        self.assertEqual(
            [
                "Artist One",
                "Artist Two",
                "Artist Three",
            ],
            detail_performers(
                html,
                "Named Programme",
            ),
        )

    def test_plain_heading_does_not_invent_performers(self):
        html = """
        <h1>
          Named Programme revient pour une nouvelle édition
        </h1>
        """

        self.assertEqual(
            [],
            detail_performers(
                html,
                "Named Programme",
            ),
        )


if __name__ == "__main__":
    unittest.main()
