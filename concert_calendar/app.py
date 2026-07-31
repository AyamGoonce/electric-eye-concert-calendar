from concert_calendar.sources import load_events
from concert_calendar.html_export import export_events_to_html

def run() -> None:
    print("Île-de-France Concert Calendar")

    events = load_events()

    output_file = export_events_to_html(events)

    print(f"\nHTML calendar written to: {output_file.resolve()}")

    for event in events:
        print(event)