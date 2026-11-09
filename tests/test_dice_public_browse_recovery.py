"""Safe, explicitly incomplete DICE recovery when the catalogue API refuses access."""

from copy import deepcopy
from datetime import datetime, timezone
import json
import unittest
from unittest.mock import patch

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

    def test_rejects_missing_or_empty_json_inventory(self):
        with self.assertRaisesRegex(ValueError, "__NEXT_DATA__"):
            dice.extract_public_browse_events("<html></html>")
        with self.assertRaisesRegex(ValueError, "no usable"):
            dice.extract_public_browse_events(html_page([]))
        with self.assertRaisesRegex(ValueError, "no parseable"):
            dice.extract_public_browse_events(html_page([{"id": "missing-date"}]))

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


if __name__ == "__main__":
    unittest.main()
