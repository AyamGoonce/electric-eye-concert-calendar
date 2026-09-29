"""Conservative whole-title rejection for commerce and status placeholders."""

import re
import unicodedata


PLACEHOLDER_TITLES = {
    "bientot en vente", "prochainement", "en vente", "sold out", "complet",
    "ticket", "tickets", "billetterie", "reserver", "reservation",
    "reservez", "reserver vos places", "reservez vos places",
    "book now", "buy tickets", "concert reporte", "concert annule",
    "spectacle reporte", "spectacle annule",
}


def is_placeholder_title(value: str | None) -> bool:
    if not value:
        return False
    folded = unicodedata.normalize("NFKD", value.casefold())
    folded = "".join(character for character in folded if not unicodedata.combining(character))
    normalized = re.sub(r"[^a-z0-9]+", " ", folded).strip()
    return normalized in PLACEHOLDER_TITLES
