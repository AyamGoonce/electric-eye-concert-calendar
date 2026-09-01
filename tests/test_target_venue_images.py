import unittest
from types import SimpleNamespace
from unittest.mock import patch

from bs4 import BeautifulSoup

from concert_calendar.event_images import background_image_url, element_image_url
from concert_calendar.deduplication import deduplicate_events, merge_events
from concert_calendar.models import ConcertEvent
from concert_calendar.scraper_loader import discover_scrapers
from concert_calendar.sources import enrich_official_venue_images
from concert_calendar.venues import normalize_event_venue
from concert_calendar.scrapers.boule_noire import parse_card as parse_boule
from concert_calendar.scrapers.elysee_montmartre import parse_card as parse_elysee
from concert_calendar.scrapers.gaite_lyrique import parse_card as parse_gaite
from concert_calendar.scrapers.hasard_ludique import parse_card as parse_hasard
from concert_calendar.scrapers.maroquinerie import parse_card as parse_maroquinerie
from concert_calendar.scrapers.new_morning import parse_card as parse_new_morning
from concert_calendar.scrapers.petit_bain import parse_card as parse_petit_bain
from concert_calendar.scrapers.salle_pleyel import parse_card as parse_pleyel
from concert_calendar.scrapers.trabendo import parse_card as parse_trabendo
from concert_calendar.scrapers.zenith_paris import parse_card as parse_zenith


def soup(value):
    return BeautifulSoup(value, "html.parser")


class TargetVenueImageTests(unittest.TestCase):
    def test_new_venue_sources_are_production_calendar_sources(self):
        names = {module.__name__ for module in discover_scrapers()}
        self.assertTrue({
            "concert_calendar.scrapers.elysee_montmartre",
            "concert_calendar.scrapers.gaite_lyrique",
            "concert_calendar.scrapers.salle_pleyel",
            "concert_calendar.scrapers.trabendo",
            "concert_calendar.scrapers.zenith_paris",
        }.issubset(names))

    def test_venue_enrichment_is_exact_and_never_overwrites_an_image(self):
        exact = ConcertEvent(date="2027-09-11", headliner="Artist", venue="Le Trabendo", city="Paris", department="75")
        different = ConcertEvent(date="2027-09-12", headliner="Artist", venue="Le Trabendo", city="Paris", department="75")
        existing = ConcertEvent(date="2027-09-11", headliner="Artist", venue="Le Trabendo", city="Paris", department="75", image_url="https://promoter.example/show.jpg", image_source="Promoter")
        candidate = ConcertEvent(date="2027-09-11", headliner="Artist", venue="Le Trabendo", city="Paris", department="75", image_url="https://trabendo.example/show.jpg", image_source="Le Trabendo")
        module = SimpleNamespace(load_events=lambda: [candidate])
        with (
            patch("concert_calendar.sources.IMAGE_ENRICHMENT_MODULES", ("test.images",)),
            patch("importlib.import_module", return_value=module),
        ):
            enrich_official_venue_images([exact, different, existing])
        self.assertEqual("https://trabendo.example/show.jpg", exact.image_url)
        self.assertIsNone(different.image_url)
        self.assertEqual("https://promoter.example/show.jpg", existing.image_url)

    def test_target_venue_card_image_remains_below_existing_official_image(self):
        venue = ConcertEvent(date="2027-09-11", headliner="Artist", venue="La Maroquinerie", city="Paris", department="75", image_url="https://venue.example/show.jpg", image_source="La Maroquinerie")
        promoter = ConcertEvent(date="2027-09-11", headliner="Artist", venue="La Maroquinerie", city="Paris", department="75", image_url="https://promoter.example/show.jpg", image_source="Live Nation")
        merged = merge_events(venue, promoter)
        self.assertEqual("https://promoter.example/show.jpg", merged.image_url)
        self.assertEqual("Live Nation", merged.image_source)

    def test_image_element_prefers_largest_safe_srcset_candidate(self):
        image = soup('<img src="/small.jpg" srcset="/small.jpg 300w, /large.jpg 900w" width="900" height="600">').img
        self.assertEqual(
            "https://venue.example/large.jpg",
            element_image_url(image, base_url="https://venue.example/agenda/"),
        )

    def test_inline_background_image_is_safe_and_absolute(self):
        self.assertEqual(
            "https://venue.example/event.jpg",
            background_image_url("background-image:url('/event.jpg')", base_url="https://venue.example/"),
        )

    def test_new_morning_card_image(self):
        card = soup('''<div class="bg-white"><a class="d-block" href="20270911-1-show.html"><img class="img-fluid" src="photos/show.jpg"></a><h3>Artist</h3></div>''').a
        event = parse_new_morning(card)
        self.assertEqual("https://www.newmorning.com/photos/show.jpg", event.image_url)

    def test_maroquinerie_card_image(self):
        card = soup('''<li class="event"><a href="/fr/agenda/view/1/show/"><div class="thumbnail"><h2>Artist</h2><img src="/files/show.png"></div></a><h3 class="date">11 septembre</h3><div class="booking"><a href="https://tickets.example/show">Réserver</a></div></li>''').li
        event = parse_maroquinerie(card, 2027)
        self.assertEqual("https://www.lamaroquinerie.fr/files/show.png", event.image_url)

    def test_hasard_ludique_background_image(self):
        card = soup('''<a class="event_card concert" href="/concert/show"><div class="image" style="background-image:url('https://images.example/show.jpg')"></div><div class="content"><div><span>#rock</span><h3>Artist</h3><strong>11.09.27</strong></div></div></a>''')
        self.assertEqual("https://images.example/show.jpg", parse_hasard(card).image_url)

    def test_petit_bain_card_image_ignores_badge(self):
        card = soup('''<div class="unevt categorie-concerts"><a href="https://petitbain.org/evenement/show/"><div id="imgunevt"><div id="absr"><img src="https://petitbain.org/logo.svg"></div><div id="contimgunevt"><img src="https://petitbain.org/show.jpg" width="500" height="500"></div></div><div id="ladatevtmin">11 septembre 2027</div><div id="nomsoiree">Artist</div></a></div>''').div
        self.assertEqual("https://petitbain.org/show.jpg", parse_petit_bain(card).image_url)

    def test_boule_noire_card_image(self):
        card = soup('''<div class="elementor-post__card"><a class="elementor-post__thumbnail__link"><div class="elementor-post__thumbnail"><img src="https://laboule-noire.fr/show.jpg" width="800" height="600"></div></a><div class="elementor-post__badge"></div><h2 class="elementor-post__title"><a href="https://laboule-noire.fr/show/">Artist</a></h2><div class="elementor-post__excerpt">11 SEPTEMBRE 2027 – 20H</div></div>''').div
        self.assertEqual("https://laboule-noire.fr/show.jpg", parse_boule(card).image_url)

    def test_trabendo_concert_card_image_and_club_rejection(self):
        card = soup('''<a class="event" href="/programmation/artist/"><picture><img data-src="https://www.letrabendo.net/show.jpg"></picture><div class="pastille concert">Concert</div><h2 class="date-event">11 ― septembre 2027</h2><h5 class="style">rock</h5><h3 class="name-event">Artist</h3></a>''').a
        self.assertEqual("https://www.letrabendo.net/show.jpg", parse_trabendo(card).image_url)
        card.select_one(".pastille")["class"] = ["pastille", "club"]
        self.assertIsNone(parse_trabendo(card))

    def test_gaite_music_card_uses_exact_date_group_and_image(self):
        card = soup('''<li class="events-date"><h2 class="events-date-title">Vendredi 11 septembre 2027</h2><article class="event"><h2 class="event-title"><a href="https://www.gaite-lyrique.net/show">Artist</a></h2><ul class="event-categories"><li><a>Musique</a></li></ul><div class="media"><img src="https://images.gaite.example/show.jpg" width="1280" height="720"></div></article></li>''').article
        self.assertEqual("https://images.gaite.example/show.jpg", parse_gaite(card).image_url)

    def test_zenith_carousel_image(self):
        card = soup('''<div class="swiper-slide"><img src="https://le-zenith.com/show.jpg"><div class="swiper-caption__name">Artist</div><div class="swiper-caption__date">Vendredi 11 sept. 2027</div><a href="/shows/Artist-1">Infos</a></div>''').div
        self.assertEqual("https://le-zenith.com/show.jpg", parse_zenith(card).image_url)

    def test_pleyel_card_expands_two_performances_with_one_card_image(self):
        card = soup('''<div class="eventPage__nextEvents-event"><div class="eventPage__nextEvents-eventImageHolder"><img src="https://www.sallepleyel.com/show.jpg"></div><a class="eventPage__nextEvents-eventTitle" href="https://www.sallepleyel.com/show/">Artist</a><div class="eventPage__nextEvents-event-category">Rock</div><div class="eventPage__nextEvents-event-startDate">11 &amp; 12 septembre 2027</div></div>''').div
        events = parse_pleyel(card)
        self.assertEqual(["2027-09-11", "2027-09-12"], [event.date for event in events])
        self.assertTrue(all(event.image_url == "https://www.sallepleyel.com/show.jpg" for event in events))

    def test_elysee_card_image(self):
        card = soup('''<div class="bloc_extrait evenement"><a class="link" href="https://www.elyseemontmartre.com/show/" title="Artist"></a><div class="date">vendredi 11 septembre 2027</div><div class="visuel"><img src="https://www.elyseemontmartre.com/show.jpg" width="700" height="700"></div></div>''').div
        self.assertEqual("https://www.elyseemontmartre.com/show.jpg", parse_elysee(card)[0].image_url)

    def test_elysee_dresden_dolls_regression(self):
        card = soup('''<div class="bloc_extrait evenement"><a class="link" href="https://www.elyseemontmartre.com/fr/programmation/the-dresden-dolls/" title="THE DRESDEN DOLLS"></a><div class="date">mardi 8 septembre 2026</div><div class="visuel"><img src="https://www.elyseemontmartre.com/dresden-dolls.jpg"></div></div>''').div
        event = parse_elysee(card)[0]
        self.assertEqual("2026-09-08", event.date)
        self.assertEqual("THE DRESDEN DOLLS", event.headliner)
        self.assertEqual("Élysée Montmartre", event.venue)

    def test_dresden_dolls_venue_and_promoter_records_merge(self):
        venue = ConcertEvent(
            date="2026-09-08",
            headliner="THE DRESDEN DOLLS",
            venue="Élysée Montmartre",
            city="Paris",
            department="75",
            ticket_url="https://www.elyseemontmartre.com/show/",
            image_url="https://www.elyseemontmartre.com/show.jpg",
            image_source="Élysée Montmartre",
            source_names=["Élysée Montmartre"],
        )
        promoter = ConcertEvent(
            date="2026-09-08",
            headliner="The Dresden Dolls",
            venue="L'ÉLYSÉE-MONTMARTRE",
            city="Paris",
            department="75",
            promoters=["Alias Production"],
            ticket_url="https://tickets.example/dresden-dolls",
            source_names=["Alias Production"],
        )
        merged = deduplicate_events([
            normalize_event_venue(venue),
            normalize_event_venue(promoter),
        ])
        self.assertEqual(1, len(merged))
        self.assertEqual(["Alias Production"], merged[0].promoters)
        self.assertEqual(
            {"Élysée Montmartre", "Alias Production"},
            set(merged[0].source_names),
        )


if __name__ == "__main__":
    unittest.main()
