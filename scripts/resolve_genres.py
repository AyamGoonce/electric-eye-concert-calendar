#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import quote

import requests
import time
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from concert_calendar.deduplication import normalize_artist_component


USER_AGENT = "ElectricEyeGenreResolver/1.0"
FNAC_SEARCH_URL = "https://www.fnacspectacles.com/search/?search={query}"
CACHE_PATH = Path("output/genre-resolver-cache.json")


def load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


MUSICBRAINZ_URL = "https://musicbrainz.org/ws/2/artist/"
MUSICAL_ARTIST_TYPES = {"Person", "Group", "Orchestra", "Choir", "Character"}

GENRE_RULES = {
    "Metal / Hard Rock": ("metal", "hard rock", "metalcore", "deathcore", "doom"),
    "Hip-hop / Rap": ("hip hop", "hip-hop", "rap", "trap", "drill"),
    "Reggae / Dub / Ska": ("reggae", "dub", "ska", "dancehall"),
    "Jazz / Blues": ("jazz", "bebop", "bop", "blues"),
    "R&B / Soul / Funk": ("r&b", "rnb", "soul", "funk", "motown"),
    "Folk / Country": ("folk", "country", "americana", "bluegrass"),
    "French chanson": ("chanson", "variété française"),
    "Electronic": ("electronic", "electronica", "techno", "house", "ambient", "synthpop", "synth-pop", "trance", "drum and bass"),
    "World / Latin": ("world", "latin", "merengue", "salsa", "cumbia", "afrobeat", "afrobeats", "bossa nova"),
    "Rock / Indie / Punk": ("rock", "punk", "indie", "shoegaze", "grunge", "new wave", "goth"),
    "Pop": ("pop", "hyperpop", "k-pop"),
    "Comedy": ("comedy",),
}


def select_musicbrainz_candidate(payload: dict, artist: str) -> tuple[dict | None, str]:
    target = normalize_artist_component(artist)
    matches = [
        candidate for candidate in payload.get("artists", [])
        if normalize_artist_component(candidate.get("name", "")) == target
        and candidate.get("score", 0) >= 90
        and candidate.get("type") in MUSICAL_ARTIST_TYPES
    ]
    if not matches:
        return None, "unresolved"
    if len(matches) != 1:
        return None, "ambiguous_identity"
    return matches[0], "matched"


def musicbrainz_lookup(artist: str) -> dict:
    r = requests.get(
        MUSICBRAINZ_URL,
        params={"query": f"artist:\"{artist}\"", "fmt": "json", "limit": 5},
        headers={"User-Agent": "ElectricEyeConcertCalendar/1.0 (https://github.com/AyamGoonce/electric-eye-concert-calendar)"},
        timeout=10,
    )
    r.raise_for_status()
    match, identity_status = select_musicbrainz_candidate(r.json(), artist)
    if match is None:
        return {"artist": artist, "genre": None, "status": identity_status,
                "scores": {}, "evidence": []}
    scores = {}
    evidence = []
    for tag in match.get("tags") or []:
        name = (tag.get("name") or "").casefold()
        weight = max(int(tag.get("count") or 0), 1)
        for public, terms in GENRE_RULES.items():
            if any(term in name for term in terms):
                scores[public] = scores.get(public, 0) + weight
                evidence.append({"tag": tag.get("name"), "count": weight, "genre": public})
                break
    if not scores:
        return {"artist": artist, "genre": None, "status": "unresolved",
                "scores": {}, "evidence": [], "musicbrainz_id": match.get("id")}
    ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    winner, winner_score = ranked[0]
    runner_up = ranked[1][1] if len(ranked) > 1 else 0
    if runner_up and winner_score < runner_up * 1.5:
        return {"artist": artist, "genre": None, "status": "ambiguous", "scores": dict(ranked), "evidence": evidence, "musicbrainz_id": match.get("id")}
    return {"artist": artist, "genre": winner, "status": "resolved", "scores": dict(ranked), "evidence": evidence, "musicbrainz_id": match.get("id")}


MUSICBRAINZ_CACHE = Path("output/musicbrainz-genre-cache.json")


def load_calendar_events(path: Path) -> list[dict]:
    body = path.read_text(encoding="utf-8")
    match = re.search(r"window\.ElectricEyeConcertData\s*=\s*Object\.freeze\((\[.*\])\);", body, re.DOTALL)
    if not match:
        raise ValueError("Not a calendar data asset")
    return json.loads(match.group(1))


def musicbrainz_batch(names: list[str]) -> dict[str, dict]:
    query = " OR ".join("artist:\"" + name.replace("\"", "\\\"") + "\"" for name in names)
    r = requests.get(
        MUSICBRAINZ_URL,
        params={"query": query, "fmt": "json", "limit": 100},
        headers={"User-Agent": "ElectricEyeConcertCalendar/1.0 (https://github.com/AyamGoonce/electric-eye-concert-calendar)"},
        timeout=20,
    )
    r.raise_for_status()
    payload = r.json()
    found = {}
    for name in names:
        identity = normalize_artist_component(name)
        artist, identity_status = select_musicbrainz_candidate(payload, name)
        if artist is None:
            found[identity] = {
                "artist": name, "genre": None, "status": identity_status,
                "scores": {}, "evidence": [],
            }
            continue
        scores = {}
        evidence = []
        for tag in artist.get("tags") or []:
            tag_name = (tag.get("name") or "").casefold()
            weight = max(int(tag.get("count") or 0), 1)
            for public, terms in GENRE_RULES.items():
                if any(term in tag_name for term in terms):
                    scores[public] = scores.get(public, 0) + weight
                    evidence.append({"tag": tag.get("name"), "count": weight, "genre": public})
                    break
        if not scores:
            found[identity] = {
                "artist": name, "genre": None, "status": "unresolved",
                "scores": {}, "evidence": [],
                "musicbrainz_id": artist.get("id"),
            }
            continue
        ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
        winner, winner_score = ranked[0]
        runner = ranked[1][1] if len(ranked) > 1 else 0
        genre = winner if not runner or winner_score >= runner * 1.5 else None
        found[identity] = {
            "artist": name, "genre": genre,
            "status": "resolved" if genre else "ambiguous",
            "scores": dict(ranked), "evidence": evidence,
            "musicbrainz_id": artist.get("id"),
        }
    return found


def resolve_calendar_asset(
    path: Path, batch_size: int = 10, cache_path: Path | None = None
) -> dict:
    events = [event for event in load_calendar_events(path) if not event.get("x") and not event.get("f")]
    names = {}
    counts = {}
    for event in events:
        identity = normalize_artist_component(event["h"])
        names.setdefault(identity, event["h"])
        counts[identity] = counts.get(identity, 0) + 1
    cache = {}
    if cache_path and cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cache = {}
    pending = [names[key] for key in names if key not in cache]
    for offset in range(0, len(pending), batch_size):
        batch = pending[offset:offset + batch_size]
        try:
            found = musicbrainz_batch(batch)
        except requests.RequestException as error:
            print(f"MusicBrainz batch failed: {error}", file=sys.stderr)
            found = {}
        for name in batch:
            identity = normalize_artist_component(name)
            cache[identity] = found.get(identity, {"artist": name, "genre": None, "status": "unresolved", "scores": {}, "evidence": []})
        if cache_path:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(
                json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        if offset + batch_size < len(pending):
            time.sleep(1.05)
    resolved = [dict(value, affected_events=counts.get(identity, 0)) for identity, value in cache.items() if identity in names and value.get("genre")]
    return {"blank_rows": len(events), "unique_artists": len(names), "resolved_artists": len(resolved), "resolved_events": sum(x["affected_events"] for x in resolved), "resolved": resolved}


BANDCAMP_SEARCH_API = "https://bandcamp.com/api/bcsearch_public_api/1/autocomplete_elastic"
BANDCAMP_CACHE = Path("output/bandcamp-genre-cache.json")


def bandcamp_lookup(artist: str) -> dict | None:
    target = normalize_artist_component(artist)
    matched = []

    for search_filter in ("b", "a"):
        r = requests.post(
            BANDCAMP_SEARCH_API,
            json={"search_text": artist, "search_filter": search_filter, "full_page": True, "fan_id": None},
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
            timeout=10,
        )
        r.raise_for_status()

        for item in r.json().get("auto", {}).get("results", []):
            candidate = item.get("name", "") if search_filter == "b" else item.get("band_name", "")
            if normalize_artist_component(candidate) == target:
                matched.append(item)

        if matched and search_filter == "b":
            break

    if not matched:
        return None

    raw = []
    urls = []
    for item in matched:
        if item.get("genre_name"):
            raw.append(item["genre_name"])
        raw.extend(item.get("tag_names") or [])
        if item.get("item_url_root"):
            urls.append(item["item_url_root"])

    scores = {}
    evidence = []
    for value in raw:
        low = value.casefold()
        for public, terms in GENRE_RULES.items():
            if any(term in low for term in terms):
                scores[public] = scores.get(public, 0) + 1
                evidence.append({"tag": value, "genre": public})
                break

    if not scores:
        return {
            "artist": artist,
            "genre": None,
            "status": "unresolved",
            "bandcamp_url": urls[0] if urls else None,
            "raw": raw,
        }

    ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    winner, winner_score = ranked[0]
    runner = ranked[1][1] if len(ranked) > 1 else 0
    genre = winner if not runner or winner_score >= 2 * runner else None

    return {
        "artist": artist,
        "genre": genre,
        "status": "resolved" if genre else "ambiguous",
        "scores": dict(ranked),
        "evidence": evidence,
        "bandcamp_url": urls[0] if urls else None,
        "raw": raw,
    }


def resolve_bandcamp_bulk(names: list[str]) -> dict:
    cache = {}
    if BANDCAMP_CACHE.exists():
        try:
            cache = json.loads(BANDCAMP_CACHE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cache = {}
    resolved = []
    ambiguous = []
    unresolved = []
    for index, name in enumerate(names, 1):
        identity = normalize_artist_component(name)
        result = cache.get(identity)
        if result is None:
            try:
                result = bandcamp_lookup(name)
            except requests.RequestException:
                result = None
            if result is None:
                result = {"artist": name, "genre": None, "status": "unresolved"}
            cache[identity] = result
            BANDCAMP_CACHE.parent.mkdir(parents=True, exist_ok=True)
            BANDCAMP_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if result.get("status") == "resolved" and result.get("genre"):
            resolved.append(result)
        elif result.get("status") == "ambiguous":
            ambiguous.append(result)
        else:
            unresolved.append(result)
        if index % 100 == 0:
            print(f"Bandcamp: {index}/{len(names)} checked", file=sys.stderr)
    return {"resolved": resolved, "ambiguous": ambiguous, "unresolved": unresolved}


ITUNES_SEARCH_API = "https://itunes.apple.com/search"
ITUNES_CACHE = Path("output/itunes-genre-cache.json")

ITUNES_GENRE_MAP = {
    "alternative": "Rock / Indie / Punk",
    "rock": "Rock / Indie / Punk",
    "punk": "Rock / Indie / Punk",
    "pop": "Pop",
    "pop indé": "Pop",
    "indie pop": "Pop",
    "électronique": "Electronic",
    "electronic": "Electronic",
    "dance": "Electronic",
    "jazz": "Jazz / Blues",
    "blues": "Jazz / Blues",
    "r&b/soul": "R&B / Soul / Funk",
    "r&b": "R&B / Soul / Funk",
    "soul": "R&B / Soul / Funk",
    "hip-hop/rap": "Hip-hop / Rap",
    "hip-hop": "Hip-hop / Rap",
    "rap": "Hip-hop / Rap",
    "metal": "Metal / Hard Rock",
    "hard rock": "Metal / Hard Rock",
    "reggae": "Reggae / Dub / Ska",
    "ska": "Reggae / Dub / Ska",
    "folk": "Folk / Country",
    "country": "Folk / Country",
    "folk contemporain": "Folk / Country",
    "musiques du monde": "World / Latin",
    "world": "World / Latin",
    "latin": "World / Latin",
    "chanson française": "French chanson",
    "variété française": "French chanson",
}

def itunes_lookup(artist: str) -> dict | None:
    r = requests.get(
        ITUNES_SEARCH_API,
        params={"term": artist, "entity": "musicArtist", "limit": 10, "country": "FR"},
        headers={"User-Agent": "ElectricEyeConcertCalendar/1.0"},
        timeout=10,
    )
    r.raise_for_status()
    target = normalize_artist_component(artist)
    exact = [
        item for item in r.json().get("results", [])
        if normalize_artist_component(item.get("artistName", "")) == target
    ]
    if not exact:
        return None

    mapped = []
    evidence = []
    for item in exact:
        raw = (item.get("primaryGenreName") or "").strip()
        genre = ITUNES_GENRE_MAP.get(raw.casefold())
        evidence.append({
            "artistName": item.get("artistName"),
            "primaryGenreName": raw,
            "artistId": item.get("artistId"),
            "genre": genre,
        })
        if genre:
            mapped.append(genre)

    genres = set(mapped)
    genre = next(iter(genres)) if len(genres) == 1 else None
    return {
        "artist": artist,
        "genre": genre,
        "status": "resolved" if genre else ("ambiguous" if len(genres) > 1 else "unresolved"),
        "evidence": evidence,
    }


def resolve_itunes_bulk(names: list[str]) -> dict:
    cache = {}
    if ITUNES_CACHE.exists():
        try:
            cache = json.loads(ITUNES_CACHE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cache = {}

    resolved = []
    ambiguous = []
    unresolved = []

    for index, name in enumerate(names, 1):
        identity = normalize_artist_component(name)
        result = cache.get(identity)

        if result is None:
            try:
                result = itunes_lookup(name)
            except requests.RequestException:
                result = None

            if result is None:
                result = {
                    "artist": name,
                    "genre": None,
                    "status": "unresolved",
                    "evidence": [],
                }

            cache[identity] = result
            ITUNES_CACHE.parent.mkdir(parents=True, exist_ok=True)
            ITUNES_CACHE.write_text(
                json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

        if result.get("status") == "resolved" and result.get("genre"):
            resolved.append(result)
        elif result.get("status") == "ambiguous":
            ambiguous.append(result)
        else:
            unresolved.append(result)

        if index % 100 == 0:
            print(f"Apple: {index}/{len(names)} checked", file=sys.stderr)

    return {
        "resolved": resolved,
        "ambiguous": ambiguous,
        "unresolved": unresolved,
    }


WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKIDATA_CACHE = Path("output/wikidata-genre-cache.json")
MUSIC_DESCRIPTORS = ("musician", "singer", "rapper", "band", "musical group", "composer", "dj", "producer", "songwriter", "artist")


def wikidata_lookup(artist: str) -> dict | None:
    search = requests.get(
        WIKIDATA_API,
        params={"action":"wbsearchentities","search":artist,"language":"en","format":"json","limit":5,"type":"item"},
        headers={"User-Agent":"ElectricEyeConcertCalendar/1.0"},
        timeout=10,
    )
    search.raise_for_status()
    target = normalize_artist_component(artist)
    candidates = []
    for item in search.json().get("search", []):
        label = item.get("label") or ""
        desc = (item.get("description") or "").casefold()
        label_match = normalize_artist_component(label) == target
        music_match = any(token in desc for token in MUSIC_DESCRIPTORS)
        if music_match and (label_match or target in normalize_artist_component(label) or normalize_artist_component(label) in target):
            candidates.append(item)
    if not candidates:
        candidates = [item for item in search.json().get("search", []) if any(token in (item.get("description") or "").casefold() for token in MUSIC_DESCRIPTORS)]
    if not candidates:
        return None
    entity = candidates[0]
    qid = entity["id"]
    data = requests.get(
        WIKIDATA_API,
        params={"action":"wbgetentities","ids":qid,"props":"claims","format":"json"},
        headers={"User-Agent":"ElectricEyeConcertCalendar/1.0"},
        timeout=10,
    )
    data.raise_for_status()
    claims = data.json()["entities"][qid]["claims"].get("P136", [])
    genre_ids = [c["mainsnak"]["datavalue"]["value"]["id"] for c in claims if c.get("mainsnak",{}).get("datavalue")]
    if not genre_ids:
        return {"artist":artist,"genre":None,"status":"unresolved","wikidata_id":qid,"label":entity.get("label"),"description":entity.get("description"),"genres":[]}
    labels = requests.get(
        WIKIDATA_API,
        params={"action":"wbgetentities","ids":"|".join(genre_ids),"props":"labels","languages":"en","format":"json"},
        headers={"User-Agent":"ElectricEyeConcertCalendar/1.0"},
        timeout=10,
    )
    labels.raise_for_status()
    values = [labels.json()["entities"][gid].get("labels",{}).get("en",{}).get("value") for gid in genre_ids]
    values = [v for v in values if v]
    scores = {}
    for value in values:
        low = value.casefold()
        for public, terms in GENRE_RULES.items():
            if any(term in low for term in terms):
                scores[public] = scores.get(public, 0) + 1
                break
    genre = next(iter(scores)) if len(scores) == 1 else None
    return {"artist":artist,"genre":genre,"status":"resolved" if genre else ("ambiguous" if len(scores)>1 else "unresolved"),"wikidata_id":qid,"label":entity.get("label"),"description":entity.get("description"),"genres":values,"scores":scores}


def fnac_search(artist: str) -> dict | None:
    url = FNAC_SEARCH_URL.format(query=quote(artist, safe=""))
    r = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "fr-FR,fr;q=0.9"},
        timeout=10,
    )
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    return {
        "artist": artist,
        "url": r.url,
        "title": soup.title.get_text(" ", strip=True) if soup.title else "",
        "text": soup.get_text(" ", strip=True)[:5000],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Manual, offline-only review helper for blank calendar genres."
    )
    parser.add_argument("calendar_asset", type=Path)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument(
        "--output", type=Path,
        help="Explicitly write the review report; the default is a dry run to stdout.",
    )
    parser.add_argument(
        "--cache", type=Path,
        help="Explicitly enable a persistent MusicBrainz response cache.",
    )
    args = parser.parse_args(argv)
    result = resolve_calendar_asset(args.calendar_asset, args.batch_size, args.cache)
    body = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body, encoding="utf-8")
    else:
        print(body, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
