from __future__ import annotations

from collections import defaultdict
from html import unescape

import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from concert_calendar.models import ConcertEvent
from concert_calendar.venues import normalize_event_venue, normalize_venue_key


ARTIST_ALIASES = {
    "alison’s halo": "alison's halo",
    "day we ran": "dayweran",
    "etran de l'aïr": "étran de l'aïr",
    "f.f.f.": "fff",
    "the flamin' groovies": "flamin' groovies",
    "gaëlle joly": "gaelle joly",
    "gregoire jokic": "grégoire jokic",
    "howlin’ jaws": "howlin' jaws",
    "la p’tité fumée": "la p’tite fumée",
    "la 808e nuit": "la 808eme nuit",
    "la 808ème nuit": "la 808eme nuit",
    "la securite": "la sécurité",
    "lewis ofman – festivals": "lewis ofman",
    "ms. lauryn hill": "lauryn hill",
    "noe preszow": "noé preszow",
    "kiwi jr.": "kiwi jr",
    "sebastien tellier": "sébastien tellier",
    "westside cowboys": "westside cowboy",
    "zoh amba (les femmes s’en mêlent)": (
        "zoh amba (les femmes s'en mêlent)"
    ),
}


# Exact reviewed display-title variants for the same performing identity.  The
# values intentionally exclude timed/set labels and bills that introduce other
# artists.  This keeps tour and presentation copy searchable while allowing
# conservative date + canonical-venue event reconciliation.
DESCRIPTIVE_ARTIST_ALIASES = {
    "2026 le sserafim tour ‘pureflow’ in paris": "le sserafim",
    "a$ap rocky - don't be dumb world tour": "a$ap rocky",
    "accept 50th anniversary tour 2026": "accept",
    "a6el – tournée d’automne": "a6el",
    "asake: in god we trust world tour": "asake",
    "bilal - celebrating 25 years of 1st born second": "bilal",
    "bleech 9:3 en concert (côté records)": "bleech 9:3",
    "bleood : kill your idols europe tour": "bleood",
    "chaton - la cigale": "chaton",
    "diiv — pitchfork music festival paris 2026": "diiv",
    "earl sweatshirt & mike | home on the range tour 2026": (
        "earl sweatshirt & mike"
    ),
    "elmiene | sounds for someone tour": "elmiene",
    "esdeekid : paris headline": "esdeekid",
    "good kid - can we hang out? tour": "good kid",
    "gracie abrams: the look at my life tour": "gracie abrams",
    "guadal tejaz release party \"megalostrata\"": "guadal tejaz",
    "haute & freddy: big disgrace tour": "haute & freddy",
    "j.cole : the fall-off tour": "j. cole",
    "john craigie en concert (côté records)": "john craigie",
    "kanadia en concert (côté records)": "kanadia",
    "katseye - the wildworld tour": "katseye",
    "kytes en concert (côté records)": "kytes",
    "moon walker en concert (côté records)": "moon walker",
    "moon walker | moon walker's wasteland country tour": "moon walker",
    "niall horan - dinner party live on tour": "niall horan",
    "placebo : 30th anniversary tour": "placebo",
    "renan luce - joue repenti": "renan luce",
    "stu larsen en concert (côté records)": "stu larsen",
    "tamarae en concert (côté records)": "tamarae",
}


# Reviewed event-level equivalences.  They intentionally do not generalize to
# other artists, dates, venues, or editorial phrases.
REVIEWED_EVENT_TITLES = {
    ("2026-09-09", "accor arena", "katseye"): (
        "KATSEYE - THE WILDWORLD TOUR"
    ),
    ("2026-09-19", "accor arena", "the pussycat dolls"): "The Pussycat Dolls",
    (
        "2026-09-19", "accor arena",
        "the pussycat dolls - pcd forever tour",
    ): "The Pussycat Dolls",
    ("2026-09-23", "la gaite lyrique", "wolfgang voigt"): (
        "WOLFGANG VOIGT presents GAS live"
    ),
    (
        "2026-09-23", "la gaite lyrique",
        "wolfgang voigt presents gas live",
    ): "WOLFGANG VOIGT presents GAS live",
    ("2026-09-30", "le hasard ludique", "augusta"): "Augusta (full band)",
    (
        "2026-09-30", "le hasard ludique", "augusta (full band)",
    ): "Augusta (full band)",
    ("2026-10-28", "la boule noire", "crenoka"): "CRENOKA (RELEASE PARTY)",
    (
        "2026-10-28", "la boule noire", "crenoka (release party)",
    ): "CRENOKA (RELEASE PARTY)",
    (
        "2026-11-02", "accor arena", "the world of hans zimmer",
    ): "THE WORLD OF HANS ZIMMER - A NEW DIMENSION",
    (
        "2026-11-02", "accor arena",
        "the world of hans zimmer - a new dimension",
    ): "THE WORLD OF HANS ZIMMER - A NEW DIMENSION",
    (
        "2027-02-10", "accor arena", "five finger death punch et lamb of god",
    ): "FIVE FINGER DEATH PUNCH",
    (
        "2027-02-10", "accor arena", "five finger death punch",
    ): "FIVE FINGER DEATH PUNCH",
    ("2027-03-18", "l olympia bruno coquatrix", "chloe"): "CHLOÉ (Live)",
    (
        "2027-03-18", "l olympia bruno coquatrix", "chloe (live)",
    ): "CHLOÉ (Live)",
    ("2026-09-05", "l olympia bruno coquatrix", "ronnie wood"): (
        "Ronnie Wood and His Band featuring Imelda May"
    ),
    (
        "2026-09-05", "l olympia bruno coquatrix",
        "ronnie wood and his band featuring imelda may",
    ): "Ronnie Wood and His Band featuring Imelda May",
    (
        "2026-09-12", "point ephemere",
        "ftv unplugged : carte blanche a grandma's ashes",
    ): "FTV UNPLUGGED : GRANDMA'S ASHES",
    (
        "2026-09-12", "point ephemere",
        "ftv unplugged : grandma's ashes",
    ): "FTV UNPLUGGED : GRANDMA'S ASHES",
}


# These relocations were individually reviewed against current authoritative
# listings.  The key is deliberately date + artist + old/new canonical venue.
REVIEWED_EVENT_MOVES = (
    ("2026-10-06", "father of peace", "L'Alhambra", "La Maroquinerie"),
    (
        "2026-10-06", "humanity's last breath",
        "Petit Bain", "La Machine du Moulin Rouge",
    ),
    ("2026-10-10", "paris jackson", "L'Alhambra", "La Bellevilloise"),
    ("2026-10-19", "my new band believe", "Point Éphémère", "La Maroquinerie"),
    ("2026-11-20", "zebrahead", "La Maroquinerie", "L'Alhambra"),
    ("2026-12-10", "blondshell", "La Gaîté Lyrique", "Élysée Montmartre"),
)


# Individually reviewed same-event bills.  These are deliberately scoped by
# date, canonical venue, and the complete set of source-card artist identities.
REVIEWED_EVENT_BILLS = (
    {
        "date": "2026-11-16",
        "venue": "Le Zénith Paris – La Villette",
        "artists": ("bloc party", "interpol"),
        "headliner": "Bloc Party",
        "co_headliners": ["Interpol"],
    },
    {
        "date": "2026-12-02",
        "venue": "Paul B – Massy",
        "artists": ("alma rechtman", "gildaa"),
        "headliner": "Alma Rechtman",
        "co_headliners": ["Gildaa"],
    },
    {
        "date": "2026-12-07",
        "venue": "Le Zénith Paris – La Villette",
        "artists": ("electric pyramid", "the dire straits experience"),
        "headliner": "The Dire Straits Experience",
        "openers": ["Electric Pyramid"],
    },
    {
        "date": "2027-02-16",
        "venue": "La Maroquinerie",
        "artists": ("bernth", "escape the internet"),
        "headliner": "Escape The Internet (feat. Bernth)",
    },
)

# The official Adidas Arena event page explicitly bills this special guest.
# GDP currently exposes the two artists as separate cards with one event URL.
VERIFIED_SUPPORT_RELATIONSHIPS = {
    ("2026-08-26", "adidas arena", "hollywood vampires"): (
        "The Last Internationale",
    ),
}

VERIFIED_ARTIST_DISPLAY_NAMES = {
    "deep purple": "Deep Purple",
    "eagles of death metal": "Eagles of Death Metal",
    "hollywood vampires": "Hollywood Vampires",
    "the last internationale": "The Last Internationale",
    "uriah heep": "Uriah Heep",
}

BILL_SEPARATOR_RE = re.compile(r"\s+(?:\+|•)\s+")
GENERIC_GUEST_RE = re.compile(r"\s+\+\s+guests?\s*$", re.IGNORECASE)
TIME_SUFFIX_RE = re.compile(r"\s+[–-]\s*(\d{1,2})\s*h(?:\s*(\d{2}))?\s*$", re.IGNORECASE)
SET_SUFFIX_RE = re.compile(r"\s+-\s+(?:1er|2e)\s+set\s*$", re.IGNORECASE)


def normalize_headliner(name: str) -> str:
    """Normalize an artist name for conservative exact deduplication."""

    if not name:
        return ""

    name = unescape(name).lower().strip()
    name = re.sub(r"\s+", " ", name)
    name = ARTIST_ALIASES.get(name, name)
    return DESCRIPTIVE_ARTIST_ALIASES.get(name, name)


def normalize_artist_component(name: str) -> str:
    """Return an accent-insensitive identity for explicit bill components."""

    normalized = unicodedata.normalize("NFKD", normalize_headliner(name))
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
    normalized = normalized.replace("’", "'")
    normalized = normalized.replace("&", " and ")
    return re.sub(r"\s+", " ", normalized).strip()


def build_event_key(event: ConcertEvent) -> tuple:
    """Build the stable date/headliner/venue exact-match key."""

    return (
        event.date,
        normalize_artist_component(event.headliner),
        (event.venue or "").lower().strip(),
    )


def _base_generic_guest_title(value: str) -> str | None:
    decoded = unescape(value or "")
    base = GENERIC_GUEST_RE.sub("", decoded).strip()
    return base if base != decoded.strip() else None


def _apply_reviewed_event_rules(events: list[ConcertEvent]) -> None:
    for event in events:
        event.headliner = unescape(event.headliner)
        event.openers = [unescape(value) for value in (event.openers or [])] or None
        event.co_headliners = [
            unescape(value) for value in (event.co_headliners or [])
        ] or None
        if event.event_title:
            event.event_title = unescape(event.event_title)
        if event.series_name:
            event.series_name = unescape(event.series_name)
        venue_identity = normalize_venue_key(event.venue)
        artist_identity = normalize_artist_component(event.headliner)
        reviewed_title = REVIEWED_EVENT_TITLES.get(
            (event.date, venue_identity, artist_identity)
        )
        if reviewed_title:
            event.headliner = reviewed_title

        first_component = _split_full_bill(event.headliner)
        move_artist = normalize_artist_component(
            first_component[0] if first_component else event.headliner
        )
        for date, artist, old_venue, new_venue in REVIEWED_EVENT_MOVES:
            if (
                event.date == date
                and move_artist == artist
                and event.venue in {old_venue, new_venue}
            ):
                event.venue = new_venue
                normalize_event_venue(event)
                break


def _stable_unique(values: list[str]) -> list[str] | None:
    result = []
    seen = set()

    for value in values:
        identity = normalize_artist_component(value)

        if not identity or identity in seen:
            continue

        seen.add(identity)
        result.append(value)

    return result or None


def _valid_http_url(value: str | None) -> bool:
    if not value:
        return False

    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def merge_events(
    existing: ConcertEvent,
    incoming: ConcertEvent,
) -> ConcertEvent:
    """Add safe missing metadata while retaining the preferred base record."""

    existing.openers = _stable_unique(
        [*(existing.openers or []), *(incoming.openers or [])]
    )
    existing.co_headliners = _stable_unique(
        [*(existing.co_headliners or []), *(incoming.co_headliners or [])]
    ) or None
    opener_identities = {
        normalize_artist_component(value) for value in (existing.openers or [])
    }
    existing.co_headliners = [
        value for value in (existing.co_headliners or [])
        if normalize_artist_component(value) not in opener_identities
    ] or None
    existing.promoters = sorted(
        {*(existing.promoters or []), *(incoming.promoters or [])}
    ) or None
    existing.source_names = sorted(
        {*(existing.source_names or []), *(incoming.source_names or [])}
    ) or None

    if not existing.genre and incoming.genre:
        existing.genre = incoming.genre

    for field in ("genre_public", "genre_source", "genre_method", "announced_at"):
        if not getattr(existing, field) and getattr(incoming, field):
            setattr(existing, field, getattr(incoming, field))

    combined_genre_evidence = []
    seen_genre_evidence = set()
    for item in [*(existing.genre_evidence or []), *(incoming.genre_evidence or [])]:
        identity = ((item.get("raw") or "").casefold(), item.get("source") or "")
        if identity not in seen_genre_evidence:
            combined_genre_evidence.append(item)
            seen_genre_evidence.add(identity)
    existing.genre_evidence = combined_genre_evidence or None

    if not existing.facebook_event_url and incoming.facebook_event_url:
        existing.facebook_event_url = incoming.facebook_event_url

    if incoming.authoritative_billing and _valid_http_url(incoming.ticket_url):
        existing.ticket_url = incoming.ticket_url
    elif not existing.ticket_url and _valid_http_url(incoming.ticket_url):
        existing.ticket_url = incoming.ticket_url

    existing.festival_name = existing.festival_name or incoming.festival_name
    existing.authoritative_billing = (
        existing.authoritative_billing or incoming.authoritative_billing
    )
    existing.sold_out = existing.sold_out or incoming.sold_out
    status_priority = {
        None: 0, "tickets": 1, "not_on_sale": 2, "free": 3,
        "sold_out": 4, "postponed": 5, "cancelled": 6,
    }
    if status_priority.get(incoming.ticket_status, 0) > status_priority.get(existing.ticket_status, 0):
        existing.ticket_status = incoming.ticket_status
    if not existing.start_time and incoming.start_time:
        existing.start_time = incoming.start_time

    if not existing.event_title and incoming.event_title:
        existing.event_title = incoming.event_title

    if not existing.series_name and incoming.series_name:
        existing.series_name = incoming.series_name

    if not existing.image_url and incoming.image_url:
        existing.image_url = incoming.image_url
        existing.image_source = incoming.image_source
    elif (
        existing.image_url
        and not existing.image_source
        and incoming.image_source
    ):
        existing.image_source = incoming.image_source

    if incoming.electric_eye_links:
        combined_links = [
            *(existing.electric_eye_links or []),
            *incoming.electric_eye_links,
        ]

        seen_urls = set()
        unique_links = []

        for link in combined_links:
            url = (link or {}).get("url")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            unique_links.append(link)

        existing.electric_eye_links = unique_links or None

    return existing


def _split_full_bill(value: str) -> list[str]:
    parts = BILL_SEPARATOR_RE.split(value or "")
    return parts if len(parts) > 1 else []


def _matches_structured_bill(
    structured: ConcertEvent,
    full_bill: ConcertEvent,
) -> bool:
    structured_artists = [
        *(structured.openers or []), *(structured.co_headliners or [])
    ]
    if not structured_artists or full_bill.openers or full_bill.co_headliners:
        return False

    components = _split_full_bill(full_bill.headliner)

    if not components:
        return False

    normalized_bill = [normalize_artist_component(value) for value in components]
    normalized_structured = [
        normalize_artist_component(value)
        for value in [structured.headliner, *structured_artists]
    ]

    return (
        normalized_bill[0] == normalized_structured[0]
        and sorted(normalized_bill) == sorted(normalized_structured)
    )


def _same_event_specific_ticket(
    left: ConcertEvent,
    right: ConcertEvent,
) -> bool:
    if not (_valid_http_url(left.ticket_url) and _valid_http_url(right.ticket_url)):
        return False

    if left.festival_name or right.festival_name:
        return False

    def normalized(value: str) -> str | None:
        parsed = urlparse(value)
        path = re.sub(r"/+", "/", parsed.path).rstrip("/")
        generic_paths = {"", "/agenda", "/events", "/event", "/billetterie", "/tickets"}
        query = [
            (key, item) for key, item in parse_qsl(parsed.query, keep_blank_values=True)
            if not key.casefold().startswith("utm_")
        ]
        if path.casefold() in generic_paths and not query:
            return None
        return urlunparse((
            parsed.scheme.casefold(), parsed.netloc.casefold(), path,
            "", urlencode(sorted(query)), "",
        ))

    return normalized(left.ticket_url) == normalized(right.ticket_url) is not None


def _shared_promoter(left: ConcertEvent, right: ConcertEvent) -> bool:
    return bool(set(left.promoters or []) & set(right.promoters or []))


def _official_and_aggregator_corroboration(
    left: ConcertEvent, right: ConcertEvent
) -> bool:
    sources = set(left.source_names or []) | set(right.source_names or [])
    return "DICE" in sources and bool(sources - {"DICE"})


def _apply_verified_support_relationships(events: list[ConcertEvent]) -> None:
    grouped = defaultdict(list)

    for event in events:
        grouped[(event.date, (event.venue or "").casefold().strip())].append(event)

    for (date, venue, headliner), opener_names in VERIFIED_SUPPORT_RELATIONSHIPS.items():
        group = grouped.get((date, venue), [])
        parent = next(
            (
                event
                for event in group
                if normalize_artist_component(event.headliner) == headliner
            ),
            None,
        )

        if parent is None:
            continue

        available = {
            normalize_artist_component(event.headliner): event.headliner
            for event in group
        }
        verified_openers = [
            available[normalize_artist_component(opener)]
            for opener in opener_names
            if normalize_artist_component(opener) in available
        ]

        if verified_openers:
            parent.openers = _stable_unique(
                [*(parent.openers or []), *verified_openers]
            )


def _display_candidates(events: list[ConcertEvent]) -> dict[str, str]:
    candidates: dict[str, str] = {}

    for event in events:
        for name in [event.headliner, *(event.openers or [])]:
            identity = normalize_artist_component(name)
            letters = [character for character in name if character.isalpha()]
            is_mixed_case = (
                any(character.islower() for character in letters)
                and any(character.isupper() for character in letters)
            )

            if identity and is_mixed_case and identity not in candidates:
                candidates[identity] = name

    mapping_path = Path(__file__).with_name("genre_mappings.json")
    try:
        mapping_data = json.loads(mapping_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        mapping_data = {}

    for section in ("artists", "overrides"):
        for record in mapping_data.get(section, []):
            artist = (record.get("artist") or "").strip()
            if artist:
                candidates[normalize_artist_component(artist)] = artist

    candidates.update(VERIFIED_ARTIST_DISPLAY_NAMES)
    return candidates


def _apply_display_capitalization(
    events: list[ConcertEvent],
    candidates: dict[str, str],
) -> None:
    def canonicalize(name: str) -> str:
        letters = [character for character in name if character.isalpha()]
        is_all_caps = bool(letters) and all(
            not character.islower()
            for character in letters
        )

        if not is_all_caps:
            return name

        return candidates.get(normalize_artist_component(name), name)

    for event in events:
        event.headliner = canonicalize(event.headliner)
        event.openers = [
            canonicalize(opener)
            for opener in (event.openers or [])
        ] or None
        event.co_headliners = [
            canonicalize(artist)
            for artist in (event.co_headliners or [])
        ] or None


def _deduplicate_exact(events: list[ConcertEvent]) -> list[ConcertEvent]:
    deduplicated: dict[tuple, ConcertEvent] = {}

    for event in events:
        key = build_event_key(event)
        if key in deduplicated:
            merge_events(deduplicated[key], event)
        else:
            deduplicated[key] = event

    return list(deduplicated.values())


def _reconcile_reviewed_event_bills(events: list[ConcertEvent]) -> list[ConcertEvent]:
    """Apply only the four manually reviewed event-level billing decisions."""

    removed = set()
    for rule in REVIEWED_EVENT_BILLS:
        venue = normalize_venue_key(rule["venue"])
        expected = set(rule["artists"])
        matches = [
            event for event in events
            if id(event) not in removed
            and event.date == rule["date"]
            and normalize_venue_key(event.venue) == venue
            and normalize_artist_component(event.headliner) in expected
        ]
        if {normalize_artist_component(event.headliner) for event in matches} != expected:
            continue

        preferred = normalize_artist_component(rule["headliner"])
        base = next(
            (event for event in matches if normalize_artist_component(event.headliner) == preferred),
            matches[0],
        )
        for event in matches:
            if event is not base:
                merge_events(base, event)
                removed.add(id(event))
        base.headliner = rule["headliner"]
        base.openers = list(rule.get("openers", [])) or None
        base.co_headliners = list(rule.get("co_headliners", [])) or None

    return [event for event in events if id(event) not in removed]


def _reconcile_generic_guest_titles(events: list[ConcertEvent]) -> list[ConcertEvent]:
    grouped = defaultdict(list)
    for event in events:
        grouped[(event.date, normalize_venue_key(event.venue))].append(event)

    removed = set()
    for group in grouped.values():
        for marked in group:
            base = _base_generic_guest_title(marked.headliner)
            if not base or id(marked) in removed:
                continue
            base_identity = normalize_artist_component(base)
            for plain in group:
                if plain is marked or id(plain) in removed:
                    continue
                if normalize_artist_component(plain.headliner) != base_identity:
                    continue
                if not (
                    _same_event_specific_ticket(plain, marked)
                    or _shared_promoter(plain, marked)
                    or _official_and_aggregator_corroboration(plain, marked)
                ):
                    continue
                merge_events(plain, marked)
                removed.add(id(marked))
                break
    return [event for event in events if id(event) not in removed]


def _reconcile_time_labeled_titles(events: list[ConcertEvent]) -> list[ConcertEvent]:
    """Attach a plain source card only to an explicitly matching timed show."""

    grouped = defaultdict(list)
    for event in events:
        grouped[(event.date, normalize_venue_key(event.venue))].append(event)
    removed = set()
    for group in grouped.values():
        for labeled in group:
            match = TIME_SUFFIX_RE.search(labeled.headliner)
            if not match:
                continue
            base = labeled.headliner[:match.start()].strip()
            expected_time = f"{int(match.group(1)):02d}:{match.group(2) or '00'}"
            for plain in group:
                if plain is labeled or id(plain) in removed:
                    continue
                if normalize_artist_component(plain.headliner) != normalize_artist_component(base):
                    continue
                if plain.start_time != expected_time:
                    continue
                merge_events(labeled, plain)
                removed.add(id(plain))
                break
    return [event for event in events if id(event) not in removed]


def _reconcile_multi_set_parent_cards(events: list[ConcertEvent]) -> list[ConcertEvent]:
    """Remove one generic product when explicit first/second-set rows exist."""

    grouped = defaultdict(list)
    for event in events:
        grouped[(event.date, normalize_venue_key(event.venue))].append(event)
    removed = set()
    for group in grouped.values():
        labeled_by_base = defaultdict(list)
        for event in group:
            match = SET_SUFFIX_RE.search(event.headliner)
            if match:
                labeled_by_base[
                    normalize_artist_component(event.headliner[:match.start()])
                ].append(event)
        for base, labeled in labeled_by_base.items():
            if len(labeled) < 2:
                continue
            parent = next(
                (
                    event for event in group
                    if event not in labeled
                    and normalize_artist_component(event.headliner) == base
                ),
                None,
            )
            if parent is None:
                continue
            for performance in labeled:
                merge_events(performance, parent)
            removed.add(id(parent))
    return [event for event in events if id(event) not in removed]


def _reconcile_full_bills(events: list[ConcertEvent]) -> list[ConcertEvent]:
    grouped = defaultdict(list)

    for event in events:
        grouped[(event.date, (event.venue or "").casefold().strip())].append(event)

    removed = set()

    for group in grouped.values():
        structured_records = [
            event for event in group if event.openers or event.co_headliners
        ]
        full_bills = [
            event for event in group
            if not event.openers and not event.co_headliners
        ]

        for structured in structured_records:
            for full_bill in full_bills:
                if id(full_bill) in removed:
                    continue

                if _matches_structured_bill(structured, full_bill):
                    merge_events(structured, full_bill)
                    removed.add(id(full_bill))

    return [event for event in events if id(event) not in removed]


def _collapse_explicit_support_cards(
    events: list[ConcertEvent],
) -> list[ConcertEvent]:
    grouped = defaultdict(list)

    for event in events:
        grouped[(event.date, (event.venue or "").casefold().strip())].append(event)

    removed = set()

    for group in grouped.values():
        for parent in group:
            opener_identities = {
                normalize_artist_component(opener)
                for opener in (parent.openers or [])
            }

            if not opener_identities:
                continue

            for candidate in group:
                if candidate is parent or id(candidate) in removed:
                    continue

                if normalize_artist_component(candidate.headliner) not in opener_identities:
                    continue

                if not (
                    _same_event_specific_ticket(parent, candidate)
                    or _shared_promoter(parent, candidate)
                ):
                    continue

                merge_events(parent, candidate)
                removed.add(id(candidate))

    return [event for event in events if id(event) not in removed]


def _consolidate_authoritative_festivals(
    events: list[ConcertEvent],
    diagnostics: dict | None = None,
) -> list[ConcertEvent]:
    """Replace artist products with one authoritative festival-day bill."""

    grouped = defaultdict(list)

    for event in events:
        grouped[(event.date, (event.venue or "").casefold().strip())].append(event)

    removed = set()
    days_aggregated = 0

    for group in grouped.values():
        authoritative = [
            event
            for event in group
            if event.authoritative_billing and event.festival_name and event.openers
        ]

        if len(authoritative) != 1:
            if len(group) > 1 and any(event.festival_name for event in group):
                print(
                    "Ambiguous festival-day billing retained: "
                    f"{group[0].date} — {group[0].venue}"
                )
            continue

        parent = authoritative[0]
        lineup_identities = {
            normalize_artist_component(name)
            for name in [parent.headliner, *(parent.openers or [])]
        }
        collapsed_here = 0

        for candidate in group:
            if candidate is parent or id(candidate) in removed:
                continue
            if normalize_artist_component(candidate.headliner) not in lineup_identities:
                continue

            merge_events(parent, candidate)
            removed.add(id(candidate))
            collapsed_here += 1

        if collapsed_here:
            days_aggregated += 1

    if diagnostics is not None:
        diagnostics["festival_days_aggregated"] = days_aggregated
        diagnostics["festival_artist_rows_collapsed"] = len(removed)

    return [event for event in events if id(event) not in removed]


def deduplicate_events(
    events: list[ConcertEvent],
    diagnostics: dict | None = None,
) -> list[ConcertEvent]:
    """Collapse exact and explicitly reconcilable duplicate concerts."""

    initial_opener_state = defaultdict(list)

    for event in events:
        initial_opener_state[build_event_key(event)].append(bool(event.openers))

    _apply_reviewed_event_rules(events)
    festival_represented_rows = _count_represented_festival_rows(events)
    display_candidates = _display_candidates(events)
    reconciled = _deduplicate_exact(events)
    reconciled = _reconcile_reviewed_event_bills(reconciled)
    _apply_verified_support_relationships(reconciled)
    reconciled = _reconcile_full_bills(reconciled)
    reconciled = _reconcile_generic_guest_titles(reconciled)
    reconciled = _reconcile_time_labeled_titles(reconciled)
    reconciled = _reconcile_multi_set_parent_cards(reconciled)
    reconciled = _consolidate_authoritative_festivals(reconciled, diagnostics)
    reconciled = _collapse_explicit_support_cards(reconciled)
    _apply_display_capitalization(reconciled, display_candidates)

    if diagnostics is not None:
        diagnostics["festival_artist_rows_collapsed"] = max(
            diagnostics.get("festival_artist_rows_collapsed", 0),
            festival_represented_rows,
        )
        diagnostics["unresolved_candidates"] = _unresolved_candidates(reconciled)

    if diagnostics is not None:
        diagnostics["opener_enriched_records"] = sum(
            bool(event.openers)
            and False in initial_opener_state.get(build_event_key(event), [])
            and True in initial_opener_state.get(build_event_key(event), [])
            for event in reconciled
        )

    return reconciled


def _count_represented_festival_rows(events: list[ConcertEvent]) -> int:
    """Count source rows represented by authoritative festival-day bills."""

    total = 0
    for parent in events:
        if not (parent.authoritative_billing and parent.festival_name and parent.openers):
            continue
        identities = {
            normalize_artist_component(name)
            for name in [parent.headliner, *(parent.openers or [])]
        }
        represented = sum(
            event is not parent
            and event.date == parent.date
            and normalize_venue_key(event.venue) == normalize_venue_key(parent.venue)
            and normalize_artist_component(event.headliner) in identities
            for event in events
        )
        total += represented
    return total


def _unresolved_candidates(events: list[ConcertEvent], limit: int = 50) -> list[dict]:
    """Return bounded, evidence-rich candidates without merging them."""

    candidates = []
    by_date_artist = defaultdict(list)
    by_ticket = defaultdict(list)
    for event in events:
        by_date_artist[(event.date, normalize_artist_component(event.headliner))].append(event)
        if _valid_http_url(event.ticket_url):
            by_ticket[event.ticket_url.rstrip("/")].append(event)

    for (date, artist), group in by_date_artist.items():
        venues = {event.venue for event in group}
        if len(venues) > 1:
            candidates.append({
                "kind": "venue_conflict", "date": date, "artist": artist,
                "venues": sorted(venues),
                "sources": sorted({s for event in group for s in (event.source_names or [])}),
            })

    for url, group in by_ticket.items():
        by_date = defaultdict(list)
        for event in group:
            by_date[event.date].append(event)
        for same_day in by_date.values():
            if len(same_day) < 2 or not _same_event_specific_ticket(same_day[0], same_day[1]):
                continue
            timed_bases = []
            timed_values = []
            for event in same_day:
                match = TIME_SUFFIX_RE.search(event.headliner)
                if not match:
                    break
                timed_bases.append(normalize_artist_component(event.headliner[:match.start()]))
                timed_values.append(
                    f"{int(match.group(1)):02d}:{match.group(2) or '00'}"
                )
            else:
                if (
                    len(set(timed_bases)) == 1
                    and len(set(timed_values)) == len(same_day)
                    and all(
                        event.start_time == expected
                        for event, expected in zip(same_day, timed_values)
                    )
                ):
                    continue
            fingerprints = {(event.venue, event.headliner) for event in same_day}
            if len(fingerprints) > 1:
                candidates.append({
                    "kind": "shared_event_ticket", "ticket_url": url,
                    "events": [
                        {
                            "date": event.date, "headliner": event.headliner,
                            "venue": event.venue,
                            "sources": event.source_names or [],
                        }
                        for event in same_day[:10]
                    ],
                })

    return candidates[:limit]
