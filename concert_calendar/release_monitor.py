"""Advisory Phase 4 publication quality monitoring.

Quality heuristics are never gates: the existing validation and hosted
verification workflows remain the only publication/rollback authorities.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _count(report: dict, *keys: str) -> int:
    current = report
    for key in keys:
        current = current.get(key, {}) if isinstance(current, dict) else {}
    return int(current) if isinstance(current, (int, float)) else 0


def build_monitoring_report(report: dict) -> dict:
    """Summarize a single candidate against its same-ID published baseline.

    Counts from individual examples are capped in the release audit; never
    interpret those example lengths as complete population counts.
    """
    quality = report.get("reconciliation_quality") or {}
    acceptance = report.get("genre_acceptance") or {}
    genre = report.get("genre_report") or {}
    comparable = _count(acceptance, "baseline_comparable_ids")
    blank = _count(genre, "blank")
    total = _count(genre, "total")
    loss_examples = acceptance.get("genre_losses_on_retained_ids") or []
    billing_examples = acceptance.get("billing_changes_on_retained_ids") or []
    provenance_examples = acceptance.get("provenance_defects") or []
    flat = _count(quality, "possible_flat_bill", "count")
    titles = _count(quality, "possible_programme_as_artist", "count")
    alerts = []

    def add(code, severity, detail):
        alerts.append({"code": code, "severity": severity, "detail": detail})

    if provenance_examples:
        add("genre_provenance", "investigate",
            f"{len(provenance_examples)} genre classification provenance examples need inspection")
    if comparable >= 100 and len(loss_examples) >= max(5, int(comparable * 0.01)):
        add("genre_loss", "investigate",
            f"{len(loss_examples)} retained event IDs lost their previously published genre")
    elif loss_examples:
        add("genre_loss", "review",
            f"{len(loss_examples)} retained event IDs lost their previously published genre")
    if comparable >= 100 and len(billing_examples) >= max(10, int(comparable * 0.02)):
        add("billing_churn", "investigate",
            f"{len(billing_examples)} retained event IDs changed performer billings")
    elif billing_examples:
        add("billing_churn", "review",
            f"{len(billing_examples)} retained event IDs changed performer billings")
    if flat >= 100:
        add("flat_bill_review_queue", "review",
            f"{flat} possible flattened bills; these are candidates, not confirmed errors")
    if titles >= 50:
        add("programme_title_review_queue", "review",
            f"{titles} possible programme-title identities; these are candidates, not confirmed errors")
    if total and blank * 2 > total:
        add("low_genre_coverage", "investigate",
            f"{blank}/{total} events have no verified genre")

    return {
        "status": "investigate" if any(a["severity"] == "investigate" for a in alerts)
                  else ("review" if alerts else "normal"),
        "published_at": report.get("published_at"),
        "event_count": report.get("event_count"),
        "source_revision": report.get("source_revision"),
        "metrics": {
            "genre_populated": _count(genre, "populated"),
            "genre_blank": blank,
            "genre_coverage_percentage": genre.get("coverage_percentage"),
            "genre_conflicts": _count(genre, "conflict_count"),
            "blank_reasons": acceptance.get("blank_reasons") or {},
            "provenance_defect_examples": len(provenance_examples),
            "comparable_prior_event_ids": comparable,
            "genre_loss_examples": len(loss_examples),
            "billing_change_examples": len(billing_examples),
            "possible_flat_bills": flat,
            "possible_programme_title_identities": titles,
            "new_event_ids": _count(acceptance, "candidate_only_ids"),
            "missing_prior_event_ids": _count(acceptance, "baseline_only_ids"),
        },
        "alerts": alerts,
        "examples": {
            "genre_losses": loss_examples[:20],
            "billing_changes": billing_examples[:20],
            "provenance_defects": provenance_examples[:20],
        },
        "note": (
            "Advisory monitoring only. Example lists are capped by the release "
            "audit and may not represent complete counts. Heuristics do not "
            "automatically classify or reject concerts."
        ),
    }


def markdown_summary(monitor: dict) -> str:
    m = monitor["metrics"]
    output = [
        "## Phase 4 — release quality monitoring",
        "",
        f"- Monitoring status: **{monitor['status']}** (advisory)",
        f"- Concerts: {monitor['event_count']}",
        f"- Genres: {m['genre_populated']} populated, {m['genre_blank']} blank ({m['genre_coverage_percentage']}% coverage)",
        f"- Retained IDs compared: {m['comparable_prior_event_ids']}",
        f"- Genre loss examples: {m['genre_loss_examples']}",
        f"- Billing change examples: {m['billing_change_examples']}",
        f"- Genre provenance defects: {m['provenance_defect_examples']}",
        f"- Review queue: {m['possible_flat_bills']} flat bills; {m['possible_programme_title_identities']} programme-title candidates",
        "",
    ]
    if monitor["alerts"]:
        output.append("### Follow-up alerts")
        output.extend(
            f"- **{row['severity']} / {row['code']}** — {row['detail']}"
            for row in monitor["alerts"]
        )
    else:
        output.append("No threshold alerts in this publication.")
    output.append("")
    output.append("Monitoring does not override publication or rollback safeguards.")
    return "\n".join(output) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Non-blocking calendar release audit")
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--json-output", required=True, type=Path)
    parser.add_argument("--markdown-output", required=True, type=Path)
    args = parser.parse_args(argv)
    report = json.loads(args.report.read_text(encoding="utf-8"))
    monitoring = build_monitoring_report(report)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(monitoring, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown_summary(monitoring), encoding="utf-8")
    print(f"QUALITY MONITOR | status={monitoring['status']} alerts={len(monitoring['alerts'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
