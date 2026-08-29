from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlparse

import requests

from concert_calendar.deduplication import TIME_SUFFIX_RE


FEED_URL = "https://www.electriceyerock.com/feeds/posts/summary"
REQUEST_TIMEOUT = 30
MAX_POSTS = 3000
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}
ARTIST_PAGE_URL = "https://ayamgoonce.github.io/electric-eye-concert-calendar/proof/artist.html?artist="
COVERAGE_PAGE_URL = "https://ayamgoonce.github.io/electric-eye-concert-calendar/proof/coverage.html?event="
EXPLICIT_ALIASES = {
    "QOTSA": "Queens of the Stone Age",
    "Sheepdogs": "The Sheepdogs",
    "69 Eyes": "The 69 Eyes",
    "Altons": "The Altons",
}

# Reviewed manual associations for Electric Eye articles whose artist identity
# cannot be established reliably from Blogger labels/title metadata.
# Add only genuine Electric Eye article URLs here.
MANUAL_ARTIST_ARTICLES = {
    "Billy Corgan": {
        "https://www.electriceyerock.com/2024/06/the-smashing-pumpkins-accor-arena-paris.html",
    },
}

# Reviewed official artist websites. Add only the artist's own official site.
OFFICIAL_ARTIST_SITES = {
}

PROSE_AUTOLINK_EXCLUSIONS = {
    # Reviewed ordinary words, geographic names, and contextually ambiguous
    # identities. They remain indexed and usable in structured calendar bills.
    "Accept", "Air", "Answer", "Ash", "Asia", "Beat", "Circle",
    "Conversation", "Down", "Earth", "Europe", "Fish", "Garbage",
    "Ghost", "Kiss", "Live", "Nails", "Ride", "Seal", "Spoon",
    "Sugar", "Trust", "Winter", "Yes",
}
GENERIC_LABELS = {
    "ad", "advertisement", "album", "album review", "announcement",
    "apple music", "concert", "concert review", "electric eye", "festival",
    "friday's playlist", "interview", "live report", "live review", "news",
    "opening", "opening act", "opener", "photo", "photography", "photos",
    "pic", "pics", "pictures", "playlist", "record", "review", "single",
    "tour", "tour dates", "video", "youtube",
    "alternative", "alternative rock", "alt-country", "alt-rock", "americana",
    "banjo", "bass", "black metal", "blues", "blues rock", "classic rock",
    "country", "death metal", "doom", "folk", "funk", "fusion", "garage",
    "goth", "gothic", "guitar", "guitarist", "hard rock", "hardcore",
    "heavy metal", "jazz", "jazz rock", "metal", "metalcore", "new wave",
    "nwobhm", "pop", "pop rock", "prog", "prog rock", "progressive rock",
    "punk", "punk rock", "rap", "rock", "rock n' roll", "soul",
    "southern rock", "stoner", "thrash", "thrash metal",
}


def normalize_artist(value):
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.replace("’", "'").casefold()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def slugify(value):
    return normalize_artist(value).replace(" ", "-")


def classify_article(title, labels):
    folded = {label.casefold() for label in labels}
    if {"concert review", "live review"} & folded or (
        "concert" in folded and "review" in folded
    ):
        return "concert_review"
    if "interview" in folded:
        return "interview"
    if "album review" in folded or re.match(r"^album review\s*:", title, re.I):
        return "album_review"
    if "playlist" in folded or "friday's playlist" in folded:
        return "playlist"
    if {"news", "announcement"} & folded:
        return "news"
    # Older Electric Eye posts predate consistent Blogger section labels. These
    # reviewed house-title conventions are used only after label evidence.
    if re.search(
        r"\s@\s.+\s[-–]\s(?:january|february|march|april|may|june|july|"
        r"august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?,\s+20\d{2}$",
        title,
        re.I,
    ):
        return "concert_review"
    if re.match(r"^(?:interview\s*:|an interview with\b)", title, re.I):
        return "interview"
    if re.match(r"^(?:friday(?:'s|’s) playlist|playlist\s*:)", title, re.I):
        return "playlist"
    if re.search(
        r"\b(?:announce(?:s|d)?|to perform|to release|unveil(?:s|ed)?|"
        r"reveal(?:s|ed)?|share(?:s|d)? (?:a |the )?new|new (?:single|album|video))\b",
        title,
        re.I,
    ):
        return "news"
    return "other"


def alternate_url(entry):
    for link in entry.get("link", []):
        if link.get("rel") == "alternate" and link.get("type") == "text/html":
            value = link.get("href")
            parsed = urlparse(value or "")
            return value if parsed.scheme == "https" and parsed.netloc else None
    return None


def resized_blogger_image(entry):
    value = (entry.get("media$thumbnail") or {}).get("url")
    if not value or urlparse(value).scheme != "https":
        return None
    return re.sub(r"/s\d+(?:-[a-z])?/", "/s320-c/", value)


def fetch_entries(session=None):
    session = session or requests.Session()
    entries = []
    start = 1
    expected_total = None
    while start <= MAX_POSTS:
        response = session.get(
            FEED_URL,
            params={"alt": "json", "max-results": 500, "start-index": start},
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        feed = response.json().get("feed") or {}
        if expected_total is None:
            expected_total = int((feed.get("openSearch$totalResults") or {}).get("$t", 0))
            if expected_total <= 0 or expected_total > MAX_POSTS:
                raise RuntimeError(f"Unexpected Electric Eye post count: {expected_total}")
        page = feed.get("entry") or []
        if not page:
            break
        entries.extend(page)
        start += len(page)
        if len(entries) >= expected_total:
            break
    if len(entries) != expected_total:
        raise RuntimeError(
            f"Incomplete Electric Eye feed: received {len(entries)} of {expected_total}"
        )
    return entries


def _label_in_text(label, text):
    identity = normalize_artist(label)
    haystack = normalize_artist(text)
    return bool(identity and re.search(r"(?:^| )" + re.escape(identity) + r"(?: |$)", haystack))


def seed_artist_labels(entries):
    seeds = Counter()
    for entry in entries:
        title = (entry.get("title") or {}).get("$t", "").strip()
        labels = [item.get("term", "").strip() for item in entry.get("category", [])]
        labels = [label for label in labels if label]
        article_type = classify_article(title, labels)
        candidate = ""
        if article_type == "concert_review" and " @ " in title:
            candidate = title.split(" @ ", 1)[0].strip()
        elif article_type == "album_review":
            candidate = re.sub(r"^album review\s*:\s*", "", title, flags=re.I)
            candidate = re.split(r"\s+[–-]\s+", candidate, maxsplit=1)[0].strip()
        if candidate:
            exact = [
                label for label in labels
                if label.casefold() not in GENERIC_LABELS
                and normalize_artist(label) == normalize_artist(candidate)
            ]
            if exact:
                seeds[exact[0]] += 4
            else:
                for label in labels:
                    if (
                        label.casefold() not in GENERIC_LABELS
                        and len(normalize_artist(label)) >= 3
                        and _label_in_text(label, candidate)
                    ):
                        seeds[label] += 1
        if article_type == "interview":
            for label in labels:
                if (
                    label.casefold() not in GENERIC_LABELS
                    and len(normalize_artist(label)) >= 4
                    and _label_in_text(label, title)
                ):
                    seeds[label] += 1
    return seeds


def build_index(entries, *, generated_at=None):
    seeds = seed_artist_labels(entries)
    canonical_by_identity = {}
    for label, _count in seeds.most_common():
        identity = normalize_artist(label)
        canonical_by_identity.setdefault(identity, label)

    # Reviewed manual artists remain valid canonical identities even when
    # automatic Blogger label/title detection misses them.
    for canonical in MANUAL_ARTIST_ARTICLES:
        identity = normalize_artist(canonical)
        if identity:
            canonical_by_identity.setdefault(identity, canonical)

    for alias, canonical in EXPLICIT_ALIASES.items():
        canonical_identity = normalize_artist(canonical)
        if canonical_identity in canonical_by_identity:
            canonical_by_identity[normalize_artist(alias)] = canonical_by_identity[canonical_identity]

    articles = []
    artist_article_ids = defaultdict(list)
    aliases_by_canonical = defaultdict(set)
    for entry in entries:
        title = (entry.get("title") or {}).get("$t", "").strip()
        url = alternate_url(entry)
        published = (entry.get("published") or {}).get("$t", "")[:10]
        labels = [item.get("term", "").strip() for item in entry.get("category", [])]
        if not title or not url or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", published):
            continue
        matched_names = []
        for label in labels:
            canonical = canonical_by_identity.get(normalize_artist(label))
            if canonical and canonical not in matched_names:
                matched_names.append(canonical)
                if label != canonical:
                    aliases_by_canonical[canonical].add(label)

        # Exact reviewed article associations override missed automatic
        # artist detection without creating identities from calendar data.
        for canonical, manual_urls in MANUAL_ARTIST_ARTICLES.items():
            if url in manual_urls and canonical not in matched_names:
                matched_names.append(canonical)

        article_type = classify_article(title, labels)
        article = {
            "u": url,
            "t": title,
            "d": published,
            "y": article_type,
            "a": [],
        }
        picture = resized_blogger_image(entry)
        if picture and article_type == "concert_review":
            article["im"] = picture
        article_id = len(articles)
        for canonical in matched_names:
            slug = slugify(canonical)
            article["a"].append(slug)
            artist_article_ids[canonical].append(article_id)
        articles.append(article)

    artists = {}
    slug_owners = {}
    collisions = []
    for canonical, article_ids in sorted(artist_article_ids.items(), key=lambda item: normalize_artist(item[0])):
        slug = slugify(canonical)
        if not slug:
            continue
        owner = slug_owners.get(slug)
        if owner and normalize_artist(owner) != normalize_artist(canonical):
            collisions.append({"slug": slug, "artists": [owner, canonical]})
            continue
        slug_owners[slug] = canonical
        aliases = sorted(aliases_by_canonical[canonical], key=normalize_artist)
        for alias, target in EXPLICIT_ALIASES.items():
            if normalize_artist(target) == normalize_artist(canonical):
                aliases.append(alias)
        item = {"n": canonical, "al": sorted(set(aliases), key=normalize_artist), "ar": article_ids}
        official_site = OFFICIAL_ARTIST_SITES.get(canonical)
        if official_site:
            parsed_site = urlparse(official_site)
            if parsed_site.scheme == "https" and parsed_site.netloc:
                item["os"] = official_site
        heroes = [
            articles[index] for index in article_ids
            if articles[index]["y"] == "concert_review" and articles[index].get("im")
        ]
        if heroes:
            hero = max(heroes, key=lambda article: article["d"])
            item["crh"] = {"im": hero["im"], "u": hero["u"], "d": hero["d"]}
        artists[slug] = item

    lookup = {}
    for slug, artist in artists.items():
        for name in [artist["n"], *artist["al"]]:
            lookup[normalize_artist(name)] = slug

    counts = Counter(article["y"] for article in articles)
    return {
        "schema": 1,
        "generatedAt": generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "artists": artists,
        "articles": articles,
        "diagnostics": {
            "articleCounts": dict(sorted(counts.items())),
            "aliases": sum(len(item["al"]) for item in artists.values()),
            "proseAutolinkExclusions": sorted(PROSE_AUTOLINK_EXCLUSIONS),
            "slugCollisions": collisions,
            "unresolvedArticles": sum(not article["a"] for article in articles),
        },
        "lookup": lookup,
    }


def enrich_events(events, index):
    artists = index["artists"]
    lookup = index["lookup"]
    for event in events:
        names = [event.headliner, *(event.co_headliners or []), *(event.openers or [])]
        links = []
        headliner_slug = None
        headliner_count = 1
        co_headliner_count = len(event.co_headliners or [])
        for position, name in enumerate(names):
            comparable = name
            match = TIME_SUFFIX_RE.search(comparable)
            if match:
                comparable = comparable[:match.start()].strip()
            slug = lookup.get(normalize_artist(comparable))
            if not slug or slug in {item["slug"] for item in links}:
                continue
            links.append({
                "name": artists[slug]["n"], "slug": slug,
                "display": name,
                "count": len(artists[slug]["ar"]),
                "role": (
                    "headliner" if position < headliner_count else
                    "co_headliner" if position < headliner_count + co_headliner_count else
                    "opener"
                ),
            })
            if position == 0:
                headliner_slug = slug
        event.electric_eye_links = links or None
        if links:
            article_ids = {
                article_id
                for link in links
                for article_id in artists[link["slug"]]["ar"]
            }
            links[0]["total"] = len(article_ids)
        hero = artists.get(headliner_slug or "", {}).get("crh")
        if hero:
            event.image_url = hero["im"]
            event.image_source = "Electric Eye concert review"


def _javascript_assignment(name, payload):
    value = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    value = value.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return f"window.{name}=Object.freeze({value});\n"


def write_assets(output_dir, index):
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    full_payload = {key: index[key] for key in ("schema", "generatedAt", "artists", "articles", "diagnostics")}
    full_asset = (
        _javascript_assignment("ElectricEyeContentIndex", full_payload)
        + "document.dispatchEvent(new CustomEvent('ee:content-index-ready'));\n"
    )
    digest = hashlib.sha256(full_asset.encode()).hexdigest()
    filename = f"electric-eye-content.{digest[:16]}.js"
    (destination / filename).write_text(full_asset, encoding="utf-8")
    pointer = _javascript_assignment("ElectricEyeContentManifest", {
        "data": filename, "sha256": digest,
        "artists": len(index["artists"]), "articles": len(index["articles"]),
    })
    pointer += "(function(){var s=document.createElement('script'),c=document.currentScript;s.src=new URL(window.ElectricEyeContentManifest.data,c&&c.src||location.href).href;document.head.appendChild(s);}());\n"
    (destination / "electric-eye-content-current.js").write_text(pointer, encoding="utf-8")
    compact = {
        "schema": 1,
        "artistPage": ARTIST_PAGE_URL,
        "proseAutolinkExclusions": sorted({
            slugify(name) for name in PROSE_AUTOLINK_EXCLUSIONS
            if slugify(name) in index["artists"]
        }),
        "terms": {
            name: slug
            for slug, artist in sorted(index["artists"].items())
            for name in [artist["n"], *artist["al"]]
        },
    }
    (destination / "electric-eye-artist-lookup.js").write_text(
        _javascript_assignment("ElectricEyeArtistLookup", compact)
        + "document.dispatchEvent(new CustomEvent('ee:artist-lookup-ready'));\n",
        encoding="utf-8",
    )
    return {
        "filename": filename, "sha256": digest,
        "artist_count": len(index["artists"]), "article_count": len(index["articles"]),
        "lookup_count": len(index["lookup"]),
    }
