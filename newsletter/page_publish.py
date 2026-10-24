"""Safely publish permanent newsletter pages to the destination repository."""

import base64
import os

import requests

from newsletter.publishing import DESTINATION_REPOSITORY

API_BASE = f"https://api.github.com/repos/{DESTINATION_REPOSITORY}"
TIMEOUT = 30

ALLOWED_PATHS = frozenset({
    "weekly/index.html",
    "monthly/index.html",
    "archives/index.html",
    "archives/index.json",
    "templates/weekly.html",
    "templates/monthly.html",
})


def publish_page(path, content, *, token=None, session=None):
    """Create or update an approved page, avoiding unnecessary commits."""
    if path not in ALLOWED_PATHS:
        raise ValueError("Unapproved newsletter page path")

    if not isinstance(content, str) or not content.strip():
        raise ValueError("Cannot publish empty page content")

    credential = token or os.environ.get("NEWSLETTER_PUBLISH_TOKEN")
    if not credential:
        raise RuntimeError("NEWSLETTER_PUBLISH_TOKEN is not configured")

    session = session or requests.Session()
    headers = {
        "Authorization": f"Bearer {credential}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    url = f"{API_BASE}/contents/{path}"

    for attempt in range(3):
        response = session.get(
            url, headers=headers, timeout=TIMEOUT
        )

        if response.status_code == 404:
            sha = None
        else:
            response.raise_for_status()
            data = response.json()
            sha = data["sha"]
            existing = base64.b64decode(
                data["content"]
            ).decode("utf-8")

            if existing == content:
                return {"action": "unchanged", "path": path}

        payload = {
            "message": f"Update Electric Eye newsletter page {path}",
            "content": base64.b64encode(
                content.encode("utf-8")
            ).decode("ascii"),
            "branch": "main",
        }

        if sha:
            payload["sha"] = sha

        response = session.put(
            url, json=payload, headers=headers, timeout=TIMEOUT
        )

        if response.status_code in (200, 201):
            return {
                "action": "updated" if sha else "created",
                "path": path,
                "commit": response.json()["commit"]["sha"],
            }

        if response.status_code not in (409, 422):
            response.raise_for_status()

    raise RuntimeError(
        f"Newsletter page publication conflicts exhausted: {path}"
    )
