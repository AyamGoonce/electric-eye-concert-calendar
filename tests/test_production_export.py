import json
from datetime import date
from pathlib import Path
import tempfile
import unittest

from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import (
    ARTIST_SORT_OVERRIDES,
    PUBLIC_GENRES,
    alphabetical_sort_key,
    build_current_pointer,
    build_data_asset,
    build_fixture_html,
    event_to_data,
    export_production_calendar,
    export_integration_prototype,
    genre_categories,
    prepare_upcoming_events,
    read_renderer,
    read_styles,
)


def make_event(
    event_date,
    headliner,
    venue="Bataclan",
    city="Paris",
    **kwargs,
):
    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        venue=venue,
        city=city,
        department="75" if city == "Paris" else "95",
        **kwargs,
    )


class ProductionDataTests(unittest.TestCase):
    def test_article_aware_sort_keys_are_conservative(self):
        examples = {
            "The Black Keys": "black keys",
            "A Certain Ratio": "certain ratio",
            "An Horse": "horse",
            "La Maroquinerie": "maroquinerie",
            "La Batterie": "batterie",
            "La Bellevilloise": "bellevilloise",
            "La CLEF": "clef",
            "L'Empreinte": "empreinte",
            "L'Européen": "europeen",
            "Le Trianon": "trianon",
            "Les Femmes s'en Mêlent": "femmes s'en melent",
            "L'Olympia": "olympia",
            "L’Olympia": "olympia",
            "Alice Cooper": "alice cooper",
            "Sammy Hagar": "sammy hagar",
            "An Pierlé": "pierle",
        }

        for displayed_name, expected_key in examples.items():
            with self.subTest(displayed_name=displayed_name):
                self.assertEqual(expected_key, alphabetical_sort_key(displayed_name))

    def test_explicit_artist_sort_override_is_separate_and_conservative(self):
        self.assertEqual(
            "perfect circle",
            alphabetical_sort_key("A Perfect Circle", ARTIST_SORT_OVERRIDES),
        )
        self.assertEqual("perfect circle", alphabetical_sort_key("A Perfect Circle"))
        self.assertEqual(
            "an pierle",
            alphabetical_sort_key("An Pierlé", ARTIST_SORT_OVERRIDES),
        )

    def test_upcoming_only_and_deterministic_sorting(self):
        events = [
            make_event("2026-08-31", "Zulu"),
            make_event("2026-08-30", "Past"),
            make_event("2026-08-31", "Álpha"),
        ]

        prepared = prepare_upcoming_events(events, today=date(2026, 8, 31))

        self.assertEqual(["Álpha", "Zulu"], [event["h"] for event in prepared])

    def test_production_fields_preserve_structured_city(self):
        event = make_event(
            "2026-09-01",
            "Long Artist + Another Artist",
            venue="Le Forum",
            city="Vauréal",
            openers=["Première Partie"],
            promoters=["Official Promoter"],
            genre="Rock alternatif",
            ticket_url="https://tickets.example/event",
        )

        prepared = prepare_upcoming_events([event], today=date(2026, 8, 31))[0]

        self.assertEqual("Le Forum", prepared["v"])
        self.assertEqual("Vauréal", prepared["c"])
        self.assertEqual(["Première Partie"], prepared["o"])
        self.assertEqual(["Rock / Indie / Punk"], prepared["x"])
        self.assertEqual("Long Artist + Another Artist", prepared["h"])
        self.assertEqual("Le Forum", prepared["v"])

    def test_invalid_ticket_url_is_omitted(self):
        event = make_event(
            "2026-09-01",
            "Artist",
            ticket_url="/relative-ticket",
        )

        prepared = prepare_upcoming_events([event], today=date(2026, 8, 31))[0]

        self.assertIsNone(prepared["t"])

    def test_unsuitable_official_image_is_omitted(self):
        event = make_event(
            "2026-09-01", "Artist",
            image_url="https://official.example/assets/placeholder-logo.png",
            image_source="Official venue",
        )
        prepared = prepare_upcoming_events([event], today=date(2026, 8, 31))[0]
        self.assertNotIn("im", prepared)
        self.assertNotIn("is", prepared)

    def test_festival_status_first_seen_and_sold_out_are_exported(self):
        event = make_event(
            "2026-09-01", "Festival Headliner",
            festival_name="Festival", sold_out=True,
            first_seen="2026-08-23T10:00:00Z",
        )
        prepared = prepare_upcoming_events([event], today=date(2026, 8, 31))[0]
        self.assertTrue(prepared["f"])
        self.assertTrue(prepared["so"])
        self.assertEqual("2026-08-23T10:00:00Z", prepared["fs"])

    def test_missing_ticket_does_not_imply_sold_out(self):
        prepared = prepare_upcoming_events(
            [make_event("2026-09-01", "Available status unknown", ticket_url=None)],
            today=date(2026, 8, 31),
        )[0]
        self.assertFalse(prepared["so"])

    def test_genre_categories_are_broad_and_meaningful(self):
        self.assertEqual(["Pop"], genre_categories("Concert - Indie Pop"))
        self.assertEqual(["Hip-hop / Rap"], genre_categories("Rap, Hip-Hop"))
        self.assertEqual(
            ["Metal / Hard Rock"],
            genre_categories("Hard / Metal"),
        )
        self.assertEqual(
            ["Rock / Indie / Punk"],
            genre_categories("Rock / Indie / Punk"),
        )
        self.assertEqual(["Jazz / Blues"], genre_categories("Jazz actuel"))
        self.assertEqual(["Jazz / Blues"], genre_categories("Jazz funk"))
        self.assertEqual([], genre_categories(None))

    def test_ambiguous_genre_does_not_combine_public_categories(self):
        self.assertEqual([], genre_categories("Pop, Rock"))
        self.assertEqual([], genre_categories("Jazz / Funk"))
        self.assertEqual([], genre_categories("Jazz, Musiques du monde"))

    def test_exact_public_genre_is_preserved_as_one_label(self):
        self.assertEqual(
            ["R&B / Soul / Funk"],
            genre_categories("R&B / Soul / Funk"),
        )


class OptionalEventMetadataTests(unittest.TestCase):

    def test_optional_event_metadata_is_exported_when_present(self):
        item = ConcertEvent(
            date="2026-09-01",
            headliner="Slow Pilot",
            venue="La Cigale",
            city="Paris",
            department="",
            event_title="The Songs of Jeff Buckley",
            series_name="Special Presentation",
            co_headliners=["Co-Headliner"],
            image_url="https://example.com/slow-pilot.jpg",
            image_source="La Cigale",
            electric_eye_links=[
                {
                    "label": "Review",
                    "url": "https://www.electriceyerock.com/example",
                    "kind": "artist",
                }
            ],
        )

        data = event_to_data(item)

        self.assertEqual("The Songs of Jeff Buckley", data["et"])
        self.assertEqual("Special Presentation", data["sn"])
        self.assertEqual(["Co-Headliner"], data["ch"])
        self.assertEqual("https://example.com/slow-pilot.jpg", data["im"])
        self.assertEqual("La Cigale", data["is"])
        self.assertEqual(
            "https://www.electriceyerock.com/example",
            data["ee"][0]["url"],
        )

    def test_optional_event_metadata_is_omitted_when_absent(self):
        item = ConcertEvent(
            date="2026-09-01",
            headliner="Slow Pilot",
            venue="La Cigale",
            city="Paris",
            department="",
        )

        data = event_to_data(item)

        self.assertNotIn("et", data)
        self.assertNotIn("sn", data)
        self.assertNotIn("ch", data)
        self.assertNotIn("im", data)
        self.assertNotIn("is", data)
        self.assertNotIn("ee", data)

    def test_dice_aggregator_image_is_not_published(self):
        item = ConcertEvent(
            date="2026-09-01",
            headliner="Slow Pilot",
            venue="La Cigale",
            city="Paris",
            department="",
            image_url="https://images.dice.fm/example.jpg",
            image_source="DICE",
        )

        data = event_to_data(item)

        self.assertNotIn("im", data)
        self.assertNotIn("is", data)


class ProductionHTMLTests(unittest.TestCase):
    def setUp(self):
        self.events = [
            make_event("2026-09-01", "Paris Artist"),
            make_event(
                "2026-09-02",
                "Énorme co-bill " + "+ Artist " * 20,
                venue="Le Forum",
                city="Vauréal",
                openers=["Support Act"],
                genre="Rock",
            ),
            make_event("2026-09-03", "No Ticket", ticket_url=None),
        ]

    def test_generated_shell_contains_required_controls_and_states(self):
        with tempfile.TemporaryDirectory() as directory:
            path = export_production_calendar(
                self.events,
                output_path=str(Path(directory) / "calendar.html"),
                today=date(2026, 8, 31),
            )
            html = path.read_text(encoding="utf-8")
            soup = BeautifulSoup(html, "html.parser")

        self.assertIsNotNone(soup.select_one("body.ee-calendar-page"))
        self.assertIsNotNone(soup.select_one("#ee-concert-calendar"))
        self.assertIn("@media (max-width: 680px)", soup.style.string)
        self.assertIn("Date — soonest first", html)
        self.assertIn("Date — latest first", html)
        self.assertIn("Headliner — A–Z", html)
        self.assertNotIn("Artist — A–Z", html)
        self.assertIn("Venue — A–Z", html)

    def test_embedded_json_is_compact_complete_and_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            path = export_production_calendar(
                self.events,
                output_path=str(Path(directory) / "calendar.html"),
                today=date(2026, 8, 31),
            )
            html = path.read_text(encoding="utf-8")

        marker = "window.ElectricEyeConcertData = Object.freeze("
        serialized = html.split(marker, 1)[1].split(");", 1)[0]
        data = json.loads(serialized)

        self.assertEqual(3, len(data))
        self.assertEqual("Vauréal", data[1]["c"])
        self.assertEqual([], data[2]["o"])

    def test_javascript_contains_combined_filter_and_venue_display_rules(self):
        with tempfile.TemporaryDirectory() as directory:
            path = export_production_calendar(
                self.events,
                output_path=str(Path(directory) / "calendar.html"),
                today=date(2026, 8, 31),
            )
            html = path.read_text(encoding="utf-8")

        self.assertIn("e.s.includes(q)", html)
        self.assertIn("e.d.startsWith(month)", html)
        self.assertIn("venueId(e.v)===venueId(venue)", html)
        self.assertIn('g==="Unsorted"?!e.x.length', html)
        self.assertIn('e.x.length&&e.x[0]===g', html)
        self.assertIn('order==="date-desc"', html)
        self.assertIn('order==="artist-asc"', html)
        self.assertIn('order==="venue-asc"', html)
        self.assertIn('"a perfect circle":"Perfect Circle"', html)
        self.assertIn("articleKey(e.h,artistOverrides)", html)
        self.assertIn("articleKey(e.v,{})", html)
        self.assertIn('e.c.toLocaleLowerCase()==="paris"?e.v:e.v+" ("+e.c+")"', html)
        self.assertIn('ticket.target="_blank"', html)
        self.assertIn('ticket.rel="noopener noreferrer"', html)
        self.assertIn('e.x[0]', html)
        self.assertNotIn('addText(metadata, "ee-calendar-promoter"', html)
        self.assertIn("ee-calendar-lineup-toggle", html)
        self.assertIn('setAttribute("aria-expanded"', html)
        self.assertIn("e.s.includes(q)", html)
        self.assertIn("URLSearchParams", html)
        self.assertIn('addEventListener("popstate"', html)
        self.assertIn('timeZone:"Europe/Paris"', html)
        self.assertIn("ee-calendar-day-separator", html)
        self.assertIn("ee-calendar-sold-out", html)
        self.assertIn("ee-calendar-new-badge", html)
        self.assertIn("e.o.slice(0,visible)", html)
        self.assertIn("Math.min(5,e.o.length)", html)

    def test_renderer_genre_filter_uses_exact_public_vocabulary(self):
        renderer = read_renderer()

        for genre in PUBLIC_GENRES:
            self.assertEqual(1, renderer.count(f'"{genre}"'))
        self.assertIn('publicGenres.concat(["Unsorted"]).map', renderer)
        self.assertNotIn("genreValues.forEach", renderer)

    def test_event_genre_label_uses_existing_filter_state(self):
        renderer = read_renderer()

        self.assertIn('genreButton(e.x[0])', renderer)
        self.assertIn('c.value===genre', renderer)
        self.assertIn('check.checked=true', renderer)
        self.assertIn('updateGenreSummary();updateURL(true);render()', renderer)

    def test_event_genre_label_is_safe_semantic_button(self):
        renderer = read_renderer()

        self.assertIn('button(document.createDocumentFragment(),"ee-calendar-genre",genre)', renderer)
        self.assertIn('setAttribute("aria-label","Filter by "+genre)', renderer)
        self.assertIn('event.preventDefault();event.stopPropagation()', renderer)
        self.assertIn('event.key==="Enter"||event.key===" "', renderer)
        self.assertIn('activateGenre(genre,event)', renderer)
        self.assertIn('e.type = "button"', renderer)

    def test_blank_event_has_no_unsorted_badge(self):
        renderer = read_renderer()

        self.assertIn('if(e.x.length)metadata.append(genreButton(e.x[0]))', renderer)
        self.assertIn('g==="Unsorted"?!e.x.length', renderer)
        self.assertNotIn('genreButton("Unsorted")', renderer)

    def test_collapsible_chronology_and_solid_month_contract(self):
        renderer = read_renderer()
        styles = read_styles()

        for required in (
            'className="ee-calendar-year-section"',
            'className="ee-calendar-month-section"',
            '"ee-calendar-year-toggle"',
            '"ee-calendar-month-toggle"',
            'setAttribute("aria-expanded",String(isExpanded))',
            'controls.expandAll.addEventListener("click"',
            'controls.collapseAll.addEventListener("click"',
            'manualCollapsedMonths.delete(linkedMonth)',
            'autoCollapsedMonths.delete(linkedMonth)',
            'list.append(separator(e.d))',
            'genreButton(e.x[0])',
            'ticket.href=e.t',
            'function autoCollapseOnUpwardScroll()',
            'y<lastScrollY-4',
            'safelyBelowViewport(section.getBoundingClientRect(),innerHeight)',
            'section.contains(focused)',
            'autoCollapseBlocked=active||!!linked',
            'function autoExpandOnDownwardScroll()',
            'autoCollapsedMonths.add(key)',
            'manualCollapsedMonths.has(key)',
            'approachingViewport(section.getBoundingClientRect(),innerHeight)',
        ):
            self.assertIn(required, renderer)
        self.assertNotIn("blogger.googleusercontent.com/img/b/", renderer)
        self.assertNotIn('monthImage', renderer)
        self.assertNotIn('.ee-calendar-month-toggle--panoramic', styles)
        self.assertNotIn('.ee-calendar-month-image', styles)
        self.assertIn('background: #25282c', styles)
        self.assertIn('border-left: 4px solid var(--ee-calendar-accent)', styles)
        self.assertIn('.ee-calendar-month-events > li::marker', styles)
        self.assertIn('counter-increment: none', styles)
        self.assertNotIn('position: sticky;\n  top:', styles.split('.ee-calendar-month-toggle', 1)[1])

    def test_year_and_month_headers_do_not_create_images(self):
        renderer = read_renderer()
        chronology = renderer[renderer.index("function monthSection"):renderer.index("function revealAll")]
        self.assertNotIn('createElement("img")', chronology)

    def test_optional_event_thumbnail_is_lazy_and_links_to_artist_page(self):
        renderer = read_renderer()
        self.assertIn('img.loading="lazy"', renderer)
        self.assertIn('img.decoding="async"', renderer)
        self.assertIn('thumb.href=coverageURL(e.i)', renderer)
        self.assertIn('internal.href=coverageURL(e.i)', renderer)
        self.assertIn('e.ee[0].total', renderer)
        self.assertIn('ticket.target="_blank"', renderer)


class IntegrationAssetTests(unittest.TestCase):
    def setUp(self):
        self.events = [
            make_event("2026-09-01", "The Black Keys", ticket_url="https://tickets.example/black-keys"),
            make_event("2026-09-02", "A Perfect Circle", venue="Le Forum", city="Vauréal", genre="Rock"),
        ]
        self.prepared = prepare_upcoming_events(self.events, today=date(2026, 8, 31))

    def test_data_asset_hash_and_filename_are_deterministic(self):
        first = build_data_asset(self.prepared)
        second = build_data_asset(self.prepared)

        self.assertEqual(first, second)
        self.assertRegex(first[0], r"^calendar-data\.[0-9a-f]{16}\.js$")
        self.assertEqual(64, len(first[1]))

    def test_data_asset_contains_only_compact_valid_event_data(self):
        filename, digest, asset = build_data_asset(self.prepared)

        self.assertIn("window.ElectricEyeConcertData", asset)
        self.assertIn('"ee:concert-data-ready"', asset)
        self.assertIn('"h":"The Black Keys"', asset)
        self.assertNotIn("calendar-renderer", asset)
        self.assertNotIn("ee-calendar-filters", asset)
        self.assertTrue(filename.startswith(f"calendar-data.{digest[:16]}"))

    def test_pointer_references_hashed_asset_and_has_error_event(self):
        filename, digest, _ = build_data_asset(self.prepared)
        pointer = build_current_pointer(filename, digest, len(self.prepared))

        self.assertIn(filename, pointer)
        self.assertIn(digest, pointer)
        self.assertIn('"ee:concert-data-error"', pointer)
        self.assertIn('"data asset unavailable"', pointer)

    def test_fixture_models_blogger_mount_and_both_load_orders(self):
        renderer_first = build_fixture_html("renderer-first")
        data_first = build_fixture_html("data-first")

        for fixture in (renderer_first, data_first):
            soup = BeautifulSoup(fixture, "html.parser")
            self.assertIsNotNone(soup.select_one("body.ee-calendar-page.ee-full-width-page"))
            self.assertIsNotNone(soup.select_one("#content-wrapper > .container"))
            self.assertIsNotNone(soup.select_one("#post-body > #ee-concert-calendar"))

        self.assertLess(renderer_first.index("calendar-renderer.js"), renderer_first.index("calendar-current.js"))
        self.assertLess(data_first.index("calendar-current.js"), data_first.index("calendar-renderer.js"))

    def test_assets_are_scoped_and_renderer_handles_failure_states(self):
        styles = read_styles()
        renderer = read_renderer()

        self.assertIn(".ee-calendar-page #ee-concert-calendar", styles)
        self.assertIn("malformed or empty event dataset", renderer)
        self.assertIn("timed out waiting for event data", renderer)
        self.assertIn('document.getElementById(MOUNT_ID)', renderer)
        self.assertIn('"Headliner — A–Z"', renderer)
        self.assertIn("event.o", renderer)
        self.assertIn("e.s.includes(q)", renderer)
        self.assertIn("venueId(e.v)===venueId(venue)", renderer)
        self.assertIn("articleKey(a,{})", renderer)
        self.assertIn("venueLabels=new Map()", renderer)
        self.assertIn(".ee-calendar-event-list > li::marker", styles)
        self.assertIn("list-style: none", styles)
        self.assertIn("position: sticky", styles)
        self.assertIn("position: static", styles)
        self.assertIn("ee-calendar-text-button", styles)

    def test_integration_export_writes_a_complete_local_bundle(self):
        with tempfile.TemporaryDirectory() as directory:
            result = export_integration_prototype(
                self.events,
                output_dir=directory,
                today=date(2026, 8, 31),
            )

            for key in (
                "renderer",
                "styles",
                "data",
                "pointer",
                "fixture",
                "data_first_fixture",
                "missing_fixture",
                "malformed_fixture",
            ):
                self.assertTrue(Path(result[key]).is_file())
            self.assertEqual(2, result["event_count"])


if __name__ == "__main__":
    unittest.main()
