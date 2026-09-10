import unittest

from scripts.research_blank_genres import public_category


class GenreResearchHelperTests(unittest.TestCase):
    def test_rap_does_not_match_inside_biographical(self):
        self.assertIsNone(
            public_category(["biographical film", "drama film"])
        )

    def test_real_rap_still_maps(self):
        self.assertEqual(
            "Hip-hop / Rap",
            public_category(["French hip-hop", "gangsta rap"])
        )

    def test_cross_bucket_hyphenated_hiphop_is_ambiguous(self):
        self.assertIsNone(
            public_category(["electronic music", "hip-hop", "independent music"])
        )

    def test_current_chanson_public_label(self):
        self.assertEqual(
            "Chanson Française / Variétés",
            public_category(["chanson"])
        )

    def test_current_comedy_public_label(self):
        self.assertEqual(
            "Comedy / Spoken Word",
            public_category(["comedy"])
        )


if __name__ == "__main__":
    unittest.main()
