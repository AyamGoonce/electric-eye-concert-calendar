from __future__ import annotations

import json
import re
from pathlib import Path

from concert_calendar.genres import (
    canonicalize_genre_term,
    genre_parent_chain,
    load_genre_taxonomy,
)


MAPPINGS_PATH = Path(__file__).with_name("genre_mappings.json")


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
    re.compile(
        r"subgenres map to one defensible public bucket:\s*(.+?)(?:\.$|$)",
        re.I,
    ),
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


def build_genre_index(
    mappings_path: str | Path = MAPPINGS_PATH,
) -> dict:
    mappings = json.loads(
        Path(mappings_path).read_text(encoding="utf-8")
    )
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

        direct_genres = set()

        for raw in extract_raw_genres(record.get("notes") or ""):
            canonical = canonicalize_genre_term(raw, taxonomy)
            if canonical:
                direct_genres.add(canonical)

        if not direct_genres:
            fallback = SAFE_BROAD_FALLBACKS.get(
                record.get("genre")
            )

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

            for inherited in genre_parent_chain(
                direct,
                taxonomy,
            ):
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
            "artists": sorted(
                record["artists"],
                key=str.casefold,
            ),
            "directArtists": sorted(
                record["directArtists"],
                key=str.casefold,
            ),
        })

    return {
        "version": 1,
        "source": "concert_calendar/genre_mappings.json",
        "genreCount": len(output_genres),
        "resolvedArtistCount": resolved_artists,
        "unresolvedArtistCount": len(unresolved_artists),
        "genres": output_genres,
        "unresolvedArtists": sorted(
            unresolved_artists,
            key=str.casefold,
        ),
    }
