from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import unicodedata

from concert_calendar.deduplication import normalize_artist_component
from concert_calendar.models import ConcertEvent


PUBLIC_GENRES = (
    "Comedy", "Electronic", "Folk / Country", "French chanson",
    "Hip-hop / Rap", "Jazz / Blues", "Metal / Hard Rock", "Pop",
    "R&B / Soul / Funk", "Reggae / Dub / Ska", "Rock / Indie / Punk",
    "World / Latin",
)

EXACT_RAW_MAPPINGS = {
    "afrobeats": "World / Latin",
    "afropop": "World / Latin",
    "afropop, afrobeats, zouk": "World / Latin",
    "alternative and indie": "Rock / Indie / Punk",
    "alternative and indie, other": "Rock / Indie / Punk",
    "alternative and indie, rock": "Rock / Indie / Punk",
    "bossa nova": "World / Latin",
    "chanson francaise": "French chanson",
    "comedy": "Comedy",
    "country": "Folk / Country",
    "cumbia": "World / Latin",
    "dark / metal": "Metal / Hard Rock",
    "elec, electro / dance / club": "Electronic",
    "electronic": "Electronic",
    "#electronica": "Electronic",
    "electro": "Electronic",
    "folk": "Folk / Country",
    "#folk": "Folk / Country",
    "hard / metal": "Metal / Hard Rock",
    "hard rock et assimiles": "Metal / Hard Rock",
    "hard rock / metal": "Metal / Hard Rock",
    "hip hop / rap": "Hip-hop / Rap",
    "hip hop / rap, rnb / soul": None,
    "hip-hop": "Hip-hop / Rap",
    "#rap": "Hip-hop / Rap",
    "jazz": "Jazz / Blues",
    "k-pop": "Pop",
    "#dreampop": "Pop",
    "#hyperpop": "Pop",
    "#indiepop": "Pop",
    "latin": "World / Latin",
    "latine": "World / Latin",
    "metal / hard rock": "Metal / Hard Rock",
    "musiques electroniques": "Electronic",
    "musiques traditionnelles": "World / Latin",
    "one man show": "Comedy",
    "pop": "Pop",
    "punk": "Rock / Indie / Punk",
    "#indie #rock": "Rock / Indie / Punk",
    "#postpunk #rock #newwave": "Rock / Indie / Punk",
    "#rock": "Rock / Indie / Punk",
    "#rock #punk": "Rock / Indie / Punk",
    "r'n'b": "R&B / Soul / Funk",
    "ragga, reggae, dub et assimiles": "Reggae / Dub / Ska",
    "rap": "Hip-hop / Rap",
    "rap / hip-hop francais": "Hip-hop / Rap",
    "rap / hip-hop international": "Hip-hop / Rap",
    "rap, hip-hop": "Hip-hop / Rap",
    "reggae": "Reggae / Dub / Ska",
    "rnb / soul": "R&B / Soul / Funk",
    "rock": "Rock / Indie / Punk",
    "rock / indie / punk": "Rock / Indie / Punk",
    "rock alternatif": "Rock / Indie / Punk",
    "rock et assimiles": "Rock / Indie / Punk",
    "rock international": "Rock / Indie / Punk",
    "indie": "Rock / Indie / Punk",
    "indie rock": "Rock / Indie / Punk",
    "epic indie music": "Rock / Indie / Punk",
    "concert - indie punk": "Rock / Indie / Punk",
    "concert - indie rock": "Rock / Indie / Punk",
    "concert - math rock": "Rock / Indie / Punk",
    "concert - rock garage fuzz psyche": "Rock / Indie / Punk",
    "concert - rock indie": "Rock / Indie / Punk",
    "concert / grunge, indie rock": "Rock / Indie / Punk",
    "concert / indie rock, garage, shoegaze": "Rock / Indie / Punk",
    "concert post-punk delure": "Rock / Indie / Punk",
    "concert grunge / post-punk / indie rock": "Rock / Indie / Punk",
    "concert indie rock / shoegaze": "Rock / Indie / Punk",
    "concert psych rock": "Rock / Indie / Punk",
    "concert punk oi! / streetpunk": "Rock / Indie / Punk",
    "soul": "R&B / Soul / Funk",
    "concert - soul": "R&B / Soul / Funk",
    "concert - pop contemporaine": "Pop",
    "concert - synth pop": "Pop",
    "concert - minimal experimental pop": "Pop",
    "concert - grime, hip-hop, spoken word": "Hip-hop / Rap",
    "musique du monde, latino": "World / Latin",
    "variete / chanson / pop francaise": "French chanson",
    "variete francaise": "French chanson",
}

WEAK_RAW_GENRES = {
    "rock",
}

SAFE_TOKEN_RULES = (
    ("Rock / Indie / Punk", ("indie rock", "post-punk", "shoegaze", "streetpunk", "math rock", "psych rock")),
    ("Metal / Hard Rock", ("metalcore", "heavy metal")),
    ("Hip-hop / Rap", ("hip-hop", "hiphop", "grime")),
    ("Electronic", ("electronica",)),
    ("R&B / Soul / Funk", ("neo soul", "neosoul")),
    ("World / Latin", ("cumbia",)),
)


def normalize_raw(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", normalized.casefold()).strip()


def map_raw_genre(value: str | None) -> str | None:
    normalized = normalize_raw(value or "")
    public = {normalize_raw(label): label for label in PUBLIC_GENRES}
    if normalized in public:
        return public[normalized]
    if normalized in EXACT_RAW_MAPPINGS:
        return EXACT_RAW_MAPPINGS[normalized]
    matches = {
        genre for genre, tokens in SAFE_TOKEN_RULES
        if any(token in normalized for token in tokens)
    }
    return next(iter(matches)) if len(matches) == 1 else None


def load_reviewed_mappings(path: Path | None = None) -> dict:
    path = path or Path(__file__).with_name("genre_mappings.json")
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("version") != 1:
        raise ValueError("Unsupported artist genre mapping version")
    result = {"artists": {}, "overrides": {}}
    for section in result:
        for record in value.get(section, []):
            genre = record.get("genre")
            artist = record.get("artist")
            required_provenance = (
                record.get("evidence_source"), record.get("evidence_type"),
                record.get("review_date"),
            )
            if genre not in PUBLIC_GENRES or not artist or not all(required_provenance):
                raise ValueError("Malformed reviewed genre mapping")
            identity = normalize_artist_component(artist)
            if identity in result[section]:
                raise ValueError(f"Duplicate reviewed genre identity: {artist}")
            result[section][identity] = record
    return result


def enrich_event_genres(events: list[ConcertEvent], mapping_path: Path | None = None) -> dict:
    mappings = load_reviewed_mappings(mapping_path)
    stats = Counter()
    raw_inventory = Counter()
    raw_sources = defaultdict(set)
    unresolved_raw = Counter()
    conflicts = []
    unresolved_artists = {}

    for event in events:
        event.genre_public = None
        evidence = event.genre_evidence or []
        if event.genre and not evidence:
            evidence = [{"raw": event.genre, "source": event.genre_source or "unknown"}]
        event.genre_evidence = evidence
        for item in evidence:
            if item.get("raw"):
                raw_inventory[item["raw"]] += 1
                raw_sources[item["raw"]].add(item.get("source") or "unknown")

        mapped = {
            map_raw_genre(item.get("raw")) for item in evidence
            if map_raw_genre(item.get("raw"))
        }
        artist_id = normalize_artist_component(event.headliner)
        override = mappings["overrides"].get(artist_id)
        artist = mappings["artists"].get(artist_id)

        weak_source_evidence = bool(evidence) and all(
            normalize_raw(item.get("raw", "")) in WEAK_RAW_GENRES
            for item in evidence
            if item.get("raw")
        )

        if event.festival_name:
            stats["blank_festival"] += 1
        elif artist and len(mapped) == 1 and weak_source_evidence:
            event.genre_public = artist["genre"]
            event.genre_method = "artist_mapping"
            event.genre_source = artist["evidence_source"]
            stats["artist_mapping"] += 1
        elif len(mapped) == 1:
            event.genre_public = next(iter(mapped))
            exact_public = any(normalize_raw(item.get("raw", "")) == normalize_raw(event.genre_public) for item in evidence)
            event.genre_method = "source_explicit" if exact_public else "source_mapping"
            stats[event.genre_method] += 1
        elif override:
            event.genre_public = override["genre"]
            event.genre_method = "manual_override"
            event.genre_source = override["evidence_source"]
            stats["override"] += 1
        elif len(mapped) > 1:
            conflicts.append({"event": event.headliner, "date": event.date, "genres": sorted(mapped)})
            stats["conflict"] += 1
        elif artist:
            event.genre_public = artist["genre"]
            event.genre_method = "artist_mapping"
            event.genre_source = artist["evidence_source"]
            stats["artist_mapping"] += 1
        else:
            stats["blank_no_raw" if not evidence else "blank_unresolved_raw"] += 1
            for item in evidence:
                if item.get("raw"):
                    unresolved_raw[item["raw"]] += 1

        if not event.genre_public:
            identity = normalize_artist_component(event.headliner)
            item = unresolved_artists.setdefault(identity, {
                "artist": event.headliner, "affected_events": 0,
                "raw_genres": set(), "sources": set(),
                "reason": "festival" if event.festival_name else (
                    "conflicting_evidence" if len(mapped) > 1 else
                    ("unresolved_raw" if evidence else "no_raw_evidence")
                ),
            })
            item["affected_events"] += 1
            item["raw_genres"].update(x.get("raw") for x in evidence if x.get("raw"))
            item["sources"].update(x.get("source") for x in evidence if x.get("source"))

    populated = sum(bool(event.genre_public) for event in events)
    return {
        "total": len(events), "populated": populated, "blank": len(events) - populated,
        "coverage_percentage": round(populated * 100 / len(events), 2) if events else 0,
        "source_explicit": stats["source_explicit"], "source_mapping": stats["source_mapping"],
        "artist_mapping": stats["artist_mapping"], "override": stats["override"],
        "blank_no_raw": stats["blank_no_raw"], "blank_unresolved_raw": stats["blank_unresolved_raw"],
        "blank_festival": stats["blank_festival"], "conflict_count": stats["conflict"],
        "conflicts": conflicts, "raw_inventory": dict(raw_inventory.most_common()),
        "raw_sources": {raw: sorted(sources) for raw, sources in sorted(raw_sources.items())},
        "raw_genres": [
            {"raw": raw, "frequency": frequency, "mapped_target": map_raw_genre(raw),
             "sources": sorted(raw_sources[raw])}
            for raw, frequency in raw_inventory.most_common()
        ],
        "artist_mappings": [
            {**record, "method": "manual_override" if section == "overrides" else "artist_mapping"}
            for section, records in mappings.items() for record in records.values()
        ],
        "unresolved_artists": sorted((
            {**item, "raw_genres": sorted(item["raw_genres"]), "sources": sorted(item["sources"])}
            for item in unresolved_artists.values()
        ), key=lambda item: (-item["affected_events"], normalize_raw(item["artist"]))),
        "unresolved_raw": dict(unresolved_raw.most_common()), "vocabulary_violations": 0,
    }
