from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from difflib import SequenceMatcher
from html import unescape
from itertools import combinations

import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import parse_qsl, unquote, urlencode, urlparse, urlunparse

from concert_calendar.models import ConcertEvent
from concert_calendar.billing_semantics import apply_structured_performer_semantics
from concert_calendar.artist_billings import apply_reviewed_artist_billings
from concert_calendar.event_titles import (
    artist_title_parts, contextual_title_parts, evidenced_series_prefixes, title_identity,
    separate_performance_marker,
)
from concert_calendar.venues import normalize_event_venue, normalize_venue_key, VENUE_ALIASES


TARGET_VENUE_IMAGE_SOURCES = {
    "New Morning", "La Maroquinerie", "Le Trabendo", "La Gaîté Lyrique",
    "Le Hasard Ludique", "Le Zénith Paris – La Villette", "Petit Bain",
    "La Boule Noire", "Salle Pleyel", "Élysée Montmartre",
    "Café de la Danse",
}

DISCOVERY_IMAGE_SOURCES = {
    "Los Production",
    "On the RoaD Again / ORDA",
}


def image_source_priority(source):
    """Keep this pass's venue-card artwork below existing official imagery."""

    if not source or source == "DICE" or source in DISCOVERY_IMAGE_SOURCES:
        return 0
    return 1 if source in TARGET_VENUE_IMAGE_SOURCES else 2


ARTIST_ALIASES = {
    "alison’s halo": "alison's halo",
    "day we ran": "dayweran",
    "dexys midnight runners": "dexys",
    "etran de l'aïr": "étran de l'aïr",
    "f.f.f.": "fff",
    "the flamin' groovies": "flamin' groovies",
    "the afghan wigs": "the afghan whigs",
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
    "two door cinema": "two door cinema club",
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
    # Stade de France's artist heading identifies JAŸ-Z; the event row uses
    # JAŸ-Z 30 as branding. Reviewed 2026-09-07 against the official listing:
    # https://www.stadefrance.com/fr/billetterie/jay-z-30
    # Deliberately event-scoped: numbers remain valid parts of artist names.
    ("2026-09-10", "stade de france", "jay-z"): "JAŸ-Z",
    ("2026-09-10", "stade de france", "jay-z 30"): "JAŸ-Z",
    (
        "2026-10-13", "cafe de la danse", "the brooks",
    ): "The Brooks",
    (
        "2026-10-13", "cafe de la danse",
        "the brooks au cafe de la danse",
    ): "The Brooks",
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
    (
        "2026-10-16", "la marbrerie", "qual and psyche",
    ): "QUAL & PSYCHE",
    (
        "2026-10-16", "la marbrerie", "qual , psyche",
    ): "QUAL & PSYCHE",
    (
        "2026-11-23", "le chinois", "litvrgy",
    ): "Liturgy",
    (
        "2026-11-23", "le chinois", "liturgy",
    ): "Liturgy",
    (
        "2027-02-20", "bal chavaux", "das ich + diary of dreams",
    ): "Das Ich + Diary of Dreams",
    (
        "2027-02-20", "bal chavaux", "diary of dreams + das ich",
    ): "Das Ich + Diary of Dreams",
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
    ("2026-10-10", "paris jackson", "L'Alhambra", "La Bellevilloise"),
    ("2026-10-19", "my new band believe", "Point Éphémère", "La Maroquinerie"),
    ("2026-11-20", "zebrahead", "La Maroquinerie", "L'Alhambra"),
    ("2026-12-10", "blondshell", "La Gaîté Lyrique", "Élysée Montmartre"),
    ("2026-10-30", "clawfinger", "Élysée Montmartre", "Le Trabendo"),
    ("2026-09-13", "os garotin", "Cabaret Sauvage", "New Morning"),
    ("2027-03-18", "south arcade", "Backstage By The Mill", "L'Alhambra"),
)


# Individually reviewed same-event bills.  These are deliberately scoped by
# date, canonical venue, and the complete set of source-card artist identities.
REVIEWED_EVENT_BILLS = (
    {
        "date": "2027-03-09",
        "venue": "Élysée Montmartre",
        "artists": ("graveyard and blues pills",),
        "headliner": "GRAVEYARD",
        "co_headliners": ["BLUES PILLS"],
        "openers": ["SPIDERS"],
    },
    {
        "date": "2027-03-21",
        "venue": "Petit Bain",
        "artists": ("evil invaders and exhorder and heathen",),
        "headliner": "EVIL INVADERS",
        "co_headliners": ["EXHORDER", "HEATHEN"],
        "openers": ["WARFIELD"],
    },
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
    "chvrches": "CHVRCHES",
    "deep purple": "Deep Purple",
    "eagles of death metal": "Eagles of Death Metal",
    "hollywood vampires": "Hollywood Vampires",
    "the last internationale": "The Last Internationale",
    "uriah heep": "Uriah Heep",
    "6lack": "6LACK",
    "diiv": "DIIV",
    "fkj": "FKJ",
    "katseye": "KATSEYE",
    "mnek": "MNEK",
    "muna": "MUNA",
}

# This parser is intentionally restricted to validating a bill whose artist
# identities were already supplied by structured source evidence. Flat titles
# elsewhere in this module remain opaque.
BILL_SEPARATOR_RE = re.compile(
    r"\s+(?:[+&×/•]|x|and|avec|with)\s+",
    re.IGNORECASE,
)
GENERIC_GUEST_RE = re.compile(
    r"\s+\+\s+(?:special\s+)?guests?\s*$",
    re.IGNORECASE,
)
TIME_SUFFIX_RE = re.compile(r"\s+[–-]\s*(\d{1,2})\s*h(?:\s*(\d{2}))?\s*$", re.IGNORECASE)
SET_SUFFIX_RE = re.compile(r"\s+-\s+(?:1er|2e)\s+set\s*$", re.IGNORECASE)
PERFORMANCE_TIME_RE = re.compile(r"(?<!\w)\d{1,2}\s*h(?:\s*\d{2})?(?!\w)", re.IGNORECASE)
PROMOTIONAL_CITY_RE = re.compile(
    r"\s+(?:paris|nanterre|boulogne(?:-billancourt)?|saint[- ]denis|montreuil)\s+20\d{2}\s*$",
    re.IGNORECASE,
)


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


def _presentation_wrapper_signature(value: str) -> tuple[str, str] | None:
    """
    Normalize only explicit presentation grammar.

    This deliberately does not perform general title decomposition. It lets
    reviewed event titles recognize equivalent language/spelling variants such
    as "presents", "présente" and "presente".
    """
    match = re.fullmatch(
        r"(?P<context>.+?)\s+"
        r"(?:présente|présentent|presente|presentent|presents?)"
        r"\s+(?P<artist>.+)",
        unescape(value or "").strip(),
        re.IGNORECASE,
    )
    if not match:
        return None

    return (
        normalize_headliner(match.group("context")),
        normalize_headliner(match.group("artist")),
    )


def _reviewed_event_title_for(event: ConcertEvent) -> str | None:
    """
    Resolve a reviewed event title without broadening reviewed equivalence.

    Exact REVIEWED_EVENT_TITLES aliases retain their existing behavior.
    Otherwise, an explicit presentation-wrapper variant may resolve only to a
    reviewed canonical title on the same reviewed date and venue.
    """
    venue_identity = normalize_venue_key(event.venue)
    artist_identity = normalize_artist_component(event.headliner)

    reviewed_title = REVIEWED_EVENT_TITLES.get(
        (event.date, venue_identity, artist_identity)
    )
    if reviewed_title:
        return reviewed_title

    signature = _presentation_wrapper_signature(event.headliner)
    if not signature:
        return None

    candidates = {
        canonical
        for (date, venue, _artist), canonical in REVIEWED_EVENT_TITLES.items()
        if date == event.date
        and venue == venue_identity
        and _presentation_wrapper_signature(canonical) == signature
    }

    if len(candidates) == 1:
        return next(iter(candidates))

    return None


def _mark_reviewed_wrapper_semantics(
    events: list[ConcertEvent],
) -> None:
    """
    Protect a reviewed canonical presentation wrapper, including an equivalent
    explicit language/spelling variant, from generic decomposition.

    Other reviewed aliases remain eligible for normal canonical semantics.
    """
    for event in events:
        reviewed_title = _reviewed_event_title_for(event)
        if not reviewed_title:
            continue

        exact = (
            normalize_headliner(event.headliner)
            == normalize_headliner(reviewed_title)
        )

        event_signature = _presentation_wrapper_signature(event.headliner)
        reviewed_signature = _presentation_wrapper_signature(reviewed_title)
        wrapper_equivalent = (
            event_signature is not None
            and reviewed_signature is not None
            and event_signature == reviewed_signature
        )

        if exact or wrapper_equivalent:
            event._reviewed_wrapper_semantics_locked = True



def _source_resolved_presentation_identity(event: ConcertEvent) -> bool:
    """
    Return True when a source has already separated artist identity from its
    presentation title.

    This requires explicit source evidence: a distinct raw title that contains
    both the canonical artist identity and the separately extracted event
    title. It must not depend on aliases created later in deduplication and
    must not infer performer structure from punctuation alone.
    """
    if not event.raw_title or not event.event_title:
        return False

    canonical = normalize_headliner(event.headliner)
    raw = normalize_headliner(event.raw_title)
    presentation = normalize_headliner(event.event_title)

    if (
        not canonical
        or not raw
        or not presentation
        or canonical == raw
    ):
        return False

    def phrase_form(value: str) -> str:
        return " ".join(re.findall(r"\w+", value, flags=re.UNICODE))

    canonical_phrase = phrase_form(canonical)
    raw_phrase = phrase_form(raw)
    presentation_phrase = phrase_form(presentation)

    if not canonical_phrase or not raw_phrase or not presentation_phrase:
        return False

    padded_raw = f" {raw_phrase} "
    return (
        f" {canonical_phrase} " in padded_raw
        and f" {presentation_phrase} " in padded_raw
    )



def _apply_reviewed_event_rules(events: list[ConcertEvent]) -> None:
    for event in events:
        original_headliner = event.headliner
        original_identity = normalize_artist_component(original_headliner)
        event.headliner = unescape(event.headliner)
        event.openers = [unescape(value) for value in (event.openers or [])] or None
        event.co_headliners = [
            unescape(value) for value in (event.co_headliners or [])
        ] or None
        if event.event_title:
            event.event_title = unescape(event.event_title)
        if event.series_name:
            event.series_name = unescape(event.series_name)
        reviewed_title = _reviewed_event_title_for(event)
        if reviewed_title:
            reviewed_matches_raw = bool(
                event.raw_title
                and normalize_headliner(reviewed_title)
                == normalize_headliner(event.raw_title)
            )
            preserve_resolved_identity = (
                reviewed_matches_raw
                and _source_resolved_presentation_identity(event)
            )

            if preserve_resolved_identity:
                event.identity_aliases = _stable_unique([
                    *(event.identity_aliases or []),
                    reviewed_title,
                ])
            else:
                if normalize_headliner(event.headliner) != normalize_headliner(
                    reviewed_title
                ):
                    event.identity_aliases = _stable_unique([
                        *(event.identity_aliases or []),
                        event.headliner,
                    ])
                event.headliner = reviewed_title
                if (
                    len(event.performers or []) == 1
                    and normalize_artist_component(event.performers[0])
                    == original_identity
                ):
                    event.performers = [reviewed_title]

        move_artist = normalize_artist_component(event.headliner)
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

    # Capture provenance before source_names are combined. Otherwise an
    # external record can inherit the venue source name during this merge
    # and subsequently appear to be an official venue record itself.
    existing_official_venue = _has_official_venue_source(existing)
    incoming_official_venue = _has_official_venue_source(incoming)

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
    existing.identity_aliases = _stable_unique([
        *(existing.identity_aliases or []),
        incoming.headliner,
        *(incoming.identity_aliases or []),
    ])
    existing.first_seen = min(
        value for value in (existing.first_seen, incoming.first_seen) if value
    ) if existing.first_seen or incoming.first_seen else None

    if (
        getattr(existing, "_reviewed_wrapper_semantics_locked", False)
        or getattr(incoming, "_reviewed_wrapper_semantics_locked", False)
    ):
        existing._reviewed_wrapper_semantics_locked = True

    # Keep independent source evidence through reconciliation. It must remain
    # available before content linking; the exporter cannot reconstruct it.
    existing.performers = _stable_unique([
        *(existing.performers or []), *(incoming.performers or [])
    ]) or None
    existing.tags = _stable_unique([
        *(existing.tags or []), *(incoming.tags or [])
    ]) or None
    for field in ("raw_title", "event_type", "category", "performance_marker"):
        if not getattr(existing, field) and getattr(incoming, field):
            setattr(existing, field, getattr(incoming, field))
    descriptions = _stable_unique([existing.description, incoming.description])
    existing.description = "\n".join(descriptions or []) or None

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
    elif (
        incoming_official_venue
        and not existing_official_venue
        and not existing.authoritative_billing
        and _valid_http_url(incoming.ticket_url)
    ):
        # Prefer the venue's own event page over an external listing when
        # both records have already been accepted as the same concert.
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

    if incoming.image_url and (
        not existing.image_url
        or image_source_priority(incoming.image_source)
        > image_source_priority(existing.image_source)
    ):
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
    """Split only when a caller already has explicit performer identities."""
    parts = [part.strip() for part in BILL_SEPARATOR_RE.split(value or "")]
    return parts if len(parts) > 1 else []


def _opaque_title_signature(value: str) -> str:
    """Normalize a complete flat title without assigning artist identities."""

    normalized = unicodedata.normalize("NFKD", unescape(value or ""))
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    ).casefold()
    normalized = PROMOTIONAL_CITY_RE.sub("", normalized)
    normalized = TIME_SUFFIX_RE.sub("", normalized)
    normalized = re.sub(
        r"\s*(?:\((?:live|uk|fr|us|usa)\)|(?:\s+|:\s*)20\d{2})\s*$",
        "",
        normalized,
        flags=re.IGNORECASE,
    )
    # Separator variants may describe the same complete source title. The
    # marker is comparison-only: its segments are never returned as artists.
    normalized = BILL_SEPARATOR_RE.sub(" | ", normalized)
    normalized = re.sub(r"[^\w|]+", " ", normalized, flags=re.UNICODE)
    normalized = re.sub(r"\s*\|\s*", " | ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _opaque_title_relation(left: str, right: str) -> str | None:
    """Return equivalence/extension for complete opaque source titles."""

    left_signature = _opaque_title_signature(left)
    right_signature = _opaque_title_signature(right)
    if not left_signature or not right_signature:
        return None
    if left_signature == right_signature:
        return "equivalent"

    # Extension is deliberately stricter than equivalence. Words such as
    # "and", "avec", and "with" may belong to an artist name and therefore
    # cannot turn a shorter opaque title into a presumed bill prefix.
    def extension_text(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", unescape(value or ""))
        normalized = "".join(
            character
            for character in normalized
            if not unicodedata.combining(character)
        ).casefold()
        normalized = PROMOTIONAL_CITY_RE.sub("", normalized)
        normalized = TIME_SUFFIX_RE.sub("", normalized)
        normalized = re.sub(
            r"\s*(?:\((?:live|uk|fr|us|usa)\)|(?:\s+|:\s*)20\d{2})\s*$",
            "",
            normalized,
            flags=re.IGNORECASE,
        )
        return re.sub(r"\s+", " ", normalized).strip()

    left_text = extension_text(left)
    right_text = extension_text(right)
    boundary = re.compile(r"^\s*(?:[+&×/•]|x)\s+", re.IGNORECASE)

    if right_text.startswith(left_text) and boundary.match(
        right_text[len(left_text):]
    ):
        return "right_extends_left"

    if left_text.startswith(right_text) and boundary.match(
        left_text[len(right_text):]
    ):
        return "left_extends_right"

    return None


def _reordered_explicit_coheadline_titles(
    left: str,
    right: str,
) -> bool:
    """
    Compare reordered flat co-headline titles without creating artist identities.

    Require explicit x/× billing evidence from at least one source. The
    complete-title normalization may then compare the already-delimited
    segments as an unordered set. This remains comparison-only.
    """
    explicit_x = re.compile(r"\s+(?:x|×)\s+", re.IGNORECASE)

    if not (
        explicit_x.search(unescape(left or ""))
        or explicit_x.search(unescape(right or ""))
    ):
        return False

    def parts(value: str) -> list[str]:
        signature = _opaque_title_signature(value)
        values = [
            part.strip()
            for part in signature.split(" | ")
            if part.strip()
        ]
        return values if len(values) >= 2 else []

    left_parts = parts(left)
    right_parts = parts(right)

    return bool(
        left_parts
        and right_parts
        and len(left_parts) == len(right_parts)
        and frozenset(left_parts) == frozenset(right_parts)
    )


def _normalized_billing_component(value: str) -> str:
    """Normalize punctuation only inside an explicitly parsed artist bill."""

    value = PROMOTIONAL_CITY_RE.sub("", value or "")
    value = TIME_SUFFIX_RE.sub("", value)
    value = re.sub(
        r"\s*(?:\((?:live|uk|fr|us|usa)\)|(?:\s+|:\s*)20\d{2})\s*$",
        "",
        value or "",
        flags=re.IGNORECASE,
    )
    value = normalize_artist_component(value).replace("'", "")
    value = re.sub(r"[^\w]+", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()


def _promotional_city_year_base(value: str) -> str | None:
    """Return the display artist with only the reviewed city/year suffix removed."""

    base = PROMOTIONAL_CITY_RE.sub("", value or "").strip()
    return base if base != (value or "").strip() else None


def _prefer_canonical_display_headliner(left: ConcertEvent, right: ConcertEvent) -> str | None:
    candidates = []
    for value in (left.headliner, right.headliner):
        base = _promotional_city_year_base(value)
        if base:
            candidates.append(base)
    if not candidates:
        return None
    return max(candidates, key=lambda value: (sum(ord(char) > 127 for char in value), -len(value)))


def _primary_billing_set(event: ConcertEvent) -> frozenset[str]:
    wrapped = _festival_event_billing(event)
    if wrapped:
        return wrapped[1]
    # Only canonical structured fields establish performer identities. A flat
    # headliner such as "Alpha + Beta & Company" is one opaque value here.
    components = [event.headliner, *(event.co_headliners or [])]
    return frozenset(
        identity
        for identity in map(_normalized_billing_component, components)
        if identity
    )


def _festival_wrapped_billing(value: str) -> tuple[str, frozenset[str]] | None:
    """Return festival and artist identities from a reordered wrapper title."""

    parts = [
        part.strip()
        for part in re.split(r"\s+[–—|-]\s+|\s*:\s*", unescape(value or ""))
        if part.strip()
    ]
    if len(parts) != 2:
        return None
    festival_parts = [part for part in parts if re.search(
        r"\b(?:festival|fest)\b", part, re.IGNORECASE
    )]
    if len(festival_parts) != 1:
        return None
    festival = festival_parts[0]
    billing = parts[1] if parts[0] == festival else parts[0]
    billing = GENERIC_GUEST_RE.sub("", billing).strip()
    billing_identity = _opaque_title_signature(billing)
    artists = frozenset([billing_identity]) if billing_identity else frozenset()
    festival_identity = _normalized_billing_component(festival)
    return (festival_identity, artists) if festival_identity and artists else None


def _same_festival_wrapped_billing(
    left: ConcertEvent, right: ConcertEvent
) -> bool:
    left_identity = _festival_event_billing(left)
    right_identity = _festival_event_billing(right)
    return bool(left_identity and left_identity == right_identity)


def _festival_event_billing(
    event: ConcertEvent,
) -> tuple[str, frozenset[str]] | None:
    return _festival_wrapped_billing(
        event.headliner
    ) or _festival_wrapped_billing(event.event_title or "")


def _cross_source_evidence(left: ConcertEvent, right: ConcertEvent) -> bool:
    left_sources = set(left.source_names or [])
    right_sources = set(right.source_names or [])
    return bool(
        (left_sources and right_sources and left_sources != right_sources)
        or _shared_promoter(left, right)
        or _same_event_specific_ticket(left, right)
    )


def _distinct_performance_evidence(left: ConcertEvent, right: ConcertEvent) -> bool:
    if _performance_conflict(left, right):
        return True
    if left.festival_name or right.festival_name:
        if (
            not left.authoritative_billing
            and not right.authoritative_billing
            and _same_festival_wrapped_billing(left, right)
        ):
            return False
        return True
    if SET_SUFFIX_RE.search(left.headliner) or SET_SUFFIX_RE.search(right.headliner):
        return True
    left_title_time = PERFORMANCE_TIME_RE.search(left.headliner)
    right_title_time = PERFORMANCE_TIME_RE.search(right.headliner)
    if left_title_time and right_title_time:
        def title_minutes(match):
            text = match.group(0).replace(" ", "").lower()
            hours, _, minutes = text.partition("h")
            return int(hours) * 60 + int(minutes or 0)
        if title_minutes(left_title_time) != title_minutes(right_title_time):
            return True
    return False


def _tour_base_identity(value: str) -> str | None:
    match = re.match(r"^(.+?)\s+[–—:|\-]\s+(.+)$", unescape(value or ""))
    if not match or not re.search(
        r"\b(?:tour|tourn[ée]e|anniversary|headline)\b",
        match.group(2),
        re.IGNORECASE,
    ):
        return None
    return _normalized_billing_component(match.group(1))


def _tour_normalization_allows_merge(left: ConcertEvent, right: ConcertEvent) -> bool:
    """Artist extraction must not manufacture same-performance evidence.

    Compare original tour wording when canonical semantics removed it. Keep
    reviewed equivalences and corroborated decorated/plain representations,
    but do not equate two different programmes merely via their artist.
    Date, venue, billing and performance-time gates remain the caller's job.
    """
    originals = []
    normalized_tours = []
    for event in (left, right):
        raw = event.raw_title or event.headliner
        extracted = (
            title_identity(raw) != title_identity(event.headliner)
            and _tour_base_identity(raw) == _normalized_billing_component(event.headliner)
        )
        originals.append(raw if extracted else event.headliner)
        normalized_tours.append(extracted)
    if not any(normalized_tours):
        return True
    if normalize_headliner(originals[0]) == normalize_headliner(originals[1]):
        # Exact raw duplicates or the existing reviewed title-equivalence map.
        return True
    # Event-scoped reviewed rewrites are affirmative evidence too. Resolve
    # original wording through that existing table before applying the generic
    # guard; canonical artist extraction alone never grants this permission.
    reviewed = [REVIEWED_EVENT_TITLES.get(
        (event.date, normalize_venue_key(event.venue), normalize_artist_component(raw))
    ) for event, raw in zip((left, right), originals)]
    if (any(reviewed)
            and left.date == right.date
            and normalize_venue_key(left.venue) == normalize_venue_key(right.venue)
            and normalize_headliner(reviewed[0] or originals[0])
            == normalize_headliner(reviewed[1] or originals[1])):
        return True
    if _same_event_specific_ticket(left, right):
        return True
    left_sources, right_sources = set(left.source_names or []), set(right.source_names or [])
    if not (left_sources and right_sources and left_sources != right_sources):
        return False
    # Independent sources can corroborate a decorated and a plain artist
    # listing; different tour/programme titles are not mutual corroboration.
    if sum(normalized_tours) != 1:
        return False
    marked = 0 if normalized_tours[0] else 1
    return _tour_base_identity(originals[marked]) == _normalized_billing_component(originals[1 - marked])


def _same_primary_billing(left: ConcertEvent, right: ConcertEvent) -> bool:
    left_festival = _festival_event_billing(left)
    right_festival = _festival_event_billing(right)
    if left_festival or right_festival:
        if left_festival and right_festival:
            return left_festival == right_festival
        wrapped = left_festival or right_festival
        plain = right if left_festival else left
        return wrapped[1] == _primary_billing_set(plain)
    left_set, right_set = _primary_billing_set(left), _primary_billing_set(right)
    if left_set and left_set == right_set:
        return True
    # A separately sourced title commonly omits the co-bill printed on the
    # venue card. Compare complete opaque titles at the explicit boundary;
    # never expose their comparison segments as performer identities.
    if _opaque_title_relation(left.headliner, right.headliner):
        return True

    # Explicit co-headline notation can be reordered across independent
    # sources. This is comparison-only and never creates performer identities.
    if _reordered_explicit_coheadline_titles(
        left.headliner,
        right.headliner,
    ):
        return True
    # Structured performer fields may safely establish subset semantics.
    if (
        left_set
        and right_set
        and min(len(left_set), len(right_set)) == 1
        and (left_set < right_set or right_set < left_set)
    ):
        return True
    left_identity = _normalized_billing_component(left.headliner)
    right_identity = _normalized_billing_component(right.headliner)
    if (
        left_identity
        and right_identity
        and SequenceMatcher(None, left_identity, right_identity).ratio() >= 0.92
    ):
        return True
    return bool(
        (_tour_base_identity(left.headliner) == right_identity)
        or (_tour_base_identity(right.headliner) == left_identity)
    )


def _billing_richness(event: ConcertEvent) -> tuple[int, ...]:
    return (
        int(bool(event.electric_eye_links)),
        len(event.electric_eye_links or []),
        len(_primary_billing_set(event)),
        len(event.openers or []) + len(event.co_headliners or []),
        len(_opaque_title_signature(event.headliner)),
        int(bool(event.genre or event.genre_public)),
        int(bool(event.image_url)),
        int(bool(event.ticket_url)),
        len(event.promoters or []),
        len(event.source_names or []),
    )


def _remove_billed_artists_from_support(event: ConcertEvent) -> None:
    headliner_evidence = _billing_evidence_key(event.headliner)
    event.openers = [
        opener for opener in (event.openers or [])
        if not _evidence_contains_artist(headliner_evidence, opener)
    ] or None
    if _festival_event_billing(event):
        event.co_headliners = [
            artist for artist in (event.co_headliners or [])
            if not re.search(r"\bguests?\b", artist, re.IGNORECASE)
        ] or None


def _corroborated_single_plus_extension(
    left: ConcertEvent,
    right: ConcertEvent,
) -> tuple[str, str] | None:
    """Resolve one '+' extension only when another source proves the primary."""

    for primary_event, extended_event in ((left, right), (right, left)):
        if (
            primary_event.openers
            or primary_event.co_headliners
            or extended_event.openers
            or extended_event.co_headliners
        ):
            continue

        primary = re.sub(
            r"\s+",
            " ",
            unescape(primary_event.headliner or ""),
        ).strip()
        extended = re.sub(
            r"\s+",
            " ",
            unescape(extended_event.headliner or ""),
        ).strip()

        if not primary or not extended:
            continue

        match = re.fullmatch(
            rf"{re.escape(primary)}\s+\+\s+(?P<additional>.+)",
            extended,
            re.IGNORECASE,
        )
        if not match:
            continue

        additional = match.group("additional").strip()

        # Multiple explicit '+' separators deliberately remain opaque.
        if not additional or re.search(r"\s+\+\s+", additional):
            continue

        return primary_event.headliner, additional

    return None


def _los_classification_fuller_bill(
    left: ConcertEvent,
    right: ConcertEvent,
) -> ConcertEvent | None:
    """Return authoritative fuller billing beside a Los artist subject.

    Los's canonical artist relationship establishes concert eligibility; it
    does not outrank fuller performing identity supplied by another primary
    source. The surrounding billing reconciler must already have established
    that both records describe the same physical event.
    """

    for los, other in ((left, right), (right, left)):
        if "Los Production" not in set(los.source_names or []):
            continue
        if not (set(other.source_names or []) - {"Los Production", "DICE"}):
            continue
        los_identity = _billing_evidence_key(los.headliner)
        other_identity = _billing_evidence_key(other.headliner)
        if (
            los_identity
            and other_identity != los_identity
            and len(other_identity) > len(los_identity)
            and _evidence_contains_artist(other_identity, los.headliner)
        ):
            return other
    return None


def _merge_los_classification_into_fuller_bill(
    fuller: ConcertEvent,
    los: ConcertEvent,
) -> ConcertEvent:
    retained_performers = {
        normalize_artist_component(value)
        for value in (fuller.performers or [])
    }
    classification_performers = {
        normalize_artist_component(value)
        for value in [los.headliner, *(los.performers or [])]
    }
    merge_events(fuller, los)
    fuller.performers = [
        value
        for value in (fuller.performers or [])
        if normalize_artist_component(value) not in classification_performers
        or normalize_artist_component(value) in retained_performers
    ] or None
    return fuller


def _reconcile_cross_source_billing_variants(
    events: list[ConcertEvent],
    diagnostics: dict | None = None,
) -> list[ConcertEvent]:
    """Merge explicit artist-set separator and conservative tour-copy variants."""

    grouped = defaultdict(list)
    for event in events:
        grouped[(event.date, normalize_venue_key(event.venue))].append(event)

    removed = set()
    merged_count = 0
    for group in grouped.values():
        for left, right in combinations(group, 2):
            if id(left) in removed or id(right) in removed:
                continue
            if _distinct_performance_evidence(left, right):
                continue
            if not _cross_source_evidence(left, right):
                continue
            if not _tour_normalization_allows_merge(left, right):
                continue
            if not _same_primary_billing(left, right):
                continue
            corroborated_extension = _corroborated_single_plus_extension(
                left,
                right,
            )

            resolved_official = next(
                (
                    event
                    for event in (left, right)
                    if _has_official_venue_source(event)
                    and _source_resolved_presentation_identity(event)
                ),
                None,
            )

            los_fuller_bill = _los_classification_fuller_bill(left, right)

            if los_fuller_bill is not None:
                preferred = los_fuller_bill
                incoming = right if preferred is left else left
                canonical_display = None
            elif corroborated_extension and resolved_official is not None:
                preferred = resolved_official
                incoming = right if preferred is left else left
                canonical_display = None
            else:
                preferred, incoming = sorted(
                    (left, right), key=_billing_richness, reverse=True
                )
                canonical_display = _prefer_canonical_display_headliner(
                    preferred,
                    incoming,
                )

            if los_fuller_bill is not None:
                _merge_los_classification_into_fuller_bill(preferred, incoming)
            else:
                merge_events(preferred, incoming)

            if corroborated_extension and resolved_official is None:
                primary, additional = corroborated_extension
                preferred.headliner = primary
                preferred.co_headliners = _stable_unique([
                    *(preferred.co_headliners or []),
                    additional,
                ]) or None
            elif canonical_display:
                preferred.headliner = canonical_display

            _remove_billed_artists_from_support(preferred)
            removed.add(id(incoming))
            merged_count += 1

    if diagnostics is not None:
        diagnostics["billing_variants_merged"] = merged_count
    return [event for event in events if id(event) not in removed]


def _billing_evidence_key(value: str | None) -> str:
    """Normalize source text for corroborating already-known bill artists."""

    normalized = unicodedata.normalize(
        "NFKD",
        unquote(unescape(value or "")),
    )
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
    normalized = normalized.casefold()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _evidence_contains_artist(evidence: str, artist: str) -> bool:
    artist_key = _billing_evidence_key(artist)
    if not artist_key:
        return False

    return bool(
        re.search(
            rf"(?<![a-z0-9]){re.escape(artist_key)}(?![a-z0-9])",
            evidence,
        )
    )


def _matches_structured_bill(
    structured: ConcertEvent,
    full_bill: ConcertEvent,
) -> bool:
    """
    Match a structured artist bill to another source representation.

    Arbitrary '+'/'&' artist names are never globally split.  Separator or
    source-text interpretation is used only when a second record already
    supplies the explicit structured artist identities being corroborated.
    """

    structured_artists = [
        *(structured.openers or []),
        *(structured.co_headliners or []),
    ]

    if (
        not structured_artists
        or full_bill.openers
        or full_bill.co_headliners
    ):
        return False

    expected_artists = [
        structured.headliner,
        *structured_artists,
    ]
    expected_normalized = [
        normalize_artist_component(value)
        for value in expected_artists
    ]

    # Existing strict path: an explicitly separable complete bill.
    components = _split_full_bill(full_bill.headliner)

    if components:
        normalized_bill = [
            normalize_artist_component(value)
            for value in components
        ]

        if (
            normalized_bill[0] == expected_normalized[0]
            and sorted(normalized_bill) == sorted(expected_normalized)
        ):
            return True

    # Corroboration path.  Another source has already told us exactly which
    # artists form the bill, so look for those identities in explicit source
    # evidence rather than inventing artists by splitting arbitrary names.
    evidence_values = [
        full_bill.headliner,
        full_bill.event_title or "",
        *(full_bill.identity_aliases or []),
        full_bill.ticket_url or "",
    ]

    evidence = " ".join(
        value
        for value in (
            _billing_evidence_key(item)
            for item in evidence_values
        )
        if value
    )

    if not evidence:
        return False

    # At least one structured artist must be represented by the source's
    # actual headliner field; a URL alone is not sufficient evidence.
    headliner_evidence = _billing_evidence_key(full_bill.headliner)

    if not any(
        _evidence_contains_artist(headliner_evidence, artist)
        for artist in expected_artists
    ):
        return False

    return all(
        _evidence_contains_artist(evidence, artist)
        for artist in expected_artists
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

        # Tracking and presentation-only parameters carry no event identity.
        ignored_query_keys = {
            "lang", "language", "locale", "hl",
        }
        query = [
            (key, item)
            for key, item in parse_qsl(parsed.query, keep_blank_values=True)
            if (
                not key.casefold().startswith("utm_")
                and key.casefold() not in ignored_query_keys
            )
        ]

        generic_leaf_names = {
            "",
            "agenda",
            "events",
            "event",
            "billetterie",
            "tickets",
            "ticketing",
            "programme",
            "programmation",
        }

        leaf = path.rsplit("/", 1)[-1].casefold() if path else ""

        # A generic ticketing/programme landing page is not made
        # event-specific merely by being nested under another path.
        # An identifying query such as ?event=123 still makes it specific.
        if leaf in generic_leaf_names and not query:
            return None

        return urlunparse((
            parsed.scheme.casefold(),
            parsed.netloc.casefold(),
            path,
            "",
            urlencode(sorted(query)),
            "",
        ))

    return normalized(left.ticket_url) == normalized(right.ticket_url) is not None


def _normalized_facebook_event_url(value: str | None) -> str | None:
    """Return only an exact Facebook Event identifier, without tracking data."""

    if not _valid_http_url(value):
        return None
    parsed = urlparse(value)
    if parsed.netloc.casefold() not in {"facebook.com", "www.facebook.com"}:
        return None
    match = re.fullmatch(r"/events/([^/]+)/?", re.sub(r"/+", "/", parsed.path))
    if not match:
        return None
    return match.group(1).casefold()


def _shares_direct_event_identifier(
    left: ConcertEvent,
    right: ConcertEvent,
) -> bool:
    left_facebook = _normalized_facebook_event_url(left.facebook_event_url)
    right_facebook = _normalized_facebook_event_url(right.facebook_event_url)
    return bool(
        (left_facebook and left_facebook == right_facebook)
        or _same_event_specific_ticket(left, right)
    )


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
        resolution = getattr(event, "_billing_resolution", {}) or {}
        if resolution.get("method") in {
            "source_profile", "canonical_identity", "cross_source",
            "external_corroboration",
        }:
            # Inferred constituents are valid identities, but their source
            # casing must not override an independently structured/official
            # spelling for the reconciled event.
            continue
        for name in [
            event.headliner,
            *(event.openers or []),
            *(event.co_headliners or []),
        ]:
            identity = normalize_artist_component(name)
            letters = [character for character in name if character.isalpha()]
            is_mixed_case = (
                any(character.islower() for character in letters)
                and any(character.isupper() for character in letters)
            )

            if identity and is_mixed_case and identity not in candidates:
                candidates[identity] = name

    candidates.update(VERIFIED_ARTIST_DISPLAY_NAMES)
    return candidates


def _apply_display_capitalization(
    events: list[ConcertEvent],
    candidates: dict[str, str],
) -> None:
    """
    Apply only evidenced artist display spellings to internal records.

    Generic ALL-CAPS normalization belongs to the public export layer.
    Keeping unsupported source capitalization here preserves source identity,
    reviewed billing semantics and performance discriminators.
    """

    contextual_re = re.compile(
        r"\b(?:"
        r"tour|tourn[ée]e|anniversary|"
        r"release\s+party|launch\s+party|"
        r"nouvel\s+album|nouveau\s+album|new\s+album|"
        r"hommage\s+[àa]|tribute\s+to|festival|"
        r"spectacle|programme|program"
        r")\b",
        re.IGNORECASE,
    )

    def canonicalize(name: str) -> str:
        letters = [
            character
            for character in name
            if character.isalpha()
        ]
        is_all_caps = bool(letters) and all(
            not character.islower()
            for character in letters
        )

        if not is_all_caps:
            return name

        # A complete branded/contextual title must remain untouched
        # internally even if its artist component has a verified spelling.
        if contextual_re.search(name):
            return name

        return candidates.get(
            normalize_artist_component(name),
            name,
        )

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
    # Keep original members: merged metadata must not manufacture evidence for
    # a later record (especially an untimed bridge between separate sets).
    buckets = defaultdict(list)
    retained = []
    for event in events:
        key = build_event_key(event)
        matches = [group for group in buckets[key]
                   if all(_same_exact_performance(member, event) for member in group[1])]
        if len(matches) == 1:
            matches[0][1].append(deepcopy(event))
            merge_events(matches[0][0], event)
        else:
            buckets[key].append((event, [deepcopy(event)]))
            retained.append(event)

    return retained


def _performance_times(event: ConcertEvent) -> set[int]:
    values = [
        event.start_time or "",
        event.headliner,
        event.event_title or "",
        event.raw_title or "",
        *(event.identity_aliases or []),
    ]
    return {int(m[1]) * 60 + int(m[2] or 0)
            for value in values
            for m in re.finditer(
                r"(?<!\w)([01]?\d|2[0-3])\s*[:h]\s*([0-5]\d)?(?!\d)",
                value,
                re.IGNORECASE,
            )}


def _performance_conflict(left: ConcertEvent, right: ConcertEvent) -> bool:
    a, b = _performance_times(left), _performance_times(right)
    if a and b and (a != b or len(a) != 1):
        return True
    # Compare discriminators, rather than treating a single marker as a conflict.
    marker = r"\b(?:(?:1er|1re|2e|2ème|first|second)\s+(?:set|show|performance|séance)|matin[ée]e|evening|early show|late show)\b"
    markers = [set(re.findall(marker, f"{event.headliner} {event.event_title or ''} {event.performance_marker or ''}".casefold()))
               for event in (left, right)]
    return bool(markers[0] and markers[1] and markers[0] != markers[1])


def _same_exact_performance(left: ConcertEvent, right: ConcertEvent) -> bool:
    return (not _performance_conflict(left, right)
            and _tour_normalization_allows_merge(left, right))


def _reconcile_reviewed_event_bills(events: list[ConcertEvent]) -> list[ConcertEvent]:
    """Apply manually reviewed event-level billing decisions."""

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
            if event is not base and not _performance_conflict(base, event):
                merge_events(base, event)
                removed.add(id(event))
        base.headliner = rule["headliner"]
        base.openers = _stable_unique([
            *(base.openers or []), *(rule.get("openers", [])),
        ]) or None
        base.co_headliners = _stable_unique([
            *(base.co_headliners or []), *(rule.get("co_headliners", [])),
        ]) or None

    return [event for event in events if id(event) not in removed]


def _reconcile_generic_guest_titles(events: list[ConcertEvent]) -> list[ConcertEvent]:
    """Resolve a terminal guest placeholder only inside a corroborated event.

    ``Guests`` remains a real performer whenever structured source metadata
    says that it is one. Flat wording alone never grants placeholder status.
    """

    def has_structured_guests(event: ConcertEvent) -> bool:
        return any(
            normalize_artist_component(artist) in {"guest", "guests", "special guest", "special guests"}
            for artist in [
                *(event.performers or []),
                *(event.co_headliners or []),
                *(event.openers or []),
            ]
        )

    grouped = defaultdict(list)
    for event in events:
        grouped[(event.date, normalize_venue_key(event.venue))].append(event)

    removed = set()
    for group in grouped.values():
        for marked in group:
            base = _base_generic_guest_title(marked.headliner)
            if not base or id(marked) in removed or has_structured_guests(marked):
                continue
            base_identity = normalize_artist_component(base)
            candidates = []
            for candidate in group:
                if candidate is marked or id(candidate) in removed:
                    continue
                exact_base = (
                    normalize_artist_component(candidate.headliner)
                    == base_identity
                )
                richer_bill = (
                    _opaque_title_relation(base, candidate.headliner)
                    == "right_extends_left"
                )
                if not (exact_base or richer_bill):
                    continue
                if not (
                    _cross_source_evidence(candidate, marked)
                    or _official_and_aggregator_corroboration(candidate, marked)
                ):
                    continue
                if _performance_conflict(candidate, marked):
                    continue
                candidates.append((int(richer_bill), candidate))

            if candidates:
                # Prefer the source that replaces the placeholder with a
                # specific named bill; otherwise retain the exact plain title.
                _, preferred = max(
                    candidates,
                    key=lambda item: (item[0], _billing_richness(item[1])),
                )
                merge_events(preferred, marked)
                removed.add(id(marked))
    return [event for event in events if id(event) not in removed]


def _reconcile_constituent_festival_wrappers(events: list[ConcertEvent]) -> list[ConcertEvent]:
    """Consolidate generic day-pass listings at explicitly named member venues."""
    def venue_key(value):
        key = normalize_venue_key(value)
        return normalize_venue_key(VENUE_ALIASES.get(key, value))

    groups = defaultdict(list)
    for event in events:
        groups[event.date].append(event)
    removed = set()
    for group in groups.values():
        for parent in group:
            venues = re.fullmatch(r"multi[- ]lieux\s*:\s*(.+)", parent.venue, re.I)
            day = re.fullmatch(r"(?:jour\s+\d+|day\s+\d+|pass\s+1\s+jour)\s*[-–:]\s*(.+)", parent.headliner, re.I)
            if not venues or not day or parent.openers or parent.co_headliners:
                continue
            identity = normalize_headliner(re.sub(r"\s+20\d{2}$", "", day[1]).strip())
            constituents = {venue_key(v.strip()) for v in venues[1].split(",")}
            if len(constituents) < 2:
                continue
            for child in group:
                if child is parent or id(child) in removed or child.openers or child.co_headliners:
                    continue
                # Exact generic wrapper identity only: artist bills and subtitles
                # do not qualify, even if they mention the same festival.
                if normalize_headliner(child.headliner) != identity:
                    continue
                if venue_key(child.venue) not in constituents:
                    continue
                if (parent.start_time and child.start_time and parent.start_time != child.start_time
                        or _distinct_performance_evidence(parent, child)):
                    continue
                merge_events(parent, child)
                removed.add(id(child))
    return [event for event in events if id(event) not in removed]


def _reconcile_confirmed_event_subtitles(events: list[ConcertEvent]) -> list[ConcertEvent]:
    """Match corroborated branding to a plain identity within one venue/day."""
    groups = defaultdict(list)
    for event in events:
        groups[(event.date, normalize_venue_key(event.venue))].append(event)
    removed = set()
    for group in groups.values():
        for marked in group:
            match = re.fullmatch(r"(.+?)\s+(?:[–-]|:)\s+(.+)", marked.headliner)
            if not match or id(marked) in removed:
                continue
            candidates = [plain for plain in group
                          if plain is not marked and id(plain) not in removed
                          and normalize_artist_component(plain.headliner) == normalize_artist_component(match[1])
                          and not _distinct_performance_evidence(plain, marked)
                          and not (plain.start_time and marked.start_time and plain.start_time != marked.start_time)
                          and _official_and_aggregator_corroboration(plain, marked)]
            if len(candidates) == 1:
                plain = candidates[0]
                if not marked.event_title:
                    marked.event_title = marked.headliner
                merge_events(plain, marked)
                removed.add(id(marked))
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
                if _performance_conflict(labeled, plain):
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
            if any(_performance_conflict(performance, parent) for performance in labeled):
                continue
            for performance in labeled:
                merge_events(performance, parent)
            removed.add(id(parent))
    return [event for event in events if id(event) not in removed]


def _has_official_venue_source(event: ConcertEvent) -> bool:
    """Return True when a record comes from the venue it describes."""
    venue_key = normalize_venue_key(event.venue)
    if not venue_key:
        return False

    return any(
        normalize_venue_key(source) == venue_key
        for source in (event.source_names or [])
    )






def _has_explicit_performance_discriminator(event: ConcertEvent) -> bool:
    """Protect records explicitly identified as separate sets or performances."""
    value = " ".join(
        item
        for item in (
            event.headliner,
            event.event_title,
            event.raw_title,
            event.series_name,
            event.performance_marker,
        )
        if item
    )

    if SET_SUFFIX_RE.search(value) or PERFORMANCE_TIME_RE.search(value):
        return True

    marker = (
        r"\b(?:(?:1er|1re|2e|2ème|first|second)\s+"
        r"(?:set|show|performance|séance)|"
        r"matin[ée]e|evening|early show|late show)\b"
    )
    return bool(re.search(marker, value.casefold()))


def _reconcile_transitive_time_bridges(
    events: list[ConcertEvent],
    diagnostics: dict | None = None,
) -> list[ConcertEvent]:
    """Merge one exact three-source bridge across conflicting source clocks.

    This pass deliberately runs before exact deduplication so the untimed
    bridge still retains both of its independent identifiers. It never treats
    date/artist/venue similarity by itself as evidence that two times are one
    performance.
    """

    grouped = defaultdict(list)
    for event in events:
        grouped[(
            event.date,
            normalize_artist_component(event.headliner),
            normalize_venue_key(event.venue),
        )].append(event)

    removed = set()
    merged_count = 0
    for group in grouped.values():
        proposals = {}
        timed = [event for event in group if event.start_time]
        for left, right in combinations(timed, 2):
            if left.start_time == right.start_time:
                continue
            if (
                _has_explicit_performance_discriminator(left)
                or _has_explicit_performance_discriminator(right)
            ):
                continue

            left_official = _has_official_venue_source(left)
            right_official = _has_official_venue_source(right)
            if left_official == right_official:
                continue
            official, external = (
                (left, right) if left_official else (right, left)
            )

            bridges = [
                bridge
                for bridge in group
                if bridge is not left
                and bridge is not right
                and set(bridge.source_names or []) - {"DICE"}
                and not _has_explicit_performance_discriminator(bridge)
                and _shares_direct_event_identifier(bridge, official)
                and _shares_direct_event_identifier(bridge, external)
            ]
            if bridges:
                proposals[(id(official), id(external))] = (
                    official,
                    external,
                    bridges,
                )

        # More than one conflicting timed pair is not an unambiguous bridge.
        if len(proposals) != 1:
            continue
        official, external, bridges = next(iter(proposals.values()))
        for bridge in bridges:
            merge_events(official, bridge)
            removed.add(id(bridge))
        merge_events(official, external)
        removed.add(id(external))
        merged_count += 1

    if diagnostics is not None:
        diagnostics["transitive_time_bridges_merged"] = merged_count
    return [event for event in events if id(event) not in removed]


def _time_minutes(value: str) -> int | None:
    match = re.fullmatch(r"(\d{1,2}):(\d{2})", value or "")
    if not match:
        return None
    hours, minutes = int(match.group(1)), int(match.group(2))
    if hours > 23 or minutes > 59:
        return None
    return hours * 60 + minutes


def _has_consensus_performance_discriminator(event: ConcertEvent) -> bool:
    """Protect explicit room/session/stage identity in addition to show labels."""

    if _has_explicit_performance_discriminator(event):
        return True
    if event.performance_marker:
        return True
    context = " ".join(
        value
        for value in (
            event.event_title,
            event.raw_title,
            event.series_name,
        )
        if value
    ).casefold()
    return bool(re.search(
        r"\b(?:session|s[ée]ance|stage|sc[èe]ne|room|salle)\s*(?:[:#-]?\s*)\w+",
        context,
    ))


def _reconcile_authoritative_time_consensus(
    events: list[ConcertEvent],
    diagnostics: dict | None = None,
) -> list[ConcertEvent]:
    """Resolve a bounded doors/show-time disagreement by primary consensus.

    This is intentionally weaker than the exact-identifier bridge only in its
    identifier requirement. It compensates by requiring one unique official
    venue listing, an additional independent non-DICE primary record, exactly
    two nearby clock values, and no evidence of distinct performances.
    """

    grouped = defaultdict(list)
    for event in events:
        grouped[(
            event.date,
            normalize_artist_component(event.headliner),
            normalize_venue_key(event.venue),
        )].append(event)

    removed = set()
    merged_count = 0
    for group in grouped.values():
        official = [event for event in group if _has_official_venue_source(event)]
        if len(official) != 1:
            continue
        official = official[0]
        official_minutes = _time_minutes(official.start_time or "")
        if official_minutes is None:
            continue
        if any(_has_consensus_performance_discriminator(event) for event in group):
            continue

        timed = [event for event in group if _time_minutes(event.start_time or "") is not None]
        time_values = {
            _time_minutes(event.start_time or "")
            for event in timed
        }
        if len(time_values) != 2 or official_minutes not in time_values:
            continue
        alternate_minutes = next(
            value for value in time_values if value != official_minutes
        )
        if abs(alternate_minutes - official_minutes) > 90:
            continue

        # Repeated listings from one source at different times are affirmative
        # evidence of multiple performances, even if presentation labels are
        # absent or incomplete.
        by_source = defaultdict(list)
        for event in group:
            for source in event.source_names or []:
                by_source[source].append(event)
        if any(
            len({
                _time_minutes(event.start_time or "")
                for event in source_events
                if _time_minutes(event.start_time or "") is not None
            }) > 1
            for source_events in by_source.values()
        ):
            continue

        official_sources = set(official.source_names or [])
        external_timed = [
            event
            for event in timed
            if event is not official
            and _time_minutes(event.start_time or "") == alternate_minutes
        ]
        if not external_timed:
            continue
        external_sources = {
            source
            for event in external_timed
            for source in (event.source_names or [])
        }
        primary_corroborators = [
            event
            for event in group
            if event is not official
            and event not in external_timed
            and set(event.source_names or []) - (
                official_sources | external_sources | {"DICE"}
            )
        ]
        if not primary_corroborators:
            continue

        for event in group:
            if event is official:
                continue
            merge_events(official, event)
            removed.add(id(event))
        merged_count += 1

    if diagnostics is not None:
        diagnostics["authoritative_time_consensus_merged"] = merged_count
    return [event for event in events if id(event) not in removed]


def _official_venue_time_disagreement(
    left: ConcertEvent,
    right: ConcertEvent,
) -> bool:
    """
    Treat an official-venue vs external clock disagreement as source semantics,
    not automatic proof of two performances.

    Explicitly labelled sets/shows remain separate.
    """
    if (
        not left.start_time
        or not right.start_time
        or left.start_time == right.start_time
    ):
        return False

    if (
        _has_explicit_performance_discriminator(left)
        or _has_explicit_performance_discriminator(right)
    ):
        return False

    left_official = _has_official_venue_source(left)
    right_official = _has_official_venue_source(right)

    # Exactly one record must originate from the venue itself.
    return left_official != right_official


def _reconcile_full_bills(events: list[ConcertEvent]) -> list[ConcertEvent]:
    grouped = defaultdict(list)
    for event in events:
        grouped[(event.date, normalize_venue_key(event.venue))].append(event)

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

                if not _matches_structured_bill(structured, full_bill):
                    continue
                if not _tour_normalization_allows_merge(structured, full_bill):
                    continue

                venue_time_disagreement = _official_venue_time_disagreement(
                    structured,
                    full_bill,
                )

                if (
                    _performance_conflict(structured, full_bill)
                    and not venue_time_disagreement
                ):
                    continue

                # Once the bill has independently matched, prefer the
                # official venue's stated time over an external source time.
                if venue_time_disagreement:
                    if (
                        _has_official_venue_source(full_bill)
                        and full_bill.start_time
                    ):
                        structured.start_time = full_bill.start_time

                merge_events(structured, full_bill)
                removed.add(id(full_bill))

    return [event for event in events if id(event) not in removed]


def _embedded_cross_source_title_relation(
    left: ConcertEvent,
    right: ConcertEvent,
) -> tuple[ConcertEvent, ConcertEvent] | None:
    """Return ``(richer, shorter)`` for a corroborated physical event.

    This is comparison-only. It never splits the richer title or assigns
    roles from punctuation. The independent source's complete artist title
    must occur as a whole phrase inside the richer source title, on the same
    canonical date/venue, without conflicting performance evidence.
    """

    if (
        left.date != right.date
        or normalize_venue_key(left.venue) != normalize_venue_key(right.venue)
        or _distinct_performance_evidence(left, right)
        or left.festival_name
        or right.festival_name
    ):
        return None

    left_sources = set(left.source_names or [])
    right_sources = set(right.source_names or [])
    if (
        not left_sources
        or not right_sources
        or not left_sources.isdisjoint(right_sources)
    ):
        return None

    left_programmes = {
        _normalized_billing_component(value)
        for value in (left.event_title, left.series_name)
        if value
    }
    right_programmes = {
        _normalized_billing_component(value)
        for value in (right.event_title, right.series_name)
        if value
    }
    if (
        left_programmes
        and right_programmes
        and left_programmes.isdisjoint(right_programmes)
    ):
        return None

    left_title = _billing_evidence_key(left.headliner)
    right_title = _billing_evidence_key(right.headliner)
    if not left_title or not right_title or left_title == right_title:
        return None

    richer, shorter = (
        (left, right)
        if len(left_title) > len(right_title)
        else (right, left)
    )
    richer_title = _billing_evidence_key(richer.headliner)
    shorter_title = _billing_evidence_key(shorter.headliner)

    if len(shorter_title) < 4:
        return None
    if not re.search(
        rf"(?<![a-z0-9]){re.escape(shorter_title)}(?![a-z0-9])",
        richer_title,
    ):
        return None

    # A bare artist-name prefix followed only by more ordinary words is not
    # sufficient evidence: it may be one longer artist name (for example,
    # "The Devil And The Almighty Blues") or venue copy.  Prefix variants
    # need visible title punctuation or a conventional production/tour cue.
    richer_display = (richer.headliner or "").strip()
    shorter_display = (shorter.headliner or "").strip()
    if richer_display.casefold().startswith(shorter_display.casefold() + " "):
        suffix = richer_display[len(shorter_display):].lstrip()
        suffix_key = _billing_evidence_key(suffix)
        if not (
            suffix.startswith(("-", "–", "—", ":", "|", "/"))
            or re.search(
                r"\b(?:anniversary|celebration|concert|live|pres(?:ents)?|"
                r"release|show|symphony|tour|world)\b",
                suffix_key,
            )
        ):
            return None

    return richer, shorter


def high_confidence_collision_pairs(
    events: list[ConcertEvent],
) -> list[dict]:
    """Return unresolved physical-event collisions with explicit evidence."""

    grouped = defaultdict(list)
    for event in events:
        grouped[(event.date, normalize_venue_key(event.venue))].append(event)

    collisions = []
    for (date, _venue_key), group in grouped.items():
        for left, right in combinations(group, 2):
            relation = _embedded_cross_source_title_relation(left, right)
            if not relation:
                continue
            richer, shorter = relation
            structured = (
                bool(left.openers or left.co_headliners or left.performers)
                != bool(right.openers or right.co_headliners or right.performers)
            )
            collisions.append({
                "classification": (
                    "STRUCTURED_VS_FLAT_BILL"
                    if structured
                    else "SAME_PHYSICAL_EVENT_TITLE_VARIANT"
                ),
                "confidence": "HIGH",
                "date": date,
                "venue": richer.venue,
                "titles": [left.headliner, right.headliner],
                "sources": [
                    list(left.source_names or []),
                    list(right.source_names or []),
                ],
                "times": [left.start_time, right.start_time],
                "ticket_urls": [left.ticket_url, right.ticket_url],
                "source_event_ids": [None, None],
                "reason": (
                    "same canonical date and venue; compatible performance "
                    "evidence; independent source title is a whole-phrase "
                    "subset of the richer source title"
                ),
                "richer_title": richer.headliner,
                "shorter_title": shorter.headliner,
            })
    return collisions


def _reconcile_exact_ticket_constituent_bills(
    events: list[ConcertEvent],
) -> tuple[list[ConcertEvent], int]:
    """Collapse exact-ticket artist cards represented by one complete bill."""

    grouped = defaultdict(list)
    for event in events:
        grouped[(event.date, normalize_venue_key(event.venue))].append(event)

    removed = set()
    merged_count = 0
    for group in grouped.values():
        # An agency roster may expose each performing act as its own card while
        # another primary source exposes the complete bill. Collapse those
        # constituent cards only when at least two distinct complete artist
        # names occur in the richer title and every record shares the same
        # event-specific ticket. This is comparison-only: the richer opaque
        # bill is preserved and no support/co-headliner hierarchy is inferred.
        for richer in group:
            if id(richer) in removed:
                continue
            richer_sources = set(richer.source_names or [])
            richer_evidence = max(
                (
                    _billing_evidence_key(value)
                    for value in (
                        richer.event_title,
                        richer.raw_title,
                        richer.headliner,
                    )
                    if value
                ),
                key=len,
                default="",
            )
            richer_headliner = _billing_evidence_key(richer.headliner)
            constituents = []
            identities = set()
            for candidate in group:
                if candidate is richer or id(candidate) in removed:
                    continue
                candidate_sources = set(candidate.source_names or [])
                identity = _billing_evidence_key(candidate.headliner)
                if (
                    not identity
                    or identity == richer_headliner
                    or not richer_sources - candidate_sources
                    or _distinct_performance_evidence(richer, candidate)
                    or not _same_event_specific_ticket(richer, candidate)
                    or not re.search(
                        rf"(?<![a-z0-9]){re.escape(identity)}(?![a-z0-9])",
                        richer_evidence,
                    )
                ):
                    continue
                if identity and identity not in identities:
                    constituents.append(candidate)
                    identities.add(identity)

            if len(constituents) < 2:
                continue
            retained_performers = deepcopy(richer.performers)
            for constituent in constituents:
                merge_events(richer, constituent)
                removed.add(id(constituent))
                merged_count += 1
            richer.performers = retained_performers
            _remove_billed_artists_from_support(richer)

    return (
        [event for event in events if id(event) not in removed],
        merged_count,
    )


def _reconcile_embedded_cross_source_titles(
    events: list[ConcertEvent],
    diagnostics: dict | None = None,
) -> list[ConcertEvent]:
    """Merge demonstrated title variants while retaining the richer row."""

    events, merged_count = _reconcile_exact_ticket_constituent_bills(events)

    grouped = defaultdict(list)
    for event in events:
        grouped[(event.date, normalize_venue_key(event.venue))].append(event)

    removed = set()
    for group in grouped.values():

        for left, right in combinations(group, 2):
            if id(left) in removed or id(right) in removed:
                continue
            relation = _embedded_cross_source_title_relation(left, right)
            if not relation:
                continue
            richer, shorter = relation
            richer_structured = bool(
                richer.openers or richer.co_headliners or richer.performers
            )
            shorter_structured = bool(
                shorter.openers or shorter.co_headliners or shorter.performers
            )

            resolved_official = [
                event
                for event in (left, right)
                if _has_official_venue_source(event)
                and _source_resolved_presentation_identity(event)
            ]

            los_fuller_bill = _los_classification_fuller_bill(left, right)

            if los_fuller_bill is not None:
                preferred = los_fuller_bill
                incoming = right if preferred is left else left
            elif len(resolved_official) == 1:
                preferred = resolved_official[0]
                incoming = right if preferred is left else left
            else:
                preferred, incoming = (
                    (shorter, richer)
                    if shorter_structured and not richer_structured
                    else (richer, shorter)
                )

            if preferred is shorter and not preferred.event_title:
                preferred.event_title = richer.headliner
            if los_fuller_bill is not None:
                _merge_los_classification_into_fuller_bill(preferred, incoming)
            else:
                merge_events(preferred, incoming)
            _remove_billed_artists_from_support(preferred)
            removed.add(id(incoming))
            merged_count += 1

    if diagnostics is not None:
        diagnostics["physical_event_title_variants_merged"] = merged_count
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

                if _performance_conflict(parent, candidate):
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

            if _performance_conflict(parent, candidate):
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


def _normalize_event_title_wrappers(events):
    """Separate explicit prose, then reconcile compatible normalized identities."""
    changed = set()
    series_prefixes = evidenced_series_prefixes(events)
    reviewed_displays = set(REVIEWED_EVENT_TITLES.values())
    for event in events:
        original = event.headliner

        if original in reviewed_displays:
            continue
        contextual, series = contextual_title_parts(event, series_prefixes)
        primary, featured = artist_title_parts(contextual)
        bare_concert = re.fullmatch(r"(.+?)\s+en concert", original, re.I)
        if primary == original and bare_concert:
            corroborated = [other for other in events if other is not event
                            and other.date == event.date
                            and normalize_venue_key(other.venue) == normalize_venue_key(event.venue)
                            and normalize_headliner(other.headliner) == normalize_headliner(bare_concert[1])
                            and _cross_source_evidence(other, event)
                            and not _distinct_performance_evidence(other, event)]
            if len(corroborated) == 1:
                primary = corroborated[0].headliner
        if primary == original and not featured:
            continue
        event.event_title = event.event_title or original
        event.series_name = event.series_name or series
        event.identity_aliases = _stable_unique([*(event.identity_aliases or []), original])
        event.headliner = primary
        event.co_headliners = _stable_unique([*(event.co_headliners or []), *featured]) or None
        changed.add(id(event))
    retained = []
    for event in events:
        candidates = [other for other in retained
                      if event.date == other.date
                      and normalize_venue_key(event.venue) == normalize_venue_key(other.venue)
                      and (
                          title_identity(event.headliner)
                          == title_identity(other.headliner)
                          or (
                              (id(event) in changed or id(other) in changed)
                              and title_identity(
                                  event.headliner,
                                  fold_accents=True,
                              )
                              == title_identity(
                                  other.headliner,
                                  fold_accents=True,
                              )
                              and _cross_source_evidence(event, other)
                          )
                      )
                      and [title_identity(n) for n in (event.co_headliners or [])]
                          == [title_identity(n) for n in (other.co_headliners or [])]
                      and not _distinct_performance_evidence(event, other)
                      and not separate_performance_marker(event)
                      and not separate_performance_marker(other)
                      and _tour_normalization_allows_merge(event, other)
                      and (_same_event_specific_ticket(event, other)
                           or ((id(event) in changed or id(other) in changed)
                               and _cross_source_evidence(event, other))
                           or _wrapper_identity_evidence(event)
                           or _wrapper_identity_evidence(other))]
        if len(candidates) == 1:
            merge_events(candidates[0], event)
            changed.add(id(candidates[0]))
        else:
            retained.append(event)
    return retained


def _wrapper_identity_evidence(event):
    """Persisted decorated source title proves an alternate representation."""
    for raw in [event.event_title or "", *(event.identity_aliases or [])]:
        primary, featured = artist_title_parts(raw)
        if primary != raw and title_identity(primary) == title_identity(event.headliner):
            if [title_identity(n) for n in featured] == [title_identity(n) for n in (event.co_headliners or [])]:
                return True
    return False



# ---------------------------------------------------------------------------
# Reviewed calendar identity fixes.
#
# These are evidence-backed exceptions, not punctuation heuristics.
# ---------------------------------------------------------------------------

REVIEWED_CALENDAR_HEADLINER_ALIASES = {
    "bootleg beatles": "The Bootleg Beatles",
    "the bootleg beatles": "The Bootleg Beatles",
}

REVIEWED_CALENDAR_MULTI_ARTIST_BILLS = {
    (
        "2026-10-10",
        "la maroquinerie",
        "monolord + dopelord",
    ): (
        "Monolord",
        ["Dopelord"],
    ),
}


def _apply_reviewed_calendar_identity_fixes(
    events: list[ConcertEvent],
) -> None:
    for event in events:
        original_headliner = event.headliner

        alias_key = normalize_artist_component(original_headliner)
        reviewed_display = REVIEWED_CALENDAR_HEADLINER_ALIASES.get(alias_key)

        if reviewed_display:
            if original_headliner != reviewed_display:
                event.identity_aliases = _stable_unique([
                    *(event.identity_aliases or []),
                    original_headliner,
                ])
            event.headliner = reviewed_display

        billing_key = (
            event.date,
            normalize_venue_key(event.venue),
            normalize_artist_component(event.headliner),
        )

        reviewed_bill = REVIEWED_CALENDAR_MULTI_ARTIST_BILLS.get(
            billing_key
        )

        if not reviewed_bill:
            continue

        reviewed_headliner, reviewed_co_headliners = reviewed_bill

        if event.headliner != reviewed_headliner:
            event.identity_aliases = _stable_unique([
                *(event.identity_aliases or []),
                event.headliner,
            ])

        event.headliner = reviewed_headliner
        event.co_headliners = _stable_unique([
            *(event.co_headliners or []),
            *reviewed_co_headliners,
        ])


def deduplicate_events(
    events: list[ConcertEvent],
    diagnostics: dict | None = None,
    *,
    billing_reviews: dict | None = None,
    billing_identity_catalog: dict[str, str] | None = None,
    billing_external_evidence: dict[str, dict] | None = None,
) -> list[ConcertEvent]:
    """Collapse exact and explicitly reconcilable duplicate concerts."""

    _mark_reviewed_wrapper_semantics(events)
    apply_structured_performer_semantics(events)
    apply_reviewed_artist_billings(
        events,
        diagnostics,
        reviews=billing_reviews,
        identity_catalog=billing_identity_catalog,
        external_evidence=billing_external_evidence,
    )
    _apply_reviewed_calendar_identity_fixes(events)

    initial_opener_state = defaultdict(list)

    for event in events:
        initial_opener_state[build_event_key(event)].append(bool(event.openers))

    _apply_reviewed_event_rules(events)
    festival_represented_rows = _count_represented_festival_rows(events)
    display_candidates = _display_candidates(events)
    reconciled = _reconcile_transitive_time_bridges(events, diagnostics)
    reconciled = _reconcile_authoritative_time_consensus(
        reconciled,
        diagnostics,
    )
    reconciled = _deduplicate_exact(reconciled)
    reconciled = _reconcile_reviewed_event_bills(reconciled)
    _apply_verified_support_relationships(reconciled)
    reconciled = _reconcile_full_bills(reconciled)
    reconciled = _reconcile_generic_guest_titles(reconciled)
    reconciled = _reconcile_constituent_festival_wrappers(reconciled)
    reconciled = _reconcile_confirmed_event_subtitles(reconciled)
    reconciled = _reconcile_cross_source_billing_variants(
        reconciled, diagnostics
    )
    reconciled = _reconcile_time_labeled_titles(reconciled)
    reconciled = _reconcile_multi_set_parent_cards(reconciled)
    reconciled = _consolidate_authoritative_festivals(reconciled, diagnostics)
    reconciled = _collapse_explicit_support_cards(reconciled)
    _apply_display_capitalization(reconciled, display_candidates)
    reconciled = _normalize_event_title_wrappers(reconciled)

    # Title normalization can expose artist identities that were previously
    # hidden behind programme/series presentation wrappers. Give the existing
    # structured/full-bill reconciler one final opportunity to merge those
    # now-comparable cross-source records.
    reconciled = _reconcile_full_bills(reconciled)
    reconciled = _reconcile_embedded_cross_source_titles(
        reconciled,
        diagnostics,
    )

    apply_structured_performer_semantics(reconciled)
    apply_reviewed_artist_billings(
        reconciled,
        reviews=billing_reviews,
        identity_catalog=billing_identity_catalog,
        external_evidence=billing_external_evidence,
        allow_inference=False,
    )

    # Final safety pass: semantic normalization can make two independently
    # sourced representations identical only after the earlier reconciliation
    # stages have run. Collapse those residual duplicates before state IDs are
    # allocated, while preserving explicit performances/programmes.
    reconciled = _reconcile_final_identity_collisions(reconciled)

    # The final identity merge can make an event-specific ticket and complete
    # bill visible on the same retained record only after the earlier
    # constituent pass. Re-run that exact conservative operation once; do not
    # iterate the broader reconciliation pipeline or infer artists from a URL.
    reconciled, late_constituents_merged = (
        _reconcile_exact_ticket_constituent_bills(reconciled)
    )
    if diagnostics is not None:
        diagnostics["late_ticket_constituents_merged"] = (
            late_constituents_merged
        )
        diagnostics["physical_event_title_variants_merged"] = (
            diagnostics.get("physical_event_title_variants_merged", 0)
            + late_constituents_merged
        )

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
        diagnostics["suspicious_near_duplicates"] = (
            suspicious_near_duplicate_pairs(reconciled)
        )

    return reconciled


def _reconcile_final_identity_collisions(
    events: list[ConcertEvent],
) -> list[ConcertEvent]:
    """
    Merge residual cross-source duplicates before persistent identity allocation.

    At this stage canonical artist semantics have already been resolved. Two
    records with the same date, normalized venue, and normalized public
    headliner represent the same physical event unless there is affirmative
    evidence of a distinct performance or conflicting explicit programme
    context.
    """

    # This is the final reconciliation boundary immediately before state
    # allocation. Use the state allocator's own canonical identity so that
    # deduplication and persistence cannot disagree about whether two rows
    # collide.
    from .event_state import canonical_event_identity

    grouped = defaultdict(list)
    for event in events:
        grouped[canonical_event_identity(event)].append(event)

    removed = set()

    for group in grouped.values():
        if len(group) < 2:
            continue

        for index, left in enumerate(group):
            if id(left) in removed:
                continue

            for right in group[index + 1:]:
                if id(right) in removed:
                    continue

                if _distinct_performance_evidence(left, right):
                    continue

                # Canonical state identity may intentionally normalize a tour
                # suffix away. That normalization alone is not evidence that
                # two listings are the same physical event.
                if not _tour_normalization_allows_merge(left, right):
                    continue

                left_programmes = {
                    _normalized_billing_component(value)
                    for value in (
                        left.event_title,
                        left.series_name,
                        left.festival_name,
                    )
                    if value
                }
                right_programmes = {
                    _normalized_billing_component(value)
                    for value in (
                        right.event_title,
                        right.series_name,
                        right.festival_name,
                    )
                    if value
                }

                if (
                    left_programmes
                    and right_programmes
                    and left_programmes.isdisjoint(right_programmes)
                ):
                    continue

                preferred, other = sorted(
                    (left, right),
                    key=_billing_richness,
                    reverse=True,
                )

                merge_events(preferred, other)
                _remove_billed_artists_from_support(preferred)
                removed.add(id(other))

                if other is left:
                    left = preferred

    return [event for event in events if id(event) not in removed]


def suspicious_near_duplicate_pairs(events: list[ConcertEvent]) -> list[dict]:
    """Report likely wording variants without automatically merging them."""

    grouped = defaultdict(list)
    for event in events:
        grouped[(event.date, normalize_venue_key(event.venue))].append(event)

    candidates = []
    for (date, _), group in grouped.items():
        for left, right in combinations(group, 2):
            left_title = _normalized_billing_component(left.headliner)
            right_title = _normalized_billing_component(right.headliner)
            similarity = SequenceMatcher(None, left_title, right_title).ratio()
            left_set, right_set = _primary_billing_set(left), _primary_billing_set(right)
            union = left_set | right_set
            overlap = len(left_set & right_set) / len(union) if union else 0.0
            if similarity < 0.72 and overlap < 0.5:
                continue
            candidates.append({
                "date": date,
                "venue": left.venue,
                "left": left.headliner,
                "right": right.headliner,
                "similarity": round(similarity, 3),
                "artist_overlap": round(overlap, 3),
                "sources": sorted(
                    set(left.source_names or []) | set(right.source_names or [])
                ),
                "different_times": bool(
                    left.start_time and right.start_time
                    and left.start_time != right.start_time
                ),
                "distinct_performance": _distinct_performance_evidence(
                    left, right
                ),
                "festival": bool(left.festival_name or right.festival_name),
            })
    return candidates


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
            # Different official venues independently listing the same
            # artist/date are not, by themselves, contradictory evidence.
            # Preserve them and require some non-venue source disagreement
            # before raising a venue-conflict diagnostic.
            independently_official = all(
                _has_official_venue_source(event)
                for event in group
            )

            if independently_official:
                continue

            candidates.append({
                "kind": "venue_conflict",
                "date": date,
                "artist": artist,
                "venues": sorted(venues),
                "sources": sorted({
                    source
                    for event in group
                    for source in (event.source_names or [])
                }),
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
