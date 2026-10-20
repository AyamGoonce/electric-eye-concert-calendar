"""Conservative recovery of reviewed/previously structured published performer bills.

A previous published row is evidence for identity continuity, not permission
for punctuation-based splitting. Source-provided structured roles always win.
"""
from __future__ import annotations

import re
from collections import defaultdict
from html import unescape
from urllib.parse import urlsplit, urlunsplit


def _norm(value):
    return re.sub(r"\s+", " ", unescape(value or "")).strip().casefold()


def _url(value):
    try:
        parts = urlsplit(value or "")
        if parts.scheme not in {"http", "https"} or not parts.netloc or not parts.path:
            return ""
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(),
                           parts.path.rstrip("/"), "", ""))
    except (ValueError, TypeError):
        return ""


def _contains_artist(bill, artist):
    """Require literal word-boundary name occurrence in the current source bill."""
    return bool(re.search(r"(?<!\w)" + re.escape(_norm(artist)) + r"(?!\w)",
                          _norm(bill), flags=re.UNICODE))


def restore_published_billing(events, published_rows):
    """Restore only unambiguous, identical-event bills from published evidence.

    Requires unique event-specific ticket URL, matching venue and calendar date,
    and every historical billed artist still explicitly named in new source title.
    Never add missing artists from old state after a possible lineup change.
    Returns auditable diagnostics; caller logs them.
    """
    report = {"restored": [], "conflicts": [], "ambiguous": []}
    if not published_rows:
        return report
    prior = defaultdict(list)
    current = defaultdict(list)
    for row in published_rows:
        if not isinstance(row, dict):
            continue
        key = (_url(row.get("t")), _norm(row.get("v")), row.get("d"))
        if all(key):
            prior[key].append(row)
    for event in events:
        key = (_url(event.ticket_url), _norm(event.venue), event.date[:10])
        if all(key):
            current[key].append(event)
    for key, records in current.items():
        old = prior.get(key) or []
        if len(old) != 1 or len(records) != 1:
            if old and (len(old) > 1 or len(records) > 1):
                report["ambiguous"].append({
                    "date": key[2], "venue": key[1],
                    "ticket_url": key[0],
                    "previous_rows": len(old), "current_rows": len(records),
                })
            continue
        event, old = records[0], old[0]
        main = old.get("h")
        colleagues = old.get("ch") or []
        support = old.get("o") or []
        if not isinstance(main, str) or not isinstance(colleagues, list) or not colleagues:
            continue
        if not all(isinstance(n, str) and n.strip() for n in [main, *colleagues, *support]):
            continue
        prior_roles = [main, *colleagues]
        # Already structured new source: do not override potentially updated evidence.
        existing = event.performers or []
        if len(existing) >= 2:
            if {_norm(n) for n in existing} != {_norm(n) for n in prior_roles}:
                report["conflicts"].append({"date": key[2], "venue": key[1],
                                           "reason": "new structured performer roster differs", "ticket_url": key[0],
                                           "previous_artists": prior_roles,
                                           "current_title": event.raw_title or event.headliner})
            continue
        raw = event.raw_title or event.headliner
        # Only recover a previous bill if all listed principal artists still
        # appear in the current title. No inference from URL slug or punctuation.
        if not all(_contains_artist(raw, n) for n in prior_roles):
            report["conflicts"].append({"date": key[2], "venue": key[1],
                                       "reason": "current bill omits historical principal artist", "ticket_url": key[0],
                                           "previous_artists": prior_roles,
                                           "current_title": event.raw_title or event.headliner})
            continue
        # A historical opener is retained only if still present in the source
        # title or explicitly named in current opening-act evidence.
        opening = [name for name in support if
                   _contains_artist(raw, name) or
                   _norm(name) in {_norm(n) for n in (event.openers or [])}]
        event.raw_title = event.raw_title or event.headliner
        event.identity_aliases = list(dict.fromkeys([
            *(event.identity_aliases or []), event.raw_title
        ]))
        event.headliner = main
        event.co_headliners = colleagues
        event.performers = prior_roles
        # Retain a verified event/series title only if it still appears in
        # the current source billing. Never invent one from a ticket URL.
        historical_title = old.get("et")
        if (not event.event_title and isinstance(historical_title, str)
                and historical_title.strip()
                and _contains_artist(raw, historical_title)):
            event.event_title = historical_title
        if opening:
            event.openers = list(dict.fromkeys([*(event.openers or []), *opening]))
        report["restored"].append({
            "date": key[2], "venue": event.venue,
            "artists": prior_roles, "source": "published_verified_bill",
            "ticket_url": key[0],
        })
    return report
