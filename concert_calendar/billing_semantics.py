import re
from html import unescape

from concert_calendar.models import ConcertEvent


def _clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", unescape(value or "")).strip()


def _key(value: str | None) -> str:
    return _clean(value).casefold()


def _stable_unique(values):
    result = []
    seen = set()

    for value in values:
        cleaned = _clean(value)
        identity = _key(cleaned)

        if not identity or identity in seen:
            continue

        seen.add(identity)
        result.append(cleaned)

    return result


def apply_structured_performer_semantics(events: list[ConcertEvent]) -> None:
    """
    Promote explicit source-provided performer metadata into calendar billing.

    This function never splits a title on punctuation.  A scraper must already
    have supplied ``event.performers`` from independent source evidence.
    """

    for event in events:
        performers = _stable_unique(event.performers or [])

        if not performers:
            continue

        event.performers = performers

        headliner_key = _key(event.headliner)
        matching_primary = next(
            (
                performer
                for performer in performers
                if _key(performer) == headliner_key
            ),
            None,
        )

        primary = matching_primary or performers[0]

        if _key(event.headliner) != _key(primary):
            event.identity_aliases = _stable_unique([
                *(event.identity_aliases or []),
                event.headliner,
            ]) or None

        event.headliner = primary

        opener_keys = {
            _key(opener)
            for opener in (event.openers or [])
            if _key(opener)
        }

        co_headliners = _stable_unique([
            *(event.co_headliners or []),
            *[
                performer
                for performer in performers
                if (
                    _key(performer) != _key(primary)
                    and _key(performer) not in opener_keys
                )
            ],
        ])

        event.co_headliners = co_headliners or None
