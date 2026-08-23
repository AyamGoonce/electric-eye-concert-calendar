from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

from concert_calendar.deduplication import normalize_headliner
from concert_calendar.models import ConcertEvent
from concert_calendar.venues import normalize_venue_key


STATE_VERSION = 1
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
    if value["version"] != STATE_VERSION or not isinstance(value["events"], dict):
        raise EventStateError("Unsupported event-state document")
    parse_timestamp(value["updated_at"])

    for identity, record in value["events"].items():
        if not isinstance(identity, str) or len(identity) != 64:
            raise EventStateError("Malformed canonical event identity")
        if not isinstance(record, dict) or set(record) != {
            "date", "first_seen", "last_seen"
        }:
            raise EventStateError("Malformed event-state record")
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
    records = {identity: dict(record) for identity, record in previous_events.items()}

    for event in events:
        identity = canonical_event_identity(event)
        existing = records.get(identity)
        first_seen = existing["first_seen"] if existing else (
            now_text if previous is not None else bootstrap_text
        )
        event.first_seen = first_seen
        records[identity] = {
            "date": event.date[:10],
            "first_seen": first_seen,
            "last_seen": now_text,
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


def write_state(path: Path, state: dict) -> str:
    validate_state(state)
    body = json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(body, encoding="utf-8")
    return hashlib.sha256(body.encode("utf-8")).hexdigest()
