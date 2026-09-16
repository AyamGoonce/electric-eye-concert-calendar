#!/usr/bin/env python3
"""Build a read-only Apple archive repair plan from captured audit evidence."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = ROOT / "scripts" / "audit_apple_archive_ownership.py"
SPEC = importlib.util.spec_from_file_location("apple_archive_audit", AUDIT_SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(audit)

CATEGORIES = ("LISTEN", "WATCH", "READ")
CONTAMINATION_FLAGS = {
    "WRONG_PRIMARY_SUSPECTED": "WRONG_PRIMARY",
    "CATALOGUE_OWNER_MISMATCH": "CATALOGUE_OWNER_MISMATCH",
    "CONTEXT_AS_ARTIST": "CONTEXT_PROMOTED_AS_ARTIST",
    "CHARLI_CONTAMINATION_SUSPECTED": "CHARLI_CONTAMINATION",
    "SHARED_SUSPICIOUS_APPLE_ID": "SUSPICIOUS_SHARED_APPLE_ID",
    "HISTORICAL_RECOVERY_UNPROVEN": "UNPROVEN_HISTORICAL_RECOVERY",
}


def repair_eligibility(evidence: dict[str, Any]) -> dict[str, Any]:
    """Python mirror of eeArchiveRepairEligibility_ plus no-payload Tier C."""
    if (
        evidence.get("taxonomy") != "ORDINARY_SINGLE_SUBJECT"
        or evidence.get("bloggerExists") is False
        or not evidence.get("authoritativeSubject")
        or not evidence.get("authoritativeArtistKey")
        or evidence.get("identityConfidence") != "HIGH"
    ):
        return {"tier": "D", "reasons": ["DEFERRED_NON_ORDINARY_OR_AMBIGUOUS"]}
    if not evidence.get("hasRecommendations"):
        return {"tier": "C", "reasons": ["NO_READY_RECOMMENDATION_PAYLOAD"]}
    reasons = [label for key, label in (
        ("wrongPrimary", "WRONG_PRIMARY"),
        ("catalogueOwnerMismatch", "CATALOGUE_OWNER_MISMATCH"),
        ("contextPromotedAsArtist", "CONTEXT_PROMOTED_AS_ARTIST"),
        ("charliContamination", "CHARLI_CONTAMINATION"),
        ("suspiciousSharedAppleId", "SUSPICIOUS_SHARED_APPLE_ID"),
        ("unprovenHistoricalRecovery", "UNPROVEN_HISTORICAL_RECOVERY"),
    ) if evidence.get(key)]
    if reasons:
        return {"tier": "A", "reasons": reasons}
    if not all((
        evidence.get("cataloguePresent"), evidence.get("catalogueResolved"),
        evidence.get("catalogueArtistKey"), evidence.get("catalogueArtistName"),
        evidence.get("catalogueAppleArtistId"),
    )):
        return {"tier": "C", "reasons": ["CATALOGUE_UNRESOLVED"]}
    if (
        audit.norm(evidence.get("authoritativeSubject")) != audit.norm(evidence.get("catalogueArtistName"))
        or evidence.get("authoritativeArtistKey") != evidence.get("catalogueArtistKey")
        or not evidence.get("payloadAppleArtistId")
        or str(evidence.get("payloadAppleArtistId")) != str(evidence.get("catalogueAppleArtistId"))
        or evidence.get("catalogueValid") is not True
        or evidence.get("exactSubjectEvidence") is not True
    ):
        return {"tier": "A", "reasons": ["INDEPENDENT_IDENTITY_EVIDENCE_INCOMPLETE_OR_CONFLICTING"]}
    return {"tier": "B", "reasons": ["INDEPENDENT_HEALTHY_LEGACY_IDENTITY"]}


def category_items(payload: dict[str, Any] | None) -> dict[str, list[dict[str, Any]]]:
    result = {category: [] for category in CATEGORIES}
    for group in (payload or {}).get("categories") or []:
        category = str(group.get("category") or "").upper()
        if category in result:
            result[category].extend(item for item in group.get("items") or [] if isinstance(item, dict))
    return result


def text_has_name(item: dict[str, Any], name: str) -> bool:
    needle = audit.norm(name)
    text = audit.norm(" ".join(str(item.get(key) or "") for key in (
        "title", "description", "relationshipContext", "relevanceReason",
    )))
    return bool(needle and f" {needle} " in f" {text} ")


def relationship_reason(item: dict[str, Any]) -> bool:
    text = audit.norm(" ".join(str(item.get(key) or "") for key in ("relationshipContext", "relevanceReason")))
    return any(phrase in text for phrase in (
        " member of the primary artist", " former member of the primary artist",
        " associated with the primary artist", " collaborator with the primary artist",
        " side project of the primary artist",
    ))


def preserve_items(
    payload: dict[str, Any] | None,
    subject: str | None,
    catalogue_id: str,
    catalogue_trusted: bool,
    relationships: set[str],
) -> tuple[dict[str, list[dict[str, Any]]], int, int, int]:
    kept = {category: [] for category in CATEGORIES}
    exact = relationship = rejected = 0
    subject_norm = audit.norm(subject)
    for category, items in category_items(payload).items():
        for item in items:
            creator = audit.norm(item.get("creator"))
            artist_id = str(item.get("appleArtistId") or item.get("collectionArtistId") or "")
            provenance = str(item.get("recommendationProvenance") or "")
            is_exact = bool(
                subject_norm and (
                    creator == subject_norm
                    or text_has_name(item, subject_norm)
                    or provenance == "EXACT_SUBJECT"
                    or (catalogue_trusted and catalogue_id and artist_id == catalogue_id)
                )
            )
            is_relationship = bool(
                not is_exact and creator and creator != subject_norm
                and (creator in relationships or relationship_reason(item))
            )
            if is_exact or is_relationship:
                kept[category].append(item)
                exact += int(is_exact)
                relationship += int(is_relationship)
            else:
                rejected += 1
    return kept, exact, relationship, rejected


def content_loss_class(current: int, preserved: int) -> str:
    if current == 0 or preserved == current:
        return "NO_ITEM_LOSS"
    if preserved == 0:
        return "TOTAL_REBUILD"
    loss = (current - preserved) / current
    return "MINOR_ITEM_LOSS" if loss <= 0.25 else "SUBSTANTIAL_ITEM_LOSS"


def build_plan(
    ownership_audit: dict[str, Any],
    payload_rows: list[dict[str, Any]],
    artist_rows: list[dict[str, Any]],
    registry: dict[str, Any],
) -> dict[str, Any]:
    preferred = audit.preferred_payload_rows(payload_rows)
    physical: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in payload_rows:
        physical[row["postId"]].append(row)
    artists = {row["artistKey"]: row for row in artist_rows}
    _, by_name = audit.registry_maps(registry)
    records = []

    for source in ownership_audit["records"]:
        post_id = source["postId"]
        row = preferred.get(post_id)
        payload = (row or {}).get("payload") or {}
        items = category_items(payload)
        current_counts = {category: len(items[category]) for category in CATEGORIES}
        has_recommendations = sum(current_counts.values()) > 0 and (row or {}).get("status") == "READY"
        subject = source.get("detectedAuthoritativeSubject")
        subject_key = source.get("detectedAuthoritativeArtistKey")
        current_primary = source.get("currentPrimaryArtists") or []
        current_keys = source.get("currentArtistKeys") or []
        flags = set(source.get("flags") or [])
        title_text = f" {audit.norm(source.get('title'))} "
        stored_subject_corroborated = bool(
            len(current_primary) == 1 and len(current_keys) == 1
            and f" {audit.norm(current_primary[0])} " in title_text
            and audit.norm(source.get("catalogueArtistName")) == audit.norm(current_primary[0])
            and source.get("catalogueArtistKey") == current_keys[0]
        )
        if stored_subject_corroborated:
            subject, subject_key = current_primary[0], current_keys[0]
            flags.difference_update({
                "WRONG_PRIMARY_SUSPECTED", "CATALOGUE_OWNER_MISMATCH", "CONTEXT_AS_ARTIST",
            })
        catalogue = artists.get(str(source.get("catalogueArtistKey") or subject_key or ""))
        catalogue_id = str(source.get("catalogueAppleArtistId") or "")
        payload_id = str((payload.get("identity") or {}).get("artistId") or "")
        catalogue_matches = bool(
            catalogue
            and catalogue.get("status") == "RESOLVED"
            and subject
            and audit.norm(catalogue.get("canonicalName")) == audit.norm(subject)
            and catalogue.get("artistKey") == subject_key
            and catalogue_id
        )
        catalogue_evidence = bool(
            catalogue_matches
            and audit.exact_subject_evidence(
                {"categories": ((catalogue or {}).get("catalogue") or {}).get("categories") or []},
                str(subject or ""), catalogue_id,
            )
        )
        exact_evidence = bool(source.get("historicalRecoveryExactEvidence")) or audit.exact_subject_evidence(
            payload, str(subject or ""), payload_id
        )
        suspicious_identity = bool(flags & {
            "CATALOGUE_OWNER_MISMATCH", "HISTORICAL_RECOVERY_UNPROVEN",
        })
        trusted_catalogue = bool(catalogue_matches and catalogue_evidence and not suspicious_identity)
        evidence = {
            "taxonomy": source.get("taxonomy"), "bloggerExists": source.get("bloggerExists"),
            "authoritativeSubject": subject, "authoritativeArtistKey": subject_key,
            "identityConfidence": "HIGH" if stored_subject_corroborated else (source.get("identityConfidence") or ("HIGH" if subject else "")),
            "hasRecommendations": has_recommendations,
            "cataloguePresent": bool(catalogue), "catalogueResolved": bool(catalogue and catalogue.get("status") == "RESOLVED"),
            "catalogueArtistKey": (catalogue or {}).get("artistKey"),
            "catalogueArtistName": (catalogue or {}).get("canonicalName"),
            "catalogueAppleArtistId": catalogue_id, "payloadAppleArtistId": payload_id,
            "catalogueValid": catalogue_matches and catalogue_evidence,
            "exactSubjectEvidence": exact_evidence,
        }
        evidence.update({
            "wrongPrimary": "WRONG_PRIMARY_SUSPECTED" in flags,
            "catalogueOwnerMismatch": "CATALOGUE_OWNER_MISMATCH" in flags,
            "contextPromotedAsArtist": "CONTEXT_AS_ARTIST" in flags,
            "charliContamination": "CHARLI_CONTAMINATION_SUSPECTED" in flags,
            "suspiciousSharedAppleId": "SHARED_SUSPICIOUS_APPLE_ID" in flags,
            "unprovenHistoricalRecovery": "HISTORICAL_RECOVERY_UNPROVEN" in flags,
        })
        classification = (
            {"tier": "B", "reasons": ["HEALTHY_OWNERSHIP_V2"]}
            if int(source.get("ownershipVersion") or 0) == 2 and "HEALTHY_V2" in flags
            else repair_eligibility(evidence)
        )
        tier = classification["tier"]
        relationships = audit.relationship_names(subject, by_name)
        kept, exact_count, relationship_count, rejected = preserve_items(
            payload, subject, catalogue_id, trusted_catalogue, relationships
        )
        preserved_counts = {category: len(kept[category]) for category in CATEGORIES}
        current_total = sum(current_counts.values())
        preserved_total = sum(preserved_counts.values())
        ownership_version = source.get("ownershipVersion")

        if source.get("taxonomy") == "ORPHAN_DELETED":
            ownership_action, catalogue_action, content_action, static_action = (
                "ORPHAN_NO_ACTION", "DEFER", "DEFER", "DEFER"
            )
        elif tier == "D":
            ownership_action, catalogue_action, content_action, static_action = "DEFER", "DEFER", "DEFER", "DEFER"
            preserved_counts = current_counts.copy()
            preserved_total = current_total
            exact_count = current_total
            relationship_count = rejected = 0
        elif int(ownership_version or 0) == 2 and "HEALTHY_V2" in flags:
            ownership_action, catalogue_action = "KEEP_V2", "KEEP_CURRENT_V2"
            content_action = "PRESERVE_ALL_VALIDATED_CONTENT"
            static_action = "STATIC_CREATE_EXPECTED" if not source.get("staticPayloadPresent") else "NO_STATIC_CHANGE_EXPECTED"
            preserved_counts = current_counts.copy()
            preserved_total = current_total
            exact_count = current_total
            relationship_count = rejected = 0
        else:
            if tier == "B":
                ownership_action, catalogue_action = "MIGRATE_LEGACY_OWNERSHIP", "REUSE_TRUSTED_CATALOGUE"
            elif tier == "C":
                ownership_action = "RESOLVE_MISSING_CATALOGUE"
                catalogue_action = "REUSE_TRUSTED_CATALOGUE" if trusted_catalogue else "RESOLVE_MISSING_CATALOGUE"
            else:
                ownership_action = "MIGRATE_LEGACY_OWNERSHIP" if trusted_catalogue else "RERESOLVE_ARTIST_IDENTITY"
                catalogue_action = "REUSE_TRUSTED_CATALOGUE" if trusted_catalogue else "RERESOLVE_CATALOGUE"
            if not current_total:
                content_action = "NO_EXISTING_CONTENT"
            elif preserved_total == current_total:
                content_action = "PRESERVE_ALL_VALIDATED_CONTENT"
            elif preserved_total:
                content_action = "PRESERVE_VALIDATED_ITEMS_REBUILD_OWNERSHIP"
            else:
                content_action = "REBUILD_RECOMMENDATIONS"
            static_action = "STATIC_CREATE_EXPECTED" if not source.get("staticPayloadPresent") else "STATIC_REWRITE_EXPECTED"

        loss = content_loss_class(current_total, preserved_total)
        warnings = []
        if current_total >= 8 and loss in {"SUBSTANTIAL_ITEM_LOSS", "TOTAL_REBUILD"}:
            warnings.append("CONTENT_PRESERVATION_REVIEW")
        duplicate_rows = physical.get(post_id) or []
        duplicate_disagree = len({json.dumps(audit.material_signature(r.get("payload")), sort_keys=True) for r in duplicate_rows}) > 1
        records.append({
            "postId": post_id, "url": source.get("url"), "title": source.get("title"),
            "taxonomy": source.get("taxonomy"), "backendStatus": source.get("backendStatus"),
            "ownershipVersion": ownership_version, "authoritativeSubject": subject,
            "authoritativeArtistKey": subject_key, "currentPrimaryArtists": source.get("currentPrimaryArtists") or [],
            "currentArtistKeys": source.get("currentArtistKeys") or [],
            "currentSourceArtistKeys": source.get("currentSourceArtistKeys") or [],
            "currentAppleArtistIds": source.get("backendAppleArtistIds") or [],
            "catalogueArtistKey": source.get("catalogueArtistKey"), "catalogueArtistName": source.get("catalogueArtistName"),
            "catalogueAppleArtistId": source.get("catalogueAppleArtistId"),
            "repairTier": tier, "repairTierReasons": classification["reasons"],
            "ownershipAction": ownership_action, "catalogueAction": catalogue_action,
            "contentAction": content_action, "staticAction": static_action,
            "currentListenCount": current_counts["LISTEN"], "preservableListenCount": preserved_counts["LISTEN"],
            "currentWatchCount": current_counts["WATCH"], "preservableWatchCount": preserved_counts["WATCH"],
            "currentReadCount": current_counts["READ"], "preservableReadCount": preserved_counts["READ"],
            "preservableExactItemCount": exact_count, "preservableRelationshipItemCount": relationship_count,
            "rejectedContaminatedItemCount": rejected,
            "requiresAppleResolution": catalogue_action in {"RERESOLVE_CATALOGUE", "RESOLVE_MISSING_CATALOGUE"},
            "requiresRecommendationRegeneration": content_action in {"REBUILD_RECOMMENDATIONS", "NO_EXISTING_CONTENT"},
            "duplicatePhysicalRowCount": len(duplicate_rows),
            "selectedCanonicalRowNumber": (row or {}).get("rowNumber"),
            "duplicateRowsDisagree": duplicate_disagree,
            "currentStaticPresent": bool(source.get("staticPayloadPresent")),
            "contentLossClass": loss, "warnings": warnings,
            "notes": (["Trusted catalogue may be reused while legacy ownership is corrected."] if tier == "A" and trusted_catalogue else []),
        })

    return {"schemaVersion": 1, "readOnly": True, "records": records, "summary": summarize(records, ownership_audit)}


def summarize(records: list[dict[str, Any]], ownership_audit: dict[str, Any]) -> dict[str, Any]:
    count = lambda key: dict(sorted(Counter(str(r.get(key)) for r in records).items()))
    content = {}
    for category, prefix in (("LISTEN", "Listen"), ("WATCH", "Watch"), ("READ", "Read")):
        current = sum(r[f"current{prefix}Count"] for r in records)
        preserved = sum(r[f"preservable{prefix}Count"] for r in records)
        content[category] = {"current": current, "preservable": preserved, "rejected": current - preserved}
    ordinary = [r for r in records if r["taxonomy"] == "ORDINARY_SINGLE_SUBJECT"]
    historical = ownership_audit.get("historicalRecoveryRisk") or []
    risky_posts = {post for group in historical for post in group.get("postIds") or []}
    risky_records = [r for r in records if r["postId"] in risky_posts]
    return {
        "totalUniquePosts": len(records), "tierCounts": count("repairTier"),
        "ownershipActionCounts": count("ownershipAction"), "catalogueActionCounts": count("catalogueAction"),
        "contentActionCounts": count("contentAction"), "staticActionCounts": count("staticAction"),
        "appleResolutionPostCount": sum(r["requiresAppleResolution"] for r in records),
        "noRediscoveryMigrationCount": sum(r["ownershipAction"] == "MIGRATE_LEGACY_OWNERSHIP" and not r["requiresAppleResolution"] for r in records),
        "recommendationRebuildCount": sum(r["requiresRecommendationRegeneration"] for r in records),
        "fullyPreservablePostCount": sum(r["contentAction"] == "PRESERVE_ALL_VALIDATED_CONTENT" for r in records),
        "partiallyPreservablePostCount": sum(r["contentAction"] == "PRESERVE_VALIDATED_ITEMS_REBUILD_OWNERSHIP" for r in records),
        "contentPreservation": content, "contentLossClassCounts": count("contentLossClass"),
        "contentPreservationReviewCount": sum("CONTENT_PRESERVATION_REVIEW" in r["warnings"] for r in records),
        "ordinaryPopulation": {
            "total": len(ordinary), "healthyV2": sum(r["ownershipAction"] == "KEEP_V2" for r in ordinary),
            "tierB": sum(r["repairTier"] == "B" for r in ordinary),
            "tierAReusableCatalogue": sum(r["repairTier"] == "A" and r["catalogueAction"] == "REUSE_TRUSTED_CATALOGUE" for r in ordinary),
            "tierARequiringCatalogueResolution": sum(r["repairTier"] == "A" and r["requiresAppleResolution"] for r in ordinary),
            "tierC": sum(r["repairTier"] == "C" for r in ordinary),
            "blockedOrDeferred": sum(r["repairTier"] == "D" for r in ordinary),
        },
        "historicalRecoveryEffect": {
            "unprovenIdentityGroupCount": len(historical), "affectedPostCount": len(risky_posts),
            "repairableWithIndependentCatalogueCount": sum(r["catalogueAction"] == "REUSE_TRUSTED_CATALOGUE" for r in risky_records),
            "requiresResolutionCount": sum(r["requiresAppleResolution"] for r in risky_records),
        },
        "duplicatePostCount": sum(r["duplicatePhysicalRowCount"] > 1 for r in records),
        "duplicateDisagreementCount": sum(r["duplicateRowsDisagree"] for r in records),
    }


FIELDS = [
    "postId", "url", "title", "taxonomy", "backendStatus", "ownershipVersion", "authoritativeSubject",
    "authoritativeArtistKey", "currentPrimaryArtists", "currentArtistKeys", "currentSourceArtistKeys",
    "currentAppleArtistIds", "catalogueArtistKey", "catalogueArtistName", "catalogueAppleArtistId",
    "repairTier", "repairTierReasons", "ownershipAction", "catalogueAction", "contentAction", "staticAction",
    "currentListenCount", "preservableListenCount", "currentWatchCount", "preservableWatchCount",
    "currentReadCount", "preservableReadCount", "preservableExactItemCount", "preservableRelationshipItemCount",
    "rejectedContaminatedItemCount", "requiresAppleResolution", "requiresRecommendationRegeneration",
    "duplicatePhysicalRowCount", "selectedCanonicalRowNumber", "duplicateRowsDisagree", "currentStaticPresent",
    "contentLossClass", "warnings", "notes",
]


def write_outputs(plan: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "apple-archive-repair-dry-run.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
    with (output_dir / "apple-archive-repair-dry-run.csv").open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS)
        writer.writeheader()
        for record in plan["records"]:
            writer.writerow({key: json.dumps(record.get(key), ensure_ascii=False, separators=(",", ":")) if isinstance(record.get(key), (list, dict)) else record.get(key) for key in FIELDS})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ownership-audit", type=Path, required=True)
    parser.add_argument("--backend-snapshot", type=Path, required=True)
    parser.add_argument("--artist-index", type=Path, default=Path("output/automation/artist-index.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("output/audits"))
    args = parser.parse_args(argv)
    ownership = json.loads(args.ownership_audit.read_text())
    payload_rows, artist_rows = audit.load_backend_snapshot(args.backend_snapshot)
    plan = build_plan(ownership, payload_rows, artist_rows, audit.artist_registry(args.artist_index))
    write_outputs(plan, args.output_dir)
    print(json.dumps({"status": "OK", **plan["summary"]}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
