import re
from datetime import date

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Le Pop-Up du Label"
PROGRAMME_URL = "https://www.popup.paris/agenda/"
REQUEST_TIMEOUT = 30
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36"
    )
}


def _clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def _background_image(card):
    image = card.select_one(".image[style]")
    if not image:
        return None
    match = re.search(r"background-image\s*:\s*url\((['\"]?)(.*?)\1\)", image.get("style", ""), re.I)
    return match.group(2).strip() if match and match.group(2).strip() else None


def _explicit_openers(card):
    detail = card.select_one(".infos_bis")
    text = _clean(detail.get_text(" ", strip=True) if detail else "")
    if not text.startswith("+"):
        return None
    names = [_clean(name) for name in re.split(r"\s*\+\s*", text.lstrip("+ "))]
    return [name for name in names if name] or None


def parse_events(soup, *, today=None):
    cutoff = today or date.today()
    events = []
    year = None

    # Month markers on the live page use invalid self-closing ``div`` markup,
    # which makes HTML parsers move later cards outside ``.concerts_mois``.
    for card in soup.select("div.concert"):
        if "mois" in (card.get("class") or []):
            marker = card.get("id", "")
            match = re.search(r"(\d{4})$", marker)
            year = int(match.group(1)) if match else year
            continue
        if year is None:
            continue

        day_text = _clean((card.select_one(".jour") or card).get_text(" ", strip=True))
        match = re.fullmatch(r"(\d{1,2})\.(\d{1,2})", day_text)
        if not match:
            continue
        day_number, month = map(int, match.groups())
        try:
            event_date = date(year, month, day_number)
        except ValueError:
            continue
        if event_date < cutoff:
            continue

        # The official agenda also advertises late-night club sessions. They are
        # identifiable by their explicit 23h-04h hours and are not concerts.
        info_text = " ".join(
            _clean(node.get_text(" ", strip=True))
            for node in card.select(".infos, .infos_bis")
        )
        if re.search(r"\b23\s*h\s*/\s*0?4\s*h\b", info_text, re.I):
            continue

        title_node = card.select_one(".titre")
        headliner = _clean(title_node.get_text(" ", strip=True) if title_node else "")
        if not headliner:
            continue

        links = card.select(".liens a[href]")
        ticket = next((link for link in links if "ticket" in _clean(link.get_text()).casefold()), None)
        facebook = next((link for link in links if "facebook" in _clean(link.get_text()).casefold()), None)
        sold_out = bool(re.search(r"\bsold\s*out\b|\bcomplet\b", info_text, re.I))
        image_url = _background_image(card)

        events.append(
            ConcertEvent(
                date=event_date.isoformat(),
                headliner=headliner,
                openers=_explicit_openers(card),
                venue=SOURCE_NAME,
                city="Paris",
                department="75",
                facebook_event_url=facebook.get("href") if facebook else None,
                ticket_url=ticket.get("href") if ticket else PROGRAMME_URL,
                ticket_status="sold_out" if sold_out else ("tickets" if ticket else None),
                sold_out=sold_out,
                image_url=image_url,
                image_source=SOURCE_NAME if image_url else None,
            )
        )
    return events


def load_events():
    session = requests.Session()
    print(f"Downloading Le Pop-Up du Label programme: {PROGRAMME_URL}")
    response = session.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    unique = {}
    for event in parse_events(BeautifulSoup(response.text, "html.parser")):
        unique.setdefault((event.date, event.headliner.casefold()), event)
    result = discard_repeated_generic_images(list(unique.values()))
    print(f"Created {len(result)} Le Pop-Up du Label ConcertEvent records")
    return result
