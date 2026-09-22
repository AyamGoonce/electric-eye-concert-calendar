"""Bounded publication snapshots for explicitly failed concert sources.

This sidecar is evidence for replay, not an ID allocator. Event-state remains
authoritative for public routes and first-seen timestamps.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.event_state import parse_timestamp, utc_iso
from concert_calendar.geography import is_ile_de_france_event, normalize_event_geography
from concert_calendar.models import ConcertEvent
from concert_calendar.promoters import normalize_event_promoters
from concert_calendar.venues import normalize_event_venue


SOURCE_STATE_FILENAME = "calendar-source-state.json"
SOURCE_STATE_VERSION = 1
RETENTION_WINDOW = timedelta(hours=72)
PARIS = ZoneInfo("Europe/Paris")
MAX_RETENTION_DETAILS = 100

# Explicit event fields needed to replay a previously published source row.
# Source names, first_seen, derived Electric Eye links, descriptions, and any
# scraper-specific dynamic attributes are deliberately excluded.
SNAPSHOT_FIELDS = (
    "date", "headliner", "venue", "city", "department", "openers",
    "co_headliners", "promoters", "genre", "facebook_event_url", "ticket_url",
    "festival_name", "authoritative_billing", "sold_out", "genre_public",
    "genre_source", "genre_method", "genre_evidence", "ticket_status",
    "start_time", "announced_at", "event_title", "series_name", "image_url",
    "image_source", "identity_aliases", "genres_public", "event_type",
    "category", "tags", "performers", "raw_title", "performance_marker",
)
REQUIRED_EVENT_FIELDS = {"date", "headliner", "venue", "city", "department"}
LIST_FIELDS = {
    "openers", "co_headliners", "promoters", "identity_aliases",
    "genres_public", "tags", "performers",
}
BOOL_FIELDS = {"authoritative_billing", "sold_out"}
EVIDENCE_FIELDS = {"raw", "source", "classification"}


class SourceStateError(ValueError):
    """A source-state document or retained identity is unsafe to publish."""


def _event_date(value: str) -> date:
    if not isinstance(value, str) or len(value) < 10:
        raise SourceStateError("Malformed source-state event date")
    try:
        return date.fromisoformat(value[:10])
    except ValueError as error:
        raise SourceStateError("Malformed source-state event date") from error


def _timestamp(value: str) -> datetime:
    try:
        return parse_timestamp(value)
    except (ValueError, TypeError) as error:
        raise SourceStateError(f"Malformed source-state timestamp: {value!r}") from error


def _snapshot_event(event: ConcertEvent) -> dict:
    values = {field: deepcopy(getattr(event, field)) for field in SNAPSHOT_FIELDS}
    if values["genre_evidence"] is not None:
        values["genre_evidence"] = [
            {key: deepcopy(item[key]) for key in ("raw", "source", "classification") if key in item}
            for item in values["genre_evidence"]
        ]
    return values


def _snapshot_record(event: ConcertEvent) -> dict:
    return {
        "event": _snapshot_event(event),
        "public_id": getattr(event, "_public_id", None),
        "state_identity": getattr(event, "_state_identity", None),
        "first_seen": event.first_seen,
    }


def _snapshot_sort_key(record: dict) -> tuple:
    row = record["event"]
    return (
        row["date"][:10], row["headliner"], row["venue"],
        row.get("start_time") or "", record.get("public_id") or "",
        json.dumps(row, ensure_ascii=False, sort_keys=True),
    )


def validate_source_state(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != {"version", "updated_at", "sources"}:
        raise SourceStateError("Malformed source-state document")
    if (type(value["version"]) is not int
            or value["version"] != SOURCE_STATE_VERSION
            or not isinstance(value["sources"], dict)):
        raise SourceStateError("Unsupported source-state document")
    _timestamp(value["updated_at"])
    for name, source in value["sources"].items():
        if not isinstance(name, str) or not name or len(name) > 200:
            raise SourceStateError("Malformed source-state source name")
        if not isinstance(source, dict) or set(source) != {
            "source_name", "last_successful_at", "events"
        } or source["source_name"] != name or not isinstance(source["events"], list):
            raise SourceStateError(f"Malformed source-state entry: {name}")
        if source["last_successful_at"] is not None:
            _timestamp(source["last_successful_at"])
        elif source["events"]:
            raise SourceStateError(f"Snapshot without success timestamp: {name}")
        for record in source["events"]:
            if not isinstance(record, dict) or set(record) != {
                "event", "public_id", "state_identity", "first_seen"
            }:
                raise SourceStateError(f"Malformed source-state snapshot: {name}")
            if record["public_id"] is not None and (
                not isinstance(record["public_id"], str)
                or not re.fullmatch(r"[0-9a-f]{16}", record["public_id"])
            ):
                raise SourceStateError(f"Malformed source-state public ID: {name}")
            if record["state_identity"] is not None and (
                not isinstance(record["state_identity"], str)
                or not re.fullmatch(r"[0-9a-f]{64}", record["state_identity"])
            ):
                raise SourceStateError(f"Malformed source-state identity: {name}")
            if record["first_seen"] is not None:
                _timestamp(record["first_seen"])
            row = record["event"]
            if not isinstance(row, dict) or set(row) != set(SNAPSHOT_FIELDS):
                raise SourceStateError(f"Malformed source-state event fields: {name}")
            for key, item in row.items():
                if key in REQUIRED_EVENT_FIELDS and not isinstance(item, str):
                    raise SourceStateError(f"Malformed source-state required field: {key}")
                if key in LIST_FIELDS and item is not None and not (
                    isinstance(item, list) and all(isinstance(entry, str) for entry in item)
                ):
                    raise SourceStateError(f"Malformed source-state list: {key}")
                if key in BOOL_FIELDS and not isinstance(item, bool):
                    raise SourceStateError(f"Malformed source-state boolean: {key}")
                if key == "genre_evidence" and item is not None:
                    if not isinstance(item, list) or not all(
                        isinstance(entry, dict)
                        and set(entry).issubset(EVIDENCE_FIELDS)
                        and all(isinstance(part, str) for part in entry.values())
                        for entry in item
                    ):
                        raise SourceStateError("Malformed source-state genre evidence")
                if key not in REQUIRED_EVENT_FIELDS | LIST_FIELDS | BOOL_FIELDS | {"genre_evidence"}:
                    if item is not None and not isinstance(item, str):
                        raise SourceStateError(f"Malformed source-state string: {key}")
            _event_date(row["date"])
        if source["events"] != sorted(source["events"], key=_snapshot_sort_key):
            raise SourceStateError(f"Unsorted source-state snapshot: {name}")
    return value


def load_source_state(path: Path | None) -> dict | None:
    if path is None or not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SourceStateError(f"Unable to read source-state document: {path}") from error
    return validate_source_state(value)


def write_source_state(path: Path, state: dict) -> str:
    validate_source_state(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = (json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.write_bytes(body)
    return hashlib.sha256(body).hexdigest()


def hydrate_failed_sources(
    prior_state: dict | None,
    source_health: list[dict],
    healthy_events: list[ConcertEvent],
    *,
    now: datetime,
) -> tuple[list[ConcertEvent], dict[str, list[dict]], list[dict]]:
    """Admit only unexpired, future, healthy-unsuperseded failed-source rows."""

    if prior_state is not None:
        validate_source_state(prior_state)
    now = now.astimezone(timezone.utc)
    today = now.astimezone(PARIS).date()
    restored = []
    healthy_by_date = defaultdict(list)
    for fresh in healthy_events:
        healthy_by_date[fresh.date[:10]].append(fresh)
    retained_snapshots: dict[str, list[dict]] = {}
    details = []
    for health in source_health:
        name = health["source_name"]
        prior = (prior_state or {}).get("sources", {}).get(name)
        last_success = prior["last_successful_at"] if prior else None
        health.update({
            "last_successful_at": last_success if health["status"] == "failed" else utc_iso(now),
            "source_state_version": SOURCE_STATE_VERSION,
            "fallback_suppressed_count": 0,
            "fallback_excluded_past_count": 0,
            "fallback_expired_count": 0,
            "fallback_excluded_geography_count": 0,
            "fallback_unavailable": False,
        })
        if health["status"] != "failed":
            continue
        retained_snapshots[name] = []
        if prior is None or not prior["events"] or last_success is None:
            health["fallback_unavailable"] = True
            continue
        age = now - _timestamp(last_success)
        if age < timedelta(0) or age > RETENTION_WINDOW:
            health["fallback_expired_count"] = len(prior["events"])
            continue
        for snapshot in prior["events"]:
            old = snapshot["event"]
            if _event_date(old["date"]) < today:
                health["fallback_excluded_past_count"] += 1
                continue
            retained = ConcertEvent(**deepcopy(old))
            retained.source_names = [name]
            normalize_event_geography(retained)
            normalize_event_venue(retained)
            normalize_event_promoters(retained)
            if not is_ile_de_france_event(retained):
                health["fallback_excluded_geography_count"] += 1
                continue
            # Compare on copies: any stale merge must never enrich a live row.
            if any(
                len(deduplicate_events([deepcopy(fresh), deepcopy(retained)])) == 1
                for fresh in healthy_by_date[retained.date[:10]]
            ):
                health["fallback_suppressed_count"] += 1
                continue
            restored.append(retained)
            retained_snapshots[name].append(deepcopy(snapshot))
            health["fallback_event_count"] += 1
            if len(details) < MAX_RETENTION_DETAILS:
                details.append({
                    "source": name,
                    "date": old["date"][:10],
                    "headliner": old["headliner"],
                    "venue": old["venue"],
                    "prior_public_id": snapshot["public_id"],
                    "snapshot_timestamp": last_success,
                    "expiration_timestamp": utc_iso(_timestamp(last_success) + RETENTION_WINDOW),
                })
    return restored, retained_snapshots, details


def build_source_state(
    events: list[ConcertEvent],
    source_health: list[dict],
    previous: dict | None,
    *,
    now: datetime,
    retained_snapshots: dict[str, list[dict]],
) -> dict:
    """Replace successful inventories; carry only admitted failed snapshots."""

    if previous is not None:
        validate_source_state(previous)
    today = now.astimezone(PARIS).date()
    now_text = utc_iso(now)
    sources = {}
    for health in source_health:
        name = health["source_name"]
        status = health["status"]
        if status in {"ok", "empty"}:
            snapshots = sorted(
                (_snapshot_record(event) for event in events
                 if name in (event.source_names or [])
                 and _event_date(event.date) >= today),
                key=_snapshot_sort_key,
            ) if status == "ok" else []
            last_success = now_text
        elif status == "failed":
            prior = (previous or {}).get("sources", {}).get(name)
            snapshots = sorted(
                (deepcopy(record) for record in retained_snapshots.get(name, [])
                 if _event_date(record["event"]["date"]) >= today),
                key=_snapshot_sort_key,
            )
            last_success = prior["last_successful_at"] if prior else None
        else:
            raise SourceStateError(f"Unknown source health status: {status}")
        sources[name] = {
            "source_name": name,
            "last_successful_at": last_success,
            "events": snapshots,
        }
    return validate_source_state({
        "version": SOURCE_STATE_VERSION,
        "updated_at": now_text,
        "sources": dict(sorted(sources.items())),
    })


def validate_retained_identities(
    events: list[ConcertEvent],
    candidate_state: dict,
    retained_snapshots: dict[str, list[dict]],
) -> None:
    """Ensure replay did not silently mint a route or reset NEW state."""

    current_by_public_id = {
        getattr(event, "_public_id", None): event for event in events
    }
    for source, snapshots in retained_snapshots.items():
        for snapshot in snapshots:
            public_id = snapshot["public_id"]
            if not public_id:
                continue  # Sidecar hints are optional; event state remains authoritative.
            event = current_by_public_id.get(public_id)
            if event is None or source not in (event.source_names or []):
                raise SourceStateError(f"Retained {source} event lost prior public ID {public_id}")
            state_record = candidate_state["events"].get(event._state_identity)
            if state_record is None or state_record.get("public_id") != public_id:
                raise SourceStateError(f"Retained {source} event has invalid state for {public_id}")
            if snapshot["first_seen"] and (
                event.first_seen != snapshot["first_seen"]
                or state_record["first_seen"] != snapshot["first_seen"]
            ):
                raise SourceStateError(f"Retained {source} event reset first_seen for {public_id}")
