import unittest

from latvia_party_sim import (
    Archetype,
    CabinetState,
    GovernmentEconomyState,
    Leader,
    NationState,
    Party,
    PartyEconomyState,
    PartyResources,
    PartyRole,
    build_default_territory,
    resolve_government_budget_pressure,
    update_party_economy,
)


class EconomyTests(unittest.TestCase):
    def test_party_economy_updates_wallets(self) -> None:
        party = Party(
            name="P1",
            archetype=Archetype(name="technocrats"),
            role=PartyRole.PARLIAMENTARY_OPPOSITION,
            leader=Leader(name="L"),
            resources=PartyResources(),
        )
        econ = PartyEconomyState(state_funding=10, private_funding_flow=5, fundraising_capacity=50, network_upkeep_cost=4)
        before = party.wallets.operations
        update_party_economy(party, econ)
        self.assertGreater(party.wallets.operations, before)

    def test_government_budget_pressure_generates_strain(self) -> None:
        municipalities, districts = build_default_territory()
        nation = NationState(turn=40, stage="late_mandate", districts=districts, municipalities=municipalities)
        party = Party(
            name="Gov",
            archetype=Archetype(name="technocrats"),
            role=PartyRole.GOVERNMENT,
            leader=Leader(name="PM"),
            resources=PartyResources(trust=70),
        )
        cabinet = CabinetState(exists=True, pm_party=party.name)
        gov_econ = GovernmentEconomyState(budget_stress=60, fiscal_room=30, pre_election_spending_temptation=70)

        signals = resolve_government_budget_pressure(cabinet, gov_econ, [party], nation)
        self.assertGreater(signals.economic_strain, 0)
        self.assertGreater(signals.coalition_budget_penalty, 0)


if __name__ == "__main__":
    unittest.main()
