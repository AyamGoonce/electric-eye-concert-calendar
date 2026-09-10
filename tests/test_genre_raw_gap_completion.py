import unittest

from concert_calendar.genres import map_raw_genres


class GenreRawGapCompletionTests(unittest.TestCase):
    def test_safe_single_bucket_source_labels(self):
        cases = {
            "psych-rock": ["Rock / Indie / Punk"],
            "Afrobeats, Afropop, Rumba": ["World / Latin"],
            "Rap, Trap, Hip Hop": ["Hip-hop / Rap"],
            "Concert / Hip hop": ["Hip-hop / Rap"],
            "French pop - Indie pop": ["Pop"],
            "Musique orientale": ["World / Latin"],
            "Musique celtique": ["World / Latin"],
            "Zouk": ["World / Latin"],
        }

        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(expected, map_raw_genres(raw))

    def test_ambiguous_or_non_genre_labels_remain_unresolved(self):
        for raw in (
            "POP ROCK FOLK",
            "Musique de Films",
            "MUSIQUE CLASSIQUE",
            "Classique",
            "Néo Classique",
            "Tribute",
            "Événement",
            "Danse",
            "Conférence",
            "Ciné concert",
            "Violon",
        ):
            with self.subTest(raw=raw):
                self.assertEqual([], map_raw_genres(raw))


if __name__ == "__main__":
    unittest.main()
