import unittest

from bs4 import BeautifulSoup

from concert_calendar.scrapers.grand_rex import _is_cine_concert


def card(info):
    soup = BeautifulSoup(
        f'<div class="row-event"><div class="infos">{info}</div></div>',
        "html.parser",
    )
    return soup.select_one(".row-event")


class GrandRexCineConcertFilterTests(unittest.TestCase):

    def test_french_cine_concert_is_excluded(self):
        self.assertTrue(
            _is_cine_concert(
                card("Projection sur grand écran autour de deux Ciné-concerts")
            )
        )

    def test_unaccented_cine_concert_is_excluded(self):
        self.assertTrue(
            _is_cine_concert(
                card("Un cine-concert exceptionnel avec orchestre")
            )
        )

    def test_hashtag_signal_is_excluded(self):
        self.assertTrue(
            _is_cine_concert(
                card("Orchestre symphonique en direct #cineconcert")
            )
        )

    def test_ordinary_orchestral_concert_is_retained(self):
        self.assertFalse(
            _is_cine_concert(
                card("Concert symphonique avec plus de 50 musiciens")
            )
        )

    def test_normal_concert_is_retained(self):
        self.assertFalse(
            _is_cine_concert(
                card("Le groupe revient au Grand Rex pour un concert exceptionnel")
            )
        )


if __name__ == "__main__":
    unittest.main()
