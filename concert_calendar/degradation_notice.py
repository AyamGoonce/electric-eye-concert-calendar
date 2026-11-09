"""Administrator-only notifications for degraded or failed calendar runs.

Never sends subscriber mail. The workflow calls this after publication
validation, so successful degraded runs generate a warning rather than hiding
behind the GitHub Actions green check.
"""

from __future__ import annotations

import argparse
from email.message import EmailMessage
import json
import os
from pathlib import Path
import smtplib
import ssl

from newsletter.zoho_notification import ADMIN_EMAIL, SMTP_HOST, SMTP_PORT


def build_message(report: dict | None, *, run_url: str, failed: bool) -> EmailMessage | None:
    health = (report or {}).get("source_health", [])
    degraded = [item for item in health if item.get("status") in {"failed", "partial"}]
    if not failed and not degraded:
        return None

    label = "FAILED — publication blocked" if failed else "WARNING — published with retained data"
    lines = [
        f"Electric Eye Concert Calendar: {label}",
        f"GitHub run: {run_url}",
        "",
    ]
    if report:
        lines.append(f"Candidate event count: {report.get('event_count', 'not available')}")
        lines.append(f"Published at: {report.get('published_at', 'not available')}")
    else:
        lines.append("No completed automation report was produced; inspect the run logs.")
    lines.append("")
    if degraded:
        lines.append("Degraded sources:")
        for item in degraded:
            lines.extend([
                f"- {item.get('source_name', 'unknown')}: {item.get('status')}",
                f"  Reason: {item.get('error') or 'incomplete fallback inventory'}",
                f"  Fresh records: {item.get('fresh_event_count', 0)}",
                f"  Retained records: {item.get('fallback_event_count', 0)}",
                f"  Last successful scrape: {item.get('last_successful_at') or 'unknown'}",
                f"  Expired records: {item.get('fallback_expired_count', 0)}",
                f"  Fallback unavailable: {item.get('fallback_unavailable', False)}",
            ])
    else:
        lines.append("See the run logs for the validation or publication failure.")

    message = EmailMessage()
    message["From"] = f"Electric Eye Notifications <{ADMIN_EMAIL}>"
    message["To"] = ADMIN_EMAIL
    message["Subject"] = f"Electric Eye Calendar — {label}"
    message.set_content("\n".join(lines) + "\n")
    return message


def notify(*, report_path: Path, run_url: str, failed: bool, smtp_factory=None) -> bool:
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    message = build_message(report, run_url=run_url, failed=failed)
    if message is None:
        print("Calendar healthy; no degradation email needed.", flush=True)
        return False
    password = os.environ.get("ZOHO_MAIL_APP_PASSWORD")
    if not password:
        raise RuntimeError("ZOHO_MAIL_APP_PASSWORD is not configured for calendar notifications")
    factory = smtp_factory or smtplib.SMTP_SSL
    with factory(SMTP_HOST, SMTP_PORT, context=ssl.create_default_context(), timeout=30) as smtp:
        smtp.login(ADMIN_EMAIL, password)
        smtp.send_message(message)
    print(f"Calendar administrator alert sent to {ADMIN_EMAIL}", flush=True)
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--status", choices=("success", "failure"), required=True)
    args = parser.parse_args()
    notify(report_path=args.report, run_url=args.run_url, failed=args.status == "failure")


if __name__ == "__main__":
    main()
