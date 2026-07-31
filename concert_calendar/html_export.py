from datetime import datetime
from html import escape
from pathlib import Path

from concert_calendar.models import ConcertEvent


def format_list(items: list[str] | None) -> str:
    if not items:
        return ""

    return ", ".join(escape(item) for item in items)


def format_link(url: str | None, label: str) -> str:
    if not url:
        return ""

    safe_url = escape(url, quote=True)
    safe_label = escape(label)

    return (
        f'<a href="{safe_url}" target="_blank" '
        f'rel="noopener noreferrer">{safe_label}</a>'
    )


def format_event_date(raw_date: str) -> str:
    try:
        parsed_date = datetime.fromisoformat(raw_date)
    except ValueError:
        return escape(raw_date)

    return parsed_date.strftime("%d/%m/%Y")


def event_to_row(event: ConcertEvent) -> str:
    openers = format_list(event.openers)
    promoters = format_list(event.promoters)
    genre = escape(event.genre or "")
    facebook_link = format_link(event.facebook_event_url, "Facebook")
    ticket_link = format_link(event.ticket_url, "Tickets")

    return f"""
            <tr>
                <td class="date-cell">{format_event_date(event.date)}</td>
                <td class="headliner-cell">{escape(event.headliner)}</td>
                <td>{openers}</td>
                <td>{genre}</td>
                <td>{escape(event.venue)}</td>
                <td>{escape(event.city)}</td>
                <td>{escape(event.department)}</td>
                <td>{promoters}</td>
                <td>{facebook_link}</td>
                <td>{ticket_link}</td>
            </tr>"""


def export_events_to_html(
    events: list[ConcertEvent],
    output_path: str = "calendar.html",
) -> Path:
    sorted_events = sorted(events, key=lambda event: event.date)
    rows = "\n".join(event_to_row(event) for event in sorted_events)

    html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Île-de-France Concert Calendar</title>
    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            background: #f4f4f4;
            color: #191919;
            font-family: Arial, Helvetica, sans-serif;
            line-height: 1.45;
        }}

        main {{
            width: min(1600px, calc(100% - 32px));
            margin: 32px auto;
        }}

        h1 {{
            margin: 0 0 8px;
            font-size: clamp(28px, 4vw, 48px);
            line-height: 1.05;
        }}

        .concert-count {{
            margin: 0 0 24px;
            color: #555;
        }}

        .table-wrapper {{
            overflow-x: auto;
            background: #fff;
            border: 1px solid #d8d8d8;
            border-radius: 8px;
        }}

        table {{
            width: 100%;
            min-width: 1250px;
            border-collapse: collapse;
        }}

        th,
        td {{
            padding: 12px 14px;
            border-bottom: 1px solid #e5e5e5;
            text-align: left;
            vertical-align: top;
        }}

        th {{
            position: sticky;
            top: 0;
            background: #222;
            color: #fff;
            font-size: 13px;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            white-space: nowrap;
        }}

        tbody tr:nth-child(even) {{
            background: #fafafa;
        }}

        tbody tr:hover {{
            background: #f0f0f0;
        }}

        tbody tr:last-child td {{
            border-bottom: 0;
        }}

        td {{
            font-size: 14px;
        }}

        .date-cell {{
            min-width: 150px;
            white-space: nowrap;
        }}

        .headliner-cell {{
            min-width: 210px;
            font-weight: 700;
        }}

        a {{
            color: #9b111e;
            font-weight: 700;
        }}

        a:hover {{
            text-decoration: none;
        }}

        @media (max-width: 700px) {{
            main {{
                width: min(100% - 20px, 1600px);
                margin: 20px auto;
            }}

            th,
            td {{
                padding: 10px 12px;
            }}
        }}
    </style>
</head>
<body>
    <main>
        <h1>Île-de-France Concert Calendar</h1>
        <p class="concert-count">{len(sorted_events)} concerts listed.</p>

        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Headliner</th>
                        <th>Openers</th>
                        <th>Genre</th>
                        <th>Venue</th>
                        <th>City</th>
                        <th>Department</th>
                        <th>Promoter</th>
                        <th>Facebook</th>
                        <th>Tickets</th>
                    </tr>
                </thead>
                <tbody>
{rows}
                </tbody>
            </table>
        </div>
    </main>
</body>
</html>
"""

    destination = Path(output_path)
    destination.write_text(html_document, encoding="utf-8")

    return destination
