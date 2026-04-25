from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from .models import MAX_SCORE, MIN_SCORE, Party


@dataclass(slots=True)
class CoalitionCandidate:
    member_names: tuple[str, ...]
    total_seats: int
    compatibility_score: float
    blocked: bool = False


@dataclass(slots=True)
class CoalitionStabilityInputs:
    discipline_bonus: float = 0.0
    compatibility_bonus: float = 0.0
    seat_buffer_bonus: float = 0.0
    portfolio_satisfaction_bonus: float = 0.0
    pm_strength_bonus: float = 0.0
    toxicity_penalty: float = 0.0
    rivalry_penalty: float = 0.0
    scandal_penalty: float = 0.0
    minister_failure_penalty: float = 0.0
    poll_divergence_penalty: float = 0.0
    election_pressure_penalty: float = 0.0
    budget_cycle_penalty: float = 0.0


class CoalitionEngine:
    def __init__(self, majority_threshold: int = 51, veto_penalty_weight: float = 4.0) -> None:
        self.majority_threshold = majority_threshold
        self.veto_penalty_weight = veto_penalty_weight

    def clamp(self, value: float) -> float:
        return max(MIN_SCORE, min(MAX_SCORE, value))

    def generate_candidates(
        self,
        parliamentary_parties: list[Party],
        hard_veto_pairs: set[frozenset[str]] | None = None,
        ideological_distance_cap: float | None = None,
    ) -> list[CoalitionCandidate]:
        hard_veto_pairs = hard_veto_pairs or set()
        candidates: list[CoalitionCandidate] = []

        for size in range(2, len(parliamentary_parties) + 1):
            for combo in combinations(parliamentary_parties, size):
                seats = sum(p.faction.seats for p in combo)
                if seats < self.majority_threshold:
                    continue

                member_names = tuple(sorted(p.name for p in combo))
                blocked = any(frozenset((a, b)) in hard_veto_pairs for a, b in combinations(member_names, 2))
                acceptability = sum(p.resources.coalition_acceptability for p in combo) / len(combo)
                toxicity = sum(p.resources.toxicity for p in combo) / len(combo)
                compatibility = self.clamp(acceptability - toxicity * 0.35)

                if ideological_distance_cap is not None and compatibility < ideological_distance_cap:
                    continue

                candidates.append(
                    CoalitionCandidate(
                        member_names=member_names,
                        total_seats=seats,
                        compatibility_score=compatibility,
                        blocked=blocked,
                    )
                )

        return sorted(candidates, key=lambda c: (c.blocked, -c.total_seats, -c.compatibility_score))

    def is_formator_eligible(
        self,
        party: Party,
        candidates: list[CoalitionCandidate],
        hard_isolation_flag: bool,
        veto_count: int,
        veto_wall_threshold: int,
        min_acceptability: float = 30.0,
    ) -> bool:
        has_majority_path = any((party.name in c.member_names and not c.blocked) for c in candidates)
        return (
            has_majority_path
            and not hard_isolation_flag
            and veto_count <= veto_wall_threshold
            and party.resources.coalition_acceptability >= min_acceptability
        )

    def formator_score(
        self,
        mandates: float,
        acceptability: float,
        legitimacy: float,
        cadres: float,
        agenda: float,
        toxicity: float,
        veto_count: int,
    ) -> float:
        # All continuous inputs expected on 0..100 scale.
        return (
            mandates * 0.35
            + acceptability * 0.25
            + legitimacy * 0.15
            + cadres * 0.10
            + agenda * 0.10
            - toxicity * 0.15
            - veto_count * self.veto_penalty_weight
        )

    def portfolio_utility(
        self,
        ideological_fit: float,
        electoral_fit: float,
        institutional_fit: float,
        prestige_fit: float,
        cadre_stress: float,
        scandal_exposure: float,
    ) -> float:
        return self.clamp(
            ideological_fit + electoral_fit + institutional_fit + prestige_fit - cadre_stress - scandal_exposure
        )

    def update_stability(self, stability_prev: float, inputs: CoalitionStabilityInputs) -> float:
        next_value = (
            stability_prev
            + inputs.discipline_bonus
            + inputs.compatibility_bonus
            + inputs.seat_buffer_bonus
            + inputs.portfolio_satisfaction_bonus
            + inputs.pm_strength_bonus
            - inputs.toxicity_penalty
            - inputs.rivalry_penalty
            - inputs.scandal_penalty
            - inputs.minister_failure_penalty
            - inputs.poll_divergence_penalty
            - inputs.election_pressure_penalty
            - inputs.budget_cycle_penalty
        )
        return self.clamp(next_value)

    def crisis_routine(
        self,
        stability: float,
        warning_threshold: float,
        reshuffle_threshold: float,
        collapse_threshold: float,
        can_concede: bool,
        problem_local: bool,
        collapse_is_electorally_beneficial: bool,
    ) -> str:
        if stability >= warning_threshold:
            return "stable"

        if can_concede:
            return "concession"

        if stability < reshuffle_threshold and problem_local:
            return "reshuffle"

        if stability < collapse_threshold and not collapse_is_electorally_beneficial:
            return "pm_replacement_attempt"

        return "collapse"
