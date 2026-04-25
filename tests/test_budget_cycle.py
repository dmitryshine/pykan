import unittest

from latvia_party_sim import (
    Archetype,
    BudgetFrame,
    CabinetState,
    Leader,
    MinisterAssignment,
    Party,
    PartyResources,
    PartyRole,
    build_default_territory,
    is_budget_turn,
    run_budget_cycle,
    GovernmentEconomyState,
)


class BudgetCycleTests(unittest.TestCase):
    def test_budget_turn_trigger(self) -> None:
        self.assertTrue(is_budget_turn(12))
        self.assertFalse(is_budget_turn(11))

    def test_budget_cycle_outputs_maps_and_deltas(self) -> None:
        municipalities, districts = build_default_territory()
        gov = Party(
            name="Gov",
            archetype=Archetype(name="technocrats"),
            role=PartyRole.GOVERNMENT,
            leader=Leader(name="PM"),
            resources=PartyResources(trust=60),
        )
        cabinet = CabinetState(
            exists=True,
            pm_party=gov.name,
            assignments=[MinisterAssignment(portfolio_id="finance", party_id=gov.name, holder_quality=70)],
        )
        econ = GovernmentEconomyState()

        out = run_budget_cycle(12, BudgetFrame.PATRONAGE, cabinet, econ, [gov], districts)

        self.assertTrue(len(out.ministerial_strain_map) >= 1)
        self.assertEqual(len(out.district_budget_impact_map), len(districts))
        self.assertNotEqual(out.future_budget_pressure_delta, 0)


if __name__ == "__main__":
    unittest.main()
