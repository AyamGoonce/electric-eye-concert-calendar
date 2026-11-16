"""Read-only release audit for genre provenance, accounting and identity continuity."""
from __future__ import annotations

from collections import Counter


BLANK_REASONS = (
    "blank_no_raw", "blank_unresolved_raw", "blank_festival",
    "blank_unresolved_taxonomy", "conflict_count",
)
EVIDENCE_METHODS = {
    "source_explicit", "source_mapping", "artist_mapping", "manual_override",
    "event_context", "bill_consensus", "artist_source_consensus",
    "editorial_reviewed_identity", "editorial_article_consensus",
}


def genre_release_audit(events, genre_report: dict, candidate: list[dict],
                        published: list[dict] | None = None) -> dict:
    """Audit the exact enriched records and public export; never infer genres.

    Baseline comparisons are advisory: a disappearing or changed source event
    may be legitimate. Corrupt internal accounting, however, is a hard error.
    """
    total = len(events)
    populated = sum(bool(e.genre_public) for e in events)
    blanks = total - populated
    reasons = {reason: int(genre_report.get(reason, 0)) for reason in BLANK_REASONS}
    if (
        genre_report.get("total") != total
        or genre_report.get("populated") != populated
        or genre_report.get("blank") != blanks
        or any(value < 0 for value in reasons.values())
        or sum(reasons.values()) != blanks
    ):
        raise ValueError(
            "Genre accounting mismatch: event totals, blank reasons or "
            "post-enrichment diagnostics are inconsistent"
        )

    by_method = Counter()
    provenance_defects = []
    for e in events:
        if not e.genre_public:
            continue
        method = e.genre_method
        by_method[method or "missing_method"] += 1
        valid = method in EVIDENCE_METHODS
        if method in {"source_explicit", "source_mapping"}:
            valid = valid and bool(e.genre_evidence)
        elif method in {"artist_mapping", "manual_override", "event_context",
                        "bill_consensus", "artist_source_consensus",
                        "editorial_reviewed_identity", "editorial_article_consensus"}:
            valid = valid and bool(e.genre_source)
        if not valid and len(provenance_defects) < 100:
            provenance_defects.append({
                "artist": e.headliner, "date": e.date[:10],
                "genre": e.genre_public, "method": method,
                "source": e.genre_source,
            })

    prior = {row["i"]: row for row in (published or []) if row.get("i")}
    current = {row["i"]: row for row in candidate if row.get("i")}
    same = set(prior) & set(current)
    losses = []
    billing_changes = []
    for identifier in sorted(same):
        before, after = prior[identifier], current[identifier]
        if before.get("x") and not after.get("x"):
            if len(losses) < 100:
                losses.append({
                    "id": identifier, "artist": after.get("h"),
                    "previous": before.get("x"),
                })
        old_bill = (before.get("h"), before.get("ch") or [], before.get("o") or [])
        new_bill = (after.get("h"), after.get("ch") or [], after.get("o") or [])
        if old_bill != new_bill and len(billing_changes) < 100:
            billing_changes.append({
                "id": identifier, "before": old_bill, "after": new_bill,
            })

    return {
        "total": total,
        "populated": populated,
        "blank": blanks,
        "blank_reasons": reasons,
        "method_counts": dict(sorted(by_method.items())),
        "provenance_defects": provenance_defects,
        "baseline_comparable_ids": len(same),
        "genre_losses_on_retained_ids": losses,
        "billing_changes_on_retained_ids": billing_changes,
        "baseline_only_ids": len(set(prior) - set(current)),
        "candidate_only_ids": len(set(current) - set(prior)),
        "policy": (
            "inconsistent genre accounting rejects publication; provenance "
            "defects and baseline identity/coverage changes are reported "
            "for review rather than automatically overwritten"
        ),
    }
