"""L’Empreinte's official Grand Paris Sud ticket office."""
from concert_calendar.scrapers._official_mapado import load_official

SOURCE_NAME = "L’Empreinte"
PROGRAMME_URL = "https://lempreinte.mapado.com/"


def load_events(today=None):
    return load_official(PROGRAMME_URL, SOURCE_NAME, "Savigny-le-Temple", "77", {"/v1/venues/51846"}, today)
