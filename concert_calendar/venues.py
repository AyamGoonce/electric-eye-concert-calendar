import re
import unicodedata

from concert_calendar.models import ConcertEvent


VENUE_ALIASES = {
    "adidas arena": "Adidas Arena",
    "adidas arena paris": "Adidas Arena",
    "bataclan": "Bataclan",
    "le bataclan": "Bataclan",
    "cafe de la danse": "Café de la Danse",
    "le grand rex": "Le Grand Rex",
    "lalhambra": "L'Alhambra",
    "alhambra": "L'Alhambra",
    "zenith paris la villette": "Le Zénith Paris – La Villette",
    "zenith de paris": "Le Zénith Paris – La Villette",
    "supersonic": "Supersonic",
    "supersonic records": "Supersonic Records",
    "mennecy metal fest": "Mennecy Metal Fest",
    "fete de l huma": "Fête de l'Humanité",
}


def normalize_venue_key(value: str) -> str:
    """
    Convert a venue name into a stable key for alias matching.
    """

    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    normalized = normalized.lower()
    normalized = normalized.replace("&", " and ")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def clean_unknown_venue_name(value: str) -> str:
    """
    Apply conservative cleanup to an unknown venue name.

    Unknown venue names are not forced into title case because that could
    damage intentional capitalization.
    """

    cleaned = re.sub(r"\s+", " ", value).strip()
    cleaned = re.sub(r"\s*-\s*paris$", "", cleaned, flags=re.IGNORECASE)

    return cleaned.strip()


def normalize_event_venue(event: ConcertEvent) -> ConcertEvent:
    """
    Normalize a ConcertEvent venue in place and return the event.
    """

    original_venue = event.venue
    venue_key = normalize_venue_key(original_venue)

    if venue_key in VENUE_ALIASES:
        event.venue = VENUE_ALIASES[venue_key]
    else:
        event.venue = clean_unknown_venue_name(original_venue)

        if event.venue:
            print(f"Unknown venue alias: {event.venue}")

    return event