import unittest

from latvia_party_sim import DISTRICT_TO_MUNICIPALITIES, aggregate_district_metrics, build_default_territory


class TerritoryTests(unittest.TestCase):
    def test_default_territory_has_42_municipalities_and_5_districts(self) -> None:
        municipalities, districts = build_default_territory()
        self.assertEqual(len(districts), 5)
        self.assertEqual(len(municipalities), 42)
        self.assertEqual(sum(len(v) for v in DISTRICT_TO_MUNICIPALITIES.values()), 42)

    def test_district_aggregation(self) -> None:
        municipalities, districts = build_default_territory()
        party_key = "my_party"
        for m in municipalities.values():
            m.party_local_support[party_key] = 55.0
            m.party_network_strength[party_key] = 40.0

        district = aggregate_district_metrics(districts["VIDZEME"], municipalities, party_key)
        self.assertGreater(district.district_turnout, 0)
        self.assertAlmostEqual(district.district_support[party_key], 55.0)
        self.assertAlmostEqual(district.district_network_score, 40.0)


if __name__ == "__main__":
    unittest.main()
