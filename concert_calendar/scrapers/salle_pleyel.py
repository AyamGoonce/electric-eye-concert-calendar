import re
import unicodedata
from datetime import date

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Salle Pleyel"
PROGRAMME_URL = "https://www.sallepleyel.com/concerts-spectacles/"
REQUEST_TIMEOUT = 30
MAX_PAGES = 5
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36"}
MONTHS = {
    "janv": 1, "janvier": 1, "fevr": 2, "fevrier": 2, "mars": 3,
    "avr": 4, "avril": 4, "mai": 5, "juin": 6, "juil": 7,
    "juillet": 7, "aout": 8, "sept": 9, "septembre": 9,
    "oct": 10, "octobre": 10, "nov": 11, "novembre": 11,
    "dec": 12, "decembre": 12,
}


def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def folded(value):
    return "".join(c for c in unicodedata.normalize("NFKD", clean(value)) if not unicodedata.combining(c)).casefold()


def parse_dates(value):
    normalized = folded(value)
    year_match = re.search(r"\b(20\d{2})\b", normalized)
    month_match = re.search(r"\b(" + "|".join(MONTHS) + r")\b", normalized)
    if not year_match or not month_match:
        return []
    days = [int(day) for day in re.findall(r"\b(\d{1,2})\b", normalized[:month_match.start()])]
    result = []
    for day in days[-2:]:
        try:
            result.append(date(int(year_match.group(1)), MONTHS[month_match.group(1)], day))
        except ValueError:
            pass
    return result


def parse_detail_billing(html, fallback_title):
    """
    Resolve explicit Salle Pleyel tribute billing from the official detail page.

    Example:
      PHIL COLLINS GENESIS - Tribute avec Martin Levac

    The named performer becomes the artist identity; the tribute wording
    remains the event title. No inference is made from artist names alone.
    """
    soup = BeautifulSoup(html or "", "html.parser")
    heading = soup.select_one("h1.eventPage__artist")
    detail_title = clean(
        heading.get_text(" ", strip=True)
        if heading
        else ""
    )

    if not detail_title:
        return None

    match = re.fullmatch(
        r"(?P<title>.+?\s+-\s+(?:tribute|hommage))\s+"
        r"(?:avec|with)\s+(?P<performer>.+)",
        detail_title,
        re.IGNORECASE,
    )

    if not match:
        return None

    performer = clean(match.group("performer"))
    event_title = clean(match.group("title"))

    if not performer or not event_title:
        return None

    return {
        "headliner": performer,
        "event_title": event_title,
        "raw_title": detail_title,
    }


def parse_card(card):
    title = card.select_one(
        ".eventPage__nextEvents-eventTitle[href], .eventTitle[href]"
    )
    headliner = clean(title.get_text(" ", strip=True)) if title else ""
    date_element = card.select_one(".eventPage__nextEvents-event-startDate")
    if date_element:
        dates = parse_dates(clean(date_element.get_text(" ", strip=True)))
    else:
        day = clean((card.select_one(".startDate-dayNumber") or card).get_text(" ", strip=True))
        month = clean((card.select_one(".eventPage__date-month") or card).get_text(" ", strip=True))
        year = clean((card.select_one(".startDate-year") or card).get_text(" ", strip=True))
        dates = parse_dates(f"{day} {month} {year}")
    image_url = element_image_url(
        card.select_one(".eventPage__nextEvents-eventImageHolder img, .holder__right img"),
        base_url=PROGRAMME_URL,
    )
    genre = clean((card.select_one(".eventPage__nextEvents-event-category, .eventCategory") or card).get_text(" ", strip=True)) or None
    if not headliner or not title:
        return []
    return [ConcertEvent(date=d.isoformat(), headliner=headliner, venue=SOURCE_NAME, city="Paris", department="75", genre=genre, ticket_url=clean(title.get("href")), image_url=image_url, image_source=SOURCE_NAME if image_url else None) for d in dates if d >= date.today()]


def load_events():
    events = {}
    detail_cache = {}
    session = requests.Session()

    for page in range(1, MAX_PAGES + 1):
        response = session.get(
            PROGRAMME_URL,
            params={"paged": page} if page > 1 else None,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select(".event-item.allEvents")
        if not cards:
            break

        for card in cards:
            for event in parse_card(card):
                if event.ticket_url:
                    if event.ticket_url not in detail_cache:
                        try:
                            detail_response = session.get(
                                event.ticket_url,
                                headers=HEADERS,
                                timeout=REQUEST_TIMEOUT,
                            )
                            detail_response.raise_for_status()
                        except requests.RequestException:
                            detail_cache[event.ticket_url] = None
                        else:
                            detail_cache[event.ticket_url] = parse_detail_billing(
                                detail_response.text,
                                event.headliner,
                            )

                    billing = detail_cache.get(event.ticket_url)
                    if billing:
                        event.headliner = billing["headliner"]
                        event.event_title = billing["event_title"]
                        event.raw_title = billing["raw_title"]

                events.setdefault(
                    (event.date, event.headliner.casefold(), event.venue.casefold()),
                    event,
                )

    return discard_repeated_generic_images(list(events.values()))
