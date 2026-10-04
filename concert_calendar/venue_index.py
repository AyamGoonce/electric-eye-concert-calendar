from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from concert_calendar.venue_metadata import VENUE_METADATA
from concert_calendar.venues import (
    VENUE_ALIASES,
    VENUE_GEOGRAPHY,
    clean_unknown_venue_name,
    normalize_venue_key,
    resolve_venue_name,
)


INVALID_PROVISIONAL_VENUE_KEYS = {
    "club",
    "grande salle",
    "hall",
    "location",
    "main room",
    "main stage",
    "n a",
    "none",
    "null",
    "petite salle",
    "room",
    "stage",
    "tba",
    "tbc",
    "tbd",
    "to be announced",
    "unknown",
    "venue",
}


def canonicalize_venue_metadata(
    metadata: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Promote reviewed current names while retaining former-name search data."""
    result: dict[str, dict[str, Any]] = {}

    for venue_name, raw in metadata.items():
        source = deepcopy(raw)
        current_name = (source.get("current_name") or "").strip()
        renamed = source.get("status") == "renamed" and current_name
        canonical_name = current_name if renamed else venue_name
        existing = result.get(canonical_name, {})
        record = {**source, **existing}
        if canonical_name in VENUE_GEOGRAPHY:
            city, department = VENUE_GEOGRAPHY[canonical_name]
            record["city"] = record.get("city") or city
            record["department"] = record.get("department") or department
        former_names = set(record.get("former_names") or [])

        if renamed:
            former_names.add(venue_name)
            record.pop("current_name", None)
            record.pop("status", None)

        if former_names:
            record["former_names"] = sorted(
                former_names,
                key=str.casefold,
            )

        result[canonical_name] = record

    return result


def _public_event(event: dict[str, Any]) -> dict[str, Any]:
    """Return the subset of calendar data required by the venue page."""

    result = {
        "date": event["d"],
        "headliner": event["h"],
        "eventId": event["i"],
        "city": event.get("c") or "",
        "ticketUrl": event.get("t") or "",
        "soldOut": bool(event.get("so")),
        "ticketStatus": event.get("ts"),
        "startTime": event.get("st"),
    }

    if event.get("o"):
        result["openers"] = list(event["o"])

    if event.get("ch"):
        result["coHeadliners"] = list(event["ch"])

    if event.get("et"):
        result["eventTitle"] = event["et"]

    if event.get("fn"):
        result["festivalName"] = event["fn"]

    return result


def _valid_provisional_venue_name(value: str) -> bool:
    """Reject only empty or unmistakable placeholder venue labels."""
    key = normalize_venue_key(value)
    return bool(
        key
        and key not in INVALID_PROVISIONAL_VENUE_KEYS
        and not key.startswith("multi lieux ")
        and not re.fullmatch(r"room\s*\d+", key)
        and not re.match(r"https?://|www\.", value, flags=re.IGNORECASE)
        and 2 <= len(value) <= 160
        and any(character.isalnum() for character in value)
    )


def _reviewed_venue_lookup(
    metadata: dict[str, dict[str, Any]],
) -> dict[str, str]:
    """Build an unambiguous lookup from reviewed canonical/former names."""
    candidates: dict[str, set[str]] = {}

    for canonical_name, source in metadata.items():
        names = [canonical_name]
        names.extend(source.get("former_names") or [])

        for name in names:
            key = normalize_venue_key(name)
            if key:
                candidates.setdefault(key, set()).add(canonical_name)

    return {
        key: next(iter(names))
        for key, names in candidates.items()
        if len(names) == 1
    }


def build_venue_index(
    events: list[dict[str, Any]],
    metadata: dict[str, dict[str, Any]] | None = None,
    *,
    articles: dict[str, list[dict[str, Any]]] | None = None,
    include_diagnostics: bool = False,
):
    """
    Build the canonical public venue index.

    `events` must be the public output from prepare_upcoming_events(), so
    venue/event semantics cannot drift from the published calendar.
    """

    metadata = VENUE_METADATA if metadata is None else metadata
    metadata = canonicalize_venue_metadata(metadata)
    venue_lookup = _reviewed_venue_lookup(metadata)
    articles = articles or {}

    index: dict[str, dict[str, Any]] = {}

    for venue_name in sorted(metadata, key=str.casefold):
        source = deepcopy(metadata[venue_name])

        lat = source.get("lat")
        lng = source.get("lng")

        record = {
            "name": venue_name,
            "city": source.get("city") or "",
            "department": source.get("department") or "",
            "address": source.get("address") or "",
            "lat": lat,
            "lng": lng,
            "website": source.get("website") or "",
            "mapReady": lat is not None and lng is not None,
            "events": [],
            "articles": [
                deepcopy(article)
                for article in articles.get(venue_name, [])
            ],
        }

        # Internal lifecycle information is useful to the renderer but venue
        # category/type remains deliberately non-public for now.
        if source.get("status"):
            record["status"] = source["status"]

        if source.get("current_name"):
            record["currentName"] = source["current_name"]

        if source.get("former_names"):
            record["aliases"] = list(source["former_names"])

        index[venue_name] = record

    # Export the same reviewed aliases used by central venue
    # canonicalization. Search consumers should not duplicate this identity
    # layer in JavaScript. Normalized spellings are sufficient because public
    # search applies punctuation and accent folding too.
    for alias, canonical_name in VENUE_ALIASES.items():
        record = index.get(canonical_name)

        if (
            record is None
            or normalize_venue_key(alias)
            == normalize_venue_key(canonical_name)
        ):
            continue

        aliases = record.setdefault("aliases", [])

        if alias not in aliases:
            aliases.append(alias)

    for record in index.values():
        if record.get("aliases"):
            unique_aliases = {}

            for alias in record["aliases"]:
                unique_aliases.setdefault(
                    normalize_venue_key(alias),
                    alias,
                )

            record["aliases"] = sorted(
                unique_aliases.values(),
                key=str.casefold,
            )

    unknown = set()
    provisional = set()
    excluded_invalid = set()
    provisional_cities: dict[str, set[str]] = {}

    for event in events:
        raw_venue_name = clean_unknown_venue_name(event.get("v") or "")

        if not raw_venue_name:
            continue

        venue_key = normalize_venue_key(raw_venue_name)
        venue_name = venue_lookup.get(venue_key)

        if venue_name is None:
            globally_resolved = resolve_venue_name(
                raw_venue_name,
                event.get("c") or "",
            )
            if globally_resolved in index:
                venue_name = globally_resolved

        # A scraper may occasionally leave an event/festival wrapper in the
        # venue field. Strip it only when the suffix independently resolves to
        # an already reviewed canonical venue.
        if venue_name is None and " @ " in raw_venue_name:
            suffix = raw_venue_name.rsplit(" @ ", 1)[-1].strip()
            venue_name = venue_lookup.get(normalize_venue_key(suffix))
            if venue_name is None:
                globally_resolved = resolve_venue_name(
                    suffix,
                    event.get("c") or "",
                )
                if globally_resolved in index:
                    venue_name = globally_resolved

        if venue_name is None:
            venue_name = raw_venue_name

        record = index.get(venue_name)

        if record is None:
            unknown.add(raw_venue_name)

            if not _valid_provisional_venue_name(venue_name):
                excluded_invalid.add(raw_venue_name)
                continue

            provisional.add(venue_name)
            record = {
                "name": venue_name,
                "city": event.get("c") or "",
                "mapReady": False,
                "events": [],
                "articles": [],
                "status": "provisional",
                "provisional": True,
            }
            index[venue_name] = record
            venue_lookup[venue_key] = venue_name

        if record.get("provisional"):
            event_city = event.get("c") or ""
            cities = provisional_cities.setdefault(venue_name, set())
            if event_city:
                cities.add(event_city)
            record["city"] = next(iter(cities)) if len(cities) == 1 else ""

        record["events"].append(_public_event(event))

    # prepare_upcoming_events() is already chronological, but keep the venue
    # index deterministic when called independently in tests/tools.
    for record in index.values():
        record["events"].sort(
            key=lambda event: (
                event["date"],
                event.get("startTime") or "",
                event["headliner"].casefold(),
                event["eventId"],
            )
        )

    if not include_diagnostics:
        return index

    return index, {
        "venueCount": len(index),
        "canonicalVenueCount": sum(
            1 for record in index.values()
            if not record.get("provisional")
        ),
        "mapReadyVenueCount": sum(
            1 for record in index.values()
            if record["mapReady"]
        ),
        "venuesWithUpcomingEvents": sum(
            1 for record in index.values()
            if record["events"]
        ),
        "venuesWithArticles": sum(
            1 for record in index.values()
            if record["articles"]
        ),
        "articleAssociations": sum(
            len(record["articles"])
            for record in index.values()
        ),
        "unknownEventVenues": sorted(unknown, key=str.casefold),
        "provisionalEventVenues": sorted(provisional, key=str.casefold),
        "provisionalVenueCount": len(provisional),
        "excludedInvalidEventVenues": sorted(
            excluded_invalid,
            key=str.casefold,
        ),
        "provisionalVenueCityConflicts": sorted(
            [
                {
                    "venue": venue_name,
                    "cities": sorted(cities, key=str.casefold),
                }
                for venue_name, cities in provisional_cities.items()
                if len(cities) > 1
            ],
            key=lambda item: item["venue"].casefold(),
        ),
    }
