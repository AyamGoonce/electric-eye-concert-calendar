from __future__ import annotations

from collections import defaultdict
import re
from urllib.parse import urlparse


MIN_IMAGE_EDGE = 240
GENERIC_IMAGE_MARKERS = (
    "tracking", "pixel", "spacer", "placeholder", "default-image",
    "default_image", "favicon", "apple-touch-icon", "site-logo",
    "logo.", "/logo/", "logo-", "-logo", "header-banner",
)


def official_image_url(value, *, width=None, height=None):
    """Return a conservative official event image URL or None."""

    if not isinstance(value, str):
        return None
    value = value.strip()
    parsed = urlparse(value)
    lowered = (parsed.path + "?" + parsed.query).casefold()
    if parsed.scheme != "https" or not parsed.netloc:
        return None
    if parsed.path.casefold().endswith(".svg"):
        return None
    if any(marker in lowered for marker in GENERIC_IMAGE_MARKERS):
        return None
    try:
        if width is not None and int(width) < MIN_IMAGE_EDGE:
            return None
        if height is not None and int(height) < MIN_IMAGE_EDGE:
            return None
    except (TypeError, ValueError):
        return None
    return value


def structured_image_url(value):
    """Read a Schema.org/API image represented as a URL, object, or list."""

    if isinstance(value, list):
        for item in value:
            if result := structured_image_url(item):
                return result
        return None
    if isinstance(value, dict):
        candidate = value.get("contentUrl") or value.get("url")
        dimensions = value.get("width"), value.get("height")
        return official_image_url(candidate, width=dimensions[0], height=dimensions[1])
    return official_image_url(value)


def metadata_image_url(soup):
    """Read an event page's OpenGraph or Twitter image metadata."""

    for selector in (
        'meta[property="og:image:secure_url"]',
        'meta[property="og:image"]',
        'meta[name="twitter:image"]',
    ):
        element = soup.select_one(selector)
        if element and (candidate := official_image_url(element.get("content"))):
            return candidate
    return None


def repeated_generic_image_urls(events, *, distinct_headliner_limit=5):
    """Return images reused across many unrelated event identities."""
    identities = defaultdict(set)
    for event in events:
        if event.image_url:
            identity = re.sub(r"\W+", " ", event.headliner.casefold()).strip()
            identities[event.image_url].add(identity)
    return {
        url for url, headliners in identities.items()
        if len(headliners) >= distinct_headliner_limit
    }


def discard_repeated_generic_images(events, *, distinct_headliner_limit=5):
    """Drop one image reused across many unrelated event identities."""

    rejected = repeated_generic_image_urls(
        events, distinct_headliner_limit=distinct_headliner_limit
    )
    for event in events:
        if event.image_url in rejected:
            event.image_url = None
            event.image_source = None
    return events
