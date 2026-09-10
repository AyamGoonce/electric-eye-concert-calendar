import json
import unittest
from datetime import date

from concert_calendar.deduplication import deduplicate_events, _normalize_event_title_wrappers
from concert_calendar.event_titles import contextual_title_parts, evidenced_series_prefixes
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import prepare_upcoming_events, serialize_data


def event(title, **kwargs):
    return ConcertEvent("2026-10-02", title, "Supersonic Records", "Paris", "75", **kwargs)


def output(events):
    return json.loads(serialize_data(prepare_upcoming_events(events, today=date(2026, 9, 1))))


class SecondTitlePassTests(unittest.TestCase):
    def test_recurring_source_series_preserves_neutral_bill(self):
        events = [event("GONZAÏ NIGHT : RUBIN STEINER", co_headliners=["SOCIÉTÉ ÉTRANGE"], source_names=["DICE"]),
                  event("GONZAÏ NIGHT : LES CLOPES", co_headliners=["AKREPTILE"], source_names=["DICE"])]
        rows = output(deduplicate_events(events))
        self.assertEqual(["Les Clopes", "Rubin Steiner"], [r["h"] for r in rows])
        self.assertTrue(all(r["sn"] == "GONZAÏ NIGHT" for r in rows))
        self.assertEqual(["Société Étrange"], rows[1]["ch"])

    def test_generic_recurring_series_requires_same_source_distinct_bills(self):
        first = event("Silver Nights : Artist", source_names=["One"])
        self.assertEqual((first.headliner, None), contextual_title_parts(first, evidenced_series_prefixes([first])))
        other = event("Silver Nights : Different Artist", source_names=["Two"])
        self.assertEqual(set(), evidenced_series_prefixes([first, other]))
        other.source_names = ["One"]
        self.assertEqual(("Artist", "Silver Nights"), contextual_title_parts(first, evidenced_series_prefixes([first, other])))

    def test_merged_plain_identity_retains_tour_branding_and_state_alias(self):
        e = event("A$AP Rocky - Don't Be Dumb World Tour", source_names=["Accor Arena", "Live Nation"],
                  identity_aliases=["A$AP Rocky"], first_seen="2026-08-20T11:02:59Z")
        row = output(deduplicate_events([e]))[0]
        self.assertEqual("A$AP Rocky", row["h"])
        self.assertIn("Don't Be Dumb World Tour", row["et"])
        self.assertEqual("2026-08-20T11:02:59Z", row["fs"])
        from concert_calendar.event_state import canonical_event_identity
        self.assertEqual(canonical_event_identity(event("A$AP Rocky - Don't Be Dumb World Tour"))[:16], row["i"])

    def test_cafe_concert_type_preserved_as_series(self):
        row = output(deduplicate_events([event("Café-Concert : Wambo")]))[0]
        self.assertEqual(("Wambo", "Café-Concert"), (row["h"], row["sn"]))

    def test_persisted_decorated_titles_reconcile_unicode_clean_identities(self):
        a = event("L’Étrangère", event_title="L’Étrangère : Release party en full band", first_seen="2026-08-01T00:00:00Z")
        b = event("L'Étrangère", event_title="L’Étrangère en concert (côté Records)", first_seen="2026-08-02T00:00:00Z")
        rows = output(deduplicate_events([a, b]))
        self.assertEqual(1, len(rows))
        self.assertEqual("L’Étrangère", rows[0]["h"])
        self.assertEqual("2026-08-01T00:00:00Z", rows[0]["fs"])

    def test_wrapper_stage_requires_positive_evidence_even_for_equal_times(self):
        for times in [(None, None), ("19:00", None), ("19:00", "19:00")]:
            a, b = event("Artist", start_time=times[0]), event("Artist", start_time=times[1])
            self.assertEqual(2, len(_normalize_event_title_wrappers([a, b])))
            a.event_title = "Artist en concert (côté Records)"
            self.assertEqual(1, len(_normalize_event_title_wrappers([a, b])))

    def test_wrapper_stage_protects_distinct_times_and_sets(self):
        a = event("Artist", start_time="19:00", event_title="Artist en concert (côté Records)")
        b = event("Artist", start_time="21:00")
        self.assertEqual(2, len(_normalize_event_title_wrappers([a, b])))
        a.start_time = b.start_time = None
        a.event_title = "Artist - first set"
        b.ticket_url = a.ticket_url = "https://tickets.example/event/1234"
        self.assertEqual(2, len(_normalize_event_title_wrappers([a, b])))
        for title in ["Artist - 1er set", "Artist - 2e set"]:
            self.assertEqual(title, deduplicate_events([event(title)])[0].headliner)

    def test_unsupported_identity_grammars_remain_unchanged(self):
        for title in ["Giovanni Mirabassi “The New York Sessions”", 'Anne Carleton Quintet - Hommage à Edgar Morin "So High"',
                      "WOLFGANG VOIGT presents GAS live", "WEIGHTLESS REMIXES – Luxie", "15 15 Saplin Club : 15 15 (live)",
                      "Marshall Sonic Nights : Daytime TV", "Artist: Name", "Artist-Name", '“Project Name”',
                      "Artist+Name", "Artist, Name", "MONKEYS ON MARS (Mars Red Sky + Monkey3)"]:
            e = event(title)
            self.assertEqual((title, None), contextual_title_parts(e, set()))


if __name__ == "__main__":
    unittest.main()
