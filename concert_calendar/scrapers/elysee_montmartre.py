import re
import unicodedata
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Élysée Montmartre"
PROGRAMME_URL = "https://www.elyseemontmartre.com/fr/programmation/"
REQUEST_TIMEOUT = 30
MAX_PAGES = 6
MAX_DETAIL_PAGES = 20
MAX_DIAGNOSTICS = 200
_DIAGNOSTICS = []
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36"}
MONTHS = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12}


def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def folded(value):
    return "".join(c for c in unicodedata.normalize("NFKD", clean(value)) if not unicodedata.combining(c)).casefold()


def parse_dates(value):
    normalized = folded(value)
    year_match = re.search(r"\b(20\d{2})\b", normalized)
    if not year_match:
        return []
    result = []
    for day, month_name in re.findall(r"\b(\d{1,2})\s+(" + "|".join(MONTHS) + r")\b", normalized):
        try:
            result.append(date(int(year_match.group(1)), MONTHS[month_name], int(day)))
        except ValueError:
            pass
    return result


def parse_card(card):
    title = card.select_one("a.link[href][title]")
    headliner = clean(title.get("title")) if title else ""
    dates = parse_dates(clean((card.select_one(".date") or card).get_text(" ", strip=True)))
    image_url = element_image_url(card.select_one(".visuel img"), base_url=PROGRAMME_URL)
    if not title or not headliner:
        return []
    events = [ConcertEvent(date=d.isoformat(), headliner=headliner, venue=SOURCE_NAME, city="Paris", department="75", ticket_url=clean(title.get("href")), image_url=image_url, image_source=SOURCE_NAME if image_url else None) for d in dates if d >= date.today()]
    if events and (re.search(r"\s[+&/]\s|\b(?:with|feat\.?|featuring)\b", headliner, re.I) or len(events) > 1):
        for event in events:
            _DIAGNOSTICS.append({
                "source_event_id": clean(title.get("data-id") or card.get("data-id")) or None,
                "listing_url": PROGRAMME_URL,
                "detail_url": clean(title.get("href")),
                "raw_event_title": headliner,
                "raw_date": clean((card.select_one(".date") or card).get_text(" ", strip=True)),
                "final_date": event.date,
                "raw_venue": SOURCE_NAME,
                "final_venue": event.venue,
                "parser_billing_path": "plain_title",
                "parsed_headliner": event.headliner,
                "parsed_co_headliners": event.co_headliners,
                "parsed_openers": event.openers,
            })
        del _DIAGNOSTICS[MAX_DIAGNOSTICS:]
    return events


def detail_performers(html, title):
    """Confirm a '+' bill only from independent official detail-page labels."""

    components = [clean(value) for value in re.split(r"\s+\+\s+", title)]
    if len(components) < 2 or any(
        re.fullmatch(r"(?:special\s+)?guests?", value, re.I)
        for value in components
    ):
        return []

    soup = BeautifulSoup(html or "", "html.parser")
    evidenced = {}
    for node in soup.select(".part.css_text strong"):
        value = clean(node.get_text(" ", strip=True))
        if value:
            evidenced.setdefault(folded(value), value)

    performers = []
    for component in components:
        matched = evidenced.get(folded(component))
        if not matched:
            return []
        performers.append(matched)
    return performers


def load_events():
    _DIAGNOSTICS.clear()
    events = {}
    detail_cache = {}
    detail_count = 0
    session = requests.Session()
    for page in range(1, MAX_PAGES + 1):
        url = PROGRAMME_URL if page == 1 else urljoin(PROGRAMME_URL, f"page/{page}/")
        response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select(".bloc_extrait.evenement")
        if not cards:
            break
        for card in cards:
            parsed_events = parse_card(card)
            if (
                parsed_events
                and re.search(r"\s+\+\s+", parsed_events[0].headliner)
                and detail_count < MAX_DETAIL_PAGES
            ):
                detail_url = parsed_events[0].ticket_url
                if detail_url not in detail_cache:
                    detail_count += 1
                    try:
                        detail_response = session.get(
                            detail_url,
                            headers=HEADERS,
                            timeout=REQUEST_TIMEOUT,
                        )
                        detail_response.raise_for_status()
                    except requests.RequestException as error:
                        detail_cache[detail_url] = []
                        _DIAGNOSTICS.append({
                            "source_event_id": None,
                            "listing_url": PROGRAMME_URL,
                            "detail_url": detail_url,
                            "raw_event_title": parsed_events[0].headliner,
                            "final_date": parsed_events[0].date,
                            "raw_venue": SOURCE_NAME,
                            "final_venue": SOURCE_NAME,
                            "parser_billing_path": "detail_fetch_failed",
                            "diagnostic_error": (
                                f"{type(error).__name__}: {error}"
                            ),
                        })
                    else:
                        detail_cache[detail_url] = detail_performers(
                            detail_response.text,
                            parsed_events[0].headliner,
                        )
                performers = detail_cache.get(detail_url, [])
                if performers:
                    for event in parsed_events:
                        event.performers = list(performers)
                        event.event_title = event.headliner
                        event.raw_title = event.headliner
            for event in parsed_events:
                events.setdefault((event.date, event.headliner.casefold(), event.venue.casefold()), event)
        if not soup.select_one("link[rel='next']"):
            break
    return discard_repeated_generic_images(list(events.values()))


def get_diagnostics():
    return list(_DIAGNOSTICS)
