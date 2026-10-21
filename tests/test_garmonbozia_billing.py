import unittest

from bs4 import BeautifulSoup
from concert_calendar.scrapers.garmonbozia import parse_card, parse_structured_billing
from concert_calendar.artist_billings import resolve_artist_billings
from concert_calendar.models import ConcertEvent



class GarmonboziaBillingTests(unittest.TestCase):

    def test_reviewed_garmonbozia_billings_survive_without_source_biographies(self):
        cases = [
            ("2027-02-02", "The Black Dahlia Murder + Fuming Mouth",
             ["The Black Dahlia Murder", "Fuming Mouth"], None),
            ("2027-03-11", "King Buffalo + Spirit Mother",
             ["King Buffalo", "Spirit Mother"], None),
            ("2027-02-14", "Shred Fest - Obscura + Pestilence + Cryptic Shift + Thus + Dvrk",
             ["Obscura", "Pestilence", "Cryptic Shift", "Thus", "Dvrk"], "Shred Fest"),
        ]
        events = [ConcertEvent(date=day, headliner=billing, venue="Petit Bain",
                               city="Paris", department="75",
                               source_names=["Garmonbozia"], performers=None)
                  for day, billing, _, _ in cases]
        resolve_artist_billings(events, identity_catalog={})
        for event, (_, billing, artists, festival) in zip(events, cases):
            with self.subTest(billing=billing):
                self.assertEqual(artists[0], event.headliner)
                self.assertEqual(artists, event.performers)
                self.assertEqual(artists[1:], event.co_headliners)
                self.assertEqual(festival, event.event_title)
                self.assertIn(billing, event.identity_aliases)
        # A later conservative re-pass must not undo an already resolved bill.
        resolve_artist_billings(events, identity_catalog={}, allow_inference=False)
        for event, (_, _, artists, _) in zip(events, cases):
            self.assertEqual(artists, event.performers)


    def test_triple_thrash_keeps_updated_date_and_artist_roles(self):
        html = """
        <dl><dd><span class="evenementNom">Evil Invaders &amp; Exhorder &amp; Heathen</span></dd>
        <time itemprop="startDate" datetime="2027-03-01"></time>
        <span class="evenementSalleNom">Petit Bain</span>
        <span class="evenementSalleVille">Paris</span>
        <a class="evenementReserver" href="https://web.digitick.com/evil-invaders-exhorder-heathen-concert-dark-metal-css5-garmonbozia-pg51-ei1131957.html"></a>
        </dl>
        """
        event = parse_card(BeautifulSoup(html, "html.parser").select_one("dl"))
        self.assertIsNotNone(event)
        self.assertEqual("2027-03-01", event.date)
        self.assertEqual("Evil Invaders", event.headliner)
        self.assertEqual(["Exhorder", "Heathen"], event.co_headliners)
        self.assertEqual(["Warfield"], event.openers)
        self.assertEqual(["Evil Invaders", "Exhorder", "Heathen"], event.performers)


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
