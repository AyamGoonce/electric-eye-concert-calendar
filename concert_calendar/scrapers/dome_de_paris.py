from datetime import date, timedelta
import re
import unicodedata
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent
from concert_calendar.title_quality import is_placeholder_title


SOURCE_NAME = "Le Dôme de Paris"
PROGRAMME_URL = "https://www.ledomedeparis.com/fr/spectacles/a-laffiche"
REQUEST_TIMEOUT = 30
MAX_TITLE_DETAILS = 16
HEADERS = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Safari/537.36"}
MONTHS = {
    "janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5,
    "juin": 6, "juillet": 7, "aout": 8, "septembre": 9,
    "octobre": 10, "novembre": 11, "decembre": 12,
}
def _clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def _key(value):
    value = unicodedata.normalize("NFKD", _clean(value).casefold())
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in value if not unicodedata.combining(c))).strip()


def _dates(value):
    normalized = _key(value)
    single = re.search(r"\b(\d{1,2})\s+([a-z]+)\s+(\d{4})\b", normalized)
    ranged = re.search(
        r"\bdu\s+(\d{1,2})(?:\s+([a-z]+))?\s+au\s+(\d{1,2})\s+([a-z]+)\s+(\d{4})\b",
        normalized,
    )
    try:
        if ranged:
            start_day, start_month_name, end_day, end_month_name, year = ranged.groups()
            end_month = MONTHS[end_month_name]
            start_month = MONTHS[start_month_name] if start_month_name else end_month
            start = date(int(year), start_month, int(start_day))
            end = date(int(year), end_month, int(end_day))
            if end < start or (end - start).days > 31:
                return []
            return [start + timedelta(days=offset) for offset in range((end - start).days + 1)]
        if single:
            day, month_name, year = single.groups()
            return [date(int(year), MONTHS[month_name], int(day))]
    except (KeyError, ValueError):
        pass
    return []


def detail_title_and_act(html, listing_title=""):
    """Return official title plus independently evidenced performer semantics."""
    soup = BeautifulSoup(html, "html.parser")
    metadata = soup.select_one('meta[property="og:title"][content]')
    title = _clean(metadata.get("content") if metadata else "")
    if not title and soup.title:
        title = _clean(soup.title.get_text(" ", strip=True))
    title = re.sub(r",\s*(?:Le\s+)?Dôme de Paris\s*$", "", title, flags=re.I).strip()
    if is_placeholder_title(title):
        return "", "", None

    description = soup.select_one('meta[name="description"][content]')
    prose_parts = [
        _clean(description.get("content") if description else "")
    ]

    # The Dôme's live event pages keep the substantive concert description
    # in an unclassed content div inside the main event column. Schedule and
    # pricing blocks use mt-4 and are deliberately excluded from billing
    # evidence.
    main_column = soup.select_one("div.col-lg-6.offset-lg-1")
    if main_column:
        for block in main_column.find_all("div", recursive=False):
            classes = set(block.get("class") or [])
            if "clearfix" in classes or "mt-4" in classes:
                continue
            visible_prose = _clean(" ".join(
                paragraph.get_text(" ", strip=True)
                for paragraph in block.find_all("p")
            ))
            if visible_prose:
                prose_parts.append(visible_prose)

    prose = _clean(" ".join(part for part in prose_parts if part))
    act = ""
    event_title = None

    # The promoter explicitly names a tribute act before describing its role.
    if re.search(r"\b(?:tribute|hommage)\b", title, re.I):
        match = re.search(
            r"\baccueillir\s+(?:à nouveau\s+)?"
            r"(?P<act>[A-ZÀ-ÖØ-Þ][A-ZÀ-ÖØ-Þ0-9'’&. -]{2,60}?)"
            r",\s+(?:le|la|un|une)\s+(?:Tribute Band|groupe|formation|artiste)\b",
            prose,
            re.I,
        )
        if match:
            candidate = _clean(match.group("act"))
            title_words = set(_key(title).split())
            if len(candidate.split()) <= 6 and set(_key(candidate).split()) & title_words:
                act = candidate
                event_title = title

    # Le Dôme sometimes publishes "PRODUCTION TITLE : ARTIST".  The colon is
    # not enough: the detail prose must independently identify that exact
    # suffix as the artist returning/performing in this current event.
    titled = title or _clean(listing_title)
    colon = re.fullmatch(r"(?P<context>.+?)\s*:\s*(?P<artist>[^:]+)", titled)
    if colon and not re.search(r"\b(?:tribute|hommage)\b", titled, re.I):
        candidate = _clean(colon.group("artist"))
        evidence = re.search(
            r"(?P<act>" + re.escape(candidate) + r")\s+"
            r"(?:revient\s+sur\s+scène|vous\s+donne\s+rendez-vous|"
            r"sera\s+(?:sur\s+scène|en\s+concert)|est\s+en\s+concert)",
            prose,
            re.I,
        )
        if evidence:
            act = _clean(evidence.group("act"))
            event_title = _clean(colon.group("context"))

    return title, act, event_title


def parse_events(soup, *, today=None, detail_resolver=None):
    cutoff = today or date.today()
    events = []
    for content in soup.select(".spectacle-content"):
        paragraph = content.select_one("p")
        title_link = content.select_one("h4 a[href]")
        if not paragraph or not title_link:
            continue
        parts = list(paragraph.stripped_strings)
        if not parts or _key(parts[0]) != "concert":
            continue
        dates = [item for item in _dates(" ".join(parts[1:])) if item >= cutoff]
        if not dates:
            continue
        listing_title = _clean(title_link.get_text(" ", strip=True))
        headliner = listing_title
        card = content.parent
        image = element_image_url(card.select_one("a.illus-img img"), base_url=PROGRAMME_URL)
        ticket_url = urljoin(PROGRAMME_URL, title_link["href"])
        event_title = None
        raw_title = None
        identity_aliases = None
        needs_detail = is_placeholder_title(listing_title) or bool(
            re.search(r"\s*:\s*", listing_title)
        )
        if needs_detail and detail_resolver is not None:
            official_title, named_act, detail_event_title = detail_title_and_act(
                detail_resolver(ticket_url), listing_title,
            )
            if is_placeholder_title(listing_title):
                if not official_title:
                    continue
                headliner = named_act or official_title
                event_title = detail_event_title or (
                    official_title if headliner != official_title else None
                )
            elif named_act:
                headliner = named_act
                event_title = detail_event_title or official_title
            if headliner != listing_title:
                raw_title = listing_title
                identity_aliases = [listing_title]
        elif is_placeholder_title(listing_title):
            continue
        if not headliner:
            continue
        for event_date in dates:
            if event_date < cutoff:
                continue
            events.append(ConcertEvent(
                date=event_date.isoformat(), headliner=headliner, venue=SOURCE_NAME,
                city="Paris", department="75", ticket_url=ticket_url,
                ticket_status="tickets", image_url=image,
                image_source=SOURCE_NAME if image else None,
                event_title=event_title,
                raw_title=raw_title,
                identity_aliases=identity_aliases,
            ))
    return events


def load_events():
    session = requests.Session()
    print(f"Downloading Le Dôme de Paris programme: {PROGRAMME_URL}")
    response = session.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    unique = {}
    title_details = {}

    def detail_resolver(url):
        if url not in title_details:
            if len(title_details) >= MAX_TITLE_DETAILS:
                raise RuntimeError("Le Dôme has too many title-detail requests")
            detail = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            detail.raise_for_status()
            title_details[url] = detail.text
        return title_details[url]

    for event in parse_events(
        BeautifulSoup(response.text, "html.parser"),
        detail_resolver=detail_resolver,
    ):
        unique.setdefault((event.date, event.headliner.casefold()), event)
    result = discard_repeated_generic_images(list(unique.values()))
    print(f"Created {len(result)} Le Dôme de Paris ConcertEvent records")
    return result
