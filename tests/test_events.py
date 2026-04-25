import unittest

from latvia_party_sim import (
    Archetype,
    CabinetState,
    EventEngine,
    EventEngineState,
    EventStage,
    EventType,
    Leader,
    MinisterAssignment,
    Party,
    PartyRole,
    ParliamentaryFaction,
    Personality,
    RoleType,
    BackgroundType,
    Gender,
    PersonalityArchetype,
    CareerState,
    build_default_territory,
    NationState,
)


class EventEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        municipalities, districts = build_default_territory()
        self.nation = NationState(turn=1, stage="mid", districts=districts, municipalities=municipalities)
        self.engine = EventEngine()
        self.state = EventEngineState()

    def _personality(self) -> Personality:
        return Personality(
            id="p1",
            first_name="A",
            last_name="B",
            full_name="A B",
            gender=Gender.MALE,
            age=45,
            district_affinity="RIGA",
            municipality_affinity=None,
            background_type=BackgroundType.MEDIA,
            role_type=RoleType.MINISTER,
            archetype=PersonalityArchetype.PUBLIC_LEADER,
            recognition=60,
            trust=50,
            charisma=60,
            competence=50,
            debate=60,
            loyalty=50,
            ambition=60,
            discipline=50,
            regional_power=40,
            coalition_acceptability=50,
            corruption_affinity=50,
            leak_risk=60,
            stress_tolerance=30,
            betrayal_risk=55,
            media_hunger=70,
            ideological_rigidity=40,
            scandal_resilience=35,
            growth_potential=60,
            burnout=70,
            scandal_load=65,
            career_state=CareerState.STABLE,
            party_fit=50,
            faction_alignment="core",
        )

    def test_endogenous_event_needs_trigger(self) -> None:
        cabinet = CabinetState(exists=True, pm_party="Gov", budget_load=20)
        parties = [Party("Gov", Archetype("a"), PartyRole.GOVERNMENT, Leader("L"), faction=ParliamentaryFaction(seats=30, in_coalition=True))]
        self.engine.generate_latent_tensions(1, self.nation, cabinet, parties, {}, self.state)
        self.engine.emit_signals(1, self.state)
        self.assertFalse(any(e.event_type == EventType.GOVERNANCE_CRISIS and e.current_stage != EventStage.LATENT for e in self.state.active_events))

    def test_buildup_signal_escalation_pipeline(self) -> None:
        cabinet = CabinetState(exists=True, pm_party="Gov", budget_load=90, corruption_load=80)
        parties = [Party("Gov", Archetype("a"), PartyRole.GOVERNMENT, Leader("L"), faction=ParliamentaryFaction(seats=30, in_coalition=True))]
        self.engine.generate_latent_tensions(1, self.nation, cabinet, parties, {}, self.state)
        self.engine.emit_signals(1, self.state)
        self.assertTrue(any(e.current_stage == EventStage.SIGNAL for e in self.state.active_events))
        self.engine.advance_active_events(2, self.state, parties, self.nation, cabinet, {"Gov": ["attack"]})
        self.engine.advance_active_events(3, self.state, parties, self.nation, cabinet, {"Gov": ["attack"]})
        self.assertTrue(any(e.current_stage in {EventStage.ESCALATION, EventStage.RESOLUTION, EventStage.MEMORY} for e in self.state.active_events))

    def test_resolution_creates_memory(self) -> None:
        cabinet = CabinetState(exists=True, pm_party="Gov", budget_load=95)
        parties = [Party("Gov", Archetype("a"), PartyRole.GOVERNMENT, Leader("L"), faction=ParliamentaryFaction(seats=30, in_coalition=True))]
        self.engine.generate_latent_tensions(1, self.nation, cabinet, parties, {}, self.state)
        self.engine.emit_signals(1, self.state)
        for _ in range(3):
            self.engine.advance_active_events(3, self.state, parties, self.nation, cabinet, {"Gov": ["localize", "crisis"]})
        self.assertGreater(len(self.state.event_memory), 0)

    def test_same_event_affects_modes_differently(self) -> None:
        cabinet = CabinetState(exists=True, pm_party="Gov", budget_load=90)
        gov = Party("Gov", Archetype("a"), PartyRole.GOVERNMENT, Leader("L"), faction=ParliamentaryFaction(seats=30, in_coalition=True))
        opp = Party("Opp", Archetype("a"), PartyRole.PARLIAMENTARY_OPPOSITION, Leader("O"), faction=ParliamentaryFaction(seats=20, in_coalition=False))
        parties = [gov, opp]
        self.engine.generate_latent_tensions(1, self.nation, cabinet, parties, {}, self.state)
        self.engine.emit_signals(1, self.state)
        self.engine.advance_active_events(2, self.state, parties, self.nation, cabinet, {"Opp": ["attack"]})
        self.engine.advance_active_events(3, self.state, parties, self.nation, cabinet, {"Opp": ["attack"]})
        self.assertNotEqual(gov.resources.trust, opp.resources.trust)

    def test_territorial_footprint_modifies_territory(self) -> None:
        cabinet = CabinetState(exists=True, pm_party="Gov", budget_load=90)
        parties = [Party("Gov", Archetype("a"), PartyRole.GOVERNMENT, Leader("L"), faction=ParliamentaryFaction(seats=30, in_coalition=True))]
        first_district = next(iter(self.nation.districts.values()))
        before = first_district.district_protest
        self.engine.generate_latent_tensions(1, self.nation, cabinet, parties, {}, self.state)
        self.engine.emit_signals(1, self.state)
        self.engine.advance_active_events(2, self.state, parties, self.nation, cabinet, {"Gov": ["attack"]})
        self.engine.advance_active_events(3, self.state, parties, self.nation, cabinet, {"Gov": ["attack"]})
        self.assertNotEqual(before, first_district.district_protest)

    def test_positive_events_spawn(self) -> None:
        cabinet = CabinetState(exists=True, pm_party="Gov", budget_load=20, cabinet_performance=80)
        parties = [Party("Gov", Archetype("a"), PartyRole.GOVERNMENT, Leader("L"), faction=ParliamentaryFaction(seats=30, in_coalition=True))]
        parties[0].resources.trust = 70
        self.engine.generate_latent_tensions(1, self.nation, cabinet, parties, {}, self.state)
        self.assertTrue(any(e.event_type == EventType.POSITIVE_WINDOW for e in self.state.active_events))

    def test_damage_control_changes_resolution(self) -> None:
        cabinet = CabinetState(exists=True, pm_party="Gov", budget_load=95)
        parties = [Party("Gov", Archetype("a"), PartyRole.GOVERNMENT, Leader("L"), faction=ParliamentaryFaction(seats=30, in_coalition=True))]
        self.engine.generate_latent_tensions(1, self.nation, cabinet, parties, {}, self.state)
        self.engine.emit_signals(1, self.state)
        start = parties[0].resources.trust
        self.engine.advance_active_events(2, self.state, parties, self.nation, cabinet, {"Gov": ["attack"]})
        trust_no_control = parties[0].resources.trust
        parties[0].resources.trust = start
        s2 = EventEngineState(active_events=[e for e in self.state.active_events], unresolved_tensions=dict(self.state.unresolved_tensions))
        self.engine.advance_active_events(2, s2, parties, self.nation, cabinet, {"Gov": ["crisis", "localize"]})
        self.assertGreaterEqual(parties[0].resources.trust, trust_no_control)

    def test_scandal_pipeline_not_one_shot(self) -> None:
        cabinet = CabinetState(exists=True, pm_party="Gov", corruption_load=85, corruption_memory=75)
        parties = [Party("Gov", Archetype("a"), PartyRole.GOVERNMENT, Leader("L"), faction=ParliamentaryFaction(seats=30, in_coalition=True))]
        self.engine.generate_latent_tensions(1, self.nation, cabinet, parties, {"p1": self._personality()}, self.state)
        scandal = next(e for e in self.state.active_events if e.event_type == EventType.CORRUPTION_SCANDAL)
        self.assertEqual(scandal.current_stage, EventStage.LATENT)
        self.engine.emit_signals(1, self.state)
        self.assertIn(scandal.current_stage, {EventStage.SIGNAL, EventStage.ESCALATION, EventStage.RESOLUTION, EventStage.MEMORY})


if __name__ == "__main__":
    unittest.main()
