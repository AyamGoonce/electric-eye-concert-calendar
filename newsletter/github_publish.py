"""Create-only publishing to the independent Electric Eye newsletter repository."""

import base64
import os

import requests

from newsletter.publishing import DESTINATION_REPOSITORY, edition_path

API_BASE = f"https://api.github.com/repos/{DESTINATION_REPOSITORY}"
TIMEOUT = 30


def publish_edition(snapshot, html, *, token=None, session=None):
    """Create a newsletter edition without overwriting an existing file."""
    path = edition_path(snapshot)

    if not isinstance(html, str) or not html.strip():
        raise ValueError("Cannot publish empty newsletter HTML")

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

    response = session.get(url, headers=headers, timeout=TIMEOUT)

    if response.status_code == 200:
        return {
            "action": "skip",
            "path": path,
            "reason": "Edition already published",
        }

    if response.status_code != 404:
        response.raise_for_status()
        raise RuntimeError("Could not determine publication status")

    payload = {
        "message": f"Publish Electric Eye newsletter {snapshot['identifier']}",
        "content": base64.b64encode(html.encode("utf-8")).decode("ascii"),
        "branch": "main",
    }

    response = session.put(
        url,
        json=payload,
        headers=headers,
        timeout=TIMEOUT,
    )

    # GitHub's create-file API returns HTTP 201.
    # HTTP 409/422 can occur if another run created the file first.
    # We fail safely rather than retry with an overwrite.
    if response.status_code != 201:
        response.raise_for_status()
        raise RuntimeError(
            f"Unexpected GitHub publication response: {response.status_code}"
        )

    result = response.json()

    return {
        "action": "created",
        "path": path,
        "commit": result["commit"]["sha"],
    }


def update_latest_manifest(snapshot, *, token=None, session=None):
    """Update latest.json after successful edition publication.

    Uses the GitHub Contents API with the current SHA and retries
    conflicting writes without discarding other edition references.
    """
    import json

    from newsletter.manifest import build_manifest, merge_manifest

    credential = token or os.environ.get("NEWSLETTER_PUBLISH_TOKEN")
    if not credential:
        raise RuntimeError("NEWSLETTER_PUBLISH_TOKEN is not configured")

    session = session or requests.Session()

    headers = {
        "Authorization": f"Bearer {credential}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Never reference an edition that has not been published.
    edition_url = (
        f"{API_BASE}/contents/{edition_path(snapshot)}"
    )
    response = session.get(
        edition_url, headers=headers, timeout=TIMEOUT
    )
    if response.status_code != 200:
        raise RuntimeError(
            "Newsletter edition must exist before updating latest.json"
        )

    url = f"{API_BASE}/contents/latest.json"

    for attempt in range(3):
        response = session.get(
            url, headers=headers, timeout=TIMEOUT
        )

        if response.status_code == 404:
            existing = build_manifest()
            sha = None
        else:
            response.raise_for_status()
            data = response.json()
            sha = data["sha"]
            decoded = base64.b64decode(data["content"])
            existing = json.loads(decoded.decode("utf-8"))

        updated = merge_manifest(existing, snapshot)

        if updated == existing:
            return {
                "action": "unchanged",
                "manifest": updated,
            }

        payload = {
            "message": (
                f"Update Electric Eye newsletter index "
                f"for {snapshot['identifier']}"
            ),
            "content": base64.b64encode(
                (json.dumps(updated, indent=2) + "\n").encode("utf-8")
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
                "action": "updated",
                "manifest": updated,
                "commit": response.json()["commit"]["sha"],
            }

        if response.status_code not in (409, 422):
            response.raise_for_status()
            raise RuntimeError("Manifest publication failed")

    raise RuntimeError(
        "Newsletter manifest changed concurrently; retries exhausted"
    )
