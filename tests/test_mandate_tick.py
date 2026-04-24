import unittest

from latvia_party_sim import (
    Archetype,
    CabinetState,
    Leader,
    MandateTickEngine,
    MandateTickInput,
    Party,
    PartyResources,
    PartyRole,
    PendingEvent,
    StageContext,
    MinisterAssignment,
    TurnAction,
    ActionEffect,
    build_default_territory,
    NationState,
)


class MandateTickTests(unittest.TestCase):
    def test_standard_tick_phase_order_and_outputs(self) -> None:
        municipalities, districts = build_default_territory()
        nation = NationState(turn=37, stage="mid_mandate", districts=districts, municipalities=municipalities)
        nation.national_theme_pressure = {"protest": 40.0}

        gov = Party(
            name="GovParty",
            archetype=Archetype(name="technocrats"),
            role=PartyRole.GOVERNMENT,
            leader=Leader(name="PM"),
            resources=PartyResources(coalition_acceptability=60, discipline=55, toxicity=20),
        )

        for m in municipalities.values():
            m.party_local_support[gov.name] = 52.0

        action = TurnAction(
            key="regional_work",
            effect=ActionEffect(org_network=1.0),
            target_district_id="LATGALE",
        )

        tick_input = MandateTickInput(
            nation_state=nation,
            parties=[gov],
            context=StageContext(turn=37, stage="mid_mandate", event_shock=0.5),
            planned_actions={gov.name: [action]},
            pending_events=[PendingEvent(key="transport_issue", district_id="LATGALE", protest_delta=2.0)],
            cabinet=CabinetState(exists=True, pm_party=gov.name, assignments=[MinisterAssignment(portfolio_id="finance", party_id=gov.name, holder_quality=75)]),
        )

        result = MandateTickEngine().run_tick(tick_input)

        self.assertEqual(len(result.phase_log), 10)
        self.assertEqual(result.phase_log[0], "phase_1_national_context")
        self.assertEqual(result.phase_log[-1], "phase_10_signals")
        self.assertIn("national_rating", gov.memory_markers)
        self.assertIn("coalition_stability", gov.memory_markers)


if __name__ == "__main__":
    unittest.main()
