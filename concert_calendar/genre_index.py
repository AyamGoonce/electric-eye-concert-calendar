from __future__ import annotations

import json
import re
from pathlib import Path

from concert_calendar.content_index import normalize_artist
from concert_calendar.genre_external import (
    apple_detailed_lookup,
    musicbrainz_relationship_genres,
    resolve_musicbrainz_genres,
    wikidata_detailed_lookup,
)
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
    re.compile(
        r"described as an?\s+([a-z0-9 &'/-]+?)\s+(?:band|artist|group|act|musician)(?:\.|$)",
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
    content_index: dict | None = None,
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
    artist_genres: dict[str, set[str]] = {}
    artist_names_by_identity: dict[str, str] = {}

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
        identity_key = normalize_artist(artist)
        artist_names_by_identity.setdefault(identity_key, artist)
        artist_genres.setdefault(identity_key, set()).update(direct_genres)

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

    if content_index:
        content_artists = content_index.get("artists") or {}
        articles = content_index.get("articles") or []

        for slug, artist_record in content_artists.items():
            artist = (artist_record.get("n") or "").strip()
            if not artist:
                continue

            direct_genres = set()

            identity = artist_record.get("identity") or {}
            for raw in identity.get("genres") or []:
                canonical = canonicalize_genre_term(raw, taxonomy)
                if canonical:
                    direct_genres.add(canonical)

            for article_id in artist_record.get("ar") or []:
                if not isinstance(article_id, int):
                    continue
                if article_id < 0 or article_id >= len(articles):
                    continue

                article = articles[article_id]
                for raw in article.get("l") or []:
                    canonical = canonicalize_genre_term(raw, taxonomy)
                    if canonical:
                        direct_genres.add(canonical)

            if not direct_genres:
                continue

            identity_key = normalize_artist(artist)
            already_known = artist_genres.get(identity_key, set())
            new_genres = direct_genres - already_known

            if identity_key not in artist_genres:
                resolved_artists += 1
                artist_genres[identity_key] = set()
                artist_names_by_identity[identity_key] = artist
            else:
                artist_names_by_identity.setdefault(identity_key, artist)

            artist_genres[identity_key].update(direct_genres)

            for direct in new_genres:
                if direct not in genres:
                    continue

                genres[direct]["directArtists"].add(artist)

                for inherited in genre_parent_chain(direct, taxonomy):
                    if inherited in genres:
                        genres[inherited]["artists"].add(artist)

    # External fallbacks are strictly hierarchical:
    #
    #   Electric Eye evidence
    #       -> MusicBrainz direct
    #       -> MusicBrainz relationship inheritance
    #       -> Wikidata
    #       -> Apple/iTunes
    #
    # Once an artist resolves at one layer, lower-priority providers do not
    # add additional genres.

    excluded_content_subjects = {
        normalize_artist("Musée de la Musique"),
        normalize_artist("Play It Loud"),
    }

    if content_index:
        content_artists = content_index.get("artists") or {}

        unresolved_content_artists = []

        for artist_record in content_artists.values():
            artist = (artist_record.get("n") or "").strip()
            if not artist:
                continue

            identity_key = normalize_artist(artist)

            if identity_key in excluded_content_subjects:
                continue

            if identity_key not in artist_genres:
                unresolved_content_artists.append(artist)

        unresolved_content_artists = sorted(
            set(unresolved_content_artists),
            key=str.casefold,
        )

        def apply_external_genres(
            artist: str,
            direct_genres: set[str],
        ) -> bool:
            nonlocal resolved_artists

            direct_genres = {
                genre
                for genre in direct_genres
                if genre in genres
            }

            if not direct_genres:
                return False

            identity_key = normalize_artist(artist)

            if identity_key not in artist_genres:
                resolved_artists += 1
                artist_genres[identity_key] = set()
                artist_names_by_identity[identity_key] = artist

            already_known = artist_genres[identity_key]
            new_genres = direct_genres - already_known
            already_known.update(direct_genres)

            for direct in new_genres:
                genres[direct]["directArtists"].add(artist)

                for inherited in genre_parent_chain(
                    direct,
                    taxonomy,
                ):
                    if inherited in genres:
                        genres[inherited]["artists"].add(artist)

            return True

        # 1. MusicBrainz direct.
        musicbrainz_results = resolve_musicbrainz_genres(
            unresolved_content_artists
        )

        remaining = []

        for artist in unresolved_content_artists:
            identity_key = normalize_artist(artist)
            result = musicbrainz_results.get(identity_key) or {}

            if apply_external_genres(
                artist,
                set(result.get("genres") or []),
            ):
                continue

            remaining.append(artist)

        # 2. MusicBrainz relationship inheritance.
        next_remaining = []

        for artist in remaining:
            identity_key = normalize_artist(artist)
            direct_result = musicbrainz_results.get(identity_key) or {}
            mbid = direct_result.get("musicbrainz_id")

            if not mbid:
                next_remaining.append(artist)
                continue

            relationship_result = musicbrainz_relationship_genres(mbid)

            if apply_external_genres(
                artist,
                set(relationship_result.get("genres") or []),
            ):
                continue

            next_remaining.append(artist)

        remaining = next_remaining

        # 3. Wikidata.
        next_remaining = []

        for artist in remaining:
            result = wikidata_detailed_lookup(artist)

            if apply_external_genres(
                artist,
                set(result.get("genres") or []),
            ):
                continue

            next_remaining.append(artist)

        remaining = next_remaining

        # 4. Apple/iTunes.
        for artist in remaining:
            result = apple_detailed_lookup(artist)

            apply_external_genres(
                artist,
                set(result.get("genres") or []),
            )

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

    resolved_identity_keys = set(artist_genres)

    final_unresolved_artists = []

    if content_index:
        excluded_content_subjects = {
            normalize_artist("Musée de la Musique"),
            normalize_artist("Play It Loud"),
        }

        for artist_record in (content_index.get("artists") or {}).values():
            artist = (artist_record.get("n") or "").strip()
            if not artist:
                continue

            identity_key = normalize_artist(artist)

            if identity_key in excluded_content_subjects:
                continue

            if identity_key not in resolved_identity_keys:
                final_unresolved_artists.append(artist)

    else:
        final_unresolved_artists = [
            artist
            for artist in unresolved_artists
            if normalize_artist(artist) not in resolved_identity_keys
        ]

    final_unresolved_artists = sorted(
        set(final_unresolved_artists),
        key=str.casefold,
    )

    return {
        "version": 1,
        "source": "concert_calendar/genre_mappings.json",
        "genreCount": len(output_genres),
        "resolvedArtistCount": len(resolved_identity_keys),
        "unresolvedArtistCount": len(final_unresolved_artists),
        "genres": output_genres,
        "unresolvedArtists": final_unresolved_artists,
    }
