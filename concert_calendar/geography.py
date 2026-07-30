import re
import unicodedata
from typing import Optional


ILE_DE_FRANCE_DEPARTMENTS = {
    "75": "Paris",
    "77": "Seine-et-Marne",
    "78": "Yvelines",
    "91": "Essonne",
    "92": "Hauts-de-Seine",
    "93": "Seine-Saint-Denis",
    "94": "Val-de-Marne",
    "95": "Val-d'Oise",
}


# Initial commune lookup.
#
# This will be expanded as new sources introduce additional cities.
# Keys are normalized by normalize_location_key().
ILE_DE_FRANCE_CITIES = {
    # Paris
    "paris": ("Paris", "75"),

    # Seine-et-Marne
    "bailly romainvilliers": ("Bailly-Romainvilliers", "77"),
    "bussy saint georges": ("Bussy-Saint-Georges", "77"),
    "chelles": ("Chelles", "77"),
    "chessy": ("Chessy", "77"),
    "coulommiers": ("Coulommiers", "77"),
    "fontainebleau": ("Fontainebleau", "77"),
    "lieusaint": ("Lieusaint", "77"),
    "meaux": ("Meaux", "77"),
    "melun": ("Melun", "77"),
    "mitry mory": ("Mitry-Mory", "77"),
    "montereau fault yonne": ("Montereau-Fault-Yonne", "77"),
    "noisiel": ("Noisiel", "77"),
    "pontault combault": ("Pontault-Combault", "77"),
    "provins": ("Provins", "77"),
    "savigny le temple": ("Savigny-le-Temple", "77"),
    "serris": ("Serris", "77"),
    "torcy": ("Torcy", "77"),

    # Yvelines
    "aubergenville": ("Aubergenville", "78"),
    "chatou": ("Chatou", "78"),
    "conflans sainte honorine": ("Conflans-Sainte-Honorine", "78"),
    "elancourt": ("Élancourt", "78"),
    "guyancourt": ("Guyancourt", "78"),
    "houilles": ("Houilles", "78"),
    "la celle saint cloud": ("La Celle-Saint-Cloud", "78"),
    "le chesnay rocquencourt": ("Le Chesnay-Rocquencourt", "78"),
    "le pecq": ("Le Pecq", "78"),
    "les mureaux": ("Les Mureaux", "78"),
    "maisons laffitte": ("Maisons-Laffitte", "78"),
    "mantes la jolie": ("Mantes-la-Jolie", "78"),
    "montigny le bretonneux": ("Montigny-le-Bretonneux", "78"),
    "poissy": ("Poissy", "78"),
    "rambouillet": ("Rambouillet", "78"),
    "saint germain en laye": ("Saint-Germain-en-Laye", "78"),
    "sartrouville": ("Sartrouville", "78"),
    "trappes": ("Trappes", "78"),
    "velizy villacoublay": ("Vélizy-Villacoublay", "78"),
    "versailles": ("Versailles", "78"),

    # Essonne
    "athis mons": ("Athis-Mons", "91"),
    "bretigny sur orge": ("Brétigny-sur-Orge", "91"),
    "corbeil essonnes": ("Corbeil-Essonnes", "91"),
    "courcouronnes": ("Courcouronnes", "91"),
    "dourdan": ("Dourdan", "91"),
    "draveil": ("Draveil", "91"),
    "evry": ("Évry-Courcouronnes", "91"),
    "evry courcouronnes": ("Évry-Courcouronnes", "91"),
    "grigny": ("Grigny", "91"),
    "juvisy sur orge": ("Juvisy-sur-Orge", "91"),
    "les ulis": ("Les Ulis", "91"),
    "longjumeau": ("Longjumeau", "91"),
    "massy": ("Massy", "91"),
    "mennecy": ("Mennecy", "91"),
    "milly la foret": ("Milly-la-Forêt", "91"),
    "montgeron": ("Montgeron", "91"),
    "orsay": ("Orsay", "91"),
    "palaiseau": ("Palaiseau", "91"),
    "ris orangis": ("Ris-Orangis", "91"),
    "sainte genevieve des bois": ("Sainte-Geneviève-des-Bois", "91"),
    "savigny sur orge": ("Savigny-sur-Orge", "91"),
    "viry chatillon": ("Viry-Châtillon", "91"),
    "yerres": ("Yerres", "91"),

    # Hauts-de-Seine
    "antony": ("Antony", "92"),
    "asnieres sur seine": ("Asnières-sur-Seine", "92"),
    "boulogne billancourt": ("Boulogne-Billancourt", "92"),
    "bourg la reine": ("Bourg-la-Reine", "92"),
    "chatenay malabry": ("Châtenay-Malabry", "92"),
    "chatillon": ("Châtillon", "92"),
    "clamart": ("Clamart", "92"),
    "clichy": ("Clichy", "92"),
    "colombes": ("Colombes", "92"),
    "courbevoie": ("Courbevoie", "92"),
    "fontenay aux roses": ("Fontenay-aux-Roses", "92"),
    "gennevilliers": ("Gennevilliers", "92"),
    "issy les moulineaux": ("Issy-les-Moulineaux", "92"),
    "la defense": ("La Défense", "92"),
    "levallois perret": ("Levallois-Perret", "92"),
    "malakoff": ("Malakoff", "92"),
    "meudon": ("Meudon", "92"),
    "montrouge": ("Montrouge", "92"),
    "nanterre": ("Nanterre", "92"),
    "neuilly sur seine": ("Neuilly-sur-Seine", "92"),
    "puteaux": ("Puteaux", "92"),
    "rueil malmaison": ("Rueil-Malmaison", "92"),
    "saint cloud": ("Saint-Cloud", "92"),
    "sevres": ("Sèvres", "92"),
    "suresnes": ("Suresnes", "92"),

    # Seine-Saint-Denis
    "aubervilliers": ("Aubervilliers", "93"),
    "aulnay sous bois": ("Aulnay-sous-Bois", "93"),
    "bagnolet": ("Bagnolet", "93"),
    "bobigny": ("Bobigny", "93"),
    "bondy": ("Bondy", "93"),
    "clichy sous bois": ("Clichy-sous-Bois", "93"),
    "drancy": ("Drancy", "93"),
    "epinay sur seine": ("Épinay-sur-Seine", "93"),
    "gagny": ("Gagny", "93"),
    "la courneuve": ("La Courneuve", "93"),
    "le blanc mesnil": ("Le Blanc-Mesnil", "93"),
    "le bourget": ("Le Bourget", "93"),
    "les lilas": ("Les Lilas", "93"),
    "livry gargan": ("Livry-Gargan", "93"),
    "montreuil": ("Montreuil", "93"),
    "neuilly plaisance": ("Neuilly-Plaisance", "93"),
    "noisy le grand": ("Noisy-le-Grand", "93"),
    "pantin": ("Pantin", "93"),
    "pierrefitte sur seine": ("Pierrefitte-sur-Seine", "93"),
    "romainville": ("Romainville", "93"),
    "rosny sous bois": ("Rosny-sous-Bois", "93"),
    "saint denis": ("Saint-Denis", "93"),
    "saint ouen": ("Saint-Ouen-sur-Seine", "93"),
    "saint ouen sur seine": ("Saint-Ouen-sur-Seine", "93"),
    "sevran": ("Sevran", "93"),
    "stains": ("Stains", "93"),
    "tremblay en france": ("Tremblay-en-France", "93"),
    "villepinte": ("Villepinte", "93"),

    # Val-de-Marne
    "alfortville": ("Alfortville", "94"),
    "arcueil": ("Arcueil", "94"),
    "cachan": ("Cachan", "94"),
    "champigny sur marne": ("Champigny-sur-Marne", "94"),
    "charenton le pont": ("Charenton-le-Pont", "94"),
    "choisy le roi": ("Choisy-le-Roi", "94"),
    "creteil": ("Créteil", "94"),
    "fontenay sous bois": ("Fontenay-sous-Bois", "94"),
    "fresnes": ("Fresnes", "94"),
    "gentilly": ("Gentilly", "94"),
    "ivry sur seine": ("Ivry-sur-Seine", "94"),
    "joinville le pont": ("Joinville-le-Pont", "94"),
    "le kremlin bicetre": ("Le Kremlin-Bicêtre", "94"),
    "maisons alfort": ("Maisons-Alfort", "94"),
    "nogent sur marne": ("Nogent-sur-Marne", "94"),
    "orly": ("Orly", "94"),
    "rungis": ("Rungis", "94"),
    "saint maur des fosses": ("Saint-Maur-des-Fossés", "94"),
    "thiais": ("Thiais", "94"),
    "villejuif": ("Villejuif", "94"),
    "villeneuve saint georges": ("Villeneuve-Saint-Georges", "94"),
    "vincennes": ("Vincennes", "94"),
    "vitry sur seine": ("Vitry-sur-Seine", "94"),

    # Val-d'Oise
    "argenteuil": ("Argenteuil", "95"),
    "bezons": ("Bezons", "95"),
    "cergy": ("Cergy", "95"),
    "cergy pontoise": ("Cergy-Pontoise", "95"),
    "deuil la barre": ("Deuil-la-Barre", "95"),
    "enghien les bains": ("Enghien-les-Bains", "95"),
    "eragny": ("Éragny", "95"),
    "ermont": ("Ermont", "95"),
    "ezanville": ("Ézanville", "95"),
    "franconville": ("Franconville", "95"),
    "garges les gonesse": ("Garges-lès-Gonesse", "95"),
    "gonesse": ("Gonesse", "95"),
    "herblay sur seine": ("Herblay-sur-Seine", "95"),
    "l isle adam": ("L'Isle-Adam", "95"),
    "montigny les cormeilles": ("Montigny-lès-Cormeilles", "95"),
    "montmorency": ("Montmorency", "95"),
    "pontoise": ("Pontoise", "95"),
    "roissy en france": ("Roissy-en-France", "95"),
    "saint gratien": ("Saint-Gratien", "95"),
    "sannois": ("Sannois", "95"),
    "sarcelles": ("Sarcelles", "95"),
    "soisy sous montmorency": ("Soisy-sous-Montmorency", "95"),
    "taverny": ("Taverny", "95"),
}


def normalize_location_key(value: str) -> str:
    """
    Convert a city name into a stable lookup key.

    Examples:
        "BRÉTIGNY-SUR-ORGE" -> "bretigny sur orge"
        "Saint-Ouen-sur-Seine" -> "saint ouen sur seine"
    """

    normalized = unicodedata.normalize("NFKD", value or "")
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    normalized = normalized.casefold()
    normalized = normalized.replace("’", "'")
    normalized = re.sub(r"['`]", " ", normalized)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def find_ile_de_france_city(
    city: str,
) -> Optional[tuple[str, str]]:
    """
    Return the canonical city name and department code.

    Returns:
        ("Brétigny-sur-Orge", "91")

    Returns None when the city is not found in the lookup table.
    """

    city_key = normalize_location_key(city)

    if not city_key:
        return None

    return ILE_DE_FRANCE_CITIES.get(city_key)


def is_ile_de_france_department(department: str) -> bool:
    """
    Return True when the department code belongs to Île-de-France.
    """

    return str(department or "").strip() in ILE_DE_FRANCE_DEPARTMENTS
from concert_calendar.models import ConcertEvent


def normalize_event_geography(
    event: ConcertEvent,
) -> ConcertEvent:
    """
    Normalize an event's city and assign its Île-de-France department.

    The event is modified in place and returned.

    When the city is unknown or outside Île-de-France, the existing city is
    left unchanged and the department is left unchanged.
    """

    city_match = find_ile_de_france_city(event.city)

    if city_match is None:
        return event

    canonical_city, department = city_match

    event.city = canonical_city
    event.department = department

    return event
def is_ile_de_france_event(event: ConcertEvent) -> bool:
    """
    Return True when the event belongs to an Île-de-France department.

    The event must be normalized before this function is called.
    """

    return is_ile_de_france_department(event.department)