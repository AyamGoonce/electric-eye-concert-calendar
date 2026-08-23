import re
import unicodedata

from concert_calendar.models import ConcertEvent


VENUE_ALIASES = {
    "accor arena": "Accor Arena",
    "adidas arena": "Adidas Arena",
    "adidas arena paris": "Adidas Arena",
    "apollo theatre": "Apollo Théâtre",
    "backstage by the mill": "Backstage By The Mill",
    "backstage": "Backstage By The Mill",
    "le backstage by the mill": "Backstage By The Mill",
    "bal chavaux": "Bal Chavaux",
    "bataclan": "Bataclan",
    "le bataclan": "Bataclan",
    "babour sauvage": "Cabaret Sauvage",
    "cabaret sauvage": "Cabaret Sauvage",
    "cafe de la danse": "Café de la Danse",
    "casino de paris": "Casino de Paris",
    "central chapelle": "Central Chapelle",
    "cirque d hiver": "Cirque d'Hiver Bouglione",
    "cirque d hiver bouglione": "Cirque d'Hiver Bouglione",
    "emb": "EMB Sannois",
    "emb sannois": "EMB Sannois",
    "elysee montmartre": "Élysée Montmartre",
    "l elysee montmartre": "Élysée Montmartre",
    "fgo barbara": "FGO-Barbara",
    "fete de l huma": "Fête de l'Humanité",
    "fete de l humanite": "Fête de l'Humanité",
    "file7": "File7",
    "lalhambra": "L'Alhambra",
    "alhambra": "L'Alhambra",
    "l archipel": "L'Archipel",
    "archipel": "L'Archipel",
    "lolympia": "L'Olympia Bruno Coquatrix",
    "l olympia": "L'Olympia Bruno Coquatrix",
    "l olympia bruno coquatrix": "L'Olympia Bruno Coquatrix",
    "olympia": "L'Olympia Bruno Coquatrix",
    "la boule noire": "La Boule Noire",
    "la batterie": "La Batterie",
    "la clef": "La CLEF",
    "boule noire": "La Boule Noire",
    "la cigale": "La Cigale",
    "cigale": "La Cigale",
    "la gaite lyrique": "La Gaîté Lyrique",
    "gaite lyrique": "La Gaîté Lyrique",
    "la machine du moulin rouge": "La Machine du Moulin Rouge",
    "machine du moulin rouge": "La Machine du Moulin Rouge",
    "la maroquinerie": "La Maroquinerie",
    "maroquinerie": "La Maroquinerie",
    "la marberie": "La Marbrerie",
    "la marbrerie": "La Marbrerie",
    "la place": "La Place",
    "la seine musicale": "La Seine Musicale",
    "seine musicale grande seine": "La Seine Musicale – Grande Seine",
    "seine musicale": "La Seine Musicale",
    "le grand rex": "Le Grand Rex",
    "le poc": "Le POC",
    "le cafe de la danse": "Café de la Danse",
    "le hasard ludique": "Le Hasard Ludique",
    "le palais des congres de paris": "Le Palais des Congrès de Paris",
    "palais des congres de paris": "Le Palais des Congrès de Paris",
    "le pop up du label": "Le Pop-Up du Label",
    "pop up du label": "Le Pop-Up du Label",
    "le pop up": "Le Pop-Up du Label",
    "pop up": "Le Pop-Up du Label",
    "popup": "Le Pop-Up du Label",
    "le trianon": "Le Trianon",
    "trianon": "Le Trianon",
    "les etoiles": "Les Étoiles",
    "etoiles": "Les Étoiles",
    "mennecy metal fest": "Mennecy Metal Fest",
    "plenitude arena": "Plénitude Arena",
    "petit bain": "Petit Bain",
    "point ephemere": "Point Éphémère",
    "le point ephemere": "Point Éphémère",
    "rock en seine": "Rock en Seine",
    "festival rock en seine": "Rock en Seine",
    "salle pleyel": "Salle Pleyel",
    "stade de france": "Stade de France",
    "supersonic": "Supersonic",
    "supersonic records": "Supersonic Records",
    "new morning": "New Morning",
    "nouveau casino": "Nouveau Casino",
    "le nouveau casino": "Nouveau Casino",
    "la maison des metallos": "Maison des Métallos",
    "maison des metallos": "Maison des Métallos",
    "theatre casino barriere d enghien les bains": (
        "Théâtre du Casino Barrière d'Enghien-les-Bains"
    ),
    "theatre de rungis": "Théâtre de Rungis",
    "trabendo": "Le Trabendo",
    "le trabendo": "Le Trabendo",
    "zenith paris la villette": "Le Zénith Paris – La Villette",
    "zenith de paris": "Le Zénith Paris – La Villette",
}


UNKNOWN_VENUES = set()


def normalize_venue_key(value: str) -> str:
    """
    Convert a venue name into a stable key for alias matching.
    """

    normalized = unicodedata.normalize("NFKD", value or "")
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

    cleaned = re.sub(r"\s+", " ", value or "").strip()
    cleaned = re.sub(
        r"\s*-\s*paris$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    return cleaned.strip()


def normalize_event_venue(event: ConcertEvent) -> ConcertEvent:
    """
    Normalize a ConcertEvent venue in place and return the event.
    """

    original_venue = event.venue or ""
    venue_key = normalize_venue_key(original_venue)
    normalized_venue = VENUE_ALIASES.get(venue_key)

    if normalized_venue is not None:
        event.venue = normalized_venue
    else:
        event.venue = clean_unknown_venue_name(original_venue)

        if event.venue and event.venue not in UNKNOWN_VENUES:
            UNKNOWN_VENUES.add(event.venue)
            print(f"Unknown venue alias: {event.venue}")

    return event
