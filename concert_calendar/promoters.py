import re
import unicodedata

from concert_calendar.models import ConcertEvent


CANONICAL_PROMOTERS = {
    "Gérard Drouot Productions": (
        "gdp",
        "gerard drouot productions",
        "gerard drouot production",
    ),
    "Supersonic": (
        "supersonic",
    ),
}

PROMOTER_ALIASES = {}

for canonical_name, aliases in CANONICAL_PROMOTERS.items():
    for alias in aliases:
        PROMOTER_ALIASES[alias] = canonical_name


def normalize_promoter_key(value: str) -> str:
    """
    Convert a promoter name into a stable alias key.
    """

    normalized = unicodedata.normalize("NFKD", value or "")
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    normalized = normalized.casefold()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def normalize_promoter_name(value: str) -> str:
    """
    Return the canonical promoter name when an alias is known.

    Unknown names are preserved with conservative whitespace cleanup.
    """

    cleaned = re.sub(r"\s+", " ", value or "").strip()

    if not cleaned:
        return ""

    promoter_key = normalize_promoter_key(cleaned)

    return PROMOTER_ALIASES.get(promoter_key, cleaned)


def normalize_event_promoters(event: ConcertEvent) -> ConcertEvent:
    """
    Normalize an event's promoter list.

    - canonical names
    - remove blanks
    - remove duplicates
    - sort alphabetically for deterministic output
    """

    normalized = sorted({
        normalize_promoter_name(promoter)
        for promoter in (event.promoters or [])
        if normalize_promoter_name(promoter)
    })

    event.promoters = normalized or None

    return event