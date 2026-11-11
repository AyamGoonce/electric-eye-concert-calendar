"""Safe, explicitly incomplete DICE recovery when the catalogue API refuses access."""

from copy import deepcopy
from datetime import datetime, date, timezone
import json
import unittest
from unittest.mock import patch, Mock

import requests

from concert_calendar.scrapers import dice
from concert_calendar.event_state import reconcile_state
from concert_calendar.source_retention import build_source_state
from concert_calendar.sources import load_events_with_report


NOW = datetime(2026, 11, 9, 15, 0, tzinfo=timezone.utc)


def raw_event(name="Public Band", *, event_id="abc", start="2027-01-23T20:00:00+01:00"):
    return {
        "id": event_id,
        "name": name,
        "status": "on-sale",
        "dates": {"event_start_date": start},
        "venues": [{"name": "Le Trabendo", "city": {"name": "Paris"}, "id": "123"}],
        "images": {"square": "https://dice-media.imgix.net/example.jpg"},
        "artists": None,
    }


def html_page(items, *, cursor="next"):
    data = {"props": {"pageProps": {"events": items, "nextCursor": cursor}}}
    return (
        '<!doctype html><script id="__NEXT_DATA__" type="application/json">'
        + json.dumps(data)
        + "</script>"
    )


class DicePublicBrowseRecoveryTests(unittest.TestCase):
    def setUp(self):
        dice._LAST_LOAD_METADATA.clear()
        dice._LAST_LOAD_METADATA.update({"path": "primary", "fallback_source": None})

    def test_uses_existing_parser_on_public_server_rendered_payload(self):
        events, has_more = dice.extract_public_browse_events(
            html_page([raw_event(), raw_event(), raw_event("Second", event_id="def")])
        )
        self.assertEqual(["Public Band", "Second"], [item.headliner for item in events])
        self.assertEqual("2027-01-23", events[0].date)
        self.assertEqual("https://dice.fm/event/abc", events[0].ticket_url)
        self.assertTrue(has_more)

    def test_dice_speed_dating_is_excluded_without_dropping_music_events(self):
        rows, _ = dice.extract_public_browse_events(html_page([
            raw_event("Le plus grand speed-dating de Paris #3", event_id="social"),
            raw_event("Legitimate Artist", event_id="concert"),
        ]))
        self.assertEqual(["Legitimate Artist"], [row.headliner for row in rows])

    def test_nonmusical_browse_entries_and_festival_passes_are_excluded(self):
        rejected = (
            "Blindtest with Dr Wax",
            "Marius Gonzalez, Generated Nightmares｜Exhibition",
            "La Rentrée de Chéries-Chéris",
            "Novemberfest by Paname Brewing Company",
            "Ici Demain Festival #7 - Pass MERCREDI",
            "Ici Demain Festival #7 - Pass JEUDI",
            "Ici Demain Festival #7 - Pass VENDREDI",
        )
        for index, title in enumerate(rejected):
            with self.subTest(title=title):
                self.assertIsNone(dice.parse_event(raw_event(title, event_id=str(index))))

    def test_similar_genuine_concert_titles_are_preserved(self):
        preserved = (
            "Balm - Afterwork",
            "Diggers Xth anniversary",
            "La Vie secrète des chansons",
            "Candlelight : Mozart & Chopin",
            "Cabaret les dessous lesbiens",
            "Indie Rock Night W/ Violet Noise, Spreaders & Veys",
            "Ici Demain Festival #7 - La soirée avec Tarmac",
            "The Blind Test",
            "Exhibition",
        )
        for index, title in enumerate(preserved):
            with self.subTest(title=title):
                self.assertIsNotNone(dice.parse_event(raw_event(title, event_id=str(index))))

    def test_rejects_missing_or_empty_json_inventory(self):
        with self.assertRaisesRegex(ValueError, "__NEXT_DATA__"):
            dice.extract_public_browse_events("<html></html>")
        with self.assertRaisesRegex(ValueError, "no usable"):
            dice.extract_public_browse_events(html_page([]))
        with self.assertRaisesRegex(ValueError, "no parseable"):
            dice.extract_public_browse_events(html_page([{"id": "missing-date"}]))

    def test_api_cursor_continues_after_duplicate_only_page(self):
        first = raw_event("First Band", event_id="first")
        second = raw_event(
            "Later Band", event_id="later",
            start="2027-01-24T20:00:00+01:00",
        )
        pages = [
            {"sections": [{"events": [first]}], "next_page_cursor": "cursor-2"},
            {"sections": [{"events": [first]}], "next_page_cursor": "cursor-3"},
            {"sections": [{"events": [second]}], "next_page_cursor": None},
        ]

        def response(payload):
            return Mock(json=Mock(return_value=payload), raise_for_status=Mock())

        with patch.object(dice.requests, "Session") as session:
            session.return_value.post.side_effect = [
                response(page) for page in pages
            ]
            events = dice._load_api_events()

        self.assertEqual(
            {"First Band", "Later Band"}, {event.headliner for event in events}
        )
        self.assertEqual(3, session.return_value.post.call_count)

    def test_dice_same_day_distinct_performances_survive_source_dedup(self):
        same = raw_event("Two Show Artist", event_id="first")
        later = raw_event(
            "Two Show Artist", event_id="second",
            start="2027-01-23T22:30:00+01:00",
        )
        first = dice.parse_event(same)
        second = dice.parse_event(later)
        self.assertNotEqual(dice.event_key(first), dice.event_key(second))
        with patch.object(dice.requests, "Session") as session:
            session.return_value.post.return_value = Mock(
                json=Mock(return_value={
                    "sections": [{"events": [same, later]}],
                    "next_page_cursor": None,
                }),
                raise_for_status=Mock(),
            )
            records = dice._load_api_events()
        self.assertEqual(2, len(records))
        from concert_calendar.deduplication import deduplicate_events
        self.assertEqual(2, len(deduplicate_events(records)))

    def test_falls_back_on_api_403_and_discloses_partial_status(self):
        page_events, _ = dice.extract_public_browse_events(html_page([raw_event()]))
        with (
            patch.object(dice, "_load_api_events", side_effect=requests.HTTPError("403 Forbidden")),
            patch.object(dice, "_load_public_browse_events", return_value=(page_events, True)),
        ):
            rows = dice.load_events()
        self.assertEqual(["Public Band"], [row.headliner for row in rows])
        self.assertEqual("fallback", dice.get_load_metadata()["path"])
        self.assertTrue(dice.get_load_metadata()["incomplete"])

    def test_successful_api_does_not_trigger_partial_fallback(self):
        rows, _ = dice.extract_public_browse_events(html_page([raw_event()]))
        with (
            patch.object(dice, "_load_api_events", return_value=rows),
            patch.object(dice, "_load_public_browse_events") as fallback,
        ):
            self.assertEqual(rows, dice.load_events())
            fallback.assert_not_called()
        self.assertEqual("primary", dice.get_load_metadata()["path"])

    def test_both_paths_fail_without_false_success(self):
        with (
            patch.object(dice, "_load_api_events", side_effect=requests.HTTPError("403")),
            patch.object(dice, "_load_public_browse_events", side_effect=ValueError("missing page")),
        ):
            with self.assertRaisesRegex(RuntimeError, "public browse fallback unavailable"):
                dice.load_events()

    def test_partial_dice_without_prior_snapshot_does_not_crash_logging(self):
        """Production regression: incomplete DICE with no historical DICE inventory."""
        from contextlib import redirect_stdout
        from io import StringIO
        from types import SimpleNamespace

        current, _ = dice.extract_public_browse_events(html_page([raw_event()]))
        module = SimpleNamespace(
            SOURCE_NAME="DICE", __name__="DICE",
            load_events=Mock(return_value=deepcopy(current)),
            get_load_metadata=Mock(return_value={
                "path": "fallback",
                "fallback_source": "DICE public Paris browse page",
                "incomplete": True,
            }),
        )
        output = StringIO()
        with (
            patch("concert_calendar.sources.discover_scrapers_with_issues",
                  return_value=([module], {})),
            redirect_stdout(output),
        ):
            rows, report = load_events_with_report(
                scraper_attempts=1, retry_delay_seconds=0,
                prior_source_state=None, now=NOW,
            )
        health = report.source_health[0]
        self.assertEqual("partial", health["status"])
        self.assertIsNone(health["fallback_inventory_ratio"])
        self.assertTrue(health["fallback_unavailable"])
        self.assertEqual(1, len(rows))
        self.assertIn("ratio=n/a (no prior inventory)", output.getvalue())

    def test_partial_page_does_not_overwrite_last_complete_snapshot(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        prior_events, _ = dice.extract_public_browse_events(
            html_page([raw_event("Older Event", event_id="old", start="2027-02-01T20:00:00+01:00")])
        )
        for row in prior_events:
            row.source_names = ["DICE"]
        reconcile_state(prior_events, None, now=NOW)
        prior = build_source_state(
            prior_events, [{"source_name": "DICE", "status": "ok"}],
            None, now=NOW, retained_snapshots={},
        )
        current, _ = dice.extract_public_browse_events(html_page([raw_event()]))
        module = SimpleNamespace(
            SOURCE_NAME="DICE", __name__="DICE",
            load_events=Mock(return_value=deepcopy(current)),
            get_load_metadata=Mock(return_value={
                "path": "fallback",
                "fallback_source": "DICE public Paris browse page",
                "incomplete": True,
            }),
        )
        with patch("concert_calendar.sources.discover_scrapers_with_issues", return_value=([module], {})):
            rows, report = load_events_with_report(
                scraper_attempts=1, retry_delay_seconds=0,
                prior_source_state=prior, now=NOW,
            )
        self.assertEqual("partial", report.source_health[0]["status"])
        self.assertEqual({"Public Band", "Older Event"}, {r.headliner for r in rows})
        self.assertEqual(1, report.source_health[0]["fallback_event_count"])
        reconcile_state(rows, None, now=NOW)
        new_state = build_source_state(
            rows, report.source_health, prior, now=NOW,
            retained_snapshots=report.retained_snapshots,
        )
        self.assertEqual(prior["sources"]["DICE"], new_state["sources"]["DICE"])


    def test_date_partitions_recover_events_beyond_initial_city_batch(self):
        city_event = raw_event("Popular", event_id="popular", start="2026-11-09T20:00:00+01:00")
        november_event = raw_event("November Band", event_id="nov", start="2026-11-10T20:00:00+01:00")
        december_event = raw_event("December Band", event_id="dec", start="2026-12-08T20:00:00+01:00")
        seen_urls = []

        def page_for_url(url, timeout):
            seen_urls.append(url)
            if "from=2026-11-09" in url:
                body = html_page([city_event, november_event], cursor=None)
            elif "from=2026-12-08" in url:
                body = html_page([december_event], cursor=None)
            else:
                body = html_page([city_event], cursor=None)
            return Mock(text=body, raise_for_status=Mock())

        with (
            patch.object(dice.requests, "Session") as session,
            patch.object(dice, "_public_browse_windows", return_value=[
                (date(2026, 11, 9), date(2026, 11, 10)),
                (date(2026, 12, 8), date(2026, 12, 9)),
            ]),
            patch.object(dice, "PUBLIC_REQUEST_PAUSE_SECONDS", 0),
        ):
            session.return_value.get.side_effect = page_for_url
            rows, incomplete = dice._load_public_browse_events(today=date(2026, 11, 9))
        self.assertEqual({"Popular", "November Band", "December Band"}, {e.headliner for e in rows})
        self.assertEqual(3, len(seen_urls))
        self.assertFalse(incomplete)

    def test_capped_date_window_is_split_to_recover_more_listings(self):
        seen = []
        events = [
            raw_event("First", event_id="one", start="2026-11-09T20:00:00+01:00"),
            raw_event("Second", event_id="two", start="2026-11-10T20:00:00+01:00"),
        ]

        def page_for_url(url, timeout):
            seen.append(url)
            if "from=2026-11-09&until=2026-11-10" in url:
                body = html_page(events, cursor="more")
            elif "from=2026-11-09&until=2026-11-09" in url:
                body = html_page([events[0]], cursor=None)
            elif "from=2026-11-10&until=2026-11-10" in url:
                body = html_page([events[1]], cursor=None)
            else:
                body = html_page([], cursor=None)
            return Mock(text=body, raise_for_status=Mock())

        with (
            patch.object(dice.requests, "Session") as session,
            patch.object(dice, "_public_browse_windows", return_value=[
                (date(2026, 11, 9), date(2026, 11, 10)),
            ]),
            patch.object(dice, "PUBLIC_REQUEST_PAUSE_SECONDS", 0),
        ):
            session.return_value.get.side_effect = page_for_url
            rows, incomplete = dice._load_public_browse_events(today=date(2026, 11, 9))
        self.assertEqual({"First", "Second"}, {e.headliner for e in rows})
        self.assertEqual(4, len(seen))
        self.assertFalse(incomplete)



if __name__ == "__main__":
    unittest.main()
