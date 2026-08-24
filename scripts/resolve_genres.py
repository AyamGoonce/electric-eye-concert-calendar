#!/usr/bin/env python3

from __future__ import annotations

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


def musicbrainz_lookup(artist: str) -> dict | None:
    r = requests.get(
        MUSICBRAINZ_URL,
        params={"query": f"artist:\"{artist}\"", "fmt": "json", "limit": 5},
        headers={"User-Agent": "ElectricEyeConcertCalendar/1.0 (https://github.com/AyamGoonce/electric-eye-concert-calendar)"},
        timeout=10,
    )
    r.raise_for_status()
    target = normalize_artist_component(artist)
    matches = [x for x in r.json().get("artists", []) if normalize_artist_component(x.get("name", "")) == target and x.get("score", 0) >= 90]
    if len(matches) != 1:
        return None
    match = matches[0]
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
        return None
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
    wanted = {normalize_artist_component(name): name for name in names}
    found = {}
    for artist in r.json().get("artists", []):
        identity = normalize_artist_component(artist.get("name", ""))
        if identity not in wanted or artist.get("score", 0) < 90:
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
            continue
        ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
        winner, winner_score = ranked[0]
        runner = ranked[1][1] if len(ranked) > 1 else 0
        genre = winner if not runner or winner_score >= runner * 1.5 else None
        candidate = {"artist": wanted[identity], "genre": genre, "status": "resolved" if genre else "ambiguous", "scores": dict(ranked), "evidence": evidence, "musicbrainz_id": artist.get("id")}
        previous = found.get(identity)
        if previous is None or artist.get("score", 0) > previous["_score"]:
            candidate["_score"] = artist.get("score", 0)
            found[identity] = candidate
    for value in found.values():
        value.pop("_score", None)
    return found


def resolve_calendar_asset(path: Path, batch_size: int = 10) -> dict:
    events = [event for event in load_calendar_events(path) if not event.get("x") and not event.get("f")]
    names = {}
    counts = {}
    for event in events:
        identity = normalize_artist_component(event["h"])
        names.setdefault(identity, event["h"])
        counts[identity] = counts.get(identity, 0) + 1
    cache = {}
    if MUSICBRAINZ_CACHE.exists():
        try:
            cache = json.loads(MUSICBRAINZ_CACHE.read_text(encoding="utf-8"))
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
        MUSICBRAINZ_CACHE.parent.mkdir(parents=True, exist_ok=True)
        MUSICBRAINZ_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
        if offset + batch_size < len(pending):
            time.sleep(1.05)
    resolved = [dict(value, affected_events=counts.get(identity, 0)) for identity, value in cache.items() if identity in names and value.get("genre")]
    return {"blank_rows": len(events), "unique_artists": len(names), "resolved_artists": len(resolved), "resolved_events": sum(x["affected_events"] for x in resolved), "resolved": resolved}


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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = resolve_calendar_asset(Path(sys.argv[1]))
    else:
        result = musicbrainz_lookup("The Cure")
    print(json.dumps(result, ensure_ascii=False, indent=2))
