"""Le Plan's official ticket office (Club and Grande Salle share the venue)."""
from concert_calendar.scrapers._official_mapado import load_official

SOURCE_NAME = "Le Plan"
PROGRAMME_URL = "https://billetterie.leplan.com/"


def load_events(today=None):
    return load_official(PROGRAMME_URL, SOURCE_NAME, "Ris-Orangis", "91", {"/v1/venues/51475", "/v1/venues/51468", "/v1/venues/51461"}, today)
