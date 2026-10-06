import unittest

from concert_calendar.scrapers.garmonbozia import parse_structured_billing


class GarmonboziaBillingTests(unittest.TestCase):

    def test_plus_inside_single_artist_name_is_not_split(self):
        result = parse_structured_billing(
            "FLORENCE + THE MACHINE",
            structured_artists=["Florence + The Machine"],
            info_text=(
                "GARMONBOZIA présente FLORENCE + THE MACHINE. "
                "FLORENCE + THE MACHINE revient à Paris."
            ),
        )

        self.assertIsNone(result)

    def test_moonspell_bill_uses_independent_artist_and_role_evidence(self):
        result = parse_structured_billing(
            "MOONSPELL + IOTUNN + TODOMAL",
            structured_artists=["IOTUNN", "Moonspell"],
            info_text=(
                "GARMONBOZIA présente MOONSPELL + IOTUNN + TODOMAL. "
                "Les icônes portugaises du dark metal, MOONSPELL, "
                "emmèneront FAR FROM GOD en tournée au printemps 2027 "
                "pour leur tournée en tête d'affiche. "
                "Deux invités spéciaux triés sur le volet viennent compléter "
                "l'affiche : IOTUNN, la nouvelle force montante du metal "
                "progressif, et TODOMAL, l'extraordinaire groupe espagnol "
                "de doom metal atmosphérique."
            ),
        )

        self.assertEqual(
            ("MOONSPELL", ["IOTUNN", "TODOMAL"], ["MOONSPELL"]),
            result,
        )

    def test_full_bill_can_split_from_independent_prose_evidence(self):
        result = parse_structured_billing(
            "PEELINGFLESH + SNUFFED ON SIGHT + CORPSE PILE + GIRL OF GLASS",
            structured_artists=[],
            info_text=(
                "GARMONBOZIA présente PEELINGFLESH + SNUFFED ON SIGHT + "
                "CORPSE PILE + GIRL OF GLASS. "
                "Formé en 2021, PEELINGFLESH a fait une entrée fracassante. "
                "Depuis leur formation en 2020, SNUFFED ON SIGHT a publié "
                "plusieurs titres. CORPSE PILE a sorti plusieurs démos. "
                "Originaire de Houston, GIRL OF GLASS insuffle une violence "
                "brute à la scène deathcore moderne."
            ),
        )

        self.assertEqual(
            (
                "PEELINGFLESH",
                None,
                [
                    "PEELINGFLESH",
                    "SNUFFED ON SIGHT",
                    "CORPSE PILE",
                    "GIRL OF GLASS",
                ],
            ),
            result,
        )


if __name__ == "__main__":
    unittest.main()
