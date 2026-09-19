#!/usr/bin/env python3

from __future__ import annotations

import base64
import gzip
import json
import os
import shutil
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = (
    "https://script.google.com/macros/s/"
    "AKfycbyxbAkw_Mcl_iXwV_N-JHS2rTf_KBwZlJKsD1RVECUlXR7WNXBt0eUAEIevZOiHXJpcaA"
    "/exec"
)

BATCH_SIZE = 100
MAX_ATTEMPTS = 6
ALLOWED_CATEGORIES = {"LISTEN", "WATCH", "READ"}


OUTPUT_DIR = Path("output/automation")

def fetch_json(params: dict[str, str | int]) -> dict:
    url = ENDPOINT + "?" + urllib.parse.urlencode(params)
    last_error: Exception | None = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "ElectricEyeStaticPayloadExporter/1.0",
                },
            )

            with urllib.request.urlopen(request, timeout=120) as response:
                raw = response.read()

            text = raw.decode("utf-8", errors="replace").lstrip()

            if not text.startswith("{"):
                raise RuntimeError(
                    "Apps Script returned non-JSON content"
                )

            value = json.loads(text)

            if not isinstance(value, dict):
                raise RuntimeError("Apps Script returned non-object JSON")

            return value

        except Exception as error:
            last_error = error

            if attempt >= MAX_ATTEMPTS - 1:
                break

            time.sleep(min(20, 2 ** (attempt + 1)))

    raise RuntimeError(
        f"Unable to fetch static payload export: {last_error}"
    )


def decode_payload_cell(stored: str) -> dict:
    stored = str(stored or "")

    if stored.startswith("GZIP64:"):
        compressed = base64.b64decode(stored[7:])
        stored = gzip.decompress(compressed).decode("utf-8")

    value = json.loads(stored)

    if not isinstance(value, dict):
        raise ValueError("payload is not an object")

    return value


def sanitize_payload(payload: dict) -> dict:
    allowed_top = (
        "schemaVersion",
        "generationVersion",
        "postId",
        "title",
        "url",
        "storefront",
        "generatedAt",
        "subject",
        "identity",
    )

    result = {
        key: payload[key]
        for key in allowed_top
        if key in payload
    }

    groups = []

    for raw_group in payload.get("categories") or []:
        if not isinstance(raw_group, dict):
            continue

        category = str(raw_group.get("category") or "").upper()

        if category not in ALLOWED_CATEGORIES:
            continue

        items = raw_group.get("items") or []

        if not isinstance(items, list) or not items:
            continue

        groups.append(
            {
                "category": category,
                "items": items,
            }
        )

    result["categories"] = groups
    return result


def generated_sort_key(value: str, row_number: int) -> tuple[str, int]:
    return (str(value or ""), int(row_number or 0))


def main() -> int:
    start_row = 2
    best: dict[str, tuple[tuple[str, int], dict]] = {}
    pages = 0

    while True:
        page = fetch_json(
            {
                "action": "payload-export",
                "startRow": start_row,
                "limit": BATCH_SIZE,
            }
        )

        if page.get("kind") != "APPLE_STATIC_PAYLOAD_EXPORT":
            raise RuntimeError(
                "Production Apps Script does not yet expose payload-export. "
                "Deploy the new Code.gs first."
            )

        pages += 1

        for record in page.get("records") or []:
            try:
                post_id = str(record.get("postId") or "")
                row_number = int(record.get("rowNumber") or 0)
                generated_at = str(record.get("generatedAt") or "")

                if not post_id.isdigit():
                    continue

                payload = sanitize_payload(
                    decode_payload_cell(
                        str(record.get("payloadCell") or "")
                    )
                )

                if not payload.get("categories"):
                    continue

                key = generated_sort_key(
                    generated_at,
                    row_number,
                )

                prior = best.get(post_id)

                if prior is None or key > prior[0]:
                    best[post_id] = (key, payload)

            except Exception as error:
                print(
                    "Skipping malformed READY row:",
                    record.get("postId"),
                    error,
                    file=sys.stderr,
                )

        if bool(page.get("complete")):
            break

        next_row = int(page.get("nextRow") or 0)

        if next_row <= start_row:
            raise RuntimeError(
                "Static export cursor did not advance."
            )

        start_row = next_row

    output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = output_dir / ".apple-payloads.tmp"

    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    temp_dir.mkdir(parents=True, exist_ok=True)

    for post_id, (_, payload) in sorted(best.items()):
        body = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        javascript = (
            "window.__EE_APPLE_STATIC_PAYLOAD__="
            + body
            + ";"
            + "if(window.__eeAppleStaticReceive)"
            + "window.__eeAppleStaticReceive("
            + "window.__EE_APPLE_STATIC_PAYLOAD__"
            + ");\n"
        )

        (temp_dir / f"apple-payload-{post_id}.js").write_text(
            javascript,
            encoding="utf-8",
        )

    manifest = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "payloadCount": len(best),
        "sourcePages": pages,
    }

    (temp_dir / "apple-payload-manifest.json").write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )

    for stale in output_dir.glob("apple-payload-*.js"):
        stale.unlink()

    manifest_path = output_dir / "apple-payload-manifest.json"

    if manifest_path.exists():
        manifest_path.unlink()

    for generated in temp_dir.iterdir():
        generated.replace(output_dir / generated.name)

    shutil.rmtree(temp_dir)

    print(
        json.dumps(
            {
                "status": "OK",
                "payloads": len(best),
                "pages": pages,
                "output": str(output_dir),
            },
            separators=(",", ":"),
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
