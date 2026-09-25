from __future__ import annotations

from copy import deepcopy
from typing import Any

from concert_calendar.venue_metadata import VENUE_METADATA


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

        index[venue_name] = record

    unknown = set()

    for event in events:
        venue_name = (event.get("v") or "").strip()

        if not venue_name:
            continue

        record = index.get(venue_name)

        if record is None:
            unknown.add(venue_name)
            continue

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
        "canonicalVenueCount": len(index),
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
    }
