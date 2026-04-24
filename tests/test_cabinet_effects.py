import unittest

from latvia_party_sim import (
    Archetype,
    CabinetState,
    Leader,
    MinisterAssignment,
    Party,
    PartyResources,
    PartyRole,
    apply_cabinet_operating_effects,
    build_default_territory,
    NationState,
)


class CabinetEffectsTests(unittest.TestCase):
    def _party(self, name: str) -> Party:
        return Party(
            name=name,
            archetype=Archetype(name="system_center"),
            role=PartyRole.GOVERNMENT,
            leader=Leader(name=f"{name} leader"),
            resources=PartyResources(trust=50, agenda_control=50, org_network=40),
        )

    def test_profiled_portfolio_with_strong_holder_performs_better(self) -> None:
        municipalities, districts = build_default_territory()
        nation = NationState(turn=31, stage="mid_mandate", districts=districts, municipalities=municipalities)

        strong_party = self._party("StrongGov")
        weak_party = self._party("WeakGov")

        strong_cabinet = CabinetState(
            exists=True,
            pm_party=strong_party.name,
            assignments=[MinisterAssignment(portfolio_id="finance", party_id=strong_party.name, holder_quality=85)],
            budget_load=40,
        )
        weak_cabinet = CabinetState(
            exists=True,
            pm_party=weak_party.name,
            assignments=[MinisterAssignment(portfolio_id="finance", party_id=weak_party.name, holder_quality=35)],
            budget_load=40,
        )

        apply_cabinet_operating_effects(strong_cabinet, {strong_party.name: strong_party}, nation)
        apply_cabinet_operating_effects(weak_cabinet, {weak_party.name: weak_party}, nation)

        self.assertGreaterEqual(strong_cabinet.cabinet_performance, weak_cabinet.cabinet_performance)

    def test_regional_portfolios_boost_network(self) -> None:
        municipalities, districts = build_default_territory()
        nation = NationState(turn=31, stage="mid_mandate", districts=districts, municipalities=municipalities)
        party = self._party("RegionalGov")
        cabinet = CabinetState(
            exists=True,
            pm_party=party.name,
            assignments=[MinisterAssignment(portfolio_id="regional_development", party_id=party.name, holder_quality=70)],
            budget_load=30,
        )

        baseline = sum(m.party_network_strength.get(party.name, 0.0) for m in municipalities.values())
        apply_cabinet_operating_effects(cabinet, {party.name: party}, nation)
        after = sum(m.party_network_strength.get(party.name, 0.0) for m in municipalities.values())

        self.assertGreater(after, baseline)


if __name__ == "__main__":
    unittest.main()
