# Phase 4 — publication quality monitoring

Phase 4 observes the production candidate **after the existing publication verification has passed**. It does not alter scraping, genre inference, artist identities, publication acceptance, or rollback decisions.

Every successful publication generates two additional diagnostics files within the existing 30-day GitHub Actions report artifact:

- `quality-monitor.json`: machine-readable measurements, severity, advisory alerts, and up to 20 examples of each change type.
- `quality-monitor.md`: a concise human-readable summary appended to the GitHub Actions run summary.

The quality monitor uses the already-computed `automation-report.json`. It compares only matching published event IDs and includes counts for genre gaps, evidence provenance, genre losses, billing changes and unresolved billing/title review queues. The monitoring indicators **do not represent confirmed classification errors**.

## Advisory thresholds

- **Review**: any genre loss or billing change on a retained public event ID; these changes may be legitimate.
- **Investigate**: at least five genre-loss examples and at least 1% of comparable IDs, or ten billing-change examples and at least 2% of comparable IDs. Also investigate any genre provenance defect or more than 50% events without a genre.
- **Review queue**: at least 100 possible flattened bills or 50 possible programme-title identities.

Release-audit example collections are capped at 100, so the monitor deliberately calls these example counts, not exhaustive totals. Existing event-count safeguards, genre accounting validation and hosted asset verification remain authoritative.

## Run and inspect locally

```bash
cd ~/Documents/idf_concert_calendar && source .venv/bin/activate && python3 -m concert_calendar.release_monitor --report output/automation/automation-report.json --json-output output/automation/quality-monitor.json --markdown-output output/automation/quality-monitor.md
```

Review the latest successful **Update Electric Eye Concert Calendar** workflow run's Summary and the `calendar-production-report-<run-id>` artifact. The `genre_acceptance` and `reconciliation_quality` sections of the full automation report contain the detailed evidence and review queues.

A monitoring failure is explicitly non-blocking and cannot revert a verified release. Investigate alerts before expanding inference rules or applying structural billing changes.
