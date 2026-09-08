import copy
import io
import time
import unittest
from contextlib import redirect_stdout
from dataclasses import asdict
from threading import Barrier, Lock
from types import SimpleNamespace
from unittest.mock import Mock, patch

from concert_calendar import sources
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import prepare_upcoming_events
from datetime import date


def event(name):
    return ConcertEvent(date="2027-01-01", headliner=name, venue="La Cigale",
                        city="Paris", department="75")


def source(name, loader):
    return SimpleNamespace(SOURCE_NAME=name, __name__=name, load_events=loader,
                           get_diagnostics=lambda: [{"marker": name}])


def run(modules, workers=4):
    with patch.object(sources, "discover_scrapers_with_issues", return_value=(modules, {})), \
         patch.object(sources, "SOURCE_WORKERS", workers), redirect_stdout(io.StringIO()):
        return sources.load_events_with_report(scraper_attempts=3, retry_delay_seconds=0)


class SourceConcurrencyTests(unittest.TestCase):
    def test_four_workers_and_ordered_output(self):
        barrier = Barrier(4)
        lock = Lock()
        active = peak = 0
        completed = []

        def loader(i):
            def load():
                nonlocal active, peak
                with lock:
                    active += 1
                    peak = max(active, peak)
                if i < 4:
                    barrier.wait(timeout=5)
                time.sleep((4 - i % 4) * .01)
                with lock:
                    completed.append(i)
                    active -= 1
                return [event(str(i))]
            return load

        modules = [source(str(i), loader(i)) for i in range(8)]
        events, report = run(modules)
        self.assertEqual(4, peak)
        self.assertNotEqual(list(range(8)), completed)
        self.assertEqual([str(i) for i in range(8)], [e.headliner for e in events])
        self.assertEqual([str(i) for i in range(8)], [h["source_name"] for h in report.source_health])
        self.assertEqual([str(i) for i in range(8)], [d["marker"] for d in report.source_diagnostics])

    def test_retry_failure_empty_and_serial_equivalence(self):
        def modules():
            return [source("retry", Mock(side_effect=[TimeoutError("temporary"), [event("Artist")]])),
                    source("healthy", Mock(return_value=[event("Artist")])),
                    source("failed", Mock(side_effect=TimeoutError("offline"))),
                    source("empty", Mock(return_value=[]))]
        serial, parallel = modules(), modules()
        left, a = run(serial, 1)
        right, b = run(parallel, 4)
        self.assertEqual(asdict(a), asdict(b))
        self.assertEqual([asdict(e) for e in left], [asdict(e) for e in right])
        self.assertEqual(prepare_upcoming_events(left, date(2026, 1, 1)),
                         prepare_upcoming_events(right, date(2026, 1, 1)))
        self.assertEqual([2, 1, 3, 3], [m.load_events.call_count for m in parallel])
        self.assertEqual(["ok", "ok", "failed", "empty"], [h["status"] for h in b.source_health])
