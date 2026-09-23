from datetime import date
from unittest import TestCase
from unittest.mock import Mock, patch

from concert_calendar.event_state import canonical_event_identity
from concert_calendar.scrapers import etoiles


def response(*, payload=None, text="", headers=None):
    result = Mock(text=text, headers=headers or {})
    result.raise_for_status = Mock()
    result.json.return_value = payload
    return result


def post(post_id, title, *, link=None, published="2026-04-01T12:00:00",
         formats=(3,), genres=(), statuses=()):
    return {
        "id": post_id,
        "date": published,
        "slug": title.casefold().replace(" ", "-"),
        "link": link or f"https://www.etoiles.paris/evenement/{title.casefold().replace(' ', '-')}/",
        "title": {"rendered": title},
        "format": list(formats),
        "genre": list(genres),
        "status-event": list(statuses),
    }


def detail(title, primary_date, primary_time, dates, *, image=None,
           related_date="31 déc.", related_time="23:59"):
    image_html = f'<img src="{image}">' if image else ""
    date_rows = "".join(f"<div>{value}</div>" for value in dates)
    return f"""
      <main><article><div class="SingleEvenement">
        <div class="SingleEvenement__header"><div class="grid">
          <div><div class="hero-copy"><h1>{title}</h1>
            <div class="primary-meta"><div class="tag"><span>Concert</span></div>
              <span class="ts-label">{primary_date}</span>
              <span class="ts-label">{primary_time}</span>
            </div>
          </div></div>
          <div class="hero-image">{image_html}</div>
        </div></div>
        <div class="SingleEvenement__content">
          <div class="event-fact"><div class="ts-label">Dates</div>
            <div class="ts-h3 font-bold">{date_rows}</div>
          </div>
        </div>
      </div></article>
      <section class="related-events">
        <a class="component-card-event"><h3>UNRELATED</h3>
          <span class="ts-label">{related_date}</span>
          <span class="ts-label">{related_time}</span>
        </a>
      </section></main>
    """


class EtoilesDateTests(TestCase):
    def test_french_juin_and_juil_remain_distinct(self):
        publication = "2026-01-01T12:00:00"
        self.assertEqual(
            date(2026, 6, 12),
            etoiles.resolve_event_date("Ven 12 juin", publication),
        )
        self.assertEqual(
            date(2026, 7, 12),
            etoiles.resolve_event_date("Dim 12 juil", publication),
        )

    def test_ambiguous_year_is_rejected_instead_of_guessed(self):
        with self.assertRaises(etoiles.EtoilesScraperError):
            etoiles.resolve_event_date(
                "Jeu 1 jan",
                "2025-01-01T12:00:00",
                candidate_years=(2026, 2032),
            )


class EtoilesDetailTests(TestCase):
    def test_primary_fields_ignore_related_cards_and_eli_expands_dates(self):
        events = etoiles.parse_detail_page(
            detail(
                "ELI", "11 oct.", "19:00", ("Dim 11 oct", "Lun 12 oct"),
                image="https://www.etoiles.paris/uploads/eli.webp",
            ),
            post(1581, "ELI", link="https://www.etoiles.paris/evenement/eli/",
                 published="2026-08-19T10:00:00"),
            today=date(2026, 9, 1),
        )

        self.assertEqual(["2026-10-11", "2026-10-12"], [event.date for event in events])
        for event in events:
            self.assertEqual("ELI", event.headliner)
            self.assertEqual("19:00", event.start_time)
            self.assertEqual("https://www.etoiles.paris/evenement/eli/", event.ticket_url)
            self.assertEqual(("Les Étoiles", "Paris", "75"), (event.venue, event.city, event.department))
            self.assertEqual("https://www.etoiles.paris/uploads/eli.webp", event.image_url)
            self.assertEqual("Les Étoiles", event.image_source)
        self.assertEqual([
            "883fbac9f2face6b9b6732ac934a7c4e350ccc6297e96fc5eeef78b2566eac08",
            "2a17ca06679ac5d30001fb910a52838475d322eb1397b78ab4079e11b1d946d7",
        ], [canonical_event_identity(event) for event in events])

    def test_past_performances_are_excluded(self):
        events = etoiles.parse_detail_page(
            detail("OLD SHOW", "12 juin", "19:30", ("Ven 12 juin",)),
            post(90, "OLD SHOW", published="2026-01-01T12:00:00"),
            today=date(2026, 9, 1),
        )
        self.assertEqual([], events)

    def test_missing_dates_block_fails_the_source(self):
        html = detail("BROKEN", "2 oct.", "19:00", ("Ven 2 oct",)).replace(
            '<div class="ts-label">Dates</div>', '<div class="ts-label">Tarifs</div>'
        )
        with self.assertRaises(etoiles.EtoilesScraperError):
            etoiles.parse_detail_page(html, post(91, "BROKEN"), today=date(2026, 9, 1))


class EtoilesRestTests(TestCase):
    def _load_responses(self):
        format_terms = response(payload=[
            {"id": 2, "slug": "club", "name": "Club"},
            # Deliberately not the live ID: discovery must resolve the slug.
            {"id": 42, "slug": "concert", "name": "Concert"},
        ])
        status_terms = response(payload=[
            {"id": 11, "slug": "complet", "name": "Complet"},
            {"id": 12, "slug": "annule", "name": "Annulé"},
        ])
        page_headers = {"X-WP-TotalPages": "2", "X-WP-Total": "6"}
        page_one = response(payload=[
            # Genuine genre-less concert: it must not be filtered out.
            # Complet is exceptional ticket state, not an upcoming/concert filter.
            # Keep the scraper's established ticket-state semantics unchanged.
            post(1, "SOULIDIFIED", formats=(42,), genres=(), statuses=(11,)),
            # Club with a genre: genre is not permission to include it.
            post(2, "GENRE CLUB", formats=(2,), genres=(17,)),
            post(3, "PAOLO", formats=(42,), genres=(17,)),
        ], headers=page_headers)
        page_two = response(payload=[
            post(4, "ESTL", formats=(42,), published="2026-04-02T12:00:00"),
            post(5, "ELI", formats=(42,), published="2026-08-19T10:00:00"),
            post(6, "CANCELLED", formats=(42,), statuses=(12,)),
        ], headers=page_headers)
        details = [
            response(text=detail("SOULIDIFIED", "2 oct.", "19:00", ("Ven 2 oct",))),
            response(text=detail("PAOLO", "19 nov.", "20:30", ("Jeu 19 nov",))),
            response(text=detail("ESTL", "2 déc.", "19:30", ("Mer 2 déc",))),
            response(text=detail("ELI", "11 oct.", "19:00", ("Dim 11 oct", "Lun 12 oct"))),
        ]
        return [format_terms, status_terms, page_one, page_two, *details]

    def test_rest_inventory_replaces_unstable_agenda_and_filters_locally(self):
        session = Mock()
        session.get.side_effect = self._load_responses()

        with patch("concert_calendar.scrapers.etoiles.requests.Session", return_value=session):
            events = etoiles.load_events(today=date(2026, 9, 23))

        rows = [(event.date, event.headliner) for event in events]
        self.assertEqual([
            ("2026-10-02", "SOULIDIFIED"),
            ("2026-10-11", "ELI"),
            ("2026-10-12", "ELI"),
            ("2026-11-19", "PAOLO"),
            ("2026-12-02", "ESTL"),
        ], rows)
        self.assertEqual("tickets", next(
            event.ticket_status for event in events if event.headliner == "SOULIDIFIED"
        ))
        urls = [call.args[0] for call in session.get.call_args_list]
        self.assertIn(etoiles.REST_EVENTS_URL, urls)
        self.assertIn(etoiles.REST_FORMATS_URL, urls)
        self.assertNotIn(etoiles.PROGRAMME_URL, urls)
        self.assertNotIn("https://www.etoiles.paris/evenement/genre-club/", urls)
        self.assertNotIn("https://www.etoiles.paris/evenement/cancelled/", urls)
        self.assertEqual(2, urls.count(etoiles.REST_EVENTS_URL))

    def test_incomplete_rest_collection_fails_loudly(self):
        session = Mock()
        session.get.side_effect = [
            response(payload=[post(1, "ONE")], headers={
                "X-WP-TotalPages": "2", "X-WP-Total": "2",
            }),
            response(payload=[], headers={
                "X-WP-TotalPages": "2", "X-WP-Total": "2",
            }),
        ]

        with self.assertRaises(etoiles.EtoilesScraperError):
            etoiles.fetch_rest_posts(session)

    def test_malformed_rest_payload_fails_loudly(self):
        session = Mock()
        session.get.return_value = response(
            payload={"unexpected": "object"},
            headers={"X-WP-TotalPages": "1", "X-WP-Total": "1"},
        )
        with self.assertRaises(etoiles.EtoilesScraperError):
            etoiles.fetch_rest_posts(session)
