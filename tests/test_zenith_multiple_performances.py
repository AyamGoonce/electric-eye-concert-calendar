from datetime import date
from unittest import TestCase, mock

from bs4 import BeautifulSoup

from concert_calendar.scrapers import zenith_paris


DETAIL = """
<section>
  <h2>infos pratiques</h2>
  <div>En vente</div><div>Jeudi 04 mars 2027</div>
  <div>En vente</div><div>Vendredi 05 mars 2027</div>
  <div>Complet</div><div>Samedi 06 mars 2027</div>
  <p>En tournée ailleurs le 23 octobre 2027.</p>
  <h2>Consignes</h2>
</section>
<section><h2>Vous aimeriez aussi</h2>
  <p>En vente Dimanche 07 mars 2027</p>
</section>
"""


class ZenithMultiplePerformanceTests(TestCase):
    def test_full_month_names_and_abbreviations(self):
        self.assertEqual(date(2027, 10, 23), zenith_paris.parse_date("23 octobre 2027"))
        self.assertEqual(date(2027, 11, 23), zenith_paris.parse_date("23 nov. 2027"))
        self.assertEqual(date(2027, 4, 23), zenith_paris.parse_date("23 avril 2027"))

    @mock.patch.object(zenith_paris, "date", wraps=date)
    def test_only_explicit_performances_before_recommendations(self, mocked_date):
        mocked_date.today.return_value = date(2026, 11, 27)
        result = zenith_paris.parse_performance_dates(BeautifulSoup(DETAIL, "html.parser"))
        self.assertEqual(
            [date(2027, 3, 4), date(2027, 3, 5), date(2027, 3, 6)],
            result,
        )

    @mock.patch.object(zenith_paris, "date", wraps=date)
    @mock.patch.object(zenith_paris.requests, "get")
    def test_homepage_range_expands_using_show_page(self, get, mocked_date):
        mocked_date.today.return_value = date(2026, 11, 27)
        homepage = """
        <div class="swiper-home-current-event"><div class="swiper-slide">
          <div class="swiper-caption__name">Test Artist</div>
          <div class="swiper-caption__date">à partir du Jeudi 04 mars 2027</div>
          <a href="/shows/test-1">Infos & Réservation</a>
        </div></div>
        """
        def response(text):
            result = mock.Mock()
            result.text = text
            return result
        get.side_effect = [response(homepage), response(DETAIL)]
        events = zenith_paris.load_primary_events()
        self.assertEqual(
            ["2027-03-04", "2027-03-05", "2027-03-06"],
            [event.date for event in events],
        )
        self.assertEqual(2, get.call_count)
