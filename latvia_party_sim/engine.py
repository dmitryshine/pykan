from __future__ import annotations

from dataclasses import dataclass
import random

from .models import MAX_SCORE, MIN_SCORE, Party, PartyLifecycleState, PartyResources, StageContext, TurnAction


@dataclass(slots=True)
class SupportWeights:
    trust: float = 0.30
    agenda: float = 0.25
    org_network: float = 0.15
    cadres: float = 0.15
    energy: float = 0.10
    toxicity_penalty: float = 0.20
    brand_wear_penalty: float = 0.20


class SimulationEngine:
    """Implementation-ready ordered turn loop for mandate-stage ticks."""

    def __init__(self, support_weights: SupportWeights | None = None) -> None:
        self.support_weights = support_weights or SupportWeights()

    def clamp(self, value: float) -> float:
        return max(MIN_SCORE, min(MAX_SCORE, value))

    def apply_action(self, party: Party, action: TurnAction) -> None:
        r = party.resources
        e = action.effect
        r.org_network = self.clamp(r.org_network + e.org_network)
        r.cadres = self.clamp(r.cadres + e.cadres)
        r.trust = self.clamp(r.trust + e.trust)
        r.agenda_control = self.clamp(r.agenda_control + e.agenda_control)
        r.toxicity = self.clamp(r.toxicity + e.toxicity)
        r.coalition_acceptability = self.clamp(r.coalition_acceptability + e.coalition_acceptability)
        r.discipline = self.clamp(r.discipline + e.discipline)
        r.activist_energy = self.clamp(r.activist_energy + e.activist_energy)
        r.brand_wear = self.clamp(r.brand_wear + e.brand_wear)
        party.wallets.operations += e.operations_wallet
        party.wallets.campaign += e.campaign_wallet

    def apply_decay(self, resources: PartyResources, role_name: str) -> None:
        role_wear_bonus = 0.2 if role_name == "government" else 0.0
        resources.activist_energy = self.clamp(resources.activist_energy - 0.6)
        resources.brand_wear = self.clamp(resources.brand_wear + 0.8 + role_wear_bonus)

    def resolve_stochastic_shocks(self, party: Party, context: StageContext) -> float:
        rng = random.Random(context.rng_seed + context.turn + hash(party.name) % 1000)
        crisis_probability = party.resources.toxicity / 250.0
        return -2.0 if rng.random() < crisis_probability else 0.0

    def compute_support_trend(self, party: Party, context: StageContext, random_shock: float) -> float:
        r = party.resources
        w = self.support_weights
        score = (
            w.trust * r.trust
            + w.agenda * r.agenda_control
            + w.org_network * r.org_network
            + w.cadres * r.cadres
            + w.energy * r.activist_energy
            - w.toxicity_penalty * r.toxicity
            - w.brand_wear_penalty * r.brand_wear
            + context.event_shock
            + random_shock
        )
        return self.clamp(score)

    def update_coalition_stability(self, party: Party, context: StageContext) -> None:
        if party.role.value != "government":
            return
        pressure = context.coalition_shock + (party.resources.toxicity * 0.05)
        party.memory_markers["coalition_stability"] = self.clamp(
            party.memory_markers.get("coalition_stability", 60.0) - pressure + party.resources.discipline * 0.03
        )

    def update_lifecycle_state(self, party: Party) -> None:
        death_pressure = (
            (100 - party.resources.org_network)
            + (100 - party.resources.cadres)
            + party.resources.brand_wear
            + (100 - party.resources.discipline)
        ) / 4
        if death_pressure > 85:
            party.lifecycle_state = PartyLifecycleState.DEAD
        elif death_pressure > 70:
            party.lifecycle_state = PartyLifecycleState.DYING
        elif party.resources.brand_wear > 75:
            party.lifecycle_state = PartyLifecycleState.REBRANDING
        else:
            party.lifecycle_state = PartyLifecycleState.ACTIVE

    def write_memory_markers(self, party: Party, context: StageContext) -> None:
        party.memory_markers["last_turn"] = float(context.turn)
        party.memory_markers["brand_wear_snapshot"] = party.resources.brand_wear

    def step_turn(self, context: StageContext, planned_actions: dict[str, list[TurnAction]], parties: list[Party]) -> None:
        """
        Fixed order:
        1) apply actions
        2) apply decay
        3) resolve stochastic shocks
        4) compute support trend
        5) update coalition stability
        6) evaluate lifecycle thresholds
        7) write memory markers
        """
        by_name = {p.name: p for p in parties}

        for party_name, actions in planned_actions.items():
            party = by_name[party_name]
            for action in actions:
                self.apply_action(party, action)

        for party in parties:
            self.apply_decay(party.resources, party.role.value)
            random_shock = self.resolve_stochastic_shocks(party, context)
            party.support_trend = self.compute_support_trend(party, context, random_shock)
            self.update_coalition_stability(party, context)
            self.update_lifecycle_state(party)
            self.write_memory_markers(party, context)
