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
)
from concert_calendar.event_state import (
    EventStateError,
    STATE_FILENAME,
    build_change_report,
    load_state,
    reconcile_state,
    write_state,
)
from concert_calendar.sources import load_events_with_report


MINIMUM_EVENT_COUNT = 100
MINIMUM_PUBLISHED_RATIO = 0.60
MAXIMUM_PUBLISHED_RATIO = 2.50
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
    "Vedettes",
    "VeryShow",
}
REQUIRED_EVENT_KEYS = {
    "d", "h", "o", "v", "c", "g", "x", "p", "t", "f", "so", "fs",
    "i", "ts", "st",
}
POINTER_PATTERN = re.compile(r"var manifest = Object\.freeze\((\{.*?\})\);")


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


def validate_events(events: list[dict]) -> None:
    if len(events) < MINIMUM_EVENT_COUNT:
        raise ProductionValidationError(
            f"Only {len(events)} final events; minimum is {MINIMUM_EVENT_COUNT}"
        )

    allowed_genres = set(PUBLIC_GENRES)
    fingerprints = set()
    public_ids = set()

    for index, event in enumerate(events):
        if set(event) != REQUIRED_EVENT_KEYS:
            raise ProductionValidationError(
                f"Event {index} has an invalid renderer contract"
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
        if not all(isinstance(event[key], list) for key in ("o", "x", "p")):
            raise ProductionValidationError(f"Event {index} has malformed lists")
        if any(genre not in allowed_genres for genre in event["x"]):
            raise ProductionValidationError(f"Event {index} has unknown public genre")
        if len(event["x"]) > 1:
            raise ProductionValidationError(
                f"Event {index} has more than one public genre"
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
        if not re.fullmatch(r"[0-9a-f]{16}", event["i"] or "") or event["i"] in public_ids:
            raise ProductionValidationError(f"Event {index} has an invalid or duplicate public ID")
        public_ids.add(event["i"])
        if event["ts"] not in {None, "tickets", "sold_out", "free", "not_on_sale"}:
            raise ProductionValidationError(f"Event {index} has an invalid ticket status")
        if event["st"] is not None and not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", event["st"]):
            raise ProductionValidationError(f"Event {index} has an invalid start time")

        fingerprint = (
            event["d"],
            event["h"].casefold(),
            tuple(opener.casefold() for opener in event["o"]),
            event["v"].casefold(),
            event["c"].casefold(),
        )
        if fingerprint in fingerprints:
            raise ProductionValidationError(
                f"Duplicate renderer record at event {index}: {event['h']}"
            )
        fingerprints.add(fingerprint)


def validate_source_report(report) -> None:
    if report.source_failures:
        failed = ", ".join(sorted(report.source_failures))
        raise ProductionValidationError(f"Scrapers exhausted retries: {failed}")
    missing = sorted(
        source for source in CORE_SOURCES if report.source_counts.get(source, 0) == 0
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
    events, pipeline_report = load_events_with_report()
    validate_source_report(pipeline_report)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
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
    events_data = prepare_upcoming_events(events)
    validate_events(events_data)
    validate_genre_coverage(pipeline_report.genre_report)
    pointer = validate_assets(output_dir, result)

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


def publish(args) -> int:
    generated = Path(args.generated_dir)
    pages = Path(args.pages_dir)
    proof = pages / "proof"
    proof.mkdir(parents=True, exist_ok=True)

    new_pointer = read_pointer(generated / "calendar-current.js")
    old_pointer = (
        read_pointer(proof / "calendar-current.js")
        if (proof / "calendar-current.js").exists()
        else None
    )
    new_data = generated / new_pointer["data"]
    if hashlib.sha256(new_data.read_bytes()).hexdigest() != new_pointer["sha256"]:
        raise ProductionValidationError("Refusing to publish invalid generated hash")
    new_state = generated / new_pointer.get("state", "")
    if (
        not new_state.is_file()
        or hashlib.sha256(new_state.read_bytes()).hexdigest()
        != new_pointer.get("stateSha256")
    ):
        raise ProductionValidationError("Refusing to publish invalid event state")

    shutil.copyfile(new_data, proof / new_data.name)
    shutil.copyfile(new_state, proof / STATE_FILENAME)
    for stable_name in ("calendar-renderer.js", "calendar.css"):
        source = generated / stable_name
        target = proof / stable_name
        if not target.exists() or source.read_bytes() != target.read_bytes():
            shutil.copyfile(source, target)
    shutil.copyfile(generated / "calendar-current.js", proof / "calendar-current.js")

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

    print("Retained data assets: " + ", ".join(sorted(keep)))
    return 0


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

    verify_parser = commands.add_parser("verify-hosted")
    verify_parser.add_argument("--base-url", required=True)
    verify_parser.add_argument("--sha256", required=True)
    verify_parser.add_argument("--timeout", type=int, default=600)
    verify_parser.set_defaults(handler=verify_hosted)

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
