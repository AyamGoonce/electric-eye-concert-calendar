"""Conservative event prose extraction, independent of artist aliases."""

import re
from html import unescape


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
