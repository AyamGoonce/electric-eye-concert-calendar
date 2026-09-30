from __future__ import annotations

import json
import time
from pathlib import Path

import requests

from concert_calendar.content_index import normalize_artist
from concert_calendar.genres import canonicalize_genre_term


MUSICBRAINZ_URL = "https://musicbrainz.org/ws/2/artist/"
MUSICBRAINZ_CACHE = Path("output/musicbrainz-detailed-genre-cache.json")
MUSICBRAINZ_RELATIONSHIP_CACHE = Path(
    "output/musicbrainz-relationship-genre-cache.json"
)
APPLE_CACHE = Path("output/apple-detailed-genre-cache.json")
WIKIDATA_CACHE = Path("output/wikidata-detailed-genre-cache.json")

MUSICAL_ARTIST_TYPES = {"Person", "Group", "Orchestra", "Choir", "Character"}

PROVIDER_MIN_INTERVAL_SECONDS = {
    "musicbrainz": 1.1,
    "apple": 1.0,
    "wikidata": 1.1,
}

TRANSIENT_HTTP_STATUS = {
    429,
    500,
    502,
    503,
    504,
}

PROVIDER_MAX_ATTEMPTS = 4
_PROVIDER_LAST_CALL: dict[str, float] = {}

HEADERS = {
    "User-Agent": (
        "ElectricEyeConcertCalendar/1.0 "
        "(https://github.com/AyamGoonce/electric-eye-concert-calendar)"
    )
}


def _pace_provider(provider: str) -> None:
    interval = PROVIDER_MIN_INTERVAL_SECONDS.get(provider, 0.0)
    if interval <= 0:
        return

    now = time.monotonic()
    previous = _PROVIDER_LAST_CALL.get(provider)

    if previous is not None:
        remaining = interval - (now - previous)
        if remaining > 0:
            time.sleep(remaining)

    _PROVIDER_LAST_CALL[provider] = time.monotonic()


def _request_json(
    provider: str,
    url: str,
    *,
    params: dict | None = None,
) -> dict:
    last_error = None

    for attempt in range(1, PROVIDER_MAX_ATTEMPTS + 1):
        _pace_provider(provider)

        try:
            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=20,
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as error:
            last_error = error
            response = getattr(error, "response", None)
            status = getattr(response, "status_code", None)

            transient = (
                isinstance(error, (requests.Timeout, requests.ConnectionError))
                or status in TRANSIENT_HTTP_STATUS
            )

            if not transient or attempt >= PROVIDER_MAX_ATTEMPTS:
                raise

            retry_after = (
                response.headers.get("Retry-After")
                if response is not None
                else None
            )

            try:
                delay = float(retry_after) if retry_after else 2 ** (attempt - 1)
            except (TypeError, ValueError):
                delay = 2 ** (attempt - 1)

            time.sleep(min(max(delay, 0.0), 60.0))

    if last_error is not None:
        raise last_error

    raise RuntimeError("Provider request failed without an exception")


def _load_cache(path: Path) -> dict:
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    return payload if isinstance(payload, dict) else {}


def _save_cache(path: Path, cache: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            cache,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )


def select_musicbrainz_artist(payload: dict, artist: str) -> tuple[dict | None, str]:
    target = normalize_artist(artist)

    matches = [
        candidate
        for candidate in payload.get("artists", [])
        if normalize_artist(candidate.get("name", "")) == target
        and candidate.get("score", 0) >= 90
        and candidate.get("type") in MUSICAL_ARTIST_TYPES
    ]

    if not matches:
        return None, "unresolved"

    if len(matches) != 1:
        return None, "ambiguous_identity"

    return matches[0], "matched"


def detailed_musicbrainz_result(artist_name: str, artist: dict) -> dict:
    tags = []
    canonical_scores: dict[str, int] = {}

    for item in artist.get("tags") or []:
        raw = (item.get("name") or "").strip()
        if not raw:
            continue

        count = max(int(item.get("count") or 0), 1)
        canonical = canonicalize_genre_term(raw)

        tags.append({
            "tag": raw,
            "count": count,
            "canonical": canonical,
        })

        if canonical:
            canonical_scores[canonical] = (
                canonical_scores.get(canonical, 0) + count
            )

    genres = [
        genre
        for genre, _score in sorted(
            canonical_scores.items(),
            key=lambda item: (-item[1], item[0].casefold()),
        )
    ]

    return {
        "artist": artist_name,
        "status": "resolved" if genres else "no_genre_match",
        "musicbrainz_id": artist.get("id"),
        "matched_name": artist.get("name"),
        "genres": genres,
        "scores": canonical_scores,
        "tags": tags,
    }


def musicbrainz_detailed_lookup(artist: str) -> dict:
    payload = _request_json(
        "musicbrainz",
        MUSICBRAINZ_URL,
        params={
            "query": f'artist:"{artist}"',
            "fmt": "json",
            "limit": 10,
        },
    )

    match, identity_status = select_musicbrainz_artist(
        payload,
        artist,
    )

    if match is None:
        return {
            "artist": artist,
            "status": identity_status,
            "musicbrainz_id": None,
            "genres": [],
            "scores": {},
            "tags": [],
        }

    return detailed_musicbrainz_result(artist, match)


def load_musicbrainz_cache(path: Path = MUSICBRAINZ_CACHE) -> dict:
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    return payload if isinstance(payload, dict) else {}


def save_musicbrainz_cache(cache: dict, path: Path = MUSICBRAINZ_CACHE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            cache,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )


def resolve_musicbrainz_genres(
    artists: list[str],
    *,
    cache_path: Path = MUSICBRAINZ_CACHE,
) -> dict[str, dict]:
    cache = load_musicbrainz_cache(cache_path)
    results = {}

    pending = []

    for artist in artists:
        identity = normalize_artist(artist)

        if identity in cache:
            results[identity] = cache[identity]
        else:
            pending.append(artist)

    for index, artist in enumerate(pending):
        identity = normalize_artist(artist)

        try:
            result = musicbrainz_detailed_lookup(artist)
        except requests.RequestException as error:
            result = {
                "artist": artist,
                "status": "request_error",
                "musicbrainz_id": None,
                "genres": [],
                "scores": {},
                "tags": [],
                "error": str(error),
            }
        else:
            # Only cache completed MusicBrainz responses.
            cache[identity] = result
            save_musicbrainz_cache(cache, cache_path)

        results[identity] = result

        if index + 1 < len(pending):
            time.sleep(1.05)

    return results


def musicbrainz_artist_by_mbid(
    mbid: str,
    *,
    includes: str = "tags",
) -> dict | None:
    try:
        return _request_json(
            "musicbrainz",
            f"{MUSICBRAINZ_URL}{mbid}",
            params={
                "inc": includes,
                "fmt": "json",
            },
        )
    except requests.RequestException:
        return None


def genres_from_musicbrainz_artist_record(record: dict) -> list[str]:
    scores: dict[str, int] = {}

    for item in record.get("tags") or []:
        raw = (item.get("name") or "").strip()
        if not raw:
            continue

        canonical = canonicalize_genre_term(raw)
        if not canonical:
            continue

        count = max(int(item.get("count") or 0), 1)
        scores[canonical] = scores.get(canonical, 0) + count

    return [
        genre
        for genre, _score in sorted(
            scores.items(),
            key=lambda item: (-item[1], item[0].casefold()),
        )
    ]


def musicbrainz_relationship_genres(
    mbid: str,
    *,
    cache_path: Path = MUSICBRAINZ_RELATIONSHIP_CACHE,
) -> dict:
    cache = _load_cache(cache_path)

    if mbid in cache:
        return cache[mbid]

    record = musicbrainz_artist_by_mbid(
        mbid,
        includes="artist-rels",
    )

    if not record:
        return {
            "status": "request_error",
            "genres": [],
            "relationships": [],
        }

    relationships = []
    inherited_scores: dict[str, int] = {}

    for relation in record.get("relations") or []:
        if relation.get("type") != "member of band":
            continue

        related = relation.get("artist") or {}
        related_mbid = related.get("id")
        related_name = related.get("name")

        if not related_mbid:
            continue

        # Use the relationship's MBID directly. Do not perform another
        # name-based identity search.
        related_record = musicbrainz_artist_by_mbid(
            related_mbid,
            includes="tags",
        )

        if not related_record:
            relationships.append({
                "name": related_name,
                "musicbrainz_id": related_mbid,
                "genres": [],
                "status": "request_error",
            })
            time.sleep(1.05)
            continue

        genres = genres_from_musicbrainz_artist_record(
            related_record
        )

        relationships.append({
            "name": related_name,
            "musicbrainz_id": related_mbid,
            "genres": genres,
            "status": "resolved" if genres else "no_genre_match",
        })

        for genre in genres:
            inherited_scores[genre] = (
                inherited_scores.get(genre, 0) + 1
            )

        time.sleep(1.05)

    genres = [
        genre
        for genre, _score in sorted(
            inherited_scores.items(),
            key=lambda item: (-item[1], item[0].casefold()),
        )
    ]

    result = {
        "status": "resolved" if genres else "no_genre_match",
        "genres": genres,
        "relationships": relationships,
    }

    # Cache only completed provider results. A transient request failure
    # must never become a persistent unresolved classification.
    if not any(
        rel.get("status") == "request_error"
        for rel in relationships
    ):
        cache[mbid] = result
        _save_cache(cache_path, cache)

    return result


ITUNES_SEARCH_API = "https://itunes.apple.com/search"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"

MUSIC_DESCRIPTORS = (
    "musician",
    "singer",
    "rapper",
    "band",
    "musical group",
    "composer",
    "dj",
    "producer",
    "songwriter",
    "artist",
)


def apple_detailed_lookup(
    artist: str,
    *,
    cache_path: Path = APPLE_CACHE,
) -> dict:
    identity = normalize_artist(artist)
    cache = _load_cache(cache_path)

    if identity in cache:
        return cache[identity]

    try:
        payload = _request_json(
            "apple",
            ITUNES_SEARCH_API,
            params={
                "term": artist,
                "entity": "musicArtist",
                "limit": 25,
                "country": "FR",
            },
        )
    except requests.RequestException as error:
        return {
            "artist": artist,
            "status": "request_error",
            "genres": [],
            "evidence": [],
            "error": str(error),
        }

    target = identity

    exact = [
        item
        for item in payload.get("results", [])
        if normalize_artist(item.get("artistName", "")) == target
    ]

    if not exact:
        result = {
            "artist": artist,
            "status": "unresolved",
            "genres": [],
            "evidence": [],
        }
        cache[identity] = result
        _save_cache(cache_path, cache)
        return result

    evidence = []
    genres = set()

    for item in exact:
        raw = (item.get("primaryGenreName") or "").strip()
        canonical = canonicalize_genre_term(raw)

        evidence.append({
            "artistName": item.get("artistName"),
            "artistId": item.get("artistId"),
            "primaryGenreName": raw,
            "canonical": canonical,
        })

        if canonical:
            genres.add(canonical)

    # We only accept Apple automatically when every useful exact-name
    # result collapses to one canonical taxonomy genre.
    if len(genres) == 1:
        result = {
            "artist": artist,
            "status": "resolved",
            "genres": sorted(genres),
            "evidence": evidence,
        }
    else:
        result = {
            "artist": artist,
            "status": "ambiguous" if len(genres) > 1 else "no_genre_match",
            "genres": [],
            "evidence": evidence,
        }

    cache[identity] = result
    _save_cache(cache_path, cache)
    return result


def wikidata_detailed_lookup(
    artist: str,
    *,
    cache_path: Path = WIKIDATA_CACHE,
) -> dict:
    identity = normalize_artist(artist)
    cache = _load_cache(cache_path)

    if identity in cache:
        return cache[identity]

    try:
        search_payload = _request_json(
            "wikidata",
            WIKIDATA_API,
            params={
                "action": "wbsearchentities",
                "search": artist,
                "language": "en",
                "format": "json",
                "limit": 5,
                "type": "item",
            },
        )
    except requests.RequestException as error:
        return {
            "artist": artist,
            "status": "request_error",
            "genres": [],
            "error": str(error),
        }

    target = identity

    def without_leading_the(value: str) -> str:
        value = normalize_artist(value)
        return value[4:] if value.startswith("the ") else value

    candidates = []

    for item in search_payload.get("search", []):
        label = item.get("label") or ""
        description = (item.get("description") or "").casefold()

        normalized_label = normalize_artist(label)

        label_match = (
            normalized_label == target
            or (
                without_leading_the(normalized_label)
                == without_leading_the(target)
            )
        )

        music_match = any(
            token in description
            for token in MUSIC_DESCRIPTORS
        )

        # Production fallback is intentionally stricter than the old
        # research resolver: exact normalized label only.
        if label_match and music_match:
            candidates.append(item)

    if len(candidates) != 1:
        result = {
            "artist": artist,
            "status": (
                "ambiguous_identity"
                if len(candidates) > 1
                else "unresolved"
            ),
            "genres": [],
        }
        cache[identity] = result
        _save_cache(cache_path, cache)
        return result

    entity = candidates[0]
    qid = entity["id"]

    try:
        data_payload = _request_json(
            "wikidata",
            WIKIDATA_API,
            params={
                "action": "wbgetentities",
                "ids": qid,
                "props": "claims",
                "format": "json",
            },
        )
    except requests.RequestException as error:
        return {
            "artist": artist,
            "status": "request_error",
            "genres": [],
            "wikidata_id": qid,
            "error": str(error),
        }

    claims = (
        data_payload
        .get("entities", {})
        .get(qid, {})
        .get("claims", {})
        .get("P136", [])
    )

    genre_ids = []

    for claim in claims:
        value = (
            claim.get("mainsnak", {})
            .get("datavalue", {})
            .get("value", {})
        )

        if isinstance(value, dict) and value.get("id"):
            genre_ids.append(value["id"])

    if not genre_ids:
        result = {
            "artist": artist,
            "status": "no_genre_match",
            "genres": [],
            "wikidata_id": qid,
        }
        cache[identity] = result
        _save_cache(cache_path, cache)
        return result

    try:
        labels_payload = _request_json(
            "wikidata",
            WIKIDATA_API,
            params={
                "action": "wbgetentities",
                "ids": "|".join(genre_ids),
                "props": "labels",
                "languages": "en",
                "format": "json",
            },
        )
    except requests.RequestException as error:
        return {
            "artist": artist,
            "status": "request_error",
            "genres": [],
            "wikidata_id": qid,
            "error": str(error),
        }

    entities = labels_payload.get("entities", {})
    genres = []

    for genre_id in genre_ids:
        raw = (
            entities.get(genre_id, {})
            .get("labels", {})
            .get("en", {})
            .get("value")
        )

        canonical = canonicalize_genre_term(raw)

        if canonical and canonical not in genres:
            genres.append(canonical)

    result = {
        "artist": artist,
        "status": "resolved" if genres else "no_genre_match",
        "genres": genres,
        "wikidata_id": qid,
        "label": entity.get("label"),
    }

    cache[identity] = result
    _save_cache(cache_path, cache)
    return result
