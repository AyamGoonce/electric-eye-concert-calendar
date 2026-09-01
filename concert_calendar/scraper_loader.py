from importlib import import_module
from pkgutil import iter_modules

import concert_calendar.scrapers as scrapers_package


def discover_scrapers():
    discovered_scrapers, _ = discover_scrapers_with_issues()
    return discovered_scrapers


def discover_scrapers_with_issues():
    discovered_scrapers = []
    issues = {}
    source_names = {}

    for module_info in iter_modules(scrapers_package.__path__):
        module_name = module_info.name

        if module_name.startswith("_"):
            continue

        qualified_name = f"{scrapers_package.__name__}.{module_name}"
        try:
            module = import_module(qualified_name)
        except Exception as error:
            issues[module_name] = f"{type(error).__name__}: {error}"
            continue

        if getattr(module, "IMAGE_ENRICHMENT_ONLY", False):
            continue

        source_name = getattr(module, "SOURCE_NAME", None)
        load_events = getattr(module, "load_events", None)

        if not source_name:
            issues[module_name] = "SOURCE_NAME is missing"
            continue

        if not callable(load_events):
            issues[module_name] = "load_events() is missing"
            continue

        duplicate = source_names.get(source_name.casefold())
        if duplicate:
            issues[module_name] = (
                f"duplicate SOURCE_NAME {source_name!r}; already used by {duplicate}"
            )
            continue

        source_names[source_name.casefold()] = module_name
        discovered_scrapers.append(module)

    discovered_scrapers.sort(
        key=lambda module: (
            getattr(module, "SOURCE_PRIORITY", 0),
            module.SOURCE_NAME.casefold(),
        )
    )

    return discovered_scrapers, issues
