"""Evidence-backed programme credits, separate from parser-specific exceptions.

Records must quote an official venue programme and match venue, title and
performance date. They are independently reviewable facts, not code branches
for named events. Unmatched and ambiguous records never modify the calendar.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

from concert_calendar.venues import normalize_venue_key


DEFAULT_CREDITS_PATH = Path(__file__).with_name("official_programme_credits.json")


def _key(value):
    value = unicodedata.normalize("NFKD", str(value or "").casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def load_official_credits(path=None):
    payload = json.loads(Path(path or DEFAULT_CREDITS_PATH).read_text(encoding="utf-8"))
    if payload.get("schemaVersion") != 1:
        raise ValueError("Unsupported official programme credit schema")
    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError("Official programme credits must be a list")
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Invalid official programme record")
        required = ("venue", "eventTitle", "artist", "startDate", "endDate",
                    "sourceUrl", "evidenceType", "reviewedAt")
        if not all(isinstance(record.get(key), str) and record[key].strip() for key in required):
            raise ValueError("Incomplete official programme credit")
        url = urlsplit(record["sourceUrl"])
        if url.scheme != "https" or not url.hostname or not url.path:
            raise ValueError("Official programme credit must cite an HTTPS source page")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", record["startDate"]) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}", record["endDate"]
        ) or record["startDate"] > record["endDate"]:
            raise ValueError("Invalid official programme date range")
        if _key(record["artist"]) == _key(record["eventTitle"]):
            raise ValueError("Artist cannot be identical to programme title")
    return records


def apply_official_programme_credits(events, *, records=None):
    """Apply only unambiguous source-attributed credits to matching performances.

    The record's original ticket URL and event date are preserved. We do not
    add the programme title as an artist alias, or override an independently
    structured different performer. The same evidence may cover multiple
    separately ticketed performances over its stated date range.
    """
    records = load_official_credits() if records is None else records
    corrected = []
    ambiguous = []
    skipped = []
    for event in events:
        venue = normalize_venue_key(event.venue)
        titles = {_key(event.headliner), _key(event.raw_title), _key(event.event_title)}
        matches = [
            record for record in records
            if normalize_venue_key(record["venue"]) == venue
            and record["startDate"] <= event.date[:10] <= record["endDate"]
            and _key(record["eventTitle"]) in titles
        ]
        if not matches:
            continue
        artists = {_key(record["artist"]) for record in matches}
        if len(artists) != 1:
            ambiguous.append({"date": event.date, "venue": event.venue,
                              "title": event.headliner, "reason": "conflicting_official_credits"})
            continue
        record = matches[0]
        artist = record["artist"]
        supplied = {_key(name) for name in (event.performers or [])}
        if supplied and supplied != {_key(artist), _key(record["eventTitle"])} and supplied != {_key(artist)}:
            skipped.append({"date": event.date, "venue": event.venue,
                            "title": event.headliner, "reason": "conflicting_structured_performers"})
            continue
        if _key(event.headliner) == _key(artist):
            continue
        if event.openers or event.co_headliners:
            skipped.append({"date": event.date, "venue": event.venue,
                            "title": event.headliner, "reason": "existing_multi_artist_billing"})
            continue
        original = event.raw_title or event.headliner
        event.raw_title = original
        event.headliner = artist
        event.event_title = record["eventTitle"]
        event.performers = [artist]
        event.performance_marker = event.performance_marker or "official_venue_programme"
        corrected.append({
            "date": event.date[:10], "venue": event.venue,
            "original": original, "artist": artist,
            "event_title": record["eventTitle"],
            "evidence_url": record["sourceUrl"],
            "evidence_type": record["evidenceType"],
        })
    return {"corrected": corrected, "ambiguous": ambiguous, "skipped": skipped}
