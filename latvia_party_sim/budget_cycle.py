from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .cabinet import CabinetState
from .economy import GovernmentEconomyState
from .models import Party
from .territory import District


class BudgetFrame(str, Enum):
    AUSTERITY = "austerity"
    BALANCED = "balanced"
    SOCIAL_EXPANSION = "social_expansion"
    REGIONAL_PUSH = "regional_push"
    SECURITY_FIRST = "security_first"
    PRE_ELECTION_SPLURGE = "pre_election_splurge"
    PATRONAGE = "patronage"


@dataclass(slots=True)
class BudgetCycleOutput:
    coalition_satisfaction_delta: float = 0.0
    cabinet_performance_delta: float = 0.0
    government_economic_strain_delta: float = 0.0
    ministerial_strain_map: dict[str, float] = field(default_factory=dict)
    district_budget_impact_map: dict[str, float] = field(default_factory=dict)
    trust_delta: float = 0.0
    protest_delta: float = 0.0
    brand_wear_delta: float = 0.0
    corruption_delta: float = 0.0
    future_budget_pressure_delta: float = 0.0


FRAME_MODIFIERS: dict[BudgetFrame, dict[str, float]] = {
    BudgetFrame.AUSTERITY: {"trust": -4.0, "brand_wear": 1.5, "future_pressure": -4.5, "corruption": -1.0},
    BudgetFrame.BALANCED: {"trust": 0.5, "brand_wear": 0.5, "future_pressure": -1.0, "corruption": 0.2},
    BudgetFrame.SOCIAL_EXPANSION: {"trust": 3.0, "brand_wear": 1.0, "future_pressure": 3.5, "corruption": 0.5},
    BudgetFrame.REGIONAL_PUSH: {"trust": 1.5, "brand_wear": 1.0, "future_pressure": 2.5, "corruption": 1.0},
    BudgetFrame.SECURITY_FIRST: {"trust": 0.8, "brand_wear": 1.2, "future_pressure": 2.0, "corruption": 0.4},
    BudgetFrame.PRE_ELECTION_SPLURGE: {"trust": 2.2, "brand_wear": 2.2, "future_pressure": 5.0, "corruption": 1.2},
    BudgetFrame.PATRONAGE: {"trust": -1.0, "brand_wear": 2.8, "future_pressure": 4.5, "corruption": 3.0},
}


def is_budget_turn(turn: int, interval: int = 12) -> bool:
    return turn % interval == 0


def run_budget_cycle(
    turn: int,
    frame: BudgetFrame,
    cabinet: CabinetState,
    gov_econ: GovernmentEconomyState,
    parties: list[Party],
    districts: dict[str, District],
    interval: int = 12,
) -> BudgetCycleOutput:
    if not is_budget_turn(turn, interval):
        return BudgetCycleOutput()

    mods = FRAME_MODIFIERS[frame]
    out = BudgetCycleOutput()

    # Ministerial strain by portfolio pressure.
    for assignment in cabinet.assignments:
        base = gov_econ.budget_stress * 0.35 + gov_econ.pre_election_spending_temptation * 0.2
        out.ministerial_strain_map[assignment.portfolio_id] = max(0.0, min(100.0, base + (100 - assignment.holder_quality) * 0.25))

    # District map from spending styles (simplified MVP).
    for district_id, district in districts.items():
        regional_bias = 1.0 if frame in {BudgetFrame.REGIONAL_PUSH, BudgetFrame.PATRONAGE} and district_id in {"LATGALE", "ZEMGALE", "KURZEME"} else 0.0
        urban_penalty = -0.8 if frame == BudgetFrame.AUSTERITY and district_id in {"RIGA", "VIDZEME"} else 0.0
        out.district_budget_impact_map[district_id] = regional_bias + urban_penalty

    partner_satisfaction_avg = 50.0
    if cabinet.partner_satisfaction:
        partner_satisfaction_avg = sum(cabinet.partner_satisfaction.values()) / len(cabinet.partner_satisfaction)

    out.coalition_satisfaction_delta = (partner_satisfaction_avg - 50.0) * 0.05 + (2.0 if frame == BudgetFrame.PATRONAGE else 0.0)
    out.government_economic_strain_delta = gov_econ.budget_stress * 0.08 + mods["future_pressure"]
    out.cabinet_performance_delta = mods["trust"] - out.government_economic_strain_delta * 0.3

    out.trust_delta = mods["trust"]
    out.protest_delta = max(0.0, out.government_economic_strain_delta * 0.15 - mods["trust"] * 0.1)
    out.brand_wear_delta = mods["brand_wear"]
    out.corruption_delta = mods["corruption"]
    out.future_budget_pressure_delta = mods["future_pressure"]

    # Apply to cabinet and ruling parties.
    cabinet.current_stability = max(0.0, min(100.0, cabinet.current_stability + out.coalition_satisfaction_delta - out.government_economic_strain_delta * 0.2))
    cabinet.cabinet_performance = max(0.0, min(100.0, cabinet.cabinet_performance + out.cabinet_performance_delta))
    cabinet.corruption_load = max(0.0, min(100.0, cabinet.corruption_load + out.corruption_delta))

    for p in parties:
        if p.role.value == "government":
            p.resources.trust = max(0.0, min(100.0, p.resources.trust + out.trust_delta))
            p.resources.brand_wear = max(0.0, min(100.0, p.resources.brand_wear + out.brand_wear_delta))

    gov_econ.budget_stress = max(0.0, min(100.0, gov_econ.budget_stress + out.future_budget_pressure_delta))
    return out
