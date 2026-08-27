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
    "other, pop": "Pop",
    "pop": "Pop",
    "pop, variete internationale": "Pop",
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
    "rock progressif": "Rock / Indie / Punk",
    "indie": "Rock / Indie / Punk",
    "indie rock": "Rock / Indie / Punk",
    "epic indie music": "Rock / Indie / Punk",
    "concert - indie punk": "Rock / Indie / Punk",
    "concert - indie rock": "Rock / Indie / Punk",
    "concert - math rock": "Rock / Indie / Punk",
    "concert - rock garage fuzz psyche": "Rock / Indie / Punk",
    "concert - rock indie": "Rock / Indie / Punk",
    "concert / grunge, indie rock": "Rock / Indie / Punk",
    "concert / the voice, century pop": "Pop",
    "concert / indie rock, garage, shoegaze": "Rock / Indie / Punk",
    "concert post-punk delure": "Rock / Indie / Punk",
    "concert grunge / post-punk / indie rock": "Rock / Indie / Punk",
    "concert indie rock / shoegaze": "Rock / Indie / Punk",
    "concert psych rock": "Rock / Indie / Punk",
    "concert punk oi! / streetpunk": "Rock / Indie / Punk",
    "soul": "R&B / Soul / Funk",
    "concert - soul": "R&B / Soul / Funk",
    "concert - pop contemporaine": "Pop",
    "concert - indie pop": "Pop",
    "concert - synth pop": "Pop",
    "concert - minimal experimental pop": "Pop",
    "concert - grime, hip-hop, spoken word": "Hip-hop / Rap",
    "musique du monde, latino": "World / Latin",
    "variete / chanson / pop francaise": "French chanson",
    "variete francaise": "French chanson",
    "variete internationale": "Pop",
    "#altpop #electropop #pop": "Pop",
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


CONTEXT_GENRE_RULES = (
    ("Jazz / Blues", (
        r"\bmardi jazz\b",
        r"\bjazz a la villette\b",
        r"\bjazzcore\b",
        r"\bjazz\b",
        r"\bblues\b",
        r"\bbebop\b",
    )),
    ("Metal / Hard Rock", (
        r"\bheavy metal\b",
        r"\bmetalcore\b",
        r"\bdeath metal\b",
        r"\bblack metal\b",
        r"\bdoom metal\b",
        r"\bmetal\b",
        r"\bhard rock\b",
    )),
    ("Hip-hop / Rap", (
        r"\bhip[- ]?hop\b",
        r"\brap\b",
        r"\bgrime\b",
        r"\btrap\b",
    )),
    ("Reggae / Dub / Ska", (
        r"\breggae\b",
        r"\bdub\b",
        r"\bska\b",
        r"\bdancehall\b",
    )),
    ("Electronic", (
        r"\belectro\b",
        r"\belectronic\b",
        r"\btechno\b",
        r"\bhouse\b",
        r"\bambient\b",
    )),
    ("R&B / Soul / Funk", (
        r"\br&b\b",
        r"\brnb\b",
        r"\bsoul\b",
        r"\bfunk\b",
        r"\bgospel\b",
    )),
    ("Folk / Country", (
        r"\bfolk\b",
        r"\bcountry\b",
        r"\bamericana\b",
        r"\bbluegrass\b",
    )),
    ("World / Latin", (
        r"\blatin\b",
        r"\bcumbia\b",
        r"\bsalsa\b",
        r"\bmerengue\b",
        r"\bafrobeat\b",
        r"\bafrobeats\b",
        r"\bbossa nova\b",
    )),
    ("French chanson", (
        r"\bchanson\b",
        r"\bvariete francaise\b",
    )),
    ("Rock / Indie / Punk", (
        r"\bpost[- ]?punk\b",
        r"\bshoegaze\b",
        r"\bgarage rock\b",
        r"\bindie rock\b",
        r"\bpunk\b",
        r"\brock\b",
    )),
    ("Pop", (
        r"\bdream pop\b",
        r"\bindie pop\b",
        r"\bhyperpop\b",
        r"\bpop\b",
    )),
)


# Reviewed source-title variants that contain harmless tour, set, or event
# presentation text.  This is an exact allow-list, not a suffix-stripping rule.
REVIEWED_MAPPING_ALIASES = {
    normalize_artist_component("ALELA DIANE (USA)"): "alela diane",
    normalize_artist_component("An Evening with Kristin Hersh"): "kristin hersh",
    normalize_artist_component("Bilal - Celebrating 25 Years of 1st Born Second"): "bilal",
    normalize_artist_component("Bleech 9:3 en concert (côté Records)"): "bleech 9:3",
    normalize_artist_component("BLEOOD : Kill Your Idols Europe Tour"): "bleood",
    normalize_artist_component("CARPENTER BRUT - THE END COMPLETE"): "carpenter brut",
    normalize_artist_component("DIIV — Pitchfork Music Festival Paris 2026"): "diiv",
    normalize_artist_component("DJ KRUSH + GUEST"): "dj krush",
    normalize_artist_component("Elmiene | Sounds For Someone Tour"): "elmiene",
    normalize_artist_component("EsDeeKid : Paris Headline"): "esdeekid",
    normalize_artist_component("Festival de Marne : Alela Diane"): "alela diane",
    normalize_artist_component("Festival de Marne : Charlie Winston"): "charlie winston",
    normalize_artist_component("Festival de Marne : Sinclair"): "sinclair",
    normalize_artist_component("Festival de Marne : Yael Naim"): "yael naim",
    normalize_artist_component("Good Kid - Can We Hang Out? Tour"): "good kid",
    normalize_artist_component('GUADAL TEJAZ Release Party "Megalostrata"'): "guadal tejaz",
    normalize_artist_component("Iceage (Double show) — Pitchfork Music Festival Paris 2026"): "iceage",
    normalize_artist_component("John Craigie en concert (côté Records)"): "john craigie",
    normalize_artist_component("Mark Guiliana - 1er set"): "mark guiliana",
    normalize_artist_component("Mark Guiliana - 2e set"): "mark guiliana",
    normalize_artist_component("Moon Walker | Moon Walker's Wasteland Country Tour"): "moon walker",
    normalize_artist_component("Moon Walker en concert (côté Records)"): "moon walker",
    normalize_artist_component("KYTES en concert (côté Records)"): "kytes",
    normalize_artist_component("Keziah Jones Symphonique"): "keziah jones",
    normalize_artist_component("THE BROOKS au Café de la Danse"): "the brooks",
    normalize_artist_component("TIANA MAJOR9 - November Scorpio Tour"): "tiana major9",
    normalize_artist_component("TIGERCUB – 16H"): "tigercub",
    normalize_artist_component("TIGERCUB – 20H"): "tigercub",
    normalize_artist_component("WOLFGANG VOIGT presents GAS live"): "wolfgang voigt",
    normalize_artist_component("Gracie Abrams: The Look at My Life Tour"): "gracie abrams",
    normalize_artist_component("Kelela - new avatar live"): "kelela",
    normalize_artist_component("Niall Horan - Dinner Party Live On Tour"): "niall horan",
    normalize_artist_component("SHEER MAG (US)"): "sheer mag",
    normalize_artist_component("THE SURFRAJETTES + GUEST"): "the surfrajettes",
    normalize_artist_component("2026 LE SSERAFIM TOUR ‘PUREFLOW’ IN PARIS"): "le sserafim",
    normalize_artist_component("DEXYS MIDNIGHT RUNNERS"): "dexys",
    normalize_artist_component("Renan Luce - Joue Repenti"): "renan luce",
}


def infer_context_genre(event: ConcertEvent) -> str | None:
    parts = [
        event.event_title or "",
        event.series_name or "",
        event.festival_name or "",
    ]
    normalized = normalize_raw(" ".join(parts))
    if not normalized:
        return None
    matches = {
        genre
        for genre, patterns in CONTEXT_GENRE_RULES
        if any(re.search(pattern, normalized) for pattern in patterns)
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


def mapping_for_artist(name: str, mappings: dict) -> dict | None:
    identity = normalize_artist_component(name)
    identity = REVIEWED_MAPPING_ALIASES.get(identity, identity)
    return mappings["overrides"].get(identity) or mappings["artists"].get(identity)


def infer_bill_genre(event: ConcertEvent, mappings: dict) -> str | None:
    if not event.co_headliners:
        return None
    headliner = mapping_for_artist(event.headliner, mappings)
    if not headliner:
        return None
    co_headliner_genres = {
        record["genre"]
        for name in event.co_headliners
        if (record := mapping_for_artist(name, mappings))
    }
    if co_headliner_genres - {headliner["genre"]}:
        return None
    return headliner["genre"]


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
        mapped_artist_id = REVIEWED_MAPPING_ALIASES.get(artist_id, artist_id)
        override = mappings["overrides"].get(mapped_artist_id)
        artist = mappings["artists"].get(mapped_artist_id)

        weak_source_evidence = bool(evidence) and all(
            normalize_raw(item.get("raw", "")) in WEAK_RAW_GENRES
            for item in evidence
            if item.get("raw")
        )

        if event.festival_name:
            event.genre_method = None
            event.genre_source = None
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
        elif override and not event.co_headliners:
            event.genre_public = override["genre"]
            event.genre_method = "manual_override"
            event.genre_source = override["evidence_source"]
            stats["override"] += 1
        elif len(mapped) > 1:
            conflicts.append({"event": event.headliner, "date": event.date, "genres": sorted(mapped)})
            stats["conflict"] += 1
        elif artist and not event.co_headliners:
            event.genre_public = artist["genre"]
            event.genre_method = "artist_mapping"
            event.genre_source = artist["evidence_source"]
            stats["artist_mapping"] += 1
        elif context_genre := infer_context_genre(event):
            event.genre_public = context_genre
            event.genre_method = "event_context"
            event.genre_source = "event_title_or_series"
            stats["event_context"] += 1
        elif bill_genre := infer_bill_genre(event, mappings):
            event.genre_public = bill_genre
            event.genre_method = "bill_consensus"
            event.genre_source = "mapped_bill_artists"
            stats["bill_consensus"] += 1
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
        "event_context": stats["event_context"], "bill_consensus": stats["bill_consensus"],
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
