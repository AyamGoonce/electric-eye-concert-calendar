from datetime import date
import json
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Plénitude Arena"
PROGRAMME_URL = "https://www.plenitudearena.com/billetterie/"
REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Safari/537.36"}


def _clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_programme(soup):
    cards = []
    for card in soup.select("article[data-listing-item][data-dl-item]"):
        try:
            tracking = json.loads(card.get("data-dl-item", "{}"))
        except (TypeError, json.JSONDecodeError):
            continue
        if _clean(tracking.get("item_category5")).casefold() != "concert":
            continue
        link = card.select_one("a.listing__card-link[href]")
        if not link:
            continue
        title = _clean(link.get_text(" ", strip=True))
        if not title:
            continue
        cards.append({
            "title": title,
            "url": urljoin(PROGRAMME_URL, link["href"]),
            "image_url": element_image_url(
                card.select_one(".listing__media img"), base_url=PROGRAMME_URL
            ),
        })
    return cards


def parse_detail(soup, card, *, today=None):
    cutoff = today or date.today()
    calendar = soup.select_one("[data-jours]")
    if not calendar:
        return _parse_structured_single(soup, card, cutoff)
    try:
        performances = json.loads(calendar.get("data-jours", "{}"))
    except (TypeError, json.JSONDecodeError):
        return []
    events = []
    for date_value, sessions in performances.items():
        try:
            event_date = date.fromisoformat(date_value)
        except (TypeError, ValueError):
            continue
        if event_date < cutoff:
            continue
        for session in sessions if isinstance(sessions, list) else []:
            event_time = _clean(session.get("heure")) or None
            link = session.get("lien") if isinstance(session.get("lien"), dict) else {}
            ticket_url = _clean(link.get("url")) or card["url"]
            status = _clean(session.get("statut")).casefold()
            sold_out = status in {"complet", "epuise", "épuisé"}
            events.append(ConcertEvent(
                date=event_date.isoformat(), headliner=card["title"], venue=SOURCE_NAME,
                city="Nanterre", department="92", start_time=event_time,
                ticket_url=ticket_url,
                ticket_status="sold_out" if sold_out else "tickets",
                sold_out=sold_out, image_url=card.get("image_url"),
                image_source=SOURCE_NAME if card.get("image_url") else None,
            ))
    return events


def _parse_structured_single(soup, card, cutoff):
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(script.string or "")
        except (TypeError, json.JSONDecodeError):
            continue
        if payload.get("@type") != "Event":
            continue
        match = re.match(
            r"(\d{4})(\d{2})(\d{2})(?:T(\d{2}):(\d{2}))?",
            str(payload.get("startDate", "")),
        )
        if not match:
            continue
        year, month, day = map(int, match.groups()[:3])
        hour, minute = match.groups()[3:]
        try:
            event_date = date(year, month, day)
        except ValueError:
            continue
        if event_date < cutoff or str(payload.get("eventStatus", "")).endswith("EventCancelled"):
            return []
        offers = payload.get("offers") if isinstance(payload.get("offers"), dict) else {}
        availability = str(offers.get("availability", ""))
        sold_out = availability.endswith("SoldOut")
        return [ConcertEvent(
            date=event_date.isoformat(), headliner=card["title"], venue=SOURCE_NAME,
            city="Nanterre", department="92",
            start_time=f"{int(hour):02d}:{int(minute):02d}" if hour and minute else None,
            ticket_url=_clean(offers.get("url")) or card["url"],
            ticket_status="sold_out" if sold_out else "tickets", sold_out=sold_out,
            image_url=card.get("image_url"),
            image_source=SOURCE_NAME if card.get("image_url") else None,
        )]
    return []


def load_events():
    session = requests.Session()
    print(f"Downloading Plénitude Arena programme: {PROGRAMME_URL}")
    response = session.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    cards = parse_programme(BeautifulSoup(response.text, "html.parser"))
    events = []
    for index, card in enumerate(cards, 1):
        print(f"Reading Plénitude Arena concert {index}/{len(cards)}: {card['title']}")
        detail = session.get(card["url"], headers=HEADERS, timeout=REQUEST_TIMEOUT)
        detail.raise_for_status()
        events.extend(parse_detail(BeautifulSoup(detail.text, "html.parser"), card))
    unique = {}
    for event in events:
        unique.setdefault((event.date, event.start_time, event.headliner.casefold()), event)
    result = discard_repeated_generic_images(list(unique.values()))
    print(f"Created {len(result)} Plénitude Arena ConcertEvent records")
    return result
