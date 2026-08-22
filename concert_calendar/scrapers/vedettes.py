import re

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Vedettes"

EVENTS_URL = "https://www.vedettes.net/billetterie"
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}


MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def clean_text(value):
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def parse_date(day, month, year):
    day = clean_text(day)
    month = clean_text(month).casefold()
    year = clean_text(year)

    try:
        day_number = int(day)
        year_number = int(year)
    except ValueError:
        return ""

    month_number = MONTHS.get(month)

    if month_number is None:
        return ""

    return (
        f"{year_number:04d}-"
        f"{month_number:02d}-"
        f"{day_number:02d}"
    )


def find_ticket_url(card):
    """
    Prefer the visible Ticket button, then fall back to the artist link.
    """

    for link in card.select(".concert-links a[href]"):
        text = clean_text(
            link.get_text(" ", strip=True)
        ).casefold()

        if "ticket" in text:
            href = clean_text(link.get("href"))

            if (
                href
                and "facebook.com/events/" not in href.casefold()
            ):
                return href

    artist_link = card.select_one(
        ".artist-name[href]"
    )

    if artist_link:
        href = clean_text(
            artist_link.get("href")
        )

        if (
            href
            and "facebook.com/events/" not in href.casefold()
        ):
            return href

    return None


def find_facebook_event_url(card):
    for link in card.select(".concert-links a[href]"):
        href = clean_text(link.get("href"))

        if "facebook.com/events/" in href:
            return href

    return None


def parse_card(card):
    artist_element = card.select_one(
        ".artist-name .heading"
    )
    day_element = card.select_one(
        ".concert-month.day"
    )
    month_element = card.select_one(
        ".concert-month.month"
    )
    year_element = card.select_one(
        ".concert-year"
    )
    venue_element = card.select_one(
        ".concert-city"
    )
    city_element = card.select_one(
        ".concert-venue"
    )

    headliner = (
        clean_text(
            artist_element.get_text(" ", strip=True)
        )
        if artist_element
        else ""
    )

    event_date = parse_date(
        day_element.get_text(" ", strip=True)
        if day_element
        else "",
        month_element.get_text(" ", strip=True)
        if month_element
        else "",
        year_element.get_text(" ", strip=True)
        if year_element
        else "",
    )

    venue = (
        clean_text(
            venue_element.get_text(" ", strip=True)
        )
        if venue_element
        else ""
    )

    city = (
        clean_text(
            city_element.get_text(" ", strip=True)
        )
        if city_element
        else ""
    )

    if not headliner:
        return None

    if not event_date:
        return None

    if not venue:
        return None

    if not city:
        return None

    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        venue=venue,
        city=city,
        department="",
        openers=None,
        promoters=["Vedettes"],
        genre=None,
        facebook_event_url=find_facebook_event_url(
            card
        ),
        ticket_url=find_ticket_url(card),
    )


def load_events():
    print(f"Downloading {EVENTS_URL}...")

    response = requests.get(
        EVENTS_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    cards = soup.select(
        "div.concert.w-dyn-item"
    )

    events = []

    for card in cards:
        event = parse_card(card)

        if event is not None:
            events.append(event)

    print(
        f"Created {len(events)} "
        "Vedettes ConcertEvent records"
    )

    return events
