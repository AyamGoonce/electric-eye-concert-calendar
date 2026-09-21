from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from concert_calendar.deduplication import (
    DESCRIPTIVE_ARTIST_ALIASES,
    REVIEWED_EVENT_MOVES,
    normalize_artist_component,
    normalize_headliner,
)
from concert_calendar.models import ConcertEvent
from concert_calendar.venues import normalize_venue_key


STATE_VERSION = 3
STATE_FILENAME = "calendar-state.json"
NEW_WINDOW = timedelta(hours=72)
PAST_RETENTION = timedelta(days=180)


class EventStateError(ValueError):
    pass


def canonical_event_identity(event: ConcertEvent | dict) -> str:
    """Return a stable identity unaffected by non-semantic metadata changes."""

    if isinstance(event, dict):
        event_date = event.get("d", "")
        headliner = event.get("h", "")
        venue = event.get("v", "")
    else:
        event_date = event.date
        headliner = event.headliner
        venue = event.venue

    value = "\x1f".join(
        (event_date[:10], normalize_headliner(headliner), normalize_venue_key(venue))
    )
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _reviewed_predecessor_identities(event: ConcertEvent) -> list[str]:
    """Return explicit prior title/location identities for reviewed changes."""

    artist = normalize_artist_component(event.headliner)
    result = []
    for alias in event.identity_aliases or []:
        value = "\x1f".join((
            event.date[:10],
            normalize_headliner(alias),
            normalize_venue_key(event.venue),
        ))
        result.append(hashlib.sha256(value.encode("utf-8")).hexdigest())
    # Sunset's previous parser embedded an explicit session time in its title.
    # Recognize that legacy spelling for state migration only, never as an
    # artist alias or as a reason to merge separate sessions.
    clock = re.fullmatch(r"([01]?\d|2[0-3])[:h]([0-5]\d)", event.start_time or "")
    if clock:
        for title in (event.headliner, event.raw_title, event.event_title):
            if not title:
                continue
            legacy_title = f"{title} – {int(clock[1]):02d}h{clock[2]}"
            value = "\x1f".join((event.date[:10], normalize_headliner(legacy_title),
                                 normalize_venue_key(event.venue)))
            result.append(hashlib.sha256(value.encode("utf-8")).hexdigest())
    for event_date, reviewed_artist, old_venue, new_venue in REVIEWED_EVENT_MOVES:
        if (
            event.date[:10] == event_date
            and artist == reviewed_artist
            and normalize_venue_key(event.venue) == normalize_venue_key(new_venue)
        ):
            value = "\x1f".join((
                event_date,
                reviewed_artist,
                normalize_venue_key(old_venue),
            ))
            result.append(hashlib.sha256(value.encode("utf-8")).hexdigest())

    venue_identity = normalize_venue_key(event.venue)
    if venue_identity == "plenitude arena":
        value = "\x1f".join((
            event.date[:10],
            normalize_headliner(event.headliner),
            "paris la defense arena",
        ))
        result.append(hashlib.sha256(value.encode("utf-8")).hexdigest())

    for prior_title, canonical_title in DESCRIPTIVE_ARTIST_ALIASES.items():
        if normalize_headliner(event.headliner) != canonical_title:
            continue
        value = "\x1f".join((
            event.date[:10],
            prior_title,
            venue_identity,
        ))
        result.append(hashlib.sha256(value.encode("utf-8")).hexdigest())
    return result


def utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def parse_timestamp(value: str) -> datetime:
    if not isinstance(value, str):
        raise EventStateError("State timestamp must be a string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise EventStateError(f"Invalid state timestamp: {value!r}") from error
    if parsed.tzinfo is None:
        raise EventStateError("State timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def is_new(first_seen: str, *, now: datetime) -> bool:
    age = now.astimezone(timezone.utc) - parse_timestamp(first_seen)
    return timedelta(0) <= age <= NEW_WINDOW


def validate_state(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != {"version", "updated_at", "events"}:
        raise EventStateError("Malformed event-state document")
    if value["version"] not in {1, 2, STATE_VERSION} or not isinstance(value["events"], dict):
        raise EventStateError("Unsupported event-state document")
    parse_timestamp(value["updated_at"])

    for identity, record in value["events"].items():
        if not isinstance(identity, str) or len(identity) != 64:
            raise EventStateError("Malformed canonical event identity")
        required = {"date", "first_seen", "last_seen"}
        if not isinstance(record, dict) or not required.issubset(record):
            raise EventStateError("Malformed event-state record")
        if value["version"] == 1 and set(record) != required:
            raise EventStateError("Malformed version-1 event-state record")
        if value["version"] >= 2:
            if not (required | {"openers", "genre", "ticket_status"}).issubset(record) or not set(record).issubset(required | {"openers", "genre", "ticket_status", "public_id", "base_identity", "performance"}):
                raise EventStateError("Malformed version-2 event-state record")
            if not isinstance(record["openers"], list) or not all(isinstance(x, str) for x in record["openers"]):
                raise EventStateError("Malformed event-state openers")
            if not isinstance(record["genre"], str) or record["ticket_status"] not in {None, "tickets", "sold_out", "free", "not_on_sale", "cancelled", "postponed"}:
                raise EventStateError("Malformed event-state metadata")
            if "public_id" in record and (not isinstance(record["public_id"], str) or not re.fullmatch(r"[0-9a-f]{16}", record["public_id"])):
                raise EventStateError("Malformed event-state public ID")
            if 'base_identity' in record and (not isinstance(record['base_identity'], str) or not re.fullmatch(r'[0-9a-f]{64}', record['base_identity'])):
                raise EventStateError('Malformed performance base identity')
            if 'performance' in record and not isinstance(record['performance'], str):
                raise EventStateError('Malformed performance discriminator')
        try:
            date.fromisoformat(record["date"])
        except (TypeError, ValueError) as error:
            raise EventStateError("Malformed event-state date") from error
        parse_timestamp(record["first_seen"])
        parse_timestamp(record["last_seen"])

    return value


def load_state(path: Path | None) -> dict | None:
    if path is None or not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EventStateError(f"Cannot read event state: {error}") from error
    return validate_state(value)


def performance_discriminator(event: ConcertEvent) -> str:
    time_value = event.start_time or ''
    match = re.fullmatch(r'(\d{1,2})[:h](\d{2})(?::00)?', time_value)
    if match:
        time_value = f'{int(match[1]):02d}:{match[2]}'
    marker = event.performance_marker or ''
    if not marker:
        found = re.search(r'\b(?:1er set|2e set|first (?:set|performance)|second (?:set|performance)|matinée|evening|early show|late show)\b',
                          f'{event.headliner} {event.event_title or ""}', re.I)
        marker = found[0].casefold() if found else ''
    return '|'.join((time_value, marker)) if time_value or marker else ''


def _programme_discriminator(event: ConcertEvent) -> str:
    """Return explicit programme context suitable for collision resolution."""
    title = (event.event_title or "").strip()
    if not title:
        return ""
    normalized = normalize_headliner(title)
    if not normalized or normalized == normalize_headliner(event.headliner):
        return ""
    return "programme:" + normalized


def assign_performance_identities(events, previous=None, *, preserve_public_ids=False):
    """Keep ordinary legacy keys; reserve one persisted key per performance.

    Only exact canonical/retained-alias identities qualify as predecessors.
    v1/v2 records lack performance data: one deterministic row inherits their
    route, and newly exposed sets inherit their age but not the same route.
    """
    previous = previous or {}
    # Standalone exports may carry routes without a state document. Reserve
    # those routes before generating any IDs, including for later-sorted rows.
    supplied_ids = {
        id(event): value
        for event in events
        if preserve_public_ids
        and isinstance(value := getattr(event, '_public_id', None), str)
        and re.fullmatch(r'[0-9a-f]{16}', value)
    }
    supplied_routes = set(supplied_ids.values())
    by_base = defaultdict(list)
    for key, record in previous.items():
        by_base[record.get('base_identity', key)].append((key, record))

    # Programme context is not normally part of persistent performance
    # identity. Use it only when multiple untimed rows would otherwise collide,
    # or when an earlier collision has already persisted that discriminator.
    regular_discriminators = {
        id(event): performance_discriminator(event)
        for event in events
    }
    programme_discriminators = {
        id(event): _programme_discriminator(event)
        for event in events
    }
    effective_discriminators = dict(regular_discriminators)

    current_by_base = defaultdict(list)
    for event in events:
        current_by_base[canonical_event_identity(event)].append(event)

    for base, group in current_by_base.items():
        untimed = [
            event
            for event in group
            if not regular_discriminators[id(event)]
        ]
        if len(untimed) < 2:
            continue

        programmes = [
            programme_discriminators[id(event)]
            for event in untimed
        ]

        # All colliding untimed rows must have explicit, distinct programme
        # context. Otherwise retain the existing loud failure rather than
        # manufacture identity from weak evidence.
        if (
            all(programmes)
            and len(set(programmes)) == len(programmes)
        ):
            for event, programme in zip(untimed, programmes):
                effective_discriminators[id(event)] = programme

    # If a prior state already persisted a programme discriminator, retain it
    # even when that performance is currently the only row of its base identity.
    # This prevents IDs changing when a sibling programme disappears/reappears.
    for event in events:
        event_id = id(event)
        if effective_discriminators[event_id]:
            continue

        programme = programme_discriminators[event_id]
        if not programme:
            continue

        bases = list(dict.fromkeys([
            canonical_event_identity(event),
            *_reviewed_predecessor_identities(event),
        ]))
        prior_performances = {
            record.get('performance', '')
            for base in bases
            for _, record in by_base.get(base, [])
        }
        if programme in prior_performances:
            effective_discriminators[event_id] = programme

    # A source may temporarily lose timing evidence for a performance that was
    # already persisted with one unambiguous discriminator. Preserve that
    # identity only when there is exactly one current row for the canonical
    # base and exactly one prior non-empty performance discriminator across
    # that base and its reviewed predecessors.
    for base, group in current_by_base.items():
        if len(group) != 1:
            continue

        event = group[0]
        event_id = id(event)

        if effective_discriminators[event_id]:
            continue

        bases = list(dict.fromkeys([
            base,
            *_reviewed_predecessor_identities(event),
        ]))

        prior_performances = {
            record.get('performance')
            for candidate in bases
            for _, record in by_base.get(candidate, [])
            if record.get('performance')
        }

        if len(prior_performances) == 1:
            effective_discriminators[event_id] = next(iter(prior_performances))

    reserved_ids = {record.get('public_id', key[:16]) for key, record in previous.items()}
    used_keys, used_ids = set(), set()
    ordered = sorted(events, key=lambda e: (
        canonical_event_identity(e),
        e.first_seen or '9999',
        0 if not regular_discriminators[id(e)] else 1,
        effective_discriminators[id(e)],
        e.raw_title or '',
        e.ticket_url or '',
        tuple(sorted(e.source_names or [])),
    ))
    for event in ordered:
        base = canonical_event_identity(event)
        supplied = supplied_ids.get(id(event))
        discriminator = effective_discriminators[id(event)]
        event._state_performance_discriminator = discriminator
        bases = list(dict.fromkeys([base, *_reviewed_predecessor_identities(event)]))
        candidates = {key: record for candidate in bases for key, record in by_base.get(candidate, [])
                      if not record.get('performance') or record['performance'] == discriminator}
        ranked = sorted(candidates, key=lambda key: (
            candidates[key].get('performance') != discriminator,
            candidates[key].get('base_identity', key) != base,
            candidates[key]['first_seen'], key))
        selected = next((key for key in ranked if key not in used_keys
                         and candidates[key].get('public_id', key[:16]) not in used_ids), None)
        event._previous_identities = ranked
        if selected:
            key = selected
            public_id = candidates[selected].get('public_id', selected[:16])
        elif (base not in used_keys and base not in previous
              and base[:16] not in reserved_ids | used_ids
              and (base[:16] not in supplied_routes or base[:16] == supplied)):
            key, public_id = base, base[:16]
        else:
            if not discriminator:
                raise EventStateError('Unresolved duplicate without a performance discriminator: ' + event.headliner)
            key = hashlib.sha256((base + '\x1fperformance\x1f' + discriminator).encode()).hexdigest()
            public_id = key[:16]
        if supplied and supplied not in used_ids and supplied not in reserved_ids:
            public_id = supplied
        if key in used_keys or public_id in used_ids:
            raise EventStateError('Duplicate persistent performance: ' + event.headliner)
        event._state_identity, event._public_id = key, public_id
        used_keys.add(key)
        used_ids.add(public_id)


def reconcile_state(
    events: list[ConcertEvent],
    previous: dict | None,
    *,
    now: datetime,
) -> dict:
    """Attach first_seen and return a validated, bounded candidate state."""

    now = now.astimezone(timezone.utc)
    now_text = utc_iso(now)
    bootstrap_text = utc_iso(now - NEW_WINDOW - timedelta(seconds=1))
    previous_events = previous["events"] if previous else {}
    records = {
        identity: {
            **dict(record),
            "openers": list(record.get("openers", [])),
            "genre": record.get("genre", ""),
            "ticket_status": record.get("ticket_status"),
        }
        for identity, record in previous_events.items()
    }

    assign_performance_identities(events, previous_events)
    for event in events:
        identity = event._state_identity
        predecessors = event._previous_identities
        existing = min((previous_events[key] for key in predecessors),
                       key=lambda record: parse_timestamp(record['first_seen']), default=None)
        first_seen = existing["first_seen"] if existing else (
            now_text if previous is not None else bootstrap_text
        )
        event.first_seen = first_seen
        records[identity] = {
            "date": event.date[:10],
            "first_seen": first_seen,
            "last_seen": now_text,
            "openers": list(event.openers or []),
            "genre": event.genre_public or "",
            "ticket_status": event.ticket_status or (
                "sold_out" if event.sold_out else ("tickets" if event.ticket_url else None)
            ),
            "public_id": event._public_id,
            "base_identity": canonical_event_identity(event),
            "performance": getattr(
                event,
                "_state_performance_discriminator",
                performance_discriminator(event),
            ),
        }

    cutoff = (now.date() - PAST_RETENTION).isoformat()
    records = {
        identity: record
        for identity, record in records.items()
        if record["date"] >= cutoff
    }
    state = {
        "version": STATE_VERSION,
        "updated_at": now_text,
        "events": records,
    }
    return validate_state(state)


def build_change_report(
    events: list[ConcertEvent], previous: dict | None, current: dict, *, now: datetime
) -> dict:
    if previous is None or previous.get("version", 1) < 2:
        return {
            "new_events": 0, "no_longer_present": 0, "new_support_acts": 0,
            "genre_enrichments": 0, "ticket_status_changes": 0,
            "newly_sold_out": 0, "details": {},
        }
    previous_events = previous["events"]
    current_ids = {getattr(event, '_state_identity', canonical_event_identity(event)): event for event in events}
    prior_present = {
        identity for identity, record in previous_events.items()
        if record["last_seen"] == previous["updated_at"]
        and record["date"] >= now.date().isoformat()
    }
    details = {"new_events": [], "no_longer_present": [], "new_support_acts": [], "genre_enrichments": [], "ticket_status_changes": []}
    for identity, event in current_ids.items():
        predecessor_keys = getattr(event, '_previous_identities', [])
        old = previous_events.get(identity) or next((previous_events[k] for k in predecessor_keys if k in previous_events), None)
        if old is None:
            details["new_events"].append(event.headliner)
            continue
        old_openers = {normalize_headliner(value) for value in old.get("openers", [])}
        additions = [value for value in (event.openers or []) if normalize_headliner(value) not in old_openers]
        if additions:
            details["new_support_acts"].append({"event": event.headliner, "artists": additions})
        if not old.get("genre") and event.genre_public:
            details["genre_enrichments"].append({"event": event.headliner, "genre": event.genre_public})
        new_status = current["events"][identity]["ticket_status"]
        if old.get("ticket_status") != new_status:
            details["ticket_status_changes"].append({"event": event.headliner, "from": old.get("ticket_status"), "to": new_status})
    matched_predecessors = {key for event in events for key in getattr(event, '_previous_identities', [])}
    for identity in sorted(prior_present - set(current_ids) - matched_predecessors):
        details["no_longer_present"].append({"identity": identity, "date": previous_events[identity]["date"]})
    return {
        "new_events": len(details["new_events"]),
        "no_longer_present": len(details["no_longer_present"]),
        "new_support_acts": sum(len(item["artists"]) for item in details["new_support_acts"]),
        "genre_enrichments": len(details["genre_enrichments"]),
        "ticket_status_changes": len(details["ticket_status_changes"]),
        "newly_sold_out": sum(item["to"] == "sold_out" for item in details["ticket_status_changes"]),
        "details": details,
    }


def write_state(path: Path, state: dict) -> str:
    validate_state(state)
    body = json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(body, encoding="utf-8")
    return hashlib.sha256(body.encode("utf-8")).hexdigest()
