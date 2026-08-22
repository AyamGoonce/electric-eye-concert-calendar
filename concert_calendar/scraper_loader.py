from importlib import import_module
from pkgutil import iter_modules

import concert_calendar.scrapers as scrapers_package


def discover_scrapers():
    discovered_scrapers = []

    for module_info in iter_modules(scrapers_package.__path__):
        module_name = module_info.name

        if module_name.startswith("_"):
            continue

        module = import_module(
            f"{scrapers_package.__name__}.{module_name}"
        )

        source_name = getattr(module, "SOURCE_NAME", None)
        load_events = getattr(module, "load_events", None)

        if not source_name:
            print(
                f"Skipping scraper '{module_name}': "
                "SOURCE_NAME is missing"
            )
            continue

        if not callable(load_events):
            print(
                f"Skipping scraper '{module_name}': "
                "load_events() is missing"
            )
            continue

        discovered_scrapers.append(module)

    discovered_scrapers.sort(
        key=lambda module: module.SOURCE_NAME.casefold()
    )

    return discovered_scrapers
