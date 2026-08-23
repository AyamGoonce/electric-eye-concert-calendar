from concert_calendar.production_export import export_production_calendar
from concert_calendar.sources import load_events


def main():
    events = load_events()
    output_file = export_production_calendar(events)

    print(f"Production calendar written to: {output_file.resolve()}")


if __name__ == "__main__":
    main()
