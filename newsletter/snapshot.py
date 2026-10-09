"""Build an Electric Eye newsletter edition from verified source records."""

from datetime import date

from newsletter.articles import extract_articles
from newsletter.concerts import extract_concerts
from newsletter.venues import filter_concerts_by_venue


def build_snapshot(entries, events, period, publication_date):
    """Build an edition without fetching data or modifying external systems."""
    date.fromisoformat(publication_date)

    if not isinstance(entries, list) or not isinstance(events, list):
        raise ValueError("Newsletter sources must be validated lists")

    if not entries:
        raise ValueError("Blogger feed is unexpectedly empty")

    if not events:
        raise ValueError("Published calendar is unexpectedly empty")

    articles = extract_articles(entries, period)

    concerts = filter_concerts_by_venue(
        extract_concerts(events, period, publication_date)
    )

    return {
        "schema_version": 1,
        "frequency": period["frequency"],
        "identifier": period["identifier"],
        "period_start": period["start"],
        "period_end_exclusive": period["end_exclusive"],
        "publication_date": publication_date,
        "articles": articles,
        "concerts": concerts,
        "counts": {
            **{
                kind: len(items)
                for kind, items in articles.items()
            },
            "concerts": len(concerts),
        },
    }
