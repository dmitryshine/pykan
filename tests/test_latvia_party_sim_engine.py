import unittest

from latvia_party_sim import (
    ActionEffect,
    Archetype,
    Leader,
    Party,
    PartyResources,
    PartyRole,
    PartyWallets,
    SimulationEngine,
    StageContext,
    TurnAction,
)


class SimulationEngineTests(unittest.TestCase):
    def test_step_turn_applies_actions_and_updates_core_outputs(self) -> None:
        engine = SimulationEngine()
        party = Party(
            name="Technocrats",
            archetype=Archetype(name="technocrats"),
            role=PartyRole.GOVERNMENT,
            leader=Leader(name="A. Prime"),
            resources=PartyResources(trust=65, agenda_control=60, org_network=58, cadres=57),
            wallets=PartyWallets(operations=100.0, campaign=20.0),
        )
        action = TurnAction(
            key="push_reform",
            effect=ActionEffect(
                trust=3.0,
                agenda_control=2.0,
                brand_wear=1.0,
                operations_wallet=-5.0,
            ),
        )
        context = StageContext(turn=9, stage="early_mandate", event_shock=1.0, coalition_shock=1.0, rng_seed=123)

        engine.step_turn(context, {party.name: [action]}, [party])

        self.assertGreater(party.support_trend, 0)
        self.assertEqual(party.memory_markers["last_turn"], 9.0)
        self.assertGreater(party.resources.brand_wear, 1.0)
        self.assertIn("coalition_stability", party.memory_markers)
        self.assertEqual(party.wallets.operations, 95.0)


if __name__ == "__main__":
    unittest.main()
