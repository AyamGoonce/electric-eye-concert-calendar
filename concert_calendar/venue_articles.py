from __future__ import annotations

from collections import defaultdict
import re
from typing import Any, Iterable

from concert_calendar.content_index import (
    alternate_url,
    classify_article,
    resized_blogger_image,
)
from concert_calendar.venue_metadata import VENUE_METADATA
from concert_calendar.venues import resolve_venue_name


# Explicit reviewed exceptions only. Do not turn this into a fuzzy-title system.
MANUAL_REVIEW_VENUES = {
    "Hellfest 2026": "Hellfest",
}


def _review_location(title: str) -> tuple[str, str] | None:
    """
    Extract venue and optional city from Electric Eye's structured review title.

    Expected house form:
        Artist @ Venue, City – Month Day, Year

    Deliberately returns None when that structure is absent.
    """

    if " @ " not in title:
        return None

    tail = title.split(" @ ", 1)[1].strip()

    # Remove the review date suffix but leave hyphens inside venue names alone.
    location = re.split(
        r"\s+[–—-]\s+",
        tail,
        maxsplit=1,
    )[0].strip()

    if not location:
        return None

    parts = [
        part.strip()
        for part in location.split(",")
        if part.strip()
    ]

    if not parts:
        return None

    venue = parts[0]
    city = parts[1] if len(parts) > 1 else ""

    return venue, city


def _article_record(entry: dict[str, Any]) -> dict[str, Any] | None:
    title = (entry.get("title") or {}).get("$t", "").strip()
    url = alternate_url(entry)
    published = (entry.get("published") or {}).get("$t", "")[:10]

    if not title or not url:
        return None

    record = {
        "date": published,
        "title": title,
        "url": url,
    }

    image = resized_blogger_image(entry)
    if image:
        record["image"] = image

    return record


def build_venue_article_associations(
    entries: Iterable[dict[str, Any]],
    known_venues: set[str] | None = None,
    *,
    include_diagnostics: bool = False,
):
    """
    Associate Electric Eye concert reviews with canonical venue identities.

    Resolution is intentionally conservative:
    - only articles classified as concert reviews are considered;
    - structured " @ " titles use the existing venue resolver;
    - explicitly reviewed manual exceptions are permitted;
    - unresolved titles are reported, never guessed.
    """

    known = (
        set(VENUE_METADATA)
        if known_venues is None
        else set(known_venues)
    )

    associations = defaultdict(list)

    for venue in known:
        associations[venue]

    diagnostics = {
        "concertReviews": 0,
        "associatedReviews": 0,
        "unresolvedReviews": [],
        "resolvedOutsideRegistry": [],
    }

    for entry in entries:
        title = (entry.get("title") or {}).get("$t", "").strip()

        labels = [
            item.get("term", "").strip()
            for item in entry.get("category", [])
            if item.get("term", "").strip()
        ]

        if classify_article(title, labels) != "concert_review":
            continue

        diagnostics["concertReviews"] += 1

        canonical = MANUAL_REVIEW_VENUES.get(title)

        raw_venue = ""
        city = ""

        if canonical is None:
            location = _review_location(title)

            if location is None:
                diagnostics["unresolvedReviews"].append({
                    "title": title,
                    "venue": "",
                    "city": "",
                })
                continue

            raw_venue, city = location
            canonical = resolve_venue_name(raw_venue, city)

        if canonical is None:
            diagnostics["unresolvedReviews"].append({
                "title": title,
                "venue": raw_venue,
                "city": city,
            })
            continue

        if canonical not in known:
            diagnostics["resolvedOutsideRegistry"].append({
                "title": title,
                "canonicalVenue": canonical,
            })
            continue

        article = _article_record(entry)
        if article is None:
            continue

        associations[canonical].append(article)
        diagnostics["associatedReviews"] += 1

    for articles in associations.values():
        articles.sort(
            key=lambda article: (
                article.get("date") or "",
                article["title"].casefold(),
                article["url"],
            ),
            reverse=True,
        )

    result = dict(associations)

    if include_diagnostics:
        return result, diagnostics

    return result
