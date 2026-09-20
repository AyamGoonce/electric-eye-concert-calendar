import unittest
from pathlib import Path

from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import event_to_data


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "concert_calendar/static/calendar-renderer.js"
CSS = ROOT / "concert_calendar/static/calendar.css"


class PublicEventContextTests(unittest.TestCase):
    def test_export_preserves_all_semantic_context(self):
        item = ConcertEvent(
            date="2026-10-01",
            headliner="Artist",
            venue="Venue",
            city="Paris",
            department="75",
            event_title="Named Show",
            series_name="Recurring Night",
            festival_name="Named Festival",
        )

        data = event_to_data(item)

        self.assertTrue(data["f"])
        self.assertEqual("Named Show", data["et"])
        self.assertEqual("Recurring Night", data["sn"])
        self.assertEqual("Named Festival", data["fn"])

    def test_non_festival_does_not_emit_festival_name(self):
        item = ConcertEvent(
            date="2026-10-01",
            headliner="Artist",
            venue="Venue",
            city="Paris",
            department="75",
        )

        data = event_to_data(item)

        self.assertFalse(data["f"])
        self.assertNotIn("fn", data)

    def test_renderer_consumes_semantic_context_fields(self):
        renderer = RENDERER.read_text()

        self.assertIn("[e.et,e.sn,e.fn]", renderer)
        self.assertIn("ee-calendar-event-context", renderer)
        self.assertIn(
            '(e.fn === undefined || typeof e.fn === "string")',
            renderer,
        )

    def test_context_has_calendar_style(self):
        css = CSS.read_text()

        self.assertIn(".ee-calendar-event-context", css)


if __name__ == "__main__":
    unittest.main()
