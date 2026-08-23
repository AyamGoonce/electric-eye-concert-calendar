from concert_calendar.production_export import (
    export_integration_prototype,
    export_production_calendar,
)
from concert_calendar.sources import load_events


def main():
    events = load_events()
    output_file = export_production_calendar(events)
    prototype = export_integration_prototype(events)

    print(f"Production calendar written to: {output_file.resolve()}")
    print(f"Integration fixture written to: {prototype['fixture'].resolve()}")


if __name__ == "__main__":
    main()
