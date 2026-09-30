#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from concert_calendar.genres import (
    canonicalize_genre_term,
    genre_parent_chain,
    load_genre_taxonomy,
)


MAPPINGS_PATH = ROOT / "concert_calendar" / "genre_mappings.json"
OUTPUT_PATH = ROOT / "output" / "genre-index.json"


SAFE_BROAD_FALLBACKS = {
    "Pop": "Pop",
    "Electronic": "Electronic",
    "Hip-hop / Rap": "Hip-Hop",
    "R&B / Soul / Funk": "R&B / Soul / Funk",
    "Chanson Française / Variétés": "Chanson Française",
    "Reggae / Dub / Ska": "Reggae / Dub / Ska",
    "Comedy / Spoken Word": "Comedy / Spoken Word",
}


EVIDENCE_PATTERNS = (
    re.compile(r"dominant MusicBrainz tags:\s*(.+?)(?:\.$|$)", re.I),
    re.compile(r"Exact Bandcamp artist match; tags:\s*(.+?)(?:\.$|$)", re.I),
    re.compile(r"Wikidata genres:\s*(.+?)(?:\.$|$)", re.I),
    re.compile(r"subgenres map to one defensible public bucket:\s*(.+?)(?:\.$|$)", re.I),
)


def extract_raw_genres(notes: str) -> list[str]:
    values: list[str] = []

    for pattern in EVIDENCE_PATTERNS:
        match = pattern.search(notes or "")
        if not match:
            continue

        for raw in match.group(1).split(","):
            raw = raw.strip()
            if raw:
                values.append(raw)

    return values


def main() -> None:
    mappings = json.loads(MAPPINGS_PATH.read_text(encoding="utf-8"))
    taxonomy = load_genre_taxonomy()

    genres: dict[str, dict] = {}
    for record in taxonomy.get("genres", []):
        name = record["name"]
        genres[name] = {
            "name": name,
            "parent": record.get("parent"),
            "artists": set(),
            "directArtists": set(),
        }

    unresolved_artists = []
    resolved_artists = 0

    for record in mappings.get("artists", []):
        artist = (record.get("artist") or "").strip()
        if not artist:
            continue

        raw_terms = extract_raw_genres(record.get("notes") or "")
        direct_genres = set()

        for raw in raw_terms:
            canonical = canonicalize_genre_term(raw, taxonomy)
            if canonical:
                direct_genres.add(canonical)

        if not direct_genres:
            broad_genre = record.get("genre")
            fallback = SAFE_BROAD_FALLBACKS.get(broad_genre)

            if fallback:
                direct_genres.add(fallback)
            else:
                unresolved_artists.append(artist)
                continue

        resolved_artists += 1

        for direct in direct_genres:
            if direct not in genres:
                continue

            genres[direct]["directArtists"].add(artist)

            for inherited in genre_parent_chain(direct, taxonomy):
                if inherited in genres:
                    genres[inherited]["artists"].add(artist)

    output_genres = []

    for name in sorted(genres, key=str.casefold):
        record = genres[name]

        if not record["artists"] and not record["directArtists"]:
            continue

        output_genres.append({
            "name": name,
            "parent": record["parent"],
            "artistCount": len(record["artists"]),
            "directArtistCount": len(record["directArtists"]),
            "artists": sorted(record["artists"], key=str.casefold),
            "directArtists": sorted(record["directArtists"], key=str.casefold),
        })

    payload = {
        "version": 1,
        "source": "concert_calendar/genre_mappings.json",
        "genreCount": len(output_genres),
        "resolvedArtistCount": resolved_artists,
        "unresolvedArtistCount": len(unresolved_artists),
        "genres": output_genres,
        "unresolvedArtists": sorted(unresolved_artists, key=str.casefold),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {OUTPUT_PATH}")
    print(f"Genres: {payload['genreCount']}")
    print(f"Resolved artists: {payload['resolvedArtistCount']}")
    print(f"Unresolved artists: {payload['unresolvedArtistCount']}")


if __name__ == "__main__":
    main()
