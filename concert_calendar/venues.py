import re
import unicodedata
from html import unescape

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
    "espace carpeaux": "Espace Carpeaux",
    "l elysee montmartre": "Élysée Montmartre",
    "fgo barbara": "FGO-Barbara",
    "fete de l huma": "Fête de l'Humanité",
    "fete de l humanite": "Fête de l'Humanité",
    "file7": "File7",
    "lalhambra": "L'Alhambra",
    "l alhambra": "L'Alhambra",
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
    "la marbrerie montreuil": "La Marbrerie",
    "l accord parfait": "L’Accord Parfait",
    "studio l accord parfait": "L’Accord Parfait",
    "la place": "La Place",
    "la seine musicale": "La Seine Musicale",
    "la seine musicale grande seine": "La Seine Musicale",
    "la seine musicale grande seine boulogne billancourt": "La Seine Musicale",
    "seine musicale grande seine": "La Seine Musicale",
    "seine musicale": "La Seine Musicale",
    "grande seine": "La Seine Musicale",
    "auditorium patrick devedjian": "La Seine Musicale",
    "petite seine": "La Seine Musicale",
    "la petite seine": "La Seine Musicale",
    "la scala": "La Scala Paris",
    "la scala paris": "La Scala Paris",
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
    "le zenith": "Le Zénith Paris – La Villette",
    "trianon": "Le Trianon",
    "les etoiles": "Les Étoiles",
    "etoiles": "Les Étoiles",
    "mennecy metal fest": "Mennecy Metal Fest",
    "paris la defense arena": "Plénitude Arena",
    "plenitude arena": "Plénitude Arena",
    "petit bain": "Petit Bain",
    "pavillon baltard": "Pavillon Baltard",
    "point ephemere": "Point Éphémère",
    "le point ephemere": "Point Éphémère",
    "philarmonie de paris": "Philharmonie de Paris",
    "philharmonie": "Philharmonie de Paris",
    "philharmonie de paris": "Philharmonie de Paris",
    "rock en seine": "Rock en Seine",
    "festival rock en seine": "Rock en Seine",
    "salle pleyel": "Salle Pleyel",
    "festival clash salle gaveau": "Salle Gaveau",
    "salle gaveau": "Salle Gaveau",
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
    "theatre claude debussy": "Théâtre Claude Debussy",
    "theatre alexandre dumas": "Théâtre Alexandre Dumas",
    "theatre de l europeen": "L'Européen",
    "trabendo": "Le Trabendo",
    "le trabendo": "Le Trabendo",
    "zenith paris la villette": "Le Zénith Paris – La Villette",
    "zenith de paris": "Le Zénith Paris – La Villette",
    "le zenith paris la villette": "Le Zénith Paris – La Villette",

    # Historical / editorial aliases.
    "zenith": "Le Zénith Paris – La Villette",
    "accorhotels arena": "Accor Arena",
    "accorhotels arena bercy": "Accor Arena",
    "palais omnisports paris bercy": "Accor Arena",
    "p o p b": "Accor Arena",
    "la defense arena": "Plénitude Arena",
    "u arena": "Plénitude Arena",
    "palais des congres": "Le Palais des Congrès de Paris",
    "grand rex": "Le Grand Rex",
    "hasard ludique": "Le Hasard Ludique",
    "l auditorium de la seine musicale": "La Seine Musicale",
    "la machine": "La Machine du Moulin Rouge",
    "bataclan paris": "Bataclan",
    "elyee montmartre": "Élysée Montmartre",
    "o sullivan s backstage by the mill": "Backstage By The Mill",
    "o sullivans backstage by the mill": "Backstage By The Mill",
    "mondial du tatouage": "Grande Halle de la Villette",
    "tattoo planetarium": "Grande Halle de la Villette",

    # Canonical venue names which may arrive from historical review titles.
    "divan du monde": "Divan du Monde",
    "le klub": "Le Klub",
    "la bellevilloise": "La Bellevilloise",
    "badaboum": "Badaboum",
    "batofar": "Batofar",
    "bateau phare": "Batofar",
    "le bateau phare": "Batofar",
    "grande halle de la villette": "Grande Halle de la Villette",
    "glazart": "Glazart",
    "la dame de canton": "La Dame de Canton",
    "la mecanique ondulatoire": "La Mécanique Ondulatoire",
    "mains d oeuvres": "Mains d'Oeuvres",
    "palais de la porte doree": "Palais de la Porte Dorée",
    "quartier general oberkampf": "Quartier Général Oberkampf",
    "le sub pigalle": "Le Sub Pigalle",
    "hippodrome de longchamp": "Hippodrome de Longchamp",
    "cite de la musique": "Cité de la Musique",
    "pan piper": "Pan Piper",
    "la fleche d or": "La Flèche d'Or",
    "le 104": "Le 104",
    "le zebre de belleville": "Le Zèbre de Belleville",
    "sunset sunside": "Sunset/Sunside",
    "flow": "Flow",
    "jazz club etoile": "Jazz Club Étoile",
    "athenee theatre louis jouvet": "Athénée-Théatre Louis Jouvet",
    "theatre du chatelet": "Théatre du Châtelet",
    "studio sextan": "Studio Sextan",
    "chateau de chantilly": "Chateau de Chantilly",
    "fnac ternes": "FNAC Ternes",
    "fnac forum": "FNAC Forum",
    "gibert disc": "Gibert Disc",
    "radio nova": "Radio Nova",
    "novotel les halles": "Novotel Les Halles",
    "the mixtape": "The Mixtape",
    "alabama bar": "Alabama Bar",
    "hellfest": "Hellfest",

    # Additional historical review venues.
    "palais des sports": "Dôme de Paris – Palais des Sports",
    "le dome de paris": "Dôme de Paris – Palais des Sports",
    "capital one city parks foundation summerstage": "SummerStage at Central Park",
    "forest hills stadium": "Forest Hills Stadium",
    "genting arena": "Genting Arena",
    "qualcomm stadium": "Qualcomm Stadium",
    "birdland": "Birdland",
    "mohegan sun arena": "Mohegan Sun Arena",
    "stade atlantique": "Stade Atlantique",
    "stade velodrome": "Stade Vélodrome",
}


# Only verified venue identities belong here.  These values correct stale or
# missing source geography; they are not guesses based on the venue spelling.
VENUE_GEOGRAPHY = {
    # Only verified venue identities belong here. These values correct stale or
    # missing source geography; they are not guesses based on venue spelling.
    "Stade de France": ("Saint-Denis", "93"),
    "La Marbrerie": ("Montreuil", "93"),
    "La Seine Musicale": ("Boulogne-Billancourt", "92"),
    "L’Accord Parfait": ("Paris", "75"),
    "Plénitude Arena": ("Nanterre", "92"),
    "Théâtre Claude Debussy": ("Maisons-Alfort", "94"),

    "Le Forum": ("Vauréal", "95"),
    "Maison des Arts de Créteil": ("Créteil", "94"),
    "Salle Jacques Brel": ("Fontenay-sous-Bois", "94"),
    "Studio Sextan": ("Malakoff", "92"),
    "Mains d'Oeuvres": ("Saint-Ouen", "93"),

    "Divan du Monde": ("Paris", "75"),
    "Le Klub": ("Paris", "75"),
    "La Bellevilloise": ("Paris", "75"),
    "Badaboum": ("Paris", "75"),
    "Batofar": ("Paris", "75"),
    "Grande Halle de la Villette": ("Paris", "75"),
    "Glazart": ("Paris", "75"),
    "La Dame de Canton": ("Paris", "75"),
    "La Mécanique Ondulatoire": ("Paris", "75"),
    "Palais de la Porte Dorée": ("Paris", "75"),
    "Quartier Général Oberkampf": ("Paris", "75"),
    "Le Sub Pigalle": ("Paris", "75"),
    "Hippodrome de Longchamp": ("Paris", "75"),
    "Cité de la Musique": ("Paris", "75"),
    "Pan Piper": ("Paris", "75"),
    "La Flèche d'Or": ("Paris", "75"),
    "Le 104": ("Paris", "75"),
    "Le Zèbre de Belleville": ("Paris", "75"),
    "Sunset/Sunside": ("Paris", "75"),
    "Flow": ("Paris", "75"),
    "Jazz Club Étoile": ("Paris", "75"),
    "Athénée-Théatre Louis Jouvet": ("Paris", "75"),
    "Théatre du Châtelet": ("Paris", "75"),
    "FNAC Ternes": ("Paris", "75"),
    "FNAC Forum": ("Paris", "75"),
    "Gibert Disc": ("Paris", "75"),
    "Radio Nova": ("Paris", "75"),
    "Novotel Les Halles": ("Paris", "75"),
    "The Mixtape": ("Paris", "75"),
    "Alabama Bar": ("Paris", "75"),

    "Hellfest": ("Clisson", "44"),
    "Chateau de Chantilly": ("Chantilly", "60"),

    "Forest Hills Stadium": ("New York", ""),
    "Greek Theatre": ("Los Angeles", ""),
    "Qualcomm Stadium": ("San Diego", ""),
    "Mohegan Sun Arena": ("Uncasville", ""),
    "Genting Arena": ("Birmingham", ""),
    "SSE Arena Wembley": ("Wembley", ""),
    "Birdland": ("New York", ""),
    "Dôme de Paris – Palais des Sports": ("Paris", "75"),
    "SummerStage at Central Park": ("New York", ""),
    "Stade Atlantique": ("Bordeaux", "33"),
    "Stade Vélodrome": ("Marseille", "13"),
}



VENUE_LOCATION_ALIASES = {
    ("le forum", "vaureal"): "Le Forum",
    ("maison des arts", "creteil"): "Maison des Arts de Créteil",
    ("salle jacques brel", "fontenay sous bois"): "Salle Jacques Brel",
    ("greek theatre", "los angeles"): "Greek Theatre",
    ("sse arena", "wembley"): "SSE Arena Wembley",
}


def normalize_location_key(value: str) -> str:
    """Normalize city/location text for city-aware venue matching."""
    return normalize_venue_key(value)


def resolve_venue_name(value: str, city: str | None = None) -> str | None:
    """
    Resolve a venue string conservatively.

    First use globally safe aliases. If that fails, use the venue + city pair
    for names which are ambiguous without geography. Unknown values remain
    unresolved.
    """
    venue_key = normalize_venue_key(value)

    if not venue_key:
        return None

    resolved = VENUE_ALIASES.get(venue_key)
    if resolved is not None:
        return resolved

    wrapped = _wrapped_known_venue(value)
    if wrapped is not None:
        return wrapped

    if city:
        return VENUE_LOCATION_ALIASES.get(
            (venue_key, normalize_location_key(city))
        )

    return None


UNKNOWN_VENUES = set()


def normalize_venue_key(value: str) -> str:
    """
    Convert a venue name into a stable key for alias matching.
    """

    normalized = unicodedata.normalize("NFKD", unescape(value or ""))
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


def _wrapped_known_venue(value: str) -> str | None:
    """
    Resolve a known venue embedded after promotional/contextual copy.

    Prefixes are discarded only when a suffix independently resolves
    through VENUE_ALIASES. Unknown wrapped venue strings remain intact.
    """
    parts = [
        part.strip()
        for part in re.split(
            r"\s+(?:[-–—]|:)\s+",
            unescape(value or ""),
        )
        if part.strip()
    ]

    if len(parts) < 2:
        return None

    for index in range(1, len(parts)):
        candidate = " ".join(parts[index:])
        normalized = VENUE_ALIASES.get(normalize_venue_key(candidate))
        if normalized is not None:
            return normalized

    return None


def clean_unknown_venue_name(value: str) -> str:
    """
    Apply conservative cleanup to an unknown venue name.

    Unknown venue names are not forced into title case because that could
    damage intentional capitalization.
    """

    cleaned = re.sub(r"\s+", " ", unescape(value or "")).strip()
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
    normalized_venue = resolve_venue_name(
        original_venue,
        event.city,
    )

    if normalized_venue is not None:
        event.venue = normalized_venue
        if normalized_venue in VENUE_GEOGRAPHY:
            event.city, event.department = VENUE_GEOGRAPHY[normalized_venue]
    else:
        event.venue = clean_unknown_venue_name(original_venue)

        if event.venue and event.venue not in UNKNOWN_VENUES:
            UNKNOWN_VENUES.add(event.venue)
            print(f"Unknown venue alias: {event.venue}")

    return event
