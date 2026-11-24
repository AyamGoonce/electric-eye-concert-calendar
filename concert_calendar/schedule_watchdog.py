"""Guarded watchdog for missed automatic calendar publications.

Checks the published gh-pages pointer rather than the success state of unrelated
GitHub Actions jobs. Deliberately never changes the publication code or data.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
from email.message import EmailMessage
import json
import os
from pathlib import Path
import re
import smtplib
import ssl

ACTIVE_STATUSES = {"queued", "in_progress", "waiting", "pending", "requested"}
STALE_AFTER = timedelta(hours=5)
RECOVERY_COOLDOWN = timedelta(hours=2)


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamp must have a timezone")
    return parsed.astimezone(timezone.utc)


def published_at(pointer_text: str) -> datetime:
    match = re.search(r'Object\.freeze\((\{[^\n]*?\})\)', pointer_text)
    if not match:
        raise ValueError("Cannot locate calendar publication manifest")
    manifest = json.loads(match.group(1))
    return parse_utc(manifest["publishedAt"])


def decide(pointer_text: str, runs_payload: dict, now: datetime) -> dict:
    now = now.astimezone(timezone.utc)
    timestamp = published_at(pointer_text)
    age = now - timestamp
    if age < timedelta(0):
        raise ValueError("Calendar publication timestamp lies in the future")
    runs = runs_payload.get("workflow_runs")
    if not isinstance(runs, list):
        raise ValueError("GitHub calendar workflow run list is unavailable")
    summary = {
        "published_at": timestamp.isoformat(),
        "age_minutes": int(age.total_seconds() // 60),
        "action": "fresh",
        "reason": "Verified publication is within five hours",
    }
    if age <= STALE_AFTER:
        return summary
    if any(item.get("status") in ACTIVE_STATUSES for item in runs):
        summary.update(action="active", reason="Calendar run already queued or running")
        return summary
    recent = [
        parse_utc(item["created_at"])
        for item in runs
        if item.get("created_at")
    ]
    if recent and now - max(recent) < RECOVERY_COOLDOWN:
        summary.update(action="cooldown", reason="Calendar workflow started within the past two hours")
        return summary
    summary.update(action="recover", reason="Publication is stale; no active or recent calendar run")
    return summary


def notify(decision: dict, run_url: str) -> None:
    from newsletter.zoho_notification import ADMIN_EMAIL, SMTP_HOST, SMTP_PORT
    password = os.environ.get("ZOHO_MAIL_APP_PASSWORD")
    if not password:
        raise RuntimeError("Missing ZOHO_MAIL_APP_PASSWORD for watchdog alert")
    message = EmailMessage()
    message["From"] = f"Electric Eye Notifications <{ADMIN_EMAIL}>"
    message["To"] = ADMIN_EMAIL
    message["Subject"] = "Electric Eye Calendar — STALE publication; recovery requested"
    message.set_content(
        "The calendar publication is stale and the watchdog requested a guarded recovery run.\n"
        f"Last published: {decision['published_at']}\n"
        f"Age at check: {decision['age_minutes']} minutes\n"
        f"Watchdog run: {run_url}\n"
        "Recovery uses the existing calendar workflow and all its publication safeguards.\n"
    )
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ssl.create_default_context(), timeout=30) as smtp:
        smtp.login(ADMIN_EMAIL, password)
        smtp.send_message(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check")
    check.add_argument("--pointer", type=Path, required=True)
    check.add_argument("--runs", type=Path, required=True)
    alert = subparsers.add_parser("notify")
    alert.add_argument("--decision", type=Path, required=True)
    alert.add_argument("--run-url", required=True)
    args = parser.parse_args()
    if args.command == "check":
        decision = decide(
            args.pointer.read_text(encoding="utf-8"),
            json.loads(args.runs.read_text(encoding="utf-8")),
            datetime.now(timezone.utc),
        )
        print(json.dumps(decision, sort_keys=True))
    else:
        decision = json.loads(args.decision.read_text(encoding="utf-8"))
        if decision.get("action") != "recover":
            raise ValueError("Refusing alert for non-recovery decision")
        notify(decision, args.run_url)


if __name__ == "__main__":
    main()
