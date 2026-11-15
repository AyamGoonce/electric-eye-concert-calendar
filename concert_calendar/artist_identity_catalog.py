"""Evidence-backed, per-publication artist identity catalogue.

This module discovers candidate identities from source-provided *separate*
performer fields. It does not split event titles, infer headliners or invent
aliases. The existing reviewed/content-index identities take precedence.
"""
from __future__ import annotations

from collections import defaultdict
from html import unescape
import re
import unicodedata


NON_IDENTITY = re.compile(
    r"^(?:guest|guests?|special guests?|support|opening act|"
    r"premi[eè]re partie|invitées?|invit[eé]s?|tba|tbc|"
    r"various artists|lineup|artistes?|unknown)$",
    re.I,
)
CONTEXT = re.compile(
    r"\b(?:release party|album release|billetterie|en concert|"
    r"premi[eè]re partie|festival pass|afterparty|blind[\s-]?test|"
    r"quiz musical|concert gratuit)\b",
    re.I,
)
SEPARATORS = re.compile(r"\s+(?:\+|/|•|&|with|avec|feat\.?|featuring)\s+", re.I)


def identity_key(value):
    value = unicodedata.normalize("NFKD", unescape(str(value or "")))
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def artist_candidate(name):
    """Reject obvious billing strings and placeholders, not arbitrary names."""
    value = " ".join(str(name or "").split())
    key = identity_key(value)
    if not key or len(key) < 2 or len(value) > 100:
        return False
    if NON_IDENTITY.fullmatch(value) or CONTEXT.search(value):
        return False
    if SEPARATORS.search(value):
        return False
    if re.search(r"\b(?:\d{1,2}h\d{0,2}|20\d{2} tour)\b", value, re.I):
        return False
    return True


def collect_structured_artist_evidence(events, *, existing=None):
    """Return new exact identities and an auditable evidence inventory.

    Only a source's individually supplied performer list is evidence. A
    repeated display name is not an alias. Short or otherwise ambiguous
    identities require corroboration by two distinct source names. A flat
    headline, a URL slug and a previous calendar billing are not proof.
    """
    existing = dict(existing or {})
    evidence = defaultdict(list)
    rejected = defaultdict(int)
    for event in events:
        raw = event.raw_title or event.headliner
        performers = list(dict.fromkeys(
            " ".join(str(name or "").split())
            for name in (event.performers or [])
        ))
        if len(performers) < 2:
            continue
        if len({identity_key(name) for name in performers}) != len(performers):
            rejected["duplicate_performer_fields"] += 1
            continue
        if any(not artist_candidate(name) for name in performers):
            rejected["non_identity_in_roster"] += 1
            continue
        # Some provider APIs repeat the entire card title in an "artists"
        # array. Such a field cannot independently substantiate a bill.
        if any(
            identity_key(name) == identity_key(raw)
            and SEPARATORS.search(name)
            for name in performers
        ):
            rejected["opaque_title_in_roster"] += 1
            continue
        sources = sorted(set(event.source_names or []))
        if not sources:
            rejected["missing_source_provenance"] += 1
            continue
        for name in performers:
            key = identity_key(name)
            evidence[key].append({
                "name": name,
                "sources": sources,
                "date": event.date[:10],
                "venue": event.venue,
                "ticket_url": event.ticket_url,
                "evidence_type": "separate_source_performer_field",
            })

    additions = {}
    verified = []
    unresolved = []
    for key in sorted(evidence):
        rows = evidence[key]
        source_set = sorted({source for row in rows for source in row["sources"]})
        display_names = sorted({row["name"] for row in rows}, key=lambda n: (n.casefold(), n))
        if key not in existing and len({
            unicodedata.normalize("NFC", value).casefold()
            for value in display_names
        }) > 1:
            unresolved.append({
                "identity": key, "display_names": display_names,
                "reason": "variant_spelling_requires_review",
                "sources": source_set, "events": len(rows),
            })
            continue
        if key in existing:
            canonical = existing[key]
            status = "already_known"
        elif len(key) < 4 and len(source_set) < 2:
            unresolved.append({
                "identity": key, "display_names": display_names,
                "reason": "short_name_requires_independent_source",
                "sources": source_set,
                "events": len(rows),
            })
            continue
        else:
            # Inconsistent spellings are not silently declared equivalent
            # unless only capitalization or Unicode accents differ.
            canonical = display_names[0]
            additions[key] = canonical
            status = "new_verified"
        verified.append({
            "identity": key, "canonical": canonical, "status": status,
            "sources": source_set,
            "evidence": rows[:10],
            "events": len(rows),
            "display_names": display_names,
        })
    return additions, {
        "new_verified": len(additions),
        "already_known": sum(x["status"] == "already_known" for x in verified),
        "unresolved": len(unresolved),
        "rejected": dict(sorted(rejected.items())),
        "verified_records": verified,
        "unresolved_records": unresolved,
        "policy": "exact identities only; no inferred aliases or artist roles",
    }
