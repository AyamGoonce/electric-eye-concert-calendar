from concert_calendar.sources import load_events


def run() -> None:
    print("Île-de-France Concert Calendar")

    events = load_events()

    for event in events:
        print(event)