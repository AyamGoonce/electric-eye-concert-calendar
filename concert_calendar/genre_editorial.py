"""Auditable, exact-identity editorial genre fallback for blank concert records.

Only manually reviewed artist genre identities or corroborating *artist-specific*
Electric Eye articles qualify. This module never calls external providers, never
looks at unrelated artist names, and never overwrites source taxonomy.
"""
from __future__ import annotations

from collections import Counter
import re

from concert_calendar.deduplication import normalize_artist_component
from concert_calendar.genres import (
    PUBLIC_GENRES,
    canonicalize_genre_term,
    genre_lookup_artist_identity,
    genre_parent_chain,
    load_genre_taxonomy,
    map_raw_genres,
)


ROOT_TO_PUBLIC = {
    "Rock": "Rock / Indie / Punk",
    "Punk": "Rock / Indie / Punk",
    "Metal": "Metal / Hard Rock",
    "Pop": "Pop",
    "Electronic": "Electronic",
    "Hip-Hop": "Hip-hop / Rap",
    "R&B / Soul / Funk": "R&B / Soul / Funk",
    "Jazz": "Jazz / Blues",
    "Blues": "Jazz / Blues",
    "Folk": "Folk / Country",
    "Country": "Folk / Country",
    "Reggae / Dub / Ska": "Reggae / Dub / Ska",
    "World": "World / Latin",
    "Chanson Française": "Chanson Française / Variétés",
    "Comedy / Spoken Word": "Comedy / Spoken Word",
}


def _artist_key(value):
    return normalize_artist_component(genre_lookup_artist_identity(value or ""))


def _safe_standalone_name(value):
    name = (value or "").strip()
    if not name or len(name) > 120:
        return False
    # Unresolved billing punctuation cannot be used to infer artist genres.
    return not re.search(
        r"\s+(?:\+|/|•|&|et|x|×|vs\.?|avec|with|feat\.?|featuring|[–—])\s+",
        name, re.I,
    )


def _reviewed_bucket(raw, taxonomy):
    if raw in PUBLIC_GENRES:
        return raw
    canonical = canonicalize_genre_term(raw, taxonomy)
    if not canonical:
        return None
    chain = genre_parent_chain(canonical, taxonomy)
    if not chain:
        return None
    return ROOT_TO_PUBLIC.get(chain[-1])


def _title_contains_artist(artist, title):
    # Exact token-sequence match, never substring matching or article labels.
    from concert_calendar.genre_index import normalized_phrase_in_text
    return normalized_phrase_in_text(artist, title)


def build_editorial_artist_genre_evidence(content_index):
    """Return unique broad genres with explicit editorial provenance."""
    taxonomy = load_genre_taxonomy()
    records = {}
    articles = content_index.get("articles") or []
    artists = content_index.get("artists") or {}
    # A normalized name must identify exactly one indexed artist. Distinct
    # slugs (homonyms, aliases) cannot silently replace one another's genre.
    key_counts = Counter(
        _artist_key(entry.get("n") or "")
        for entry in artists.values()
        if _artist_key(entry.get("n") or "")
    )
    for slug, entry in artists.items():
        name = (entry.get("n") or "").strip()
        key = _artist_key(name)
        if not key or key_counts[key] != 1 or not _safe_standalone_name(name):
            continue
        identity = entry.get("identity") or {}
        if identity.get("ambiguityClass", "distinctive") != "distinctive":
            continue

        reviewed = identity.get("genres") or []
        if reviewed:
            buckets = [_reviewed_bucket(value, taxonomy) for value in reviewed]
            if all(buckets) and len(set(buckets)) == 1:
                records[key] = {
                    "genre": buckets[0],
                    "method": "editorial_reviewed_identity",
                    "evidence": ["manually reviewed artist genre identity"],
                }
            # The reviewed identity is authoritative; conflicting or
            # unclassifiable tags may not be bypassed by article heuristics.
            continue

        confirmed_articles = {}
        article_conflict = False
        for index in set(entry.get("da") or []):
            if not isinstance(index, int) or not (0 <= index < len(articles)):
                continue
            article = articles[index]
            credited = article.get("a") or []
            if set(credited) != {slug} or not _title_contains_artist(name, article.get("t") or ""):
                continue
            raw_labels = article.get("l") or []
            article_buckets = {
                genre for raw in raw_labels
                for genre in map_raw_genres(raw)
            }
            if len(article_buckets) > 1:
                article_conflict = True
                break
            if len(article_buckets) == 1:
                confirmed_articles[index] = next(iter(article_buckets))

        if article_conflict or len(confirmed_articles) < 2:
            continue
        buckets = set(confirmed_articles.values())
        if len(buckets) != 1:
            continue
        records[key] = {
            "genre": next(iter(buckets)),
            "method": "editorial_article_consensus",
            "evidence": [
                (articles[index].get("u") or articles[index].get("t") or "")
                for index in sorted(confirmed_articles)[:5]
            ],
        }
    return records


def enrich_unclassified_with_editorial_genres(events, content_index, report):
    """Apply editorial genres only to otherwise genre-less standalone concerts.

    The same calendar events are amended, and the already computed genre
    diagnostics remain consistent with the newly populated values.
    """
    records = build_editorial_artist_genre_evidence(content_index)
    assigned = []
    method_counts = Counter()
    resolved_per_artist = Counter()

    for event in events:
        if (
            event.genre_public or event.genre or event.genre_evidence
            or event.festival_name or event.co_headliners or event.openers
            or not _safe_standalone_name(event.headliner)
            or (
                event.event_title
                and _artist_key(event.event_title) != _artist_key(event.headliner)
            )
        ):
            continue
        artist = _artist_key(event.headliner)
        source = records.get(artist)
        if not source:
            continue
        event.genre_public = source["genre"]
        event.genre_method = source["method"]
        event.genre_source = "Electric Eye artist-specific editorial evidence"
        method_counts[source["method"]] += 1
        resolved_per_artist[artist] += 1
        if len(assigned) < 100:
            assigned.append({
                "artist": event.headliner,
                "date": event.date[:10],
                "venue": event.venue,
                "genre": source["genre"],
                "method": source["method"],
                "evidence": source["evidence"],
            })

    count = sum(method_counts.values())
    report["populated"] += count
    report["blank"] -= count
    report["blank_no_raw"] -= count
    report["coverage_percentage"] = (
        round(report["populated"] * 100 / report["total"], 2)
        if report["total"] else 0
    )
    for method, value in method_counts.items():
        report[method] = value

    unresolved_rows = []
    for row in report.get("unresolved_artists") or []:
        key = _artist_key(row["artist"])
        remainder = row["affected_events"] - resolved_per_artist[key]
        if remainder > 0:
            unresolved_rows.append({**row, "affected_events": remainder})
    report["unresolved_artists"] = unresolved_rows
    report["editorial_genre_evidence"] = {
        "eligible_artist_identities": len(records),
        "assigned_events": count,
        "by_method": dict(method_counts),
        "assignments": assigned,
        "policy": (
            "exact canonical artist identities only; reviewed or 2 independently "
            "artist-specific articles; preserve source genre and concert roles"
        ),
    }
    return report
