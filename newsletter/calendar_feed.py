"""Read and verify the published Electric Eye concert calendar."""

import hashlib
import json
import re
from urllib.parse import urljoin

import requests

BASE_URL = "https://archive.electriceyerock.com/proof/"
MANIFEST_URL = urljoin(BASE_URL, "calendar-current.js")

MANIFEST_PATTERN = re.compile(
    r"var manifest = Object\.freeze\((\{[^\n]+\})\);"
)
DATA_PATTERN = re.compile(
    r"window\.ElectricEyeConcertData\s*=\s*Object\.freeze\((\[.*?\])\);",
    re.S,
)
SAFE_DATA_NAME = re.compile(r"^calendar-data\.[0-9a-f]{16}\.js$")


def fetch_calendar(session=None):
    """Return verified published calendar records and their manifest."""
    session = session or requests.Session()

    response = session.get(MANIFEST_URL, timeout=30)
    response.raise_for_status()

    match = MANIFEST_PATTERN.search(response.text)
    if not match:
        raise ValueError("Calendar manifest could not be parsed")

    manifest = json.loads(match.group(1))
    filename = manifest.get("data", "")

    if not SAFE_DATA_NAME.fullmatch(filename):
        raise ValueError("Calendar manifest contains an invalid data filename")

    response = session.get(urljoin(BASE_URL, filename), timeout=60)
    response.raise_for_status()

    actual_sha = hashlib.sha256(response.content).hexdigest()
    if actual_sha != manifest.get("sha256"):
        raise ValueError("Calendar data checksum mismatch")

    match = DATA_PATTERN.search(response.text)
    if not match:
        raise ValueError("Calendar data array could not be parsed")

    events = json.loads(match.group(1))

    if not isinstance(events, list) or len(events) != manifest.get("count"):
        raise ValueError("Calendar data record count mismatch")

    if not events:
        raise ValueError("Published calendar is unexpectedly empty")

    return events, manifest
