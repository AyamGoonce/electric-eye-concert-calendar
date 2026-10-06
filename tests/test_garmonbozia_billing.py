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
                "CORPSE PILE + GIRL OF GLASS."
            ),
            info_blocks=[
                (
                    "Formé en 2021, le quatuor PEELINGFLESH a fait une entrée "
                    "fracassante sur la scène musicale avec son premier album. "
                    "Avec un son mêlant agressivité brute et précision rythmique, "
                    "le groupe développe depuis plusieurs années une approche du "
                    "slam death nourrie par plusieurs sorties et tournées."
                ),
                (
                    "Depuis leur formation en 2020, SNUFFED ON SIGHT a publié de "
                    "nombreux titres, démos, singles et EPs. Le groupe poursuit "
                    "une activité soutenue dans le brutal death metal et le slam, "
                    "avec plusieurs enregistrements et sorties qui ont développé "
                    "son identité musicale au fil des années."
                ),
                (
                    "Né en 2019 à Houston, CORPSE PILE a sorti plusieurs démos, "
                    "singles et EPs avant de signer chez Maggot Stomp. Le groupe "
                    "s'est progressivement imposé dans la nouvelle vague du death "
                    "metal brutal et du slam grâce à plusieurs enregistrements, "
                    "concerts et sorties successives."
                ),
                (
                    "Originaire de Houston, GIRL OF GLASS insuffle une violence "
                    "brute à la scène deathcore moderne. Le groupe développe une "
                    "écriture viscérale ancrée dans le hardcore, le metal et le "
                    "deathcore, avec plusieurs enregistrements et sorties qui ont "
                    "contribué à définir son identité musicale."
                ),
            ],
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
