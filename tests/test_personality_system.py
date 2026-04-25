import unittest

from latvia_party_sim import (
    ARCHETYPE_PRESETS,
    Archetype,
    CabinetState,
    Leader,
    MinisterAssignment,
    Party,
    PartyResources,
    PartyRole,
    PersonalityArchetype,
    RoleType,
    generate_personality,
    apply_cabinet_operating_effects,
    build_default_territory,
    NationState,
)


class PersonalitySystemTests(unittest.TestCase):
    def test_generator_produces_required_fields_and_valid_ranges(self) -> None:
        p = generate_personality(
            uid=1,
            region_affinity="LATGALE",
            role_type=RoleType.MINISTER,
            archetype=PersonalityArchetype.TECHNOCRAT,
            seed=42,
        )
        self.assertTrue(len(p.first_name) > 0)
        self.assertTrue(len(p.last_name) > 0)
        self.assertTrue(len(p.full_name) > 0)
        self.assertGreaterEqual(p.competence, 0)
        self.assertLessEqual(p.competence, 100)
        self.assertIn(p.archetype, ARCHETYPE_PRESETS)

    def test_personality_traits_influence_cabinet_runtime(self) -> None:
        municipalities, districts = build_default_territory()
        nation = NationState(turn=22, stage="mid_mandate", districts=districts, municipalities=municipalities)

        party = Party(
            name="GovParty",
            archetype=Archetype(name="technocrats"),
            role=PartyRole.GOVERNMENT,
            leader=Leader(name="PM"),
            resources=PartyResources(),
        )

        strong = generate_personality(10, "RIGA", RoleType.MINISTER, PersonalityArchetype.TECHNOCRAT, seed=1)
        weak = generate_personality(11, "RIGA", RoleType.MINISTER, PersonalityArchetype.CAREERIST, seed=2)
        weak.competence = 25
        weak.stress_tolerance = 25
        weak.leak_risk = 80

        strong_cabinet = CabinetState(
            exists=True,
            pm_party=party.name,
            assignments=[MinisterAssignment(portfolio_id="finance", party_id=party.name, holder_quality=50, personality_id=strong.id)],
        )
        weak_cabinet = CabinetState(
            exists=True,
            pm_party=party.name,
            assignments=[MinisterAssignment(portfolio_id="finance", party_id=party.name, holder_quality=50, personality_id=weak.id)],
            budget_load=70,
        )

        apply_cabinet_operating_effects(strong_cabinet, {party.name: party}, nation, {strong.id: strong})
        apply_cabinet_operating_effects(weak_cabinet, {party.name: party}, nation, {weak.id: weak})

        self.assertGreaterEqual(strong_cabinet.cabinet_performance, weak_cabinet.cabinet_performance)


if __name__ == "__main__":
    unittest.main()
