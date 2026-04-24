import unittest

from latvia_party_sim import (
    Archetype,
    CoalitionEngine,
    CoalitionStabilityInputs,
    Leader,
    Party,
    PartyResources,
    PartyRole,
)


def build_party(name: str, seats: int, acceptability: float, toxicity: float) -> Party:
    party = Party(
        name=name,
        archetype=Archetype(name="template"),
        role=PartyRole.PARLIAMENTARY_OPPOSITION,
        leader=Leader(name=f"{name} leader"),
        resources=PartyResources(coalition_acceptability=acceptability, toxicity=toxicity),
    )
    party.faction.seats = seats
    return party


class CoalitionEngineTests(unittest.TestCase):
    def test_candidate_generation_and_eligibility(self) -> None:
        engine = CoalitionEngine()
        a = build_party("A", 30, 65, 15)
        b = build_party("B", 25, 55, 20)
        c = build_party("C", 20, 40, 30)

        candidates = engine.generate_candidates([a, b, c])
        self.assertTrue(any(cand.total_seats >= 51 for cand in candidates))

        eligible = engine.is_formator_eligible(
            party=a,
            candidates=candidates,
            hard_isolation_flag=False,
            veto_count=1,
            veto_wall_threshold=2,
        )
        self.assertTrue(eligible)

    def test_stability_formula_and_crisis_routine(self) -> None:
        engine = CoalitionEngine()
        inputs = CoalitionStabilityInputs(
            discipline_bonus=2,
            compatibility_bonus=2,
            seat_buffer_bonus=1,
            portfolio_satisfaction_bonus=1,
            pm_strength_bonus=1,
            toxicity_penalty=4,
            rivalry_penalty=2,
            scandal_penalty=3,
            minister_failure_penalty=2,
            poll_divergence_penalty=2,
            election_pressure_penalty=2,
            budget_cycle_penalty=2,
        )
        stability = engine.update_stability(60, inputs)
        self.assertLess(stability, 60)

        outcome = engine.crisis_routine(
            stability=stability,
            warning_threshold=55,
            reshuffle_threshold=45,
            collapse_threshold=35,
            can_concede=False,
            problem_local=True,
            collapse_is_electorally_beneficial=False,
        )
        self.assertIn(outcome, {"stable", "reshuffle", "pm_replacement_attempt", "collapse", "concession"})


if __name__ == "__main__":
    unittest.main()
