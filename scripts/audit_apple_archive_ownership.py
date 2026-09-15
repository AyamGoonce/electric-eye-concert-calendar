#!/usr/bin/env python3
"""Read-only archive audit for Electric Eye Apple recommendation ownership.

The tool consumes exported data only.  It never invokes Apps Script mutation
helpers and never writes to Blogger, Sheets, Apps Script, or the static source
worktree.  Its only writes are the requested JSON/CSV audit artifacts.
"""

from __future__ import annotations

import argparse
import base64
import csv
import gzip
import json
import re
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


BLOGGER_FEED = "https://www.electriceyerock.com/feeds/posts/summary"
CHARLI_NAMES = {"charli xcx", "charli x c x"}
TAXONOMIES = {
    "ORDINARY_SINGLE_SUBJECT",
    "PLAYLIST_MULTI_ARTIST",
    "AMBIGUOUS_NO_CLEAR_TITLE",
    "ORPHAN_DELETED",
}
SERIOUS_FLAGS = {
    "CHARLI_CONTAMINATION_SUSPECTED",
    "WRONG_PRIMARY_SUSPECTED",
    "CLEAR_TITLE_UNRESOLVED",
    "NAMED_SUBJECT_GENERIC_FALLBACK",
    "CATALOGUE_OWNER_MISMATCH",
    "CONTEXT_AS_ARTIST",
    "HISTORICAL_RECOVERY_UNPROVEN",
    "SHARED_SUSPICIOUS_APPLE_ID",
    "STATIC_BACKEND_MISMATCH",
}
GENERIC_FALLBACK_MODES = {
    "GENRE_FALLBACK",
    "CONTENT_GENRE_FALLBACK",
    "SITE_FALLBACK",
}


def norm(value: Any) -> str:
    text = str(value or "").lower().replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9'+]+", " ", text)).strip()


def slug(value: Any) -> str:
    return re.sub(r"^-|-+$", "", re.sub(r"[^a-z0-9]+", "-", norm(value)))


def unique(values: Iterable[Any]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw or "").strip()
        key = norm(value)
        if value and key and key not in seen:
            seen.add(key)
            result.append(value)
    return result


def blogger_post_id(entry: dict[str, Any]) -> str:
    value = str((entry.get("id") or {}).get("$t") or entry.get("postId") or "")
    match = re.search(r"post-(\d+)$", value)
    return match.group(1) if match else (value if value.isdigit() else "")


def alternate_url(entry: dict[str, Any]) -> str:
    if entry.get("url"):
        return str(entry["url"])
    for link in entry.get("link") or []:
        if link.get("rel") == "alternate":
            return str(link.get("href") or "")
    return ""


def feed_entries(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if not isinstance(value, dict):
        return []
    if isinstance(value.get("posts"), list):
        return [item for item in value["posts"] if isinstance(item, dict)]
    return [
        item
        for item in ((value.get("feed") or {}).get("entry") or [])
        if isinstance(item, dict)
    ]


def normalize_post(entry: dict[str, Any]) -> dict[str, Any] | None:
    post_id = blogger_post_id(entry)
    if not post_id:
        return None
    title = entry.get("title")
    if isinstance(title, dict):
        title = title.get("$t")
    labels = entry.get("labels")
    if labels is None:
        labels = [item.get("term") for item in entry.get("category") or []]
    return {
        "postId": post_id,
        "url": alternate_url(entry),
        "title": str(title or ""),
        "labels": unique(labels or []),
    }


def fetch_blogger_posts() -> list[dict[str, Any]]:
    posts: list[dict[str, Any]] = []
    start = 1
    expected: int | None = None
    while True:
        query = urllib.parse.urlencode(
            {"alt": "json", "orderby": "published", "start-index": start, "max-results": 500}
        )
        request = urllib.request.Request(
            BLOGGER_FEED + "?" + query,
            headers={"User-Agent": "ElectricEyeAppleOwnershipAudit/1.0"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            page = json.load(response)
        feed = page.get("feed") or {}
        if expected is None:
            expected = int((feed.get("openSearch$totalResults") or {}).get("$t") or 0)
        entries = feed_entries(page)
        if not entries:
            break
        posts.extend(entries)
        start += len(entries)
        if expected is not None and len(posts) >= expected:
            break
    if expected is None or len(posts) != expected:
        raise RuntimeError(f"Incomplete Blogger feed: received {len(posts)} of {expected}")
    return [post for entry in posts if (post := normalize_post(entry))]


def load_blogger_posts(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return fetch_blogger_posts()
    value = json.loads(path.read_text(encoding="utf-8"))
    return [post for entry in feed_entries(value) if (post := normalize_post(entry))]


def decode_payload(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    stored = str(value or "")
    if not stored:
        return None
    if stored.startswith("GZIP64:"):
        stored = gzip.decompress(base64.b64decode(stored[7:])).decode("utf-8")
    parsed = json.loads(stored)
    return parsed if isinstance(parsed, dict) else None


def normalize_payload_row(row: Any, index: int) -> dict[str, Any] | None:
    if isinstance(row, list):
        row = {
            "postId": row[0] if len(row) > 0 else "",
            "url": row[1] if len(row) > 1 else "",
            "generatedAt": row[2] if len(row) > 2 else "",
            "storefront": row[3] if len(row) > 3 else "",
            "payloadCell": row[4] if len(row) > 4 else "",
            "status": row[5] if len(row) > 5 else "",
            "error": row[6] if len(row) > 6 else "",
            "retryCount": row[7] if len(row) > 7 else 0,
        }
    if not isinstance(row, dict):
        return None
    post_id = str(row.get("postId") or "")
    if not post_id:
        return None
    try:
        payload = decode_payload(row.get("payload", row.get("payloadCell")))
    except Exception:
        payload = None
    return {
        **row,
        "postId": post_id,
        "rowNumber": int(row.get("rowNumber") or index + 2),
        "status": str(row.get("status") or ""),
        "generatedAt": str(row.get("generatedAt") or ""),
        "payload": payload,
    }


def normalize_artist_row(row: Any, index: int) -> dict[str, Any] | None:
    if isinstance(row, list):
        row = {
            "artistKey": row[0] if len(row) > 0 else "",
            "canonicalName": row[1] if len(row) > 1 else "",
            "appleArtistId": row[4] if len(row) > 4 else "",
            "musicBrainzId": row[5] if len(row) > 5 else "",
            "identityConfidence": row[6] if len(row) > 6 else "",
            "status": row[7] if len(row) > 7 else "",
            "catalogueCell": row[8] if len(row) > 8 else "",
            "representativePostId": row[11] if len(row) > 11 else "",
            "error": row[12] if len(row) > 12 else "",
        }
    if not isinstance(row, dict):
        return None
    key = str(row.get("artistKey") or "")
    if not key:
        return None
    try:
        catalogue = decode_payload(row.get("catalogue", row.get("catalogueCell")))
    except Exception:
        catalogue = None
    return {
        **row,
        "rowNumber": int(row.get("rowNumber") or index + 2),
        "artistKey": key,
        "canonicalName": str(row.get("canonicalName") or ""),
        "appleArtistId": str(row.get("appleArtistId") or ""),
        "status": str(row.get("status") or ""),
        "catalogue": catalogue,
    }


def load_backend_snapshot(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Backend snapshot must be a JSON object")
    payload_rows = [
        item
        for index, row in enumerate(value.get("payloadRows") or [])
        if (item := normalize_payload_row(row, index))
    ]
    artist_rows = [
        item
        for index, row in enumerate(value.get("artistRows") or [])
        if (item := normalize_artist_row(row, index))
    ]
    if "payloadRows" not in value or "artistRows" not in value:
        raise ValueError("Backend snapshot requires payloadRows and artistRows arrays")
    return payload_rows, artist_rows


def payload_ready(row: dict[str, Any]) -> bool:
    payload = row.get("payload") or {}
    return row.get("status") == "READY" and any(
        (group.get("items") or []) for group in payload.get("categories") or []
    )


def preferred_payload_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        current = result.get(row["postId"])
        candidate_key = (payload_ready(row), row.get("generatedAt") or "", row["rowNumber"])
        current_key = (
            payload_ready(current), current.get("generatedAt") or "", current["rowNumber"]
        ) if current else None
        if current_key is None or candidate_key > current_key:
            result[row["postId"]] = row
    return result


def parse_static_payload(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    prefix = "window.__EE_APPLE_STATIC_PAYLOAD__="
    marker = ";if(window.__eeAppleStaticReceive)"
    if not text.startswith(prefix) or marker not in text:
        return None
    return decode_payload(text[len(prefix): text.index(marker)])


def load_static_payloads(root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob("apple-payload-*.js")):
        match = re.fullmatch(r"apple-payload-(\d+)\.js", path.name)
        if not match:
            continue
        try:
            payload = parse_static_payload(path)
        except Exception:
            payload = None
        if payload:
            result[match.group(1)] = payload
    return result


def artist_registry(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("artists"), list):
        raise ValueError("Artist index is missing artists")
    return value


def names_for_artist(artist: dict[str, Any]) -> list[str]:
    return unique(
        [artist.get("canonicalName")]
        + list(artist.get("aliases") or [])
        + list(artist.get("alternateSpellings") or [])
    )


def registry_maps(registry: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    by_key: dict[str, dict[str, Any]] = {}
    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for artist in registry.get("artists") or []:
        by_key[str(artist.get("slug") or "")] = artist
        for name in names_for_artist(artist):
            by_name[norm(name)].append(artist)
    return by_key, by_name


def article_type(title: str, labels: list[str]) -> str:
    joined = " ".join(labels)
    if re.search(r"\bplaylist\b|roundup|best of|festival line.?up", title + " " + joined, re.I):
        return "playlist"
    if " @ " in title:
        return "concert_review"
    if re.match(r"^album review\s*(?::|[–-])", title, re.I):
        return "album_review"
    if re.match(r"^(?:a\s+)?(?:conversation|interview)\s+with\b", title, re.I):
        return "interview"
    return "other"


def title_candidate(title: str, kind: str) -> str:
    if kind == "concert_review" and " @ " in title:
        return title.split(" @ ", 1)[0].strip()
    if kind == "album_review":
        value = re.sub(r"^album review\s*(?::|[–-])\s*", "", title, flags=re.I)
        return re.split(r"\s+[–-]\s+", value, maxsplit=1)[0].strip()
    if kind == "interview":
        match = re.match(r"^(?:a\s+)?(?:conversation|interview)\s+with\s+(.+?)(?:\s+[–-]\s+|$)", title, re.I)
        return match.group(1).strip() if match else ""
    match = re.match(
        r"^(.+?)\s+(?:announce|announces|release|releases|share|shares|unveil|unveils|return|returns|back|perform|performs|bring|brings|headline|headlines|to\s+(?:celebrate|perform|play|bring|return|release|announce|headline|tour|mark))\b",
        title,
        re.I,
    )
    return match.group(1).strip() if match else ""


def detect_subject(post: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    title = post.get("title") or ""
    labels = post.get("labels") or []
    kind = article_type(title, labels)
    if kind == "playlist":
        return {"taxonomy": "PLAYLIST_MULTI_ARTIST", "name": None, "key": None, "evidence": ["playlist/roundup title or label"]}
    candidate = title_candidate(title, kind)
    structural = {norm(value) for value in registry.get("structuralLabels") or []}
    if not candidate or norm(candidate) in structural:
        return {"taxonomy": "AMBIGUOUS_NO_CLEAR_TITLE", "name": None, "key": None, "evidence": []}
    by_key, by_name = registry_maps(registry)
    matches = by_name.get(norm(candidate)) or []
    if len(matches) == 1:
        artist = matches[0]
        return {
            "taxonomy": "ORDINARY_SINGLE_SUBJECT",
            "name": artist.get("canonicalName") or candidate,
            "key": artist.get("slug") or slug(candidate),
            "evidence": [f"{kind} title structure", f"exact registry identity: {candidate}"],
        }
    if len(matches) > 1:
        return {"taxonomy": "AMBIGUOUS_NO_CLEAR_TITLE", "name": None, "key": None, "evidence": [f"ambiguous exact title identity: {candidate}"]}
    return {
        "taxonomy": "ORDINARY_SINGLE_SUBJECT",
        "name": candidate,
        "key": slug(candidate),
        "evidence": [f"{kind} title structure", "unresolved title-derived artist identity"],
    }


def payload_primary(payload: dict[str, Any] | None) -> list[str]:
    return unique((((payload or {}).get("subject") or {}).get("primaryArtists") or []))


def payload_diagnostics(payload: dict[str, Any] | None) -> dict[str, Any]:
    value = (payload or {}).get("diagnostics") or {}
    return value if isinstance(value, dict) else {}


def payload_items(payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    return [
        item
        for group in ((payload or {}).get("categories") or [])
        for item in (group.get("items") or [])
        if isinstance(item, dict)
    ]


def payload_apple_ids(payload: dict[str, Any] | None) -> list[str]:
    identity = str((((payload or {}).get("identity") or {}).get("artistId") or ""))
    return unique([identity] + [item.get("appleArtistId") for item in payload_items(payload)])


def charli_locations(payload: dict[str, Any] | None, prefix: str) -> list[str]:
    if not payload:
        return []
    found: list[str] = []
    diagnostics = payload_diagnostics(payload)
    for name in payload_primary(payload):
        if norm(name) in CHARLI_NAMES:
            found.append(prefix + ".primaryArtists")
    for field in ("artistKeys", "sourceArtistKeys"):
        if any(norm(value).replace("-", " ") in CHARLI_NAMES for value in diagnostics.get(field) or []):
            found.append(prefix + "." + field)
    for item in payload_items(payload):
        if norm(item.get("creator")) in CHARLI_NAMES:
            found.append(prefix + ".recommendations")
            break
    return unique(found)


def exact_subject_evidence(payload: dict[str, Any], artist_name: str, artist_id: str) -> bool:
    subject = norm(artist_name)
    if not subject:
        return False
    for item in payload_items(payload):
        if norm(item.get("creator")) == subject:
            return True
        text = " ".join(
            str(item.get(key) or "")
            for key in ("title", "description", "relationshipContext", "relevanceReason")
        )
        if re.search(r"(?:^| )" + re.escape(subject) + r"(?: |$)", norm(text)):
            return True
    return False


def relationship_names(subject: str | None, by_name: dict[str, list[dict[str, Any]]]) -> set[str]:
    if not subject:
        return set()
    matches = by_name.get(norm(subject)) or []
    result = {norm(subject)}
    for artist in matches:
        values: list[Any] = []
        for key in ("members", "formerMembers", "associatedActs", "sideProjects", "collaborators", "producers", "songwriters"):
            values.extend(artist.get(key) or [])
        result.update(norm(value) for value in values if norm(value))
    return result


def material_signature(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not payload:
        return None
    return {
        "primaryArtists": [norm(value) for value in payload_primary(payload)],
        "artistId": str(((payload.get("identity") or {}).get("artistId") or "")),
        "categories": [
            {
                "category": str(group.get("category") or "").upper(),
                "items": [
                    str(item.get("stableId") or item.get("url") or item.get("title") or "")
                    for item in group.get("items") or []
                ],
            }
            for group in payload.get("categories") or []
        ],
    }


def historical_recovery_groups(payload_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in payload_rows:
        payload = row.get("payload") or {}
        names = payload_primary(payload)
        identity = payload.get("identity") or {}
        artist_id = str(identity.get("artistId") or "")
        if row.get("status") != "READY" or len(names) != 1 or identity.get("level") != "HIGH" or not artist_id:
            continue
        groups[norm(names[0])].append(row)
    result: dict[str, dict[str, Any]] = {}
    for name, rows in groups.items():
        ids = unique(str((row["payload"].get("identity") or {}).get("artistId") or "") for row in rows)
        if len(ids) != 1:
            continue
        artist_id = ids[0]
        proven = [row for row in rows if exact_subject_evidence(row["payload"], name, artist_id)]
        result[name] = {
            "artistName": payload_primary(rows[0]["payload"])[0],
            "artistKey": slug(name),
            "appleArtistId": artist_id,
            "agreeingRows": len(rows),
            "postIds": unique(row["postId"] for row in rows),
            "exactEvidence": bool(proven),
            "exactEvidencePostIds": unique(row["postId"] for row in proven),
            "legacyPostIds": unique(
                row["postId"]
                for row in rows
                if int(payload_diagnostics(row["payload"]).get("ownershipVersion") or 0) != 2
            ),
        }
    return result


def build_audit(
    posts: list[dict[str, Any]],
    payload_rows: list[dict[str, Any]],
    artist_rows: list[dict[str, Any]],
    registry: dict[str, Any],
    static_payloads: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    payload_rows = [
        item
        for index, row in enumerate(payload_rows)
        if (item := normalize_payload_row(row, index))
    ]
    artist_rows = [
        item
        for index, row in enumerate(artist_rows)
        if (item := normalize_artist_row(row, index))
    ]
    posts_by_id = {post["postId"]: post for post in posts}
    preferred = preferred_payload_rows(payload_rows)
    artist_by_key = {row["artistKey"]: row for row in artist_rows}
    _, by_name = registry_maps(registry)
    historical = historical_recovery_groups(payload_rows)
    all_ids = sorted(set(posts_by_id) | set(preferred) | set(static_payloads), key=lambda value: (not value.isdigit(), value))
    records: list[dict[str, Any]] = []

    for post_id in all_ids:
        post = posts_by_id.get(post_id)
        row = preferred.get(post_id)
        backend = (row or {}).get("payload")
        static = static_payloads.get(post_id)
        exists = post is not None
        if exists:
            detected = detect_subject(post, registry)
        else:
            detected = {"taxonomy": "ORPHAN_DELETED", "name": None, "key": None, "evidence": []}
        taxonomy = detected["taxonomy"]
        current_primary = payload_primary(backend)
        diagnostics = payload_diagnostics(backend)
        current_keys = unique(diagnostics.get("artistKeys") or [])
        source_keys = unique(diagnostics.get("sourceArtistKeys") or [])
        ownership = diagnostics.get("ownershipVersion")
        backend_ids = payload_apple_ids(backend)
        key = detected.get("key")
        catalogue_lookup_key = (current_keys or [key or ""])[0]
        catalogue = artist_by_key.get(catalogue_lookup_key)
        static_primary = payload_primary(static)
        static_ids = payload_apple_ids(static)
        locations = charli_locations(backend, "backend") + charli_locations(static, "static")
        charli_present = bool(locations)
        allowed_relationships = relationship_names(detected.get("name"), by_name)
        charli_legitimate = bool(CHARLI_NAMES & allowed_relationships)
        structural = {norm(value) for value in registry.get("structuralLabels") or []}
        title_suffix = norm((post or {}).get("title", "").split(" @ ", 1)[-1])
        label_names = {norm(value) for value in (post or {}).get("labels") or []}
        title_lead = norm((post or {}).get("title", "").split(" @ ", 1)[0])
        context_values = unique(
            value
            for value in current_primary + [str(v).replace("-", " ") for v in current_keys]
            if norm(value) != norm(detected.get("name"))
            and norm(value) not in allowed_relationships
            and (
                norm(value) in structural
                or (norm(value) and norm(value) in title_suffix)
                or (norm(value) in label_names and norm(value) not in title_lead)
            )
        )
        recovery = historical.get(norm(detected.get("name"))) if detected.get("name") else None
        flags: list[str] = []
        if backend and int(ownership or 0) != 2:
            flags.append("LEGACY_OWNERSHIP")
        if charli_present:
            flags.append("CHARLI_PRESENT")
            if norm(detected.get("name")) not in CHARLI_NAMES and not charli_legitimate:
                flags.append("CHARLI_CONTAMINATION_SUSPECTED")
        if detected.get("name") and current_primary and norm(current_primary[0]) != norm(detected["name"]):
            flags.append("WRONG_PRIMARY_SUSPECTED")
        identity = (backend or {}).get("identity") or {}
        if detected.get("name") and (not backend or identity.get("level") in (None, "", "LOW", "NONE") or not current_primary):
            flags.append("CLEAR_TITLE_UNRESOLVED")
        fallback_modes = {
            str(item.get("recommendationMode") or "") for item in payload_items(backend)
        } | {str(diagnostics.get("recommendationMode") or "")}
        if detected.get("name") and fallback_modes & GENERIC_FALLBACK_MODES:
            flags.append("NAMED_SUBJECT_GENERIC_FALLBACK")
        if catalogue and detected.get("name") and norm(catalogue.get("canonicalName")) != norm(detected["name"]):
            flags.append("CATALOGUE_OWNER_MISMATCH")
        if current_keys and key and current_keys[0] != key:
            flags.append("CATALOGUE_OWNER_MISMATCH")
        if context_values:
            flags.append("CONTEXT_AS_ARTIST")
        if recovery and not recovery["exactEvidence"]:
            flags.append("HISTORICAL_RECOVERY_UNPROVEN")
        should_have_static = bool(row and row.get("status") == "READY" and backend and payload_items(backend))
        if should_have_static and not static:
            flags.append("MISSING_STATIC_PAYLOAD")
        different = bool(backend and static and material_signature(backend) != material_signature(static))
        if static and (
            different
            or context_values
            or "CHARLI_CONTAMINATION_SUSPECTED" in flags
        ):
            flags.append("STATIC_LEGACY_OR_STALE")
        if different:
            flags.append("STATIC_BACKEND_MISMATCH")
        if not exists:
            flags.append("ORPHAN_BLOGGER_NOT_FOUND")
        flags = unique(flags)
        serious = any(flag in SERIOUS_FLAGS for flag in flags)
        if taxonomy == "ORDINARY_SINGLE_SUBJECT" and backend and int(ownership or 0) == 2 and not serious:
            flags.append("HEALTHY_V2")
        if taxonomy == "PLAYLIST_MULTI_ARTIST":
            flags.append("PLAYLIST_MULTI_ARTIST")
        if taxonomy == "AMBIGUOUS_NO_CLEAR_TITLE":
            flags.append("AMBIGUOUS_NO_CLEAR_TITLE")

        if taxonomy in {"PLAYLIST_MULTI_ARTIST", "AMBIGUOUS_NO_CLEAR_TITLE"}:
            action = "DEFER"
        elif taxonomy == "ORPHAN_DELETED":
            action = "REVIEW_ORPHAN"
        elif "HEALTHY_V2" in flags:
            action = "NONE"
        elif flags:
            action = "REVIEW_ORDINARY_REPAIR"
        else:
            action = "NONE"

        records.append({
            "postId": post_id,
            "url": (post or {}).get("url") or (row or {}).get("url") or "",
            "title": (post or {}).get("title") or ((backend or {}).get("subject") or {}).get("title") or "",
            "bloggerExists": exists,
            "backendStatus": (row or {}).get("status"),
            "taxonomy": taxonomy,
            "currentPrimaryArtists": current_primary,
            "currentArtistKeys": current_keys,
            "currentSourceArtistKeys": source_keys,
            "ownershipVersion": ownership,
            "detectedAuthoritativeSubject": detected.get("name"),
            "detectedAuthoritativeArtistKey": key,
            "subjectEvidence": detected.get("evidence") or [],
            "identityConfidence": identity.get("level"),
            "backendAppleArtistIds": backend_ids,
            "catalogueArtistKey": (catalogue or {}).get("artistKey"),
            "catalogueArtistName": (catalogue or {}).get("canonicalName"),
            "catalogueAppleArtistId": (catalogue or {}).get("appleArtistId"),
            "charliPresent": charli_present,
            "charliLocations": unique(locations),
            "contextPromotedAsArtist": bool(context_values),
            "contextArtistValues": context_values,
            "historicalRecoveryCandidate": bool(recovery),
            "historicalRecoveryExactEvidence": recovery.get("exactEvidence") if recovery else None,
            "historicalRecoveryAppleArtistId": recovery.get("appleArtistId") if recovery else None,
            "staticPayloadPresent": static is not None,
            "staticDiagnosticsPresent": bool(payload_diagnostics(static)),
            "staticPrimaryArtists": static_primary,
            "staticAppleArtistIds": static_ids,
            "backendStaticMateriallyDifferent": different,
            "flags": flags,
            "proposedAction": action,
            "notes": [],
        })

    subject_ids: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for record in records:
        subject = record.get("detectedAuthoritativeSubject")
        backend = preferred.get(record["postId"], {}).get("payload") or {}
        ownership_id = str((backend.get("identity") or {}).get("artistId") or "")
        catalogue_id = str(record.get("catalogueAppleArtistId") or "")
        for artist_id in unique([ownership_id, catalogue_id]):
            if subject and artist_id:
                subject_ids[artist_id][norm(subject)].add(record["postId"])
    id_collisions = []
    suspicious_ids: set[str] = set()
    for artist_id, subjects in sorted(subject_ids.items()):
        if len(subjects) < 2:
            continue
        suspicious_ids.add(artist_id)
        id_collisions.append({
            "appleArtistId": artist_id,
            "authoritativeSubjects": sorted(subjects),
            "postIds": sorted({post_id for ids in subjects.values() for post_id in ids}),
            "suspicious": True,
        })
    for record in records:
        if suspicious_ids & set(record.get("backendAppleArtistIds") or []):
            if "SHARED_SUSPICIOUS_APPLE_ID" not in record["flags"]:
                record["flags"].append("SHARED_SUSPICIOUS_APPLE_ID")
            if "HEALTHY_V2" in record["flags"]:
                record["flags"].remove("HEALTHY_V2")
            if record["taxonomy"] == "ORDINARY_SINGLE_SUBJECT":
                record["proposedAction"] = "REVIEW_ORDINARY_REPAIR"

    context_counts: dict[str, set[str]] = defaultdict(set)
    for record in records:
        for value in record["contextArtistValues"]:
            context_counts[norm(value)].add(record["postId"])
    artist_key_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in artist_rows:
        artist_key_groups[row["artistKey"]].append(row)
    artist_key_collisions = [
        {
            "artistKey": key,
            "canonicalNames": unique(row.get("canonicalName") for row in rows),
            "appleArtistIds": unique(row.get("appleArtistId") for row in rows),
            "rowNumbers": [row["rowNumber"] for row in rows],
            "contextLike": norm(key.replace("-", " ")) in {norm(value) for value in registry.get("structuralLabels") or []},
        }
        for key, rows in sorted(artist_key_groups.items())
        if len(rows) > 1 or len(unique(row.get("canonicalName") for row in rows)) > 1
        or norm(key.replace("-", " ")) in {norm(value) for value in registry.get("structuralLabels") or []}
    ]
    backend_ids = set(preferred)
    blogger_ids = set(posts_by_id)
    static_ids = set(static_payloads)
    static_gaps = {
        "backendValidStaticMissing": sorted(
            record["postId"] for record in records if "MISSING_STATIC_PAYLOAD" in record["flags"]
        ),
        "backendStaticMateriallyDivergent": sorted(
            record["postId"] for record in records if record["backendStaticMateriallyDifferent"]
        ),
        "staticOnly": sorted(static_ids - backend_ids - blogger_ids),
    }
    flag_counts: dict[str, int] = defaultdict(int)
    taxonomy_counts: dict[str, int] = defaultdict(int)
    status_counts: dict[str, int] = defaultdict(int)
    for record in records:
        taxonomy_counts[record["taxonomy"]] += 1
        status_counts[str(record["backendStatus"] or "MISSING")] += 1
        for flag in record["flags"]:
            flag_counts[flag] += 1
    assert set(taxonomy_counts) <= TAXONOMIES
    return {
        "schemaVersion": 1,
        "readOnly": True,
        "records": records,
        "summary": {
            "totalRecords": len(records),
            "bloggerPosts": len(posts_by_id),
            "backendPostIds": len(preferred),
            "staticPayloads": len(static_payloads),
            "taxonomyCounts": dict(sorted(taxonomy_counts.items())),
            "backendStatusCounts": dict(sorted(status_counts.items())),
            "flagCounts": dict(sorted(flag_counts.items())),
        },
        "appleArtistIdCollisions": id_collisions,
        "artistKeyCollisions": artist_key_collisions,
        "historicalRecoveryRisk": [value for value in historical.values() if not value["exactEvidence"]],
        "contextPromotion": [
            {"value": value, "postIds": sorted(ids), "count": len(ids)}
            for value, ids in sorted(context_counts.items(), key=lambda item: (-len(item[1]), item[0]))
        ],
        "staticPublicationGaps": static_gaps,
    }


CSV_FIELDS = [
    "postId", "url", "title", "bloggerExists", "backendStatus", "taxonomy",
    "currentPrimaryArtists", "currentArtistKeys", "currentSourceArtistKeys",
    "ownershipVersion", "detectedAuthoritativeSubject", "detectedAuthoritativeArtistKey",
    "subjectEvidence", "identityConfidence", "backendAppleArtistIds",
    "catalogueArtistKey", "catalogueArtistName", "catalogueAppleArtistId",
    "charliPresent", "charliLocations", "contextPromotedAsArtist", "contextArtistValues",
    "historicalRecoveryCandidate", "historicalRecoveryExactEvidence",
    "historicalRecoveryAppleArtistId", "staticPayloadPresent", "staticDiagnosticsPresent",
    "staticPrimaryArtists", "staticAppleArtistIds", "backendStaticMateriallyDifferent",
    "flags", "proposedAction", "notes",
]


def write_outputs(audit: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "apple-archive-ownership-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "apple-archive-ownership-summary.json").write_text(
        json.dumps(
            {key: value for key, value in audit.items() if key != "records"},
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    with (output_dir / "apple-archive-ownership-audit.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for record in audit["records"]:
            writer.writerow({
                field: json.dumps(record.get(field), ensure_ascii=False, separators=(",", ":"))
                if isinstance(record.get(field), (list, dict)) else record.get(field)
                for field in CSV_FIELDS
            })


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--backend-snapshot", type=Path, required=True)
    value.add_argument("--blogger-feed", type=Path, help="Saved Blogger JSON feed; omit for a read-only live fetch")
    value.add_argument("--artist-index", type=Path, default=Path("output/automation/artist-index.json"))
    value.add_argument("--static-root", type=Path, default=Path("../idf_concert_calendar-gh-pages/proof"))
    value.add_argument("--output-dir", type=Path, default=Path("output/audits"))
    return value


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    payload_rows, artist_rows = load_backend_snapshot(args.backend_snapshot)
    audit = build_audit(
        load_blogger_posts(args.blogger_feed),
        payload_rows,
        artist_rows,
        artist_registry(args.artist_index),
        load_static_payloads(args.static_root),
    )
    write_outputs(audit, args.output_dir)
    print(json.dumps({"status": "OK", **audit["summary"]}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
