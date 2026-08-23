from __future__ import annotations

from collections import defaultdict
import re
import unicodedata
from urllib.parse import urlparse

from concert_calendar.models import ConcertEvent


ARTIST_ALIASES = {
    "alison’s halo": "alison's halo",
    "day we ran": "dayweran",
    "f.f.f.": "fff",
    "gaëlle joly": "gaelle joly",
    "gregoire jokic": "grégoire jokic",
    "howlin’ jaws": "howlin' jaws",
    "la p’tité fumée": "la p’tite fumée",
    "la securite": "la sécurité",
    "lewis ofman – festivals": "lewis ofman",
    "noe preszow": "noé preszow",
    "sebastien tellier": "sébastien tellier",
    "zoh amba (les femmes s’en mêlent)": (
        "zoh amba (les femmes s'en mêlent)"
    ),
}

# The official Adidas Arena event page explicitly bills this special guest.
# GDP currently exposes the two artists as separate cards with one event URL.
VERIFIED_SUPPORT_RELATIONSHIPS = {
    ("2026-08-26", "adidas arena", "hollywood vampires"): (
        "The Last Internationale",
    ),
}

VERIFIED_ARTIST_DISPLAY_NAMES = {
    "hollywood vampires": "Hollywood Vampires",
    "the last internationale": "The Last Internationale",
}

BILL_SEPARATOR_RE = re.compile(r"\s+(?:\+|•)\s+")


def normalize_headliner(name: str) -> str:
    """Normalize an artist name for conservative exact deduplication."""

    if not name:
        return ""

    name = name.lower().strip()
    name = re.sub(r"\s+", " ", name)
    return ARTIST_ALIASES.get(name, name)


def normalize_artist_component(name: str) -> str:
    """Return an accent-insensitive identity for explicit bill components."""

    normalized = unicodedata.normalize("NFKD", normalize_headliner(name))
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
    normalized = normalized.replace("’", "'")
    normalized = normalized.replace("&", " and ")
    return re.sub(r"\s+", " ", normalized).strip()


def build_event_key(event: ConcertEvent) -> tuple:
    """Build the stable date/headliner/venue exact-match key."""

    return (
        event.date,
        normalize_headliner(event.headliner),
        (event.venue or "").lower().strip(),
    )


def _stable_unique(values: list[str]) -> list[str] | None:
    result = []
    seen = set()

    for value in values:
        identity = normalize_artist_component(value)

        if not identity or identity in seen:
            continue

        seen.add(identity)
        result.append(value)

    return result or None


def _valid_http_url(value: str | None) -> bool:
    if not value:
        return False

    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def merge_events(
    existing: ConcertEvent,
    incoming: ConcertEvent,
) -> ConcertEvent:
    """Add safe missing metadata while retaining the preferred base record."""

    existing.openers = _stable_unique(
        [*(existing.openers or []), *(incoming.openers or [])]
    )
    existing.promoters = sorted(
        {*(existing.promoters or []), *(incoming.promoters or [])}
    ) or None

    if not existing.genre and incoming.genre:
        existing.genre = incoming.genre

    if not existing.facebook_event_url and incoming.facebook_event_url:
        existing.facebook_event_url = incoming.facebook_event_url

    if incoming.authoritative_billing and _valid_http_url(incoming.ticket_url):
        existing.ticket_url = incoming.ticket_url
    elif not existing.ticket_url and _valid_http_url(incoming.ticket_url):
        existing.ticket_url = incoming.ticket_url

    existing.festival_name = existing.festival_name or incoming.festival_name
    existing.authoritative_billing = (
        existing.authoritative_billing or incoming.authoritative_billing
    )

    return existing


def _split_full_bill(value: str) -> list[str]:
    parts = BILL_SEPARATOR_RE.split(value or "")
    return parts if len(parts) > 1 else []


def _matches_structured_bill(
    structured: ConcertEvent,
    full_bill: ConcertEvent,
) -> bool:
    if not structured.openers or full_bill.openers:
        return False

    components = _split_full_bill(full_bill.headliner)

    if not components:
        return False

    normalized_bill = [normalize_artist_component(value) for value in components]
    normalized_structured = [
        normalize_artist_component(value)
        for value in [structured.headliner, *structured.openers]
    ]

    return (
        normalized_bill[0] == normalized_structured[0]
        and sorted(normalized_bill) == sorted(normalized_structured)
    )


def _same_event_specific_ticket(
    left: ConcertEvent,
    right: ConcertEvent,
) -> bool:
    if not (_valid_http_url(left.ticket_url) and _valid_http_url(right.ticket_url)):
        return False

    return left.ticket_url.rstrip("/") == right.ticket_url.rstrip("/")


def _shared_promoter(left: ConcertEvent, right: ConcertEvent) -> bool:
    return bool(set(left.promoters or []) & set(right.promoters or []))


def _apply_verified_support_relationships(events: list[ConcertEvent]) -> None:
    grouped = defaultdict(list)

    for event in events:
        grouped[(event.date, (event.venue or "").casefold().strip())].append(event)

    for (date, venue, headliner), opener_names in VERIFIED_SUPPORT_RELATIONSHIPS.items():
        group = grouped.get((date, venue), [])
        parent = next(
            (
                event
                for event in group
                if normalize_artist_component(event.headliner) == headliner
            ),
            None,
        )

        if parent is None:
            continue

        available = {
            normalize_artist_component(event.headliner): event.headliner
            for event in group
        }
        verified_openers = [
            available[normalize_artist_component(opener)]
            for opener in opener_names
            if normalize_artist_component(opener) in available
        ]

        if verified_openers:
            parent.openers = _stable_unique(
                [*(parent.openers or []), *verified_openers]
            )


def _display_candidates(events: list[ConcertEvent]) -> dict[str, str]:
    candidates: dict[str, str] = {}

    for event in events:
        for name in [event.headliner, *(event.openers or [])]:
            identity = normalize_artist_component(name)
            letters = [character for character in name if character.isalpha()]
            is_mixed_case = (
                any(character.islower() for character in letters)
                and any(character.isupper() for character in letters)
            )

            if identity and is_mixed_case and identity not in candidates:
                candidates[identity] = name

    candidates.update(VERIFIED_ARTIST_DISPLAY_NAMES)
    return candidates


def _apply_display_capitalization(
    events: list[ConcertEvent],
    candidates: dict[str, str],
) -> None:
    def canonicalize(name: str) -> str:
        letters = [character for character in name if character.isalpha()]
        is_all_caps = bool(letters) and all(
            not character.islower()
            for character in letters
        )

        if not is_all_caps:
            return name

        return candidates.get(normalize_artist_component(name), name)

    for event in events:
        event.headliner = canonicalize(event.headliner)
        event.openers = [
            canonicalize(opener)
            for opener in (event.openers or [])
        ] or None


def _deduplicate_exact(events: list[ConcertEvent]) -> list[ConcertEvent]:
    deduplicated: dict[tuple, ConcertEvent] = {}

    for event in events:
        key = build_event_key(event)

        if key in deduplicated:
            deduplicated[key] = merge_events(deduplicated[key], event)
        else:
            deduplicated[key] = event

    return list(deduplicated.values())


def _reconcile_full_bills(events: list[ConcertEvent]) -> list[ConcertEvent]:
    grouped = defaultdict(list)

    for event in events:
        grouped[(event.date, (event.venue or "").casefold().strip())].append(event)

    removed = set()

    for group in grouped.values():
        structured_records = [event for event in group if event.openers]
        full_bills = [event for event in group if not event.openers]

        for structured in structured_records:
            for full_bill in full_bills:
                if id(full_bill) in removed:
                    continue

                if _matches_structured_bill(structured, full_bill):
                    merge_events(structured, full_bill)
                    removed.add(id(full_bill))

    return [event for event in events if id(event) not in removed]


def _collapse_explicit_support_cards(
    events: list[ConcertEvent],
) -> list[ConcertEvent]:
    grouped = defaultdict(list)

    for event in events:
        grouped[(event.date, (event.venue or "").casefold().strip())].append(event)

    removed = set()

    for group in grouped.values():
        for parent in group:
            opener_identities = {
                normalize_artist_component(opener)
                for opener in (parent.openers or [])
            }

            if not opener_identities:
                continue

            for candidate in group:
                if candidate is parent or id(candidate) in removed:
                    continue

                if normalize_artist_component(candidate.headliner) not in opener_identities:
                    continue

                if not (
                    _same_event_specific_ticket(parent, candidate)
                    or _shared_promoter(parent, candidate)
                ):
                    continue

                merge_events(parent, candidate)
                removed.add(id(candidate))

    return [event for event in events if id(event) not in removed]


def _consolidate_authoritative_festivals(
    events: list[ConcertEvent],
    diagnostics: dict | None = None,
) -> list[ConcertEvent]:
    """Replace artist products with one authoritative festival-day bill."""

    grouped = defaultdict(list)

    for event in events:
        grouped[(event.date, (event.venue or "").casefold().strip())].append(event)

    removed = set()
    days_aggregated = 0

    for group in grouped.values():
        authoritative = [
            event
            for event in group
            if event.authoritative_billing and event.festival_name and event.openers
        ]

        if len(authoritative) != 1:
            if len(group) > 1 and any(event.festival_name for event in group):
                print(
                    "Ambiguous festival-day billing retained: "
                    f"{group[0].date} — {group[0].venue}"
                )
            continue

        parent = authoritative[0]
        lineup_identities = {
            normalize_artist_component(name)
            for name in [parent.headliner, *(parent.openers or [])]
        }
        collapsed_here = 0

        for candidate in group:
            if candidate is parent or id(candidate) in removed:
                continue
            if normalize_artist_component(candidate.headliner) not in lineup_identities:
                continue

            merge_events(parent, candidate)
            removed.add(id(candidate))
            collapsed_here += 1

        if collapsed_here:
            days_aggregated += 1

    if diagnostics is not None:
        diagnostics["festival_days_aggregated"] = days_aggregated
        diagnostics["festival_artist_rows_collapsed"] = len(removed)

    return [event for event in events if id(event) not in removed]


def deduplicate_events(
    events: list[ConcertEvent],
    diagnostics: dict | None = None,
) -> list[ConcertEvent]:
    """Collapse exact and explicitly reconcilable duplicate concerts."""

    initial_opener_state = defaultdict(list)

    for event in events:
        initial_opener_state[build_event_key(event)].append(bool(event.openers))

    display_candidates = _display_candidates(events)
    reconciled = _deduplicate_exact(events)
    _apply_verified_support_relationships(reconciled)
    reconciled = _reconcile_full_bills(reconciled)
    reconciled = _consolidate_authoritative_festivals(reconciled, diagnostics)
    reconciled = _collapse_explicit_support_cards(reconciled)
    _apply_display_capitalization(reconciled, display_candidates)

    if diagnostics is not None:
        diagnostics["opener_enriched_records"] = sum(
            bool(event.openers)
            and False in initial_opener_state.get(build_event_key(event), [])
            and True in initial_opener_state.get(build_event_key(event), [])
            for event in reconciled
        )

    return reconciled
