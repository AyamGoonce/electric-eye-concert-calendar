"""Explicit fixture clocks; never patch the global datetime module."""

from contextlib import contextmanager
from datetime import date
from unittest.mock import patch


@contextmanager
def freeze_date(module, reference="2026-09-01"):
    """Freeze a consumer's date.today(), preserving real date construction.

    Usable as a context manager or test decorator. Callers with a ``today``
    argument should continue passing their fixture reference date directly.
    """
    with patch(f"{module}.date", wraps=date) as clock:
        clock.today.return_value = date.fromisoformat(reference)
        yield
