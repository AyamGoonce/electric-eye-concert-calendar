"""Generate and optionally publish an Electric Eye newsletter edition."""

import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

from concert_calendar.content_index import fetch_entries
from newsletter.calendar_feed import fetch_calendar
from newsletter.github_publish import publish_edition, update_latest_manifest
from newsletter.periods import reporting_period
from newsletter.render import render_newsletter
from newsletter.snapshot import build_snapshot

PARIS = ZoneInfo("Europe/Paris")


def is_publication_day(frequency, today):
    """Allow scheduled publication only on the correct Paris calendar day."""
    if frequency == "weekly":
        return today.weekday() == 0
    if frequency == "monthly":
        return today.day == 1
    raise ValueError(f"Unsupported newsletter frequency: {frequency}")


def generate(frequency, *, now=None):
    """Generate an edition using the existing verified source readers."""
    current = (now or datetime.now(PARIS)).astimezone(PARIS)
    period = reporting_period(frequency, now=current)

    entries = fetch_entries()
    events, calendar_manifest = fetch_calendar()

    snapshot = build_snapshot(
        entries,
        events,
        period,
        current.date().isoformat(),
    )
    html = render_newsletter(snapshot)

    if not isinstance(html, str) or not html.strip():
        raise ValueError("Newsletter renderer returned empty HTML")

    return snapshot, html, calendar_manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--frequency",
        choices=("weekly", "monthly"),
        required=True,
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish to GitHub; omitted by default for safety",
    )
    parser.add_argument(
        "--scheduled",
        action="store_true",
        help="Skip unless today is the correct publication day in Paris",
    )
    args = parser.parse_args()

    now = datetime.now(PARIS)

    if args.scheduled and not is_publication_day(
        args.frequency, now.date()
    ):
        print("Not a publication day in Europe/Paris; skipping.")
        return

    snapshot, html, calendar_manifest = generate(
        args.frequency, now=now
    )

    print(
        f"Generated {args.frequency} edition "
        f"{snapshot['identifier']}"
    )
    print(f"Articles and concerts: {snapshot['counts']}")
    print(f"HTML size: {len(html.encode('utf-8'))} bytes")

    if not args.publish:
        print("DRY RUN: no files published.")
        return

    result = publish_edition(snapshot, html)
    print(f"Edition publication: {result['action']}")

    manifest_result = update_latest_manifest(snapshot)
    print(f"Latest manifest: {manifest_result['action']}")


if __name__ == "__main__":
    main()
