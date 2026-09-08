"""Le Forum, Vauréal: official Cergy-Pontoise agenda and Event JSON-LD."""
import json
import re
from copy import deepcopy
from datetime import datetime
from html import unescape
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, official_image_url
from concert_calendar.geography import ILE_DE_FRANCE_DEPARTMENTS, normalize_location_key
from concert_calendar.models import ConcertEvent

SOURCE_NAME = "Le Forum (Vauréal)"
PROGRAMME_URL = "https://leforum.cergypontoise.fr/agenda"
MAX_DETAILS = 100
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ConcertCalendar/1.0)"}
MONTHS = {name: number for number, name in enumerate(
    ("janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout",
     "septembre", "octobre", "novembre", "decembre"), 1)}
WEEKDAYS = "lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche"


def performance_starts(item):
    """Use startDate; never expand an endDate range into assumed performances.

    The official description can explicitly enumerate two same-month evenings.
    Accept that construction only when its dates/time agree with both JSON-LD
    boundaries. Unexplained multi-day spans fail rather than losing a show.
    """
    start = datetime.fromisoformat(item["startDate"]).astimezone(ZoneInfo("Europe/Paris"))
    end = datetime.fromisoformat(item.get("endDate") or item["startDate"]).astimezone(ZoneInfo("Europe/Paris"))
    if start.date() == end.date():
        return [start]
    description = normalize_location_key(unescape(item.get("description", "")))
    match = re.search(
        rf"\bles ({WEEKDAYS}) (\d{{1,2}}) et ({WEEKDAYS}) (\d{{1,2}}) "
        r"([a-z]+) a (\d{1,2})h(\d{2})\b", description)
    if match and start.year == end.year and start.month == end.month == MONTHS.get(match[5]):
        if (int(match[2]), int(match[4]), int(match[6]), int(match[7])) == (start.day, end.day, start.hour, start.minute):
            weekdays = WEEKDAYS.split("|")
            if (weekdays[start.weekday()], weekdays[end.weekday()]) == (match[1], match[3]):
                return [start, start.replace(day=end.day)]
    raise ValueError("Le Forum: multi-day span needs explicit performance evidence")


def parse_detail(html, card, today):
    soup = BeautifulSoup(html, "html.parser")
    items = [json.loads(node.text) for node in soup.select('script[type="application/ld+json"]')]
    items = [item for item in items if item.get("@type") in {"Event", "MusicEvent", "EventSeries"}]
    if not items:
        raise ValueError("Le Forum: missing Event structured data")
    output = []
    for item in items:
        location = item.get("location", {})
        address = location.get("address", {})
        venue = (location.get("name") or "").strip()
        city = (address.get("addressLocality") or "").strip()
        postcode = str(address.get("postalCode", "")).strip()
        # Off-site concerts retain their explicit physical address. A different
        # "Le Forum" is not an alias for the Vauréal venue.
        if not venue or not city or not re.fullmatch(r"\d{5}", postcode):
            continue
        department = postcode[:2]
        if department not in ILE_DE_FRANCE_DEPARTMENTS or address.get("addressCountry") != "FR":
            continue
        if venue == "Le Forum" and (postcode != "95490" or normalize_location_key(city) != "vaureal"):
            continue
        categories = [x.strip() for x in item.get("keywords", "").split(",")]
        if "ROLLER DISCO PARTY" in categories or re.search(r"\b(?:PORTES OUVERTES|MARKET)\b", item["name"], re.I):
            continue
        status = item.get("eventStatus", "")
        if status.endswith(("EventCancelled", "EventPostponed")) or card.select('[data-status-key="cancelled"], [data-status-key="postponed"]'):
            continue
        starts = performance_starts(item)
        subtitle = card.select_one(".agenda--subtitle")
        subtitle = subtitle.get_text(" ", strip=True) if subtitle else ""
        # The visible card has a separate over-title for tour/promoter wording.
        # Its artist heading can be more precise than JSON-LD's event name.
        heading = deepcopy(card.select_one(".agenda--title"))
        if heading:
            for overtitle in heading.select(".ssks-event-over-title"):
                overtitle.decompose()
        title = heading.get_text(" ", strip=True) if heading else item["name"].strip()
        # A flat '+' subtitle is a full bill, not evidence of support hierarchy.
        if subtitle.startswith("+") and not re.fullmatch(r"\+\s*1[ÈE]RE PARTIE", subtitle, re.I):
            title += " " + subtitle
        image = item.get("image", {})
        image = official_image_url(image.get("url") if isinstance(image, dict) else image)
        offers = item.get("offers", [])
        if isinstance(offers, dict):
            offers = [offers]
        ticket = next((o.get("url") for o in offers if o.get("url")), item.get("url"))
        if isinstance(ticket, dict):
            ticket = ticket.get("uri")
        sold = bool(card.select('[data-status-key="full"]'))
        genre = ", ".join(c for c in categories if c not in {"Diffusion", "Événement", "Evénement", "Gratuit", "EN FAMILLE", "Jeune Public", "TOUT GENRE", "SPECTACLE", "Hors les murs", "DANSE", "MUSIQUE"}) or None
        for start in starts:
            if start.date() < today:
                continue
            output.append(ConcertEvent(
                date=start.date().isoformat(), start_time=start.strftime("%H:%M"),
                headliner=title, event_title=item["name"].strip(), venue=venue, city=city, department=department,
                genre=genre, ticket_url=ticket, sold_out=sold,
                ticket_status="sold_out" if sold else ("free" if "Gratuit" in categories else None),
                image_url=image, image_source=SOURCE_NAME if image else None,
            ))
    return output


def load_events(today=None):
    today = today or datetime.now(ZoneInfo("Europe/Paris")).date()
    with requests.Session() as session:
        session.headers.update(HEADERS)
        def get(url):
            response = session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        soup = BeautifulSoup(get(PROGRAMME_URL), "html.parser")
        cards = soup.select("a.agenda--item")
        if len(cards) > MAX_DETAILS or soup.select('.pager a[rel="next"], .pager__item--next a'):
            raise ValueError("Le Forum: programme exceeds captured complete agenda")
        output = {}
        for card in cards:
            url = urljoin(PROGRAMME_URL, card["href"])
            for event in parse_detail(get(url), card, today):
                output.setdefault((event.date, event.start_time, event.venue, event.headliner), event)
    return discard_repeated_generic_images(list(output.values()))
