from __future__ import annotations

from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
import unicodedata
from urllib.parse import urlparse

import requests

from concert_calendar.deduplication import TIME_SUFFIX_RE


FEED_URL = "https://www.electriceyerock.com/feeds/posts/summary"
CONCERT_REVIEWS_URL = "https://www.electriceyerock.com/p/concert-photos-reviews.html"
CONCERT_REVIEW_ARRAY_NAMES = ("EE_NEW_REVIEWS", "EE_ARCHIVE_REVIEWS")
REQUEST_TIMEOUT = 30
MAX_POSTS = 3000
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}
ARTIST_PAGE_URL = "https://archive.electriceyerock.com/artist/"
COVERAGE_PAGE_URL = "https://archive.electriceyerock.com/concert/"
IDENTITY_OVERRIDES_PATH = Path(__file__).with_name("artist_identity_overrides.json")


def load_artist_identity_overrides(path=IDENTITY_OVERRIDES_PATH):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schemaVersion") != 1:
        raise ValueError("Unsupported artist identity override schema")
    return payload


_IDENTITY_OVERRIDES = load_artist_identity_overrides()
EXPLICIT_ALIASES = dict(_IDENTITY_OVERRIDES.get("aliases") or {})

# Reviewed manual associations for Electric Eye articles whose artist identity
# cannot be established reliably from Blogger labels/title metadata.
# Add only genuine Electric Eye article URLs here.
MANUAL_ARTIST_ARTICLES = {
    artist: set(urls)
    for artist, urls in (_IDENTITY_OVERRIDES.get("manualArticleAssociations") or {}).items()
}

# Reviewed official artist websites. Add only the artist's own official site.
OFFICIAL_ARTIST_SITES = dict(_IDENTITY_OVERRIDES.get("officialSites") or {})

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
    "obituary", "opening", "opening act", "opener", "photo", "photography", "photos",
    "pic", "pics", "pictures", "playlist", "record", "review", "single",
    "tour", "tour dates", "video", "youtube",
    # Geographic taxonomy labels are structural unless independent title
    # structure establishes a legitimate artist collision.
    "paris",
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


def normalize_content_identity(value):
    """Exact Unicode spelling for article association; never fold accents."""
    value = unicodedata.normalize("NFC", value or "").casefold().replace("’", "'")
    return " ".join(value.split())


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


def blogger_post_id(entry):
    value = str((entry.get("id") or {}).get("$t") or "")
    match = re.search(r"post-(\d+)$", value)
    return match.group(1) if match else None



def _extract_javascript_array(source, name):
    match = re.search(r"\bvar\s+" + re.escape(name) + r"\s*=", source)
    if not match:
        return ""

    start = source.find("[", match.end())
    if start < 0:
        return ""

    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False

    index = start
    while index < len(source):
        char = source[index]
        next_char = source[index + 1] if index + 1 < len(source) else ""

        if line_comment:
            if char == "\n":
                line_comment = False
            index += 1
            continue

        if block_comment:
            if char == "*" and next_char == "/":
                block_comment = False
                index += 2
                continue
            index += 1
            continue

        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue

        if char == "/" and next_char == "/":
            line_comment = True
            index += 2
            continue

        if char == "/" and next_char == "*":
            block_comment = True
            index += 2
            continue

        if char in {'"', "'"}:
            quote = char
            index += 1
            continue

        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]

        index += 1

    return ""


def _extract_javascript_objects(array_source):
    objects = []
    start = None
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False

    index = 0
    while index < len(array_source):
        char = array_source[index]
        next_char = array_source[index + 1] if index + 1 < len(array_source) else ""

        if line_comment:
            if char == "\n":
                line_comment = False
            index += 1
            continue

        if block_comment:
            if char == "*" and next_char == "/":
                block_comment = False
                index += 2
                continue
            index += 1
            continue

        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue

        if char == "/" and next_char == "/":
            line_comment = True
            index += 2
            continue

        if char == "/" and next_char == "*":
            block_comment = True
            index += 2
            continue

        if char in {'"', "'"}:
            quote = char
            index += 1
            continue

        if char == "{":
            if depth == 0:
                start = index
            depth += 1
        elif char == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                objects.append(array_source[start:index + 1])
                start = None

        index += 1

    return objects


def _javascript_string_field(source, field):
    key = r'["\']?' + re.escape(field) + r'["\']?'
    patterns = (
        key + r'\s*:\s*"((?:\\.|[^"\\])*)"',
        key + r"\s*:\s*'((?:\\.|[^'\\])*)'",
    )
    for pattern in patterns:
        match = re.search(pattern, source, flags=re.DOTALL)
        if not match:
            continue

        value = match.group(1)
        value = re.sub(
            r"\\u([0-9a-fA-F]{4})",
            lambda item: chr(int(item.group(1), 16)),
            value,
        )
        return (
            value
            .replace(r"\/", "/")
            .replace(r"\"", '"')
            .replace(r"\'", "'")
            .replace(r"\n", "\n")
            .replace(r"\r", "\r")
            .replace(r"\t", "\t")
            .replace("\\\\", "\\")
            .strip()
        )

    return ""


def _canonical_electric_eye_article_url(value):
    parsed = urlparse(str(value or "").strip())
    host = parsed.netloc.lower().split(":", 1)[0]

    if parsed.scheme not in {"http", "https"}:
        return None
    if host not in {"electriceyerock.com", "www.electriceyerock.com"}:
        return None
    if not parsed.path:
        return None

    path = parsed.path.rstrip("/") or "/"
    return "https://www.electriceyerock.com" + path


def parse_concert_review_associations(source):
    associations = defaultdict(list)

    for array_name in CONCERT_REVIEW_ARRAY_NAMES:
        array_source = _extract_javascript_array(source, array_name)
        if not array_source:
            continue

        for object_source in _extract_javascript_objects(array_source):
            artist = _javascript_string_field(object_source, "artist")
            url = _canonical_electric_eye_article_url(
                _javascript_string_field(object_source, "url")
            )

            # Identity evidence must come from the explicit archive artist field.
            # Do not reproduce the theme's title-prefix fallback here.
            if not artist or not url:
                continue

            if artist not in associations[url]:
                associations[url].append(artist)

    return dict(associations)


def fetch_concert_review_associations(session=None):
    session = session or requests.Session()
    response = session.get(
        CONCERT_REVIEWS_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    associations = parse_concert_review_associations(response.text)
    if not associations:
        raise RuntimeError("Concert Reviews archive contained no usable artist mappings")

    return associations


def fetch_entries(session=None):
    session = session or requests.Session()
    entries = []
    start = 1
    expected_total = None
    while start <= MAX_POSTS:
        for attempt in range(3):
            try:
                response = session.get(
                    FEED_URL,
                    params={"alt": "json", "max-results": 500, "start-index": start},
                    headers=HEADERS,
                    timeout=REQUEST_TIMEOUT,
                )
                break
            except (requests.Timeout, requests.ConnectionError):
                if attempt == 2:
                    raise
                time.sleep(2)
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


def _title_artist_candidate(title, article_type):
    if article_type == "concert_review" and " @ " in title:
        return title.split(" @ ", 1)[0].strip()
    if article_type == "album_review":
        candidate = re.sub(r"^album review\s*(?::|[–-])\s*", "", title, flags=re.I)
        return re.split(r"\s+[–-]\s+", candidate, maxsplit=1)[0].strip()
    if article_type == "interview":
        interview = re.match(
            r"^(?:a\s+)?(?:conversation|interview)\s+with\s+(.+?)(?:\s+[–-]\s+|$)",
            title,
            re.I,
        )
        if interview:
            return interview.group(1).strip()
    action = re.match(
        r"^(.+?)\s+(?:announce|announces|release|releases|share|shares|"
        r"unveil|unveils|return|returns|back|perform|performs)\b",
        title,
        re.I,
    )
    return action.group(1).strip() if action else ""


def _artist_label_allowed(label, title, article_type=None):
    """Require independent title evidence before a structural label is an artist."""

    if label.casefold() not in GENERIC_LABELS:
        return True
    candidate = _title_artist_candidate(
        title, article_type or classify_article(title, [label])
    )
    return normalize_artist(label) == normalize_artist(candidate)


def _label_is_article_primary(label, title, article_type):
    """Do not promote billmates or associated people over a titled subject."""

    if not _artist_label_allowed(label, title, article_type):
        return False
    candidate = _title_artist_candidate(title, article_type)
    return not candidate or _label_in_text(label, candidate)


def seed_artist_labels(entries):
    seeds = Counter()
    for entry in entries:
        title = (entry.get("title") or {}).get("$t", "").strip()
        labels = [item.get("term", "").strip() for item in entry.get("category", [])]
        labels = [label for label in labels if label]
        article_type = classify_article(title, labels)
        candidate = _title_artist_candidate(title, article_type)
        if candidate:
            exact = [
                label for label in labels
                if _artist_label_allowed(label, title, article_type)
                and normalize_artist(label) == normalize_artist(candidate)
            ]
            if exact:
                seeds[exact[0]] += 4
            else:
                for label in labels:
                    if (
                        _artist_label_allowed(label, title, article_type)
                        and len(normalize_artist(label)) >= 3
                        and _label_in_text(label, candidate)
                    ):
                        seeds[label] += 1
        if article_type == "interview":
            for label in labels:
                if (
                    _artist_label_allowed(label, title, article_type)
                    and len(normalize_artist(label)) >= 4
                    and _label_in_text(label, title)
                ):
                    seeds[label] += 1
    return seeds



def _concert_review_identity_text(value):
    value = re.sub(
        r"\s*\(\s*DJ\s+Set\s*\)\s*$",
        "",
        str(value or ""),
        flags=re.IGNORECASE,
    ).strip()
    identity = normalize_artist(value)
    words = identity.split()
    if words and words[0] == "the":
        words = words[1:]
    return " ".join(words)


def _concert_review_matches_existing(value, canonical):
    subject = _concert_review_identity_text(value)
    known = _concert_review_identity_text(canonical)

    if not subject or not known:
        return False

    # The/Pineapple Thief type variation.
    if subject == known:
        return True

    # Duff Mc Kagan / Duff McKagan and Earth Motion / EarthMotion.
    if subject.replace(" ", "") == known.replace(" ", ""):
        return True

    # Touring/project descriptions which contain an already-established
    # canonical artist as complete words:
    # Brant Bjork Trio -> Brant Bjork
    # The Warren Haynes Band -> Warren Haynes
    # Lex Koritni -> Koritni
    known_words = known.split()
    if len(known) >= 5:
        pattern = r"(?:^|\s)" + re.escape(known) + r"(?:$|\s)"
        if re.search(pattern, subject):
            return True

    return False


def _concert_review_existing_canonical(value, canonical_by_identity):
    exact = canonical_by_identity.get(normalize_artist(value))
    if exact:
        return exact

    canonicals = sorted(
        set(canonical_by_identity.values()),
        key=lambda item: len(_concert_review_identity_text(item)),
        reverse=True,
    )

    for canonical in canonicals:
        if _concert_review_matches_existing(value, canonical):
            return canonical

    return None


def _concert_review_artist_can_seed(value):
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    identity = normalize_artist(value)

    if not identity or identity in GENERIC_LABELS:
        return False

    # Old archive rows occasionally stored part of the venue/title in artist.
    # They remain useful when they resolve to an already-known artist, but they
    # must never manufacture a new identity.
    if "@" in value:
        return False
    if re.search(r"\s+-\s+[^,]+,\s*[^,]+$", value):
        return False

    # Composite/event billing is evidence about the article, not a new
    # canonical Apple artist identity.
    if re.search(r"\b(?:feat\.?|featuring)\b", value, flags=re.IGNORECASE):
        return False
    if re.search(r"\s+(?:\+|&|and|et)\s+", value, flags=re.IGNORECASE):
        return False
    if re.search(r"\b(?:hellfest|festival)\b", value, flags=re.IGNORECASE):
        return False

    return True


def build_index(entries, *, generated_at=None, concert_review_associations=None):
    overrides = load_artist_identity_overrides()
    reviewed_artists = overrides.get("artists") or {}
    concert_review_associations = concert_review_associations or {}
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
    # The Concert Reviews page is a structured editorial source. Its
    # explicit artist field may seed a simple canonical identity when Blogger
    # metadata missed it. Composite/event billing cannot create a new identity.
    for review_artists in concert_review_associations.values():
        for canonical in review_artists:
            existing = _concert_review_existing_canonical(
                canonical,
                canonical_by_identity,
            )
            if existing:
                continue

            identity = normalize_artist(canonical)
            if identity and _concert_review_artist_can_seed(canonical):
                canonical_by_identity.setdefault(identity, canonical)

    for override in (overrides.get("articleOverrides") or {}).values():
        for canonical in override.get("primaryArtists", []):
            identity = normalize_artist(canonical)
            if identity:
                canonical_by_identity.setdefault(identity, canonical)

    for alias, canonical in EXPLICIT_ALIASES.items():
        canonical_identity = normalize_artist(canonical)
        if canonical_identity in canonical_by_identity:
            canonical_by_identity[normalize_artist(alias)] = canonical_by_identity[canonical_identity]

    concert_review_canonicals = {}
    for review_url, review_artists in concert_review_associations.items():
        canonical_url = _canonical_electric_eye_article_url(review_url)
        if not canonical_url:
            continue
        matched = []
        for review_artist in review_artists:
            if not _concert_review_artist_can_seed(review_artist):
                continue

            canonical = _concert_review_existing_canonical(
                review_artist,
                canonical_by_identity,
            )
            if canonical and canonical not in matched:
                matched.append(canonical)
        if matched:
            concert_review_canonicals[canonical_url] = matched

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
        post_id = blogger_post_id(entry)
        article_type = classify_article(title, labels)
        for label in labels:
            if not _label_is_article_primary(label, title, article_type):
                continue
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
        canonical_article_url = _canonical_electric_eye_article_url(url)
        for canonical in concert_review_canonicals.get(canonical_article_url, []):
            if canonical not in matched_names:
                matched_names.append(canonical)

        reviewed_article = (overrides.get("articleOverrides") or {}).get(post_id or "") or {}
        for canonical in reviewed_article.get("primaryArtists", []):
            if canonical not in matched_names:
                matched_names.append(canonical)

        article = {
            "u": url,
            "t": title,
            "d": published,
            "y": article_type,
            "a": [],
        }
        if post_id:
            article["pi"] = post_id
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
        reviewed = reviewed_artists.get(canonical) or {}
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
        item["identity"] = {
            "schemaVersion": 1,
            "canonicalName": canonical,
            "slug": slug,
            "aliases": item["al"],
            "alternateSpellings": reviewed.get("alternateSpellings", []),
            "members": reviewed.get("members", []),
            "formerMembers": reviewed.get("formerMembers", []),
            "associatedActs": reviewed.get("associatedActs", []),
            "sideProjects": reviewed.get("sideProjects", []),
            "collaborators": reviewed.get("collaborators", []),
            "producers": reviewed.get("producers", []),
            "songwriters": reviewed.get("songwriters", []),
            "genres": reviewed.get("genres", []),
            "keywords": reviewed.get("keywords", []),
            "musicBrainzId": reviewed.get("musicBrainzId"),
            "appleArtistId": reviewed.get("appleArtistId"),
            "appleIdentityConfidence": reviewed.get("appleIdentityConfidence"),
            "ambiguityClass": reviewed.get("ambiguityClass", "distinctive"),
            "identityEvidence": reviewed.get("identityEvidence", []),
            "articleCount": len(article_ids),
            "articleIds": [articles[index].get("pi") for index in article_ids if articles[index].get("pi")],
            "reviewedArticleIds": [
                articles[index].get("pi")
                for index in article_ids
                if articles[index].get("pi") and (
                    articles[index]["u"] in MANUAL_ARTIST_ARTICLES.get(canonical, set())
                    or canonical in (
                        (overrides.get("articleOverrides") or {})
                        .get(articles[index].get("pi"), {})
                        .get("primaryArtists", [])
                    )
                )
            ],
            "concertReviewArchiveArticleIds": [
                articles[index].get("pi")
                for index in article_ids
                if articles[index].get("pi")
                and canonical in concert_review_canonicals.get(
                    _canonical_electric_eye_article_url(articles[index]["u"]),
                    [],
                )
            ],
            "articleUrls": [articles[index]["u"] for index in article_ids],
            "lastIdentityUpdatedAt": reviewed.get("lastIdentityUpdatedAt"),
            "lastAppleCatalogueUpdatedAt": reviewed.get("lastAppleCatalogueUpdatedAt"),
        }
        artists[slug] = item

    lookup = {}
    for slug, artist in artists.items():
        for name in [artist["n"], *artist["al"]]:
            lookup[normalize_artist(name)] = slug

    counts = Counter(article["y"] for article in articles)
    return {
        "schema": 2,
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
    # The legacy search lookup folds accents. It must not establish article
    # ownership, even when only one of two namesakes has indexed content.
    lookup = {normalize_content_identity(artist["n"]): slug
              for slug, artist in artists.items()}
    for alias, canonical in EXPLICIT_ALIASES.items():
        slug = lookup.get(normalize_content_identity(canonical))
        if slug:
            lookup.setdefault(normalize_content_identity(alias), slug)
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
            slug = lookup.get(normalize_content_identity(comparable))
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


def write_artist_exports(output_dir, index):
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    records = [
        index["artists"][slug]["identity"]
        for slug in sorted(index["artists"], key=lambda value: normalize_artist(index["artists"][value]["n"]))
    ]
    registry = {
        "schemaVersion": 1,
        "contentIndexSchema": index["schema"],
        "generatedAt": index["generatedAt"],
        "structuralLabels": sorted(GENERIC_LABELS),
        "artists": records,
        "articleOverrides": load_artist_identity_overrides().get("articleOverrides", {}),
    }
    (destination / "artist-index.json").write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    columns = [
        "canonicalName", "slug", "aliases", "alternateSpellings", "members",
        "formerMembers", "associatedActs", "sideProjects", "collaborators",
        "producers", "songwriters", "genres", "keywords", "musicBrainzId",
        "appleArtistId", "appleIdentityConfidence", "ambiguityClass",
        "identityEvidence", "articleCount", "lastIdentityUpdatedAt",
        "lastAppleCatalogueUpdatedAt", "reviewedArticleIds",
        "concertReviewArchiveArticleIds",
    ]
    with (destination / "artist-index.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for record in records:
            writer.writerow({
                key: " | ".join(map(str, record.get(key) or []))
                if isinstance(record.get(key), list) else record.get(key)
                for key in columns
            })
    with (destination / "artist-article-associations.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("slug", "canonicalName", "postId", "articleUrl"))
        writer.writeheader()
        for slug, artist in index["artists"].items():
            for article_id in artist["ar"]:
                article = index["articles"][article_id]
                writer.writerow({
                    "slug": slug, "canonicalName": artist["n"],
                    "postId": article.get("pi", ""),
                    "articleUrl": article["u"],
                })
    return {"artists": len(records), "associations": sum(item["articleCount"] for item in records)}


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
    export_result = write_artist_exports(destination, index)
    return {
        "filename": filename, "sha256": digest,
        "artist_count": len(index["artists"]), "article_count": len(index["articles"]),
        "lookup_count": len(index["lookup"]),
        "artist_export_count": export_result["artists"],
    }
