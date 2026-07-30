from __future__ import annotations

import re

from concert_calendar.models import ConcertEvent


def normalize_headliner(name: str) -> str:
    """
    Normalize an artist name for deduplication.
    """

    if not name:
        return ""

    name = name.lower().strip()
    name = re.sub(r"\s+", " ", name)

    return name


def build_event_key(event: ConcertEvent) -> tuple:
    """
    Build a stable key that identifies an event.

    Current strategy:
        date
        normalized headliner
        normalized venue
    """

    date = event.date
    venue = (event.venue or "").lower().strip()
    artist = normalize_headliner(event.headliner)

    return (
        date,
        artist,
        venue,
    )


def merge_events(
    existing: ConcertEvent,
    incoming: ConcertEvent,
) -> ConcertEvent:
    """
    Merge two records representing the same concert.

    The existing event remains the base record.
    Missing or complementary data is added from the incoming event.
    """

    existing.openers = sorted(
        {
            *(existing.openers or []),
            *(incoming.openers or []),
        }
    ) or None

    existing.promoters = sorted(
        {
            *(existing.promoters or []),
            *(incoming.promoters or []),
        }
    ) or None

    if not existing.genre and incoming.genre:
        existing.genre = incoming.genre

    if not existing.facebook_event_url and incoming.facebook_event_url:
        existing.facebook_event_url = incoming.facebook_event_url

    if not existing.ticket_url and incoming.ticket_url:
        existing.ticket_url = incoming.ticket_url

    return existing


def deduplicate_events(
    events: list[ConcertEvent],
) -> list[ConcertEvent]:
    """
    Collapse exact duplicate events into one merged ConcertEvent.
    """

    deduplicated: dict[tuple, ConcertEvent] = {}

    for event in events:
        key = build_event_key(event)

        if key in deduplicated:
            deduplicated[key] = merge_events(
                deduplicated[key],
                event,
            )
        else:
            deduplicated[key] = event

    return list(deduplicated.values())