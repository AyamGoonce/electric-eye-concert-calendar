"""Read-only publication quality diagnostics. Never changes event eligibility."""
from collections import Counter
import re


FLAT_BILL_SEPARATOR = re.compile(r"\s+(?:\+|/|•)\s+")
PROGRAMME_WORDS = re.compile(
    r"\b(?:release party|concert dessine|spectacle|festival|hommage|"
    r"conf[eé]rence|premi[eè]re partie)\b", re.I,
)


def reconciliation_quality_report(events, *, example_limit=50):
    """Summarize actionable uncertainties without guessing performer roles."""
    missing_genre = []
    possible_flat_bills = []
    programme_title_candidates = []
    blank_by_source = Counter()
    for event in events:
        record = {
            "date": event.date[:10],
            "headliner": event.headliner,
            "venue": event.venue,
            "ticket_url": event.ticket_url,
        }
        if not event.genre_public:
            missing_genre.append(record)
            for source in event.source_names or ["unknown"]:
                blank_by_source[source] += 1
        if (
            FLAT_BILL_SEPARATOR.search(event.headliner or "")
            and not event.co_headliners and not event.openers
        ):
            possible_flat_bills.append(record)
        if (
            PROGRAMME_WORDS.search(event.headliner or "")
            or len((event.headliner or "").split()) >= 10
        ) and event.headliner != (event.event_title or ""):
            programme_title_candidates.append(record)
    return {
        "total_events": len(events),
        "missing_genre": {
            "count": len(missing_genre),
            "by_source": dict(sorted(blank_by_source.items())),
            "examples": missing_genre[:example_limit],
        },
        "possible_flat_bill": {
            "count": len(possible_flat_bills),
            "examples": possible_flat_bills[:example_limit],
            "note": "Separator heuristics identify review candidates, not proven bad bills.",
        },
        "possible_programme_as_artist": {
            "count": len(programme_title_candidates),
            "examples": programme_title_candidates[:example_limit],
            "note": "Conservative title heuristics; legitimate band names may be included.",
        },
    }
