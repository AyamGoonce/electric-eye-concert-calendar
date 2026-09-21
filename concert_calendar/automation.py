from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from urllib.request import Request, urlopen

from concert_calendar.production_export import (
    PUBLIC_GENRES,
    export_integration_prototype,
    prepare_upcoming_events,
    safe_ticket_url,
    write_clean_routes,
)
from concert_calendar.event_state import (
    EventStateError,
    STATE_FILENAME,
    build_change_report,
    load_state,
    reconcile_state,
    write_state,
)
from concert_calendar.content_index import build_index, enrich_events, fetch_entries, write_assets
from concert_calendar.sources import load_events_with_report


MINIMUM_EVENT_COUNT = 100
MINIMUM_PUBLISHED_RATIO = 0.60
MAXIMUM_PUBLISHED_RATIO = 2.50
MINIMUM_VENUE_BASELINE_COUNT = 20
MINIMUM_VENUE_PUBLISHED_RATIO = 0.50
MINIMUM_GENRE_COVERAGE = 0.10
CORE_SOURCES = {
    "AEG Presents France",
    "Alias Production",
    "Corida",
    "Gérard Drouot Productions",
    "Live Nation",
    "Radical Production",
    "Rock en Seine",
    "Supersonic",
    "Sunset/Sunside",
    "Le Trianon",
    "Vedettes",
    "VeryShow",
}
REQUIRED_EVENT_KEYS = {
    "d", "h", "o", "v", "c", "x", "p", "t", "f", "so", "fs",
    "i", "ts", "st",
}

OPTIONAL_EVENT_KEYS = {
    "an",
    "ch",
    "et",
    "sn",
    "fn",
    "im",
    "is",
    "ee",
}
POINTER_PATTERN = re.compile(r"var manifest = Object\.freeze\((\{.*?\})\);")
RAW_MARKUP_OR_URL_RE = re.compile(
    r"</?(?:a|div|span|p|br|strong|em|script|style)\b[^>]*>|https?://|[\r\n]",
    re.IGNORECASE,
)
RELOCATION_HEADLINER_RE = re.compile(
    r"^(?:changement de (?:salle|lieu)|d(?:é|e)plac(?:é|e)|"
    r"transf(?:é|e)r(?:é|e)|venue change|moved|relocated)\s*[_:|–-]",
    re.IGNORECASE,
)
DESCRIPTIVE_VENUE_RE = re.compile(
    r"(?:\||\ben premi(?:è|e)re partie de\b|\bspecial guests?\b|"
    r"\bsupport\s*:)",
    re.IGNORECASE,
)
PUBLIC_STABLE_ASSETS = (
    "calendar-renderer.js", "calendar.css", "artist-page.js",
    "artist-page.css", "artist-autolinker.js", "artist.html",
    "coverage-page.js", "coverage.html",
    "electric-eye-artist-lookup.js", "electric-eye-content-current.js",
    "artist-index.json", "artist-index.csv", "artist-article-associations.csv",
)

PUBLIC_ROOT_ASSETS = ("index.html",)
PUBLIC_ROUTE_DIRS = ("artist", "concert")
STALE_PUBLIC_TEST_ASSETS = (
    "calendar-current-missing.js", "calendar-malformed.js",
    "data-first.html", "diagnostic.html", "index.html", "malformed.html",
    "missing.html", "responsive-harness.html",
)


class ProductionValidationError(RuntimeError):
    pass


def read_pointer(path: Path) -> dict:
    match = POINTER_PATTERN.search(path.read_text(encoding="utf-8"))
    if not match:
        raise ProductionValidationError(f"Malformed calendar pointer: {path}")
    try:
        manifest = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        raise ProductionValidationError(f"Malformed calendar pointer: {path}") from error
    if (
        not isinstance(manifest.get("data"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", manifest.get("sha256", ""))
        or not isinstance(manifest.get("count"), int)
    ):
        raise ProductionValidationError(f"Malformed calendar pointer: {path}")
    return manifest


def read_published_calendar_events(pointer_path: Path) -> list[dict]:
    """Read the exact public event array referenced by a published pointer."""

    manifest = read_pointer(pointer_path)
    data_path = pointer_path.parent / manifest["data"]
    if not data_path.is_file():
        raise ProductionValidationError(
            f"Published calendar data is missing: {data_path}"
        )

    match = re.search(
        r"window\.ElectricEyeConcertData\s*=\s*Object\.freeze\((\[.*\])\);",
        data_path.read_text(encoding="utf-8"),
        re.DOTALL,
    )
    if not match:
        raise ProductionValidationError(
            f"Malformed published calendar data: {data_path}"
        )

    try:
        events = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        raise ProductionValidationError(
            f"Malformed published calendar data: {data_path}"
        ) from error

    if not isinstance(events, list) or not all(
        isinstance(event, dict) for event in events
    ):
        raise ProductionValidationError(
            f"Published calendar data is not an event array: {data_path}"
        )

    return events


def _venue_inventory_key(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def _venue_product_counts(
    events: list[dict],
    *,
    cutoff: date | None = None,
) -> tuple[dict[str, int], dict[str, str]]:
    """
    Count public ticket products per venue.

    A repeated same-date/headliner/ticket product counts once even if the
    published representation contains several session times. This prevents
    legitimate public-session collapsing from looking like catastrophic
    inventory loss.
    """

    products: dict[str, set[tuple[str, str, str]]] = {}
    display_names: dict[str, str] = {}

    for event in events:
        raw_date = str(event.get("d") or "")[:10]
        try:
            event_date = date.fromisoformat(raw_date)
        except ValueError:
            continue

        if cutoff is not None and event_date < cutoff:
            continue

        venue_display = re.sub(
            r"\s+", " ", str(event.get("v") or "").strip()
        )
        venue = _venue_inventory_key(venue_display)
        if not venue:
            continue

        headliner = re.sub(
            r"\s+", " ", str(event.get("h") or "").strip()
        ).casefold()
        ticket = str(event.get("t") or "").strip()

        # A ticket URL identifies the public product. When no ticket URL is
        # available, retain the session time so genuinely separate
        # performances are not collapsed merely for validation.
        discriminator = ticket or str(event.get("st") or "").strip()

        products.setdefault(venue, set()).add(
            (raw_date, headliner, discriminator)
        )
        display_names.setdefault(venue, venue_display)

    return (
        {venue: len(items) for venue, items in products.items()},
        display_names,
    )


def validate_venue_inventory_regression(
    candidate_events: list[dict],
    published_events: list[dict],
    *,
    allow_large_change: bool = False,
) -> None:
    """
    Refuse publication when a substantial venue catastrophically collapses.

    This is intentionally independent of scraper/source health. It protects
    the public calendar whether the loss came from a failed primary scraper,
    an incomplete fallback, a parser regression, or a later pipeline stage.
    """

    if allow_large_change or not candidate_events or not published_events:
        return

    candidate_dates = []
    for event in candidate_events:
        try:
            candidate_dates.append(
                date.fromisoformat(str(event.get("d") or "")[:10])
            )
        except ValueError:
            continue

    if not candidate_dates:
        return

    # Compare only the horizon represented by the candidate. This prevents
    # ordinary date rollover from being mistaken for venue inventory loss.
    cutoff = min(candidate_dates)

    published_counts, published_names = _venue_product_counts(
        published_events,
        cutoff=cutoff,
    )
    candidate_counts, _ = _venue_product_counts(
        candidate_events,
        cutoff=cutoff,
    )

    regressions = []

    for venue, published_count in published_counts.items():
        if published_count < MINIMUM_VENUE_BASELINE_COUNT:
            continue

        candidate_count = candidate_counts.get(venue, 0)
        retained_ratio = candidate_count / published_count

        if retained_ratio < MINIMUM_VENUE_PUBLISHED_RATIO:
            regressions.append(
                (
                    published_names.get(venue, venue),
                    candidate_count,
                    published_count,
                    retained_ratio,
                )
            )

    if regressions:
        details = "; ".join(
            f"{venue}: {candidate}/{published} retained ({ratio:.0%})"
            for venue, candidate, published, ratio in sorted(regressions)
        )
        raise ProductionValidationError(
            "Catastrophic venue inventory regression: "
            + details
            + f"; minimum retained ratio is "
            f"{MINIMUM_VENUE_PUBLISHED_RATIO:.0%}"
        )


def load_published_content_index(calendar_pointer: Path) -> dict:
    """
    Load the last-known-good published Electric Eye content index.

    Used only as a fallback when live Concert Reviews identity evidence is
    temporarily unavailable. This prevents a transient upstream failure from
    deleting established artist/article associations during an otherwise
    healthy calendar publication.
    """

    proof = calendar_pointer.parent
    content_pointer = proof / "electric-eye-content-current.js"

    if not content_pointer.is_file():
        raise ProductionValidationError(
            "Published Electric Eye content pointer is unavailable"
        )

    match = re.search(
        r"ElectricEyeContentManifest\s*=\s*Object\.freeze\((\{.*?\})\)",
        content_pointer.read_text(encoding="utf-8"),
        re.DOTALL,
    )
    if not match:
        raise ProductionValidationError(
            "Published Electric Eye content pointer is malformed"
        )

    try:
        manifest = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        raise ProductionValidationError(
            "Published Electric Eye content pointer is malformed"
        ) from error

    filename = manifest.get("data")
    expected_digest = manifest.get("sha256")

    if not isinstance(filename, str) or not filename:
        raise ProductionValidationError(
            "Published Electric Eye content pointer has no data asset"
        )

    data_path = proof / filename
    if not data_path.is_file():
        raise ProductionValidationError(
            f"Published Electric Eye content asset is missing: {data_path}"
        )

    body = data_path.read_bytes()
    if (
        isinstance(expected_digest, str)
        and re.fullmatch(r"[0-9a-f]{64}", expected_digest)
        and hashlib.sha256(body).hexdigest() != expected_digest
    ):
        raise ProductionValidationError(
            "Published Electric Eye content asset hash is invalid"
        )

    data_match = re.search(
        r"window\.ElectricEyeContentIndex\s*=\s*Object\.freeze\((\{.*\})\);\s*$",
        body.decode("utf-8"),
        re.DOTALL,
    )
    if not data_match:
        raise ProductionValidationError(
            "Published Electric Eye content asset is malformed"
        )

    try:
        index = json.loads(data_match.group(1))
    except json.JSONDecodeError as error:
        raise ProductionValidationError(
            "Published Electric Eye content asset is malformed"
        ) from error

    if not isinstance(index, dict) or not isinstance(index.get("artists"), dict):
        raise ProductionValidationError(
            "Published Electric Eye content index is invalid"
        )

    return index


def print_pointer_digest(args) -> int:
    print(read_pointer(Path(args.pointer))["sha256"])
    return 0


def validate_events(events: list[dict]) -> None:
    if len(events) < MINIMUM_EVENT_COUNT:
        raise ProductionValidationError(
            f"Only {len(events)} final events; minimum is {MINIMUM_EVENT_COUNT}"
        )

    allowed_genres = set(PUBLIC_GENRES)
    fingerprints = set()
    public_ids = {}

    for index, event in enumerate(events):
        event_keys = set(event)
        if (
            not REQUIRED_EVENT_KEYS.issubset(event_keys)
            or not event_keys.issubset(REQUIRED_EVENT_KEYS | OPTIONAL_EVENT_KEYS)
        ):
            missing = sorted(REQUIRED_EVENT_KEYS - event_keys)
            unexpected = sorted(event_keys - (REQUIRED_EVENT_KEYS | OPTIONAL_EVENT_KEYS))
            raise ProductionValidationError(
                f"Event {index} has an invalid renderer contract; "
                f"missing={missing}, unexpected={unexpected}, "
                f"keys={sorted(event_keys)}"
            )
        try:
            date.fromisoformat(event["d"])
        except (TypeError, ValueError) as error:
            raise ProductionValidationError(
                f"Event {index} has malformed date {event['d']!r}"
            ) from error
        if not all(
            isinstance(event[key], str) and event[key].strip()
            for key in ("h", "v", "c")
        ):
            raise ProductionValidationError(
                f"Event {index} is missing headliner, venue, or city"
            )
        public_text = [event["h"], event["v"], event["c"], *event["o"]]
        if any(RAW_MARKUP_OR_URL_RE.search(value) for value in public_text):
            raise ProductionValidationError(
                f"Event {index} contains markup, a URL, or a newline in a public field"
            )
        if RELOCATION_HEADLINER_RE.search(event["h"]):
            raise ProductionValidationError(
                f"Event {index} exposes a venue-change notice as its headliner"
            )
        if DESCRIPTIVE_VENUE_RE.search(event["v"]):
            raise ProductionValidationError(
                f"Event {index} contains descriptive billing text in its venue"
            )
        if not all(isinstance(event[key], list) for key in ("o", "x", "p")):
            raise ProductionValidationError(f"Event {index} has malformed lists")
        if any(genre not in allowed_genres for genre in event["x"]):
            raise ProductionValidationError(f"Event {index} has unknown public genre")
        if len(event["x"]) != len(set(event["x"])):
            raise ProductionValidationError(
                f"Event {index} has duplicate public genres"
            )
        if event["t"] is not None and safe_ticket_url(event["t"]) is None:
            raise ProductionValidationError(f"Event {index} has an unsafe ticket URL")
        if not isinstance(event["f"], bool) or not isinstance(event["so"], bool):
            raise ProductionValidationError(f"Event {index} has malformed status fields")
        try:
            datetime.fromisoformat(event["fs"].replace("Z", "+00:00"))
        except (AttributeError, ValueError) as error:
            raise ProductionValidationError(
                f"Event {index} has malformed first_seen"
            ) from error
        public_id = event["i"]
        if not re.fullmatch(r"[0-9a-f]{16}", public_id or ""):
            raise ProductionValidationError(
                f"Event {index} has invalid public ID {public_id!r}: "
                f"{event['d']} | {event['h']} | {event['v']} | "
                f"start={event.get('st')!r} | title={event.get('et')!r}"
            )
        if public_id in public_ids:
            previous_index, previous_event = public_ids[public_id]
            raise ProductionValidationError(
                f"Event {index} has duplicate public ID {public_id}; "
                f"current={event['d']} | {event['h']} | {event['v']} | "
                f"start={event.get('st')!r} | title={event.get('et')!r}; "
                f"previous_event={previous_index}: "
                f"{previous_event['d']} | {previous_event['h']} | "
                f"{previous_event['v']} | start={previous_event.get('st')!r} | "
                f"title={previous_event.get('et')!r}"
            )
        public_ids[public_id] = (index, event)
        if event["ts"] not in {None, "tickets", "sold_out", "free", "not_on_sale", "cancelled", "postponed"}:
            raise ProductionValidationError(f"Event {index} has an invalid ticket status")
        if event["st"] is not None and not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", event["st"]):
            raise ProductionValidationError(f"Event {index} has an invalid start time")

        fingerprint = (
            event["d"],
            event["h"].casefold(),
            tuple(opener.casefold() for opener in event["o"]),
            event["v"].casefold(),
            event["c"].casefold(),
            event.get("st"),
            event.get("et"),
        )
        if fingerprint in fingerprints:
            raise ProductionValidationError(
                f"Duplicate renderer record at event {index}: {event['h']}"
            )
        fingerprints.add(fingerprint)


def validate_source_report(report) -> None:
    if report.registration_failures:
        failures = ", ".join(
            f"{module}: {error}"
            for module, error in sorted(report.registration_failures.items())
        )
        raise ProductionValidationError(
            "Scraper registration failures: " + failures
        )
    if report.source_failures:
        failed = ", ".join(sorted(report.source_failures))
        print(
            "SOURCE DEGRADATION: scrapers exhausted retries and contributed "
            f"no fresh records: {failed}"
        )
    exercised = {item["source_name"] for item in report.source_health}
    unexercised = sorted(set(report.configured_sources) - exercised)
    if unexercised:
        raise ProductionValidationError(
            "Registered scrapers were not exercised: " + ", ".join(unexercised)
        )
    unexpected_empty = sorted(
        item["source_name"]
        for item in report.source_health
        if item["status"] == "empty" and not item["allow_empty"]
    )
    if unexpected_empty:
        raise ProductionValidationError(
            "Scrapers unexpectedly returned zero future events: "
            + ", ".join(unexpected_empty)
        )
    missing = sorted(
        source
        for source in CORE_SOURCES
        if report.source_counts.get(source, 0) == 0
        and source not in report.source_failures
    )
    if missing:
        raise ProductionValidationError(
            "Core scrapers returned zero events: " + ", ".join(missing)
        )
    if not all(
        count > 0
        for count in (report.raw_count, report.idf_count, report.final_count)
    ):
        raise ProductionValidationError("Pipeline produced a zero event count")


def validate_count_regression(
    new_count: int,
    published_count: int | None,
    *,
    allow_large_change: bool = False,
) -> None:
    if published_count is None or allow_large_change:
        return
    lower = int(published_count * MINIMUM_PUBLISHED_RATIO)
    upper = int(published_count * MAXIMUM_PUBLISHED_RATIO)
    if new_count < lower or new_count > upper:
        raise ProductionValidationError(
            f"Event count {new_count} is outside guarded range "
            f"{lower}..{upper} derived from published count {published_count}"
        )


def validate_genre_coverage(report: dict) -> None:
    """Catch parser-wide genre loss while allowing normal inventory drift."""

    total = report.get("total", 0)
    populated = report.get("populated", 0)
    if total and populated / total < MINIMUM_GENRE_COVERAGE:
        raise ProductionValidationError(
            f"Genre coverage {populated}/{total} is below the catastrophic "
            f"{MINIMUM_GENRE_COVERAGE:.0%} floor"
        )


def validate_assets(output_dir: Path, result: dict) -> dict:
    pointer = read_pointer(Path(result["pointer"]))
    data_path = Path(result["data"])
    digest = hashlib.sha256(data_path.read_bytes()).hexdigest()

    if pointer["data"] != data_path.name:
        raise ProductionValidationError("Pointer does not reference generated data")
    if pointer["sha256"] != digest or result["sha256"] != digest:
        raise ProductionValidationError("Generated data hash does not match pointer")
    if pointer["count"] != result["event_count"]:
        raise ProductionValidationError("Generated count does not match pointer")
    state_path = output_dir / STATE_FILENAME
    if not state_path.exists():
        raise ProductionValidationError("Generated event state is missing")
    state_digest = hashlib.sha256(state_path.read_bytes()).hexdigest()
    if pointer.get("state") != STATE_FILENAME or pointer.get("stateSha256") != state_digest:
        raise ProductionValidationError("Generated event state hash does not match pointer")

    renderer = (output_dir / "calendar-renderer.js").read_text(encoding="utf-8")
    styles = (output_dir / "calendar.css").read_text(encoding="utf-8")
    for required in (
        "ee-calendar-search",
        "ee-calendar-month",
        "ee-calendar-venue",
        "ee-calendar-genre",
        "Headliner — A–Z",
    ):
        if required not in renderer:
            raise ProductionValidationError(f"Renderer is missing {required}")
    if ".ee-calendar-page #ee-concert-calendar" not in styles:
        raise ProductionValidationError("Calendar CSS is not integration-scoped")

    return pointer


def build(args) -> int:
    print("PHASE START | source_and_pipeline_loading", flush=True)
    phase_started = time.perf_counter()
    events, pipeline_report = load_events_with_report()
    print(f"PHASE COMPLETE | source_and_pipeline_loading | elapsed={max(0.0, time.perf_counter() - phase_started):.2f}s", flush=True)
    validate_source_report(pipeline_report)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print("Building Electric Eye editorial content index...")
    print("PHASE START | blogger_content_retrieval_indexing", flush=True)
    phase_started = time.perf_counter()
    from concert_calendar.content_index import fetch_concert_review_associations

    try:
        concert_review_associations = fetch_concert_review_associations()
    except Exception as error:
        print(
            "Concert Reviews identity evidence unavailable; "
            f"reusing published content index: {error}"
        )
        if not args.published_pointer:
            raise ProductionValidationError(
                "Concert Reviews identity evidence unavailable and no "
                "published content fallback exists"
            ) from error
        content_index = load_published_content_index(
            Path(args.published_pointer)
        )
    else:
        content_index = build_index(
            fetch_entries(),
            concert_review_associations=concert_review_associations,
        )
    print(f"PHASE COMPLETE | blogger_content_retrieval_indexing | elapsed={max(0.0, time.perf_counter() - phase_started):.2f}s", flush=True)
    print("PHASE START | content_index_enrichment", flush=True)
    phase_started = time.perf_counter()
    enrich_events(events, content_index)
    content_result = write_assets(output_dir, content_index)
    print(f"PHASE COMPLETE | content_index_enrichment | elapsed={max(0.0, time.perf_counter() - phase_started):.2f}s", flush=True)
    print("PHASE START | state_export", flush=True)
    phase_started = time.perf_counter()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    try:
        previous_state = load_state(
            Path(args.published_state) if args.published_state else None
        )
        candidate_state = reconcile_state(events, previous_state, now=now)
        change_report = build_change_report(events, previous_state, candidate_state, now=now)
        state_digest = write_state(output_dir / STATE_FILENAME, candidate_state)
    except EventStateError as error:
        raise ProductionValidationError(f"Persistent event state is invalid: {error}") from error
    published_at = candidate_state["updated_at"]
    result = export_integration_prototype(
        events,
        output_dir=args.output_dir,
        published_at=published_at,
        state_sha256=state_digest,
    )
    print(f"PHASE COMPLETE | state_export | elapsed={max(0.0, time.perf_counter() - phase_started):.2f}s", flush=True)
    print("PHASE START | render_validation", flush=True)
    phase_started = time.perf_counter()
    events_data = prepare_upcoming_events(events)
    validate_events(events_data)

    if args.published_pointer and Path(args.published_pointer).exists():
        published_events = read_published_calendar_events(
            Path(args.published_pointer)
        )
        validate_venue_inventory_regression(
            events_data,
            published_events,
            allow_large_change=args.allow_large_count_change,
        )

    route_result = write_clean_routes(output_dir, content_index, events_data)
    print(
        f"Created {route_result['artists']} artist routes and "
        f"{route_result['concerts']} concert routes"
    )
    validate_genre_coverage(pipeline_report.genre_report)
    pointer = validate_assets(output_dir, result)
    print(f"PHASE COMPLETE | render_validation | elapsed={max(0.0, time.perf_counter() - phase_started):.2f}s", flush=True)

    published_count = None
    if args.published_pointer and Path(args.published_pointer).exists():
        published_count = read_pointer(Path(args.published_pointer))["count"]
    validate_count_regression(
        pointer["count"],
        published_count,
        allow_large_change=args.allow_large_count_change,
    )

    report = {
        **asdict(pipeline_report),
        "published_baseline_count": published_count,
        "data_filename": pointer["data"],
        "sha256": pointer["sha256"],
        "event_count": pointer["count"],
        "state_event_count": len(candidate_state["events"]),
        "state_sha256": state_digest,
        "published_at": published_at,
        "state_bootstrapped": previous_state is None,
        "genre_report": pipeline_report.genre_report,
        "change_report": change_report,
        "content_index": {
            **content_result,
            "diagnostics": content_index["diagnostics"],
            "compact_bytes": (output_dir / "electric-eye-artist-lookup.js").stat().st_size,
            "full_bytes": (output_dir / content_result["filename"]).stat().st_size,
        },
    }
    report_path = output_dir / "automation-report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_github_outputs(report)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    if args.simulate_validation_failure:
        raise ProductionValidationError("Controlled validation failure requested")
    return 0


def write_github_outputs(report: dict) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with Path(output_path).open("a", encoding="utf-8") as output:
        for key in ("event_count", "raw_count", "idf_count", "sha256", "data_filename"):
            output.write(f"{key}={report[key]}\n")
        for key, value in report["change_report"].items():
            if key != "details":
                output.write(f"{key}={value}\n")
        for key in ("populated", "blank", "coverage_percentage", "conflict_count"):
            output.write(f"genre_{key}={report['genre_report'][key]}\n")


def git_timestamp(repository: Path, relative_path: Path) -> int:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%ct", "--", str(relative_path)],
        cwd=repository,
        text=True,
        capture_output=True,
        check=True,
    )
    return int(result.stdout.strip() or 0)


def validated_publication_files(source: Path) -> tuple[dict, list[Path]]:
    pointer_path = source / "calendar-current.js"
    pointer = read_pointer(pointer_path)
    data = source / pointer["data"]
    state = source / pointer.get("state", "")
    if not data.is_file() or hashlib.sha256(data.read_bytes()).hexdigest() != pointer["sha256"]:
        raise ProductionValidationError("Refusing to publish invalid generated data")
    if (
        not state.is_file()
        or hashlib.sha256(state.read_bytes()).hexdigest() != pointer.get("stateSha256")
    ):
        raise ProductionValidationError("Refusing to publish invalid event state")

    files = [pointer_path, data, state]
    for stable_name in PUBLIC_STABLE_ASSETS:
        stable = source / stable_name
        if not stable.is_file():
            raise ProductionValidationError(f"Generated publication is missing {stable_name}")
        files.append(stable)

    content_pointer = source / "electric-eye-content-current.js"
    content_match = re.search(
        r"ElectricEyeContentManifest=Object\.freeze\((\{.*?\})\)",
        content_pointer.read_text(encoding="utf-8"),
    )
    if not content_match:
        raise ProductionValidationError("Generated content pointer is malformed")
    content_manifest = json.loads(content_match.group(1))
    content_data = source / content_manifest.get("data", "")
    if (
        not content_data.is_file()
        or hashlib.sha256(content_data.read_bytes()).hexdigest()
        != content_manifest.get("sha256")
    ):
        raise ProductionValidationError("Generated content index hash is invalid")
    files.append(content_data)

    for root_name in PUBLIC_ROOT_ASSETS:
        root_asset = source / root_name
        if not root_asset.is_file():
            raise ProductionValidationError(
                f"Generated publication is missing root asset {root_name}"
            )
        files.append(root_asset)

    for route_name in PUBLIC_ROUTE_DIRS:
        route_dir = source / route_name
        if not route_dir.is_dir():
            raise ProductionValidationError(
                f"Generated publication is missing route directory {route_name}"
            )
        route_pages = sorted(route_dir.glob("*/index.html"))
        if not route_pages:
            raise ProductionValidationError(
                f"Generated publication has no pages in route directory {route_name}"
            )
        files.extend(route_pages)

    return pointer, list(dict.fromkeys(files))


def stage_candidate(args) -> int:
    generated = Path(args.generated_dir)
    pages = Path(args.pages_dir)
    if not re.fullmatch(r"[0-9a-f]{64}-[0-9]+", args.candidate_id):
        raise ProductionValidationError("Candidate ID is malformed")
    pointer, files = validated_publication_files(generated)
    candidate = pages / "proof" / "candidates" / args.candidate_id
    if candidate.exists():
        raise ProductionValidationError(f"Candidate already exists: {args.candidate_id}")
    candidate.mkdir(parents=True)
    for source in files:
        relative = source.relative_to(generated)
        target = candidate / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    print(f"Staged immutable candidate {args.candidate_id}: {pointer['count']} events")
    return 0


def publish(args) -> int:
    generated = Path(args.generated_dir)
    pages = Path(args.pages_dir)
    proof = pages / "proof"
    proof.mkdir(parents=True, exist_ok=True)

    new_pointer, publication_files = validated_publication_files(generated)
    old_pointer = (
        read_pointer(proof / "calendar-current.js")
        if (proof / "calendar-current.js").exists()
        else None
    )
    new_data = generated / new_pointer["data"]
    new_state = generated / new_pointer.get("state", "")

    shutil.copyfile(new_data, proof / new_data.name)
    shutil.copyfile(new_state, proof / STATE_FILENAME)
    for stable_name in PUBLIC_STABLE_ASSETS:
        source = generated / stable_name
        target = proof / stable_name
        if not target.exists() or source.read_bytes() != target.read_bytes():
            shutil.copyfile(source, target)
    for source in publication_files:
        if source.name.startswith("electric-eye-content."):
            shutil.copyfile(source, proof / source.name)
    shutil.copyfile(generated / "calendar-current.js", proof / "calendar-current.js")

    for root_name in PUBLIC_ROOT_ASSETS:
        shutil.copyfile(generated / root_name, pages / root_name)

    for route_name in PUBLIC_ROUTE_DIRS:
        source_routes = generated / route_name
        target_routes = pages / route_name
        if target_routes.exists():
            shutil.rmtree(target_routes)
        shutil.copytree(source_routes, target_routes)

    previous = []
    for candidate in proof.glob("calendar-data.*.js"):
        if candidate.name == new_data.name:
            continue
        priority = 1 if old_pointer and candidate.name == old_pointer["data"] else 0
        previous.append(
            (priority, git_timestamp(pages, candidate.relative_to(pages)), candidate)
        )
    keep = {new_data.name}
    keep.update(item[2].name for item in sorted(previous, reverse=True)[:2])
    for candidate in proof.glob("calendar-data.*.js"):
        if candidate.name not in keep:
            candidate.unlink()
    content_candidates = sorted(
        proof.glob("electric-eye-content.*.js"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for candidate in content_candidates[3:]:
        candidate.unlink()
    for stale_name in STALE_PUBLIC_TEST_ASSETS:
        stale = proof / stale_name
        if stale.exists():
            stale.unlink()
    candidates = proof / "candidates"
    if candidates.exists():
        shutil.rmtree(candidates)

    print("Retained data assets: " + ", ".join(sorted(keep)))
    return 0


def promote_verified(args, verifier=None) -> int:
    (verifier or verify_hosted)(args)
    publish_args = type(
        "PublishArgs",
        (),
        {"generated_dir": args.candidate_dir, "pages_dir": args.pages_dir},
    )()
    return publish(publish_args)


def verify_hosted(args) -> int:
    pointer_url = args.base_url.rstrip("/") + "/calendar-current.js"
    deadline = time.monotonic() + args.timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            pointer_body, pointer_type = fetch(pointer_url + f"?verify={args.sha256[:16]}")
            match = POINTER_PATTERN.search(pointer_body.decode("utf-8"))
            if not match:
                raise ProductionValidationError("Hosted pointer is malformed")
            manifest = json.loads(match.group(1))
            if manifest.get("sha256") != args.sha256:
                raise ProductionValidationError("Hosted pointer has not propagated")
            data_url = args.base_url.rstrip("/") + "/" + manifest["data"]
            data_body, data_type = fetch(data_url + f"?verify={args.sha256[:16]}")
            if hashlib.sha256(data_body).hexdigest() != args.sha256:
                raise ProductionValidationError("Hosted data hash mismatch")
            if "javascript" not in pointer_type or "javascript" not in data_type:
                raise ProductionValidationError("Hosted JavaScript content type is invalid")
            state_body, state_type = fetch(
                args.base_url.rstrip("/") + "/" + manifest["state"]
                + f"?verify={args.sha256[:16]}"
            )
            if (
                hashlib.sha256(state_body).hexdigest() != manifest["stateSha256"]
                or "json" not in state_type
            ):
                raise ProductionValidationError("Hosted event state is invalid")
            for stable in ("calendar-renderer.js", "calendar.css"):
                body, content_type = fetch(
                    args.base_url.rstrip("/") + "/" + stable + f"?verify={args.sha256[:16]}"
                )
                if not body or not any(
                    value in content_type for value in ("javascript", "css")
                ):
                    raise ProductionValidationError(f"Hosted {stable} is invalid")
            for stable in (
                "electric-eye-artist-lookup.js", "electric-eye-content-current.js",
                "artist-page.js", "artist-page.css", "artist-autolinker.js", "artist.html",
                "coverage-page.js", "coverage.html",
            ):
                body, content_type = fetch(
                    args.base_url.rstrip("/") + "/" + stable + f"?verify={args.sha256[:16]}"
                )
                expected_types = ("html",) if stable.endswith(".html") else ("javascript", "css")
                if not body or not any(value in content_type for value in expected_types):
                    raise ProductionValidationError(f"Hosted {stable} is invalid")
            content_pointer_body, _ = fetch(
                args.base_url.rstrip("/") + "/electric-eye-content-current.js"
                + f"?verify={args.sha256[:16]}"
            )
            content_match = re.search(
                rb"ElectricEyeContentManifest=Object\.freeze\((\{.*?\})\)",
                content_pointer_body,
            )
            if not content_match:
                raise ProductionValidationError("Hosted content pointer is malformed")
            content_manifest = json.loads(content_match.group(1))
            content_body, content_type = fetch(
                args.base_url.rstrip("/") + "/" + content_manifest["data"]
                + f"?verify={args.sha256[:16]}"
            )
            if (
                hashlib.sha256(content_body).hexdigest() != content_manifest["sha256"]
                or "javascript" not in content_type
            ):
                raise ProductionValidationError("Hosted content index is invalid")
            print(
                f"Hosted publication verified: {manifest['count']} events, "
                f"SHA-256 {args.sha256}"
            )
            return 0
        except Exception as error:
            last_error = error
            time.sleep(15)

    raise ProductionValidationError(
        f"Hosted publication did not validate within {args.timeout}s: {last_error}"
    )


def fetch(url: str) -> tuple[bytes, str]:
    request = Request(url, headers={"User-Agent": "ElectricEyeCalendarAutomation/1.0"})
    with urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise ProductionValidationError(f"HTTP {response.status} for {url}")
        return response.read(), response.headers.get_content_type()


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Electric Eye production automation")
    commands = parser.add_subparsers(dest="command", required=True)

    build_parser = commands.add_parser("build")
    build_parser.add_argument("--output-dir", required=True)
    build_parser.add_argument("--published-pointer")
    build_parser.add_argument("--published-state")
    build_parser.add_argument("--allow-large-count-change", action="store_true")
    build_parser.add_argument("--simulate-validation-failure", action="store_true")
    build_parser.set_defaults(handler=build)

    publish_parser = commands.add_parser("publish")
    publish_parser.add_argument("--generated-dir", required=True)
    publish_parser.add_argument("--pages-dir", required=True)
    publish_parser.set_defaults(handler=publish)

    candidate_parser = commands.add_parser("stage-candidate")
    candidate_parser.add_argument("--generated-dir", required=True)
    candidate_parser.add_argument("--pages-dir", required=True)
    candidate_parser.add_argument("--candidate-id", required=True)
    candidate_parser.set_defaults(handler=stage_candidate)

    promote_parser = commands.add_parser("promote-verified")
    promote_parser.add_argument("--candidate-dir", required=True)
    promote_parser.add_argument("--pages-dir", required=True)
    promote_parser.add_argument("--base-url", required=True)
    promote_parser.add_argument("--sha256", required=True)
    promote_parser.add_argument("--timeout", type=int, default=600)
    promote_parser.set_defaults(handler=promote_verified)

    verify_parser = commands.add_parser("verify-hosted")
    verify_parser.add_argument("--base-url", required=True)
    verify_parser.add_argument("--sha256", required=True)
    verify_parser.add_argument("--timeout", type=int, default=600)
    verify_parser.set_defaults(handler=verify_hosted)

    digest_parser = commands.add_parser("pointer-digest")
    digest_parser.add_argument("--pointer", required=True)
    digest_parser.set_defaults(handler=print_pointer_digest)

    return parser


def main() -> int:
    args = make_parser().parse_args()
    try:
        return args.handler(args)
    except ProductionValidationError as error:
        print(f"PRODUCTION VALIDATION FAILED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
