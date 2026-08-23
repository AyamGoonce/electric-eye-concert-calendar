#!/usr/bin/env python3
"""One-time Wikidata audit helper; never imported by production builds."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import sys
import time

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from concert_calendar.deduplication import normalize_artist_component


ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "ElectricEyeGenreAudit/1.0 (https://github.com/AyamGoonce/electric-eye-concert-calendar)"

RULES = (
    ("Metal / Hard Rock", ("metal", "hard rock", "deathcore", "metalcore")),
    ("Hip-hop / Rap", ("hip hop", "rap", "trap music", "drill music")),
    ("Reggae / Dub / Ska", ("reggae", "dub music", "ska", "dancehall")),
    ("Jazz / Blues", ("jazz", "blues", "bebop")),
    ("R&B / Soul / Funk", ("rhythm and blues", "neo soul", "soul music", "funk")),
    ("Folk / Country", ("folk", "country music", "americana", "bluegrass")),
    ("French chanson", ("chanson", "variété française")),
    ("Electronic", ("electronic", "electronica", "house music", "techno", "ambient music", "synth-pop", "trance music", "drum and bass")),
    ("World / Latin", ("world music", "latin music", "cumbia", "salsa music", "afrobeat", "afropop", "bossa nova")),
    ("Rock / Indie / Punk", ("rock", "punk", "shoegaze", "grunge", "new wave", "post-punk")),
    ("Pop", ("pop music", "art pop", "indie pop", "dream pop", "hyperpop", "k-pop")),
    ("Comedy", ("comedy",)),
)


def public_category(genres: list[str]) -> str | None:
    categories = set()

    for genre in genres:
        value = genre.casefold()
        matches = {
            public
            for public, terms in RULES
            if any(term in value for term in terms)
        }

        if len(matches) == 1:
            categories.update(matches)
        elif len(matches) > 1:
            return None

    # Accept only when all recognized genre evidence converges on
    # exactly one public category. Unrecognized descriptors do not
    # veto otherwise coherent evidence, but zero recognized evidence
    # still remains unresolved.
    return next(iter(categories)) if len(categories) == 1 else None


def load_events(path: Path) -> list[dict]:
    body = path.read_text(encoding="utf-8")
    match = re.search(r"ElectricEyeConcertData = Object\.freeze\((\[.*\])\);", body)
    if not match:
        raise ValueError("Not a calendar data asset")
    return json.loads(match.group(1))


def query_batch(names: list[str]) -> list[dict]:
    values = " ".join(json.dumps(name, ensure_ascii=False) + "@en" for name in names)
    query = f"""
SELECT ?label ?artist ?genre ?genreLabel WHERE {{
  VALUES ?label {{ {values} }}
  ?artist rdfs:label ?label; wdt:P136 ?genre.
  ?genre rdfs:label ?genreLabel.
  FILTER(LANG(?genreLabel) = "en")
}}
"""
    for attempt in range(3):
        response = requests.post(
            ENDPOINT, data={"query": query, "format": "json"},
            headers={"User-Agent": USER_AGENT}, timeout=60,
        )
        if response.ok:
            return response.json()["results"]["bindings"]
        if attempt < 2 and response.status_code in {429, 500, 502, 503, 504}:
            time.sleep(2 ** attempt)
            continue
        response.raise_for_status()
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_asset", type=Path)
    parser.add_argument("--batch-size", type=int, default=20)
    args = parser.parse_args()
    events = [event for event in load_events(args.data_asset) if not event["x"] and not event["f"]]
    counts = Counter(normalize_artist_component(event["h"]) for event in events)
    labels = {normalize_artist_component(event["h"]): event["h"] for event in events}
    simple = [labels[key] for key, _ in counts.most_common() if not re.search(r"\s(?:\+|x)\s|\||:|\bFestival\b", labels[key], re.I)]
    evidence = defaultdict(lambda: defaultdict(set))
    for offset in range(0, len(simple), args.batch_size):
        for row in query_batch(simple[offset:offset + args.batch_size]):
            evidence[row["label"]["value"]][row["artist"]["value"]].add(row["genreLabel"]["value"])
        time.sleep(1)
    candidates = []
    ambiguous = []
    for name in simple:
        entities = evidence.get(name, {})
        if len(entities) != 1:
            if entities:
                ambiguous.append({"artist": name, "affected_events": counts[normalize_artist_component(name)], "entities": len(entities)})
            continue
        entity, genre_set = next(iter(entities.items()))
        genres = sorted(genre_set)
        category = public_category(genres)
        record = {
            "artist": name, "affected_events": counts[normalize_artist_component(name)],
            "public_genre": category, "wikidata_url": entity,
            "wikidata_genres": genres,
        }
        (candidates if category else ambiguous).append(record)
    print(json.dumps({
        "blank_nonfestival_rows": len(events), "unique_artists": len(counts),
        "queried_exact_simple_labels": len(simple), "candidates": candidates,
        "ambiguous": ambiguous,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
