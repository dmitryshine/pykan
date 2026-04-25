import unittest

from latvia_party_sim import (
    ActionEffect,
    Archetype,
    CabinetState,
    Leader,
    MandateTickEngine,
    MandateTickInput,
    MinisterAssignment,
    MODE_PROFILES,
    Party,
    PartyMode,
    PartyRole,
    ParliamentaryFaction,
    StageContext,
    TurnAction,
    NationState,
    build_default_territory,
    determine_party_mode,
)


class PartyModeTests(unittest.TestCase):
    def test_mode_assignment(self) -> None:
        cabinet = CabinetState(exists=True, pm_party="Lead", assignments=[MinisterAssignment(portfolio_id="finance", party_id="Junior", holder_quality=70)])
        lead = Party("Lead", Archetype("a"), PartyRole.GOVERNMENT, Leader("L"), faction=ParliamentaryFaction(seats=30, in_coalition=True))
        junior = Party("Junior", Archetype("a"), PartyRole.GOVERNMENT, Leader("J"), faction=ParliamentaryFaction(seats=12, in_coalition=True))
        opp = Party("Opp", Archetype("a"), PartyRole.PARLIAMENTARY_OPPOSITION, Leader("O"), faction=ParliamentaryFaction(seats=20, in_coalition=False))
        extra = Party("Extra", Archetype("a"), PartyRole.EXTRA_PARLIAMENTARY, Leader("E"), faction=ParliamentaryFaction(seats=0))

        self.assertEqual(determine_party_mode(lead, cabinet), PartyMode.GOVERNMENT_LEAD)
        self.assertEqual(determine_party_mode(junior, cabinet), PartyMode.GOVERNMENT_JUNIOR)
        self.assertEqual(determine_party_mode(opp, cabinet), PartyMode.PARLIAMENTARY_OPPOSITION)
        self.assertEqual(determine_party_mode(extra, cabinet), PartyMode.EXTRA_PARLIAMENTARY)

    def test_mode_profiles_differ_on_priority(self) -> None:
        self.assertGreater(
            MODE_PROFILES[PartyMode.GOVERNMENT_JUNIOR].resource_weights["distinctiveness"],
            MODE_PROFILES[PartyMode.GOVERNMENT_LEAD].resource_weights["distinctiveness"],
        )
        self.assertGreater(
            MODE_PROFILES[PartyMode.EXTRA_PARLIAMENTARY].entry_pressure,
            MODE_PROFILES[PartyMode.PARLIAMENTARY_OPPOSITION].entry_pressure,
        )

    def test_actions_and_outcome_depend_on_mode(self) -> None:
        municipalities, districts = build_default_territory()
        nation = NationState(turn=1, stage="mid", districts=districts, municipalities=municipalities)
        cabinet = CabinetState(exists=True, pm_party="Lead")

        lead = Party("Lead", Archetype("a"), PartyRole.GOVERNMENT, Leader("L"), faction=ParliamentaryFaction(seats=25, in_coalition=True))
        extra = Party("Extra", Archetype("a"), PartyRole.EXTRA_PARLIAMENTARY, Leader("E"), faction=ParliamentaryFaction(seats=0))

        budget_action = TurnAction("budget_frame", ActionEffect(trust=1.0), tags=("budget",))
        entry_action = TurnAction("entry_push", ActionEffect(org_network=1.0), tags=("entry",))

        tick_input = MandateTickInput(
            nation_state=nation,
            parties=[lead, extra],
            context=StageContext(turn=1, stage="mid_mandate"),
            planned_actions={"Lead": [budget_action, entry_action], "Extra": [budget_action, entry_action]},
            cabinet=cabinet,
        )
        MandateTickEngine().run_tick(tick_input)

        # Lead keeps budget tools; extra-parliamentary keeps entry tools.
        self.assertEqual(lead.mode, PartyMode.GOVERNMENT_LEAD)
        self.assertEqual(extra.mode, PartyMode.EXTRA_PARLIAMENTARY)
        self.assertGreater(extra.resources.org_network, lead.resources.org_network)
        # Same turn gets mode-specific evaluation.
        self.assertNotEqual(lead.memory_markers["mode_success_score"], extra.memory_markers["mode_success_score"])


if __name__ == "__main__":
    unittest.main()
