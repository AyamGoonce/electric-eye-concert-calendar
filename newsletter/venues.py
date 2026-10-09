"""Approved concert venues for Electric Eye newsletters."""

import re
import unicodedata


VENUE_ALIASES = {
    "Accor Arena": ("accor arena", "accorhotels arena", "bercy"),
    "Zénith": ("zenith",),
    "Stade de France": ("stade de france",),
    "Adidas Arena": ("adidas arena",),
    "Le Trianon": ("trianon",),
    "La Cigale": ("cigale",),
    "Élysée Montmartre": ("elysee montmartre",),
    "New Morning": ("new morning",),
    "Olympia": ("olympia",),
    "Bataclan": ("bataclan",),
    "La Maroquinerie": ("maroquinerie",),
    "La Machine du Moulin Rouge": ("machine du moulin rouge",),
    "Petit Bain": ("petit bain",),
}


def normalize_venue(value):
    """Normalize case, accents and punctuation."""
    value = unicodedata.normalize("NFKD", (value or "").casefold())
    value = "".join(
        character for character in value
        if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def approved_venue(venue):
    """Return the canonical newsletter venue name, or None."""
    normalized = normalize_venue(venue)

    for canonical, aliases in VENUE_ALIASES.items():
        for alias in aliases:
            normalized_alias = normalize_venue(alias)

            # Match complete words, not arbitrary substrings.
            if re.search(
                r"(?:^| )" + re.escape(normalized_alias) + r"(?: |$)",
                normalized,
            ):
                return canonical

    return None


def filter_concerts_by_venue(concerts):
    """Preserve every concert at an approved venue."""
    return [
        concert for concert in concerts
        if approved_venue(concert.get("venue"))
    ]
