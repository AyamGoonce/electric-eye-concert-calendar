"""Audit resilient coverage of Alias dates by independent official venue feeds.

This never generates an event, assigns Alias promoter credit, or alters the
retention snapshot. Fresh official venue events already flow through the
normal publication pipeline, including when Alias is unavailable.
"""
from datetime import datetime
import re
import unicodedata
from zoneinfo import ZoneInfo

from concert_calendar.venues import normalize_venue_key


def _key(value):
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def alias_official_overlap(prior_state, source_health, fresh_events, *, now):
    """Return independent-venue coverage diagnostics for failed Alias inventory."""
    alias = next((h for h in source_health if h["source_name"] == "Alias Production"), None)
    if alias is None or alias["status"] != "failed":
        return []
    rows = ((prior_state or {}).get("sources") or {}).get("Alias Production", {}).get("events", [])
    today = now.astimezone(ZoneInfo("Europe/Paris")).date().isoformat()
    official = {}
    for event in fresh_events:
        venue = normalize_venue_key(event.venue)
        # Only source names matching the independently scraped venue count as
        # first-party venue corroboration; aggregators and promoters cannot.
        sources = [
            name for name in (event.source_names or [])
            if name != "Alias Production" and normalize_venue_key(name) == venue
        ]
        if not sources:
            continue
        key = (event.date[:10], venue, _key(event.headliner))
        official.setdefault(key, []).append((event, sources))

    covered = []
    uncovered = []
    for row in rows:
        old = row["event"]
        if old["date"][:10] < today:
            continue
        key = (old["date"][:10], normalize_venue_key(old["venue"]), _key(old["headliner"]))
        matches = [
            (event, sources) for event, sources in official.get(key, [])
            if not old.get("start_time") or not event.start_time
            or old["start_time"] == event.start_time
        ]
        item = {"date": old["date"][:10], "headliner": old["headliner"], "venue": old["venue"]}
        if matches:
            item["official_sources"] = sorted(set(name for _, names in matches for name in names))
            covered.append(item)
        else:
            uncovered.append(item)

    diagnostics = [{
        "source_name": "Alias Production",
        "kind": "official_venue_coverage_summary",
        "prior_future_events": len(covered) + len(uncovered),
        "independently_covered": len(covered),
        "not_independently_verified": len(uncovered),
        "note": "Read-only coverage evidence; no inferred Alias promoter attribution",
    }]
    diagnostics.extend({"source_name": "Alias Production", "kind": "official_venue_covered", **item} for item in covered[:100])
    diagnostics.extend({"source_name": "Alias Production", "kind": "official_venue_uncovered", **item} for item in uncovered[:100])
    return diagnostics
