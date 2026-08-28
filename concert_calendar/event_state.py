from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

from concert_calendar.deduplication import (
    DESCRIPTIVE_ARTIST_ALIASES,
    REVIEWED_EVENT_MOVES,
    normalize_artist_component,
    normalize_headliner,
)
from concert_calendar.models import ConcertEvent
from concert_calendar.venues import normalize_venue_key


STATE_VERSION = 2
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


def empty_state(updated_at: datetime) -> dict:
    return {
        "version": STATE_VERSION,
        "updated_at": utc_iso(updated_at),
        "events": {},
    }


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
    if value["version"] not in {1, STATE_VERSION} or not isinstance(value["events"], dict):
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
        if value["version"] == STATE_VERSION:
            if set(record) != required | {"openers", "genre", "ticket_status"}:
                raise EventStateError("Malformed version-2 event-state record")
            if not isinstance(record["openers"], list) or not all(isinstance(x, str) for x in record["openers"]):
                raise EventStateError("Malformed event-state openers")
            if not isinstance(record["genre"], str) or record["ticket_status"] not in {None, "tickets", "sold_out", "free", "not_on_sale", "cancelled", "postponed"}:
                raise EventStateError("Malformed event-state metadata")
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

    for event in events:
        identity = canonical_event_identity(event)
        existing = records.get(identity)
        if existing is None:
            existing = next(
                (
                    records[candidate]
                    for candidate in _reviewed_predecessor_identities(event)
                    if candidate in records
                ),
                None,
            )
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
    if previous is None or previous.get("version", 1) < STATE_VERSION:
        return {
            "new_events": 0, "no_longer_present": 0, "new_support_acts": 0,
            "genre_enrichments": 0, "ticket_status_changes": 0,
            "newly_sold_out": 0, "details": {},
        }
    previous_events = previous["events"]
    current_ids = {canonical_event_identity(event): event for event in events}
    prior_present = {
        identity for identity, record in previous_events.items()
        if record["last_seen"] == previous["updated_at"]
        and record["date"] >= now.date().isoformat()
    }
    details = {"new_events": [], "no_longer_present": [], "new_support_acts": [], "genre_enrichments": [], "ticket_status_changes": []}
    for identity, event in current_ids.items():
        old = previous_events.get(identity)
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
    for identity in sorted(prior_present - set(current_ids)):
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
