"""Read-only editorial article extraction for Electric Eye newsletters."""

from datetime import datetime
from html import unescape
import re
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

from concert_calendar.content_index import (
    alternate_url,
    blogger_post_id,
    classify_article,
)

PARIS = ZoneInfo("Europe/Paris")

ARTICLE_TYPES = (
    "concert_review",
    "album_review",
    "interview",
    "news",
    "playlist",
)



def newsletter_image_url(url):
    """Request a high-resolution Blogger image."""
    if not url or not isinstance(url, str):
        return url

    from urllib.parse import urlsplit, urlunsplit

    parsed = urlsplit(url)

    if parsed.hostname not in {
        "blogger.googleusercontent.com",
        "1.bp.blogspot.com",
        "2.bp.blogspot.com",
        "3.bp.blogspot.com",
        "4.bp.blogspot.com",
    }:
        return url

    path = parsed.path

    # Blogger composite sizing:
    # /s72-w640-h426-c-rw/image.jpg -> /w1200-h800/image.jpg
    path = re.sub(
        r"/s\d+(?:-[a-z0-9-]+)?(?=/)",
        "/w1200-h800",
        path,
        flags=re.I,
    )

    # Blogger equals-style sizing.
    path = re.sub(
        r"=s\d+(?:-[a-z0-9-]+)?$",
        "=w1200-h800",
        path,
        flags=re.I,
    )

    return urlunsplit((
        parsed.scheme,
        parsed.netloc,
        path,
        parsed.query,
        parsed.fragment,
    ))


def clean_summary(value, limit=300):
    """Convert a Blogger summary into a short plain-text excerpt."""
    text = BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", unescape(text)).strip()
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)

    if len(text) <= limit:
        return text

    shortened = text[: limit + 1].rsplit(" ", 1)[0]
    return shortened.rstrip(" ,;:") + "…"


def extract_articles(entries, period):
    """Select articles published within a completed reporting period."""
    start = period["start"]
    end = period["end_exclusive"]
    sections = {kind: [] for kind in ARTICLE_TYPES}
    seen = set()

    for entry in entries:
        title = (entry.get("title") or {}).get("$t", "").strip()
        url = alternate_url(entry)
        published = (entry.get("published") or {}).get("$t", "")

        if not title or not url or not published:
            continue

        timestamp = datetime.fromisoformat(
            published.replace("Z", "+00:00")
        )
        if timestamp.tzinfo is None:
            raise ValueError("Blogger publication timestamp lacks timezone")

        local_date = timestamp.astimezone(PARIS).date().isoformat()
        if not start <= local_date < end:
            continue

        labels = [
            item.get("term", "").strip()
            for item in entry.get("category", [])
        ]
        kind = classify_article(title, labels)

        if kind not in sections:
            continue

        post_id = blogger_post_id(entry)
        identity = post_id or url

        if identity in seen:
            continue
        seen.add(identity)

        sections[kind].append({
            "id": post_id,
            "title": title,
            "url": url,
            "published": timestamp.isoformat(),
            "date": local_date,
            "summary": clean_summary(
                (entry.get("summary") or {}).get("$t", "")
            ),
            "image": newsletter_image_url(
                (entry.get("media$thumbnail") or {}).get("url")
            ),
        })

    for articles in sections.values():
        articles.sort(
            key=lambda item: (item["published"], item["url"]),
            reverse=True,
        )

    return sections
