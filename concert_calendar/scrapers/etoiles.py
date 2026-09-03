import re
import unicodedata
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent

SOURCE_NAME = "Les Étoiles"
PROGRAMME_URL = "https://www.etoiles.paris/agenda/"
REQUEST_TIMEOUT = 30
MAX_PAGES = 10
HEADERS = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Safari/537.36"}
MONTHS = {"jan": 1, "fev": 2, "mar": 3, "avr": 4, "mai": 5, "juin": 6,
          "juil": 7, "aou": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}

def clean(value): return re.sub(r"\s+", " ", value or "").strip()
def fold(value):
    value = unicodedata.normalize("NFKD", clean(value))
    return "".join(c for c in value if not unicodedata.combining(c)).casefold()

def parse_card(card, *, today=None):
    tags = [fold(x.get_text(" ", strip=True)) for x in card.select(".tag")]
    if "concert" not in tags:
        return None
    title = clean((card.select_one(".component__title") or card).get_text(" ", strip=True))
    labels = [clean(x.get_text(" ", strip=True)) for x in card.select(".ts-label")]
    date_label = next((x for x in labels if re.fullmatch(r"\d{1,2}\s+[A-Za-zÀ-ÿ]+\.?", x)), "")
    match = re.fullmatch(r"(\d{1,2})\s+([A-Za-zÀ-ÿ]+)\.?", date_label)
    heading = card.find_previous("h2")
    year_match = re.search(r"20\d{2}", heading.get_text(" ", strip=True) if heading else "")
    if not title or not match or not year_match:
        return None
    month = MONTHS.get(fold(match.group(2))[:3])
    if not month:
        return None
    try: event_date = date(int(year_match.group()), month, int(match.group(1)))
    except ValueError: return None
    if event_date < (today or date.today()): return None
    time_label = next((x for x in labels if re.fullmatch(r"\d{2}:\d{2}", x)), None)
    image = element_image_url(card.select_one("img"), base_url=PROGRAMME_URL)
    return ConcertEvent(date=event_date.isoformat(), headliner=title, venue=SOURCE_NAME,
        city="Paris", department="75", ticket_url=urljoin(PROGRAMME_URL, card.get("href")),
        ticket_status="tickets", start_time=time_label, image_url=image,
        image_source=SOURCE_NAME if image else None)

def load_events():
    session=requests.Session(); events={}; url=PROGRAMME_URL; visited=set()
    for _ in range(MAX_PAGES):
        if not url or url in visited: break
        visited.add(url); print(f"Downloading Les Étoiles agenda: {url}")
        response=session.get(url,headers=HEADERS,timeout=REQUEST_TIMEOUT); response.raise_for_status()
        soup=BeautifulSoup(response.text,"html.parser"); cards=soup.select("a.component-card-event")
        if not cards: break
        for card in cards:
            event=parse_card(card)
            if event: events.setdefault((event.date,fold(event.headliner)),event)
        link=soup.select_one("link[rel='next'][href], a.next[href]")
        url=urljoin(url,link.get("href")) if link else None
    result=discard_repeated_generic_images(list(events.values()))
    print(f"Created {len(result)} Les Étoiles ConcertEvent records"); return result
