"""Safe publication planning for Electric Eye newsletter editions."""

import re

DESTINATION_REPOSITORY = "AyamGoonce/electric-eye-newsletters"

MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
WEEK = re.compile(r"^\d{4}-W(0[1-9]|[1-4]\d|5[0-3])$")


def edition_path(snapshot):
    """Return the destination path for a validated newsletter edition."""
    frequency = snapshot.get("frequency")
    identifier = snapshot.get("identifier", "")

    if frequency == "monthly" and MONTH.fullmatch(identifier):
        return f"monthly/{identifier}.html"

    if frequency == "weekly" and WEEK.fullmatch(identifier):
        return f"weekly/{identifier}.html"

    raise ValueError("Invalid newsletter edition identifier")


def publication_plan(snapshot, existing_paths):
    """Plan a new publication without changing any remote files."""
    destination = edition_path(snapshot)

    if destination in existing_paths:
        return {
            "action": "skip",
            "reason": "Edition already published",
            "path": destination,
        }

    return {
        "action": "create",
        "path": destination,
        "repository": DESTINATION_REPOSITORY,
    }
