"""Conservative event prose extraction, independent of artist aliases."""

import re
import unicodedata
from collections import defaultdict
from html import unescape


def title_identity(value):
    """Exact Unicode spelling, with typographic apostrophe equivalence only."""
    return " ".join(unicodedata.normalize("NFC", unescape(value or ""))
                    .replace("’", "'").casefold().split())


def split_series_prefix(value):
    match = re.fullmatch(r"(.+?)\s*:\s+(.+)", value)
    return match.groups() if match else None


def separate_performance_marker(event):
    """Do not erase explicit set/session evidence carried in the raw title."""
    return bool(re.search(
        r"\b(?:(?:1er|2e|first|second)\s+(?:set|show)|matin[ée]e|evening|early show|late show)\b",
        f"{event.headliner} {event.event_title or ''}", re.I))


def evidenced_series_prefixes(events):
    """Require recurring programme grammar AND distinct bills from one source."""
    bills = defaultdict(set)
    for event in events:
        parts = split_series_prefix(event.event_title or event.headliner)
        if not parts or not re.search(r"\bfestival\b|\bnights?$", parts[0], re.I):
            continue
        for source in event.source_names or []:
            bills[(source, title_identity(parts[0]))].add(title_identity(parts[1]))
    return {key for key, values in bills.items() if len(values) >= 2}


def contextual_title_parts(event, series_prefixes):
    """Separate only source-evidenced series and corroborated artist branding."""
    parts = split_series_prefix(event.headliner)
    if parts and (title_identity(parts[0]) == "café-concert" or any(
            (source, title_identity(parts[0])) in series_prefixes
            for source in event.source_names or [])):
        return parts[1], parts[0]
    # A prior merged plain source identity is evidence; punctuation alone is not.
    if len(set(event.source_names or [])) >= 2:
        branding = re.fullmatch(r"(.+?)(?:\s+[-–:]\s+.+|\s+[“«][^”»]+[”»])", event.headliner)
        if branding and any(title_identity(alias) == title_identity(branding[1])
                            for alias in event.identity_aliases or []):
            return branding[1], None
    return event.headliner, None


CONCERT_WRAPPER = re.compile(
    r"\s+(?:en concert\s+\(c[oô]t[ée] Records\)|"
    r":\s*release party en full band)\s*$", re.I
)
# Both a recognized musical descriptor AND an explicit origin are required.
DESCRIPTOR = re.compile(
    r"\s+\((?:(?:psychedelic|psychedelique|psychédélique|indie|alternative|"
    r"progressive|garage|hard|folk|punk)\s+)?(?:rock|pop|jazz|metal|folk|punk)"
    r"\s+[-–]\s+(?:Norvège|Norway|France|Belgique|Belgium|UK|USA|"
    r"Allemagne|Germany|Suède|Sweden|Italie|Italy)\)", re.I
)


def artist_title_parts(value):
    """Return artist and neutral featured entities; never split +, &, or projects.

    Quoted programme names are extracted only in the explicit featured-artist
    construction. Arbitrary quoted/parenthetical artist names remain intact.
    """
    title = unescape(value or "").strip()
    title = CONCERT_WRAPPER.sub("", title).strip()
    title = DESCRIPTOR.sub("", title).strip()
    featured = re.fullmatch(r"(.+?)\s+(?:ft\.|feat\.|featuring)\s+(.+)", title, re.I)
    if (featured and not any(c in featured[2] for c in "()&+•|⎥:«»\"–")
            and not re.search(r"\b\d{1,2}\s*h|\b(?:1er|2e)\s+set\b", title, re.I)):
        primary = re.sub(r"\s+«[^«»]+»\s*$", "", featured[1]).strip()
        return primary, [featured[2].strip()]
    return title, []
