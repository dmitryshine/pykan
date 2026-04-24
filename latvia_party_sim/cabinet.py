from __future__ import annotations

from dataclasses import dataclass, field

from .models import Party
from .territory import NationState


@dataclass(slots=True)
class PortfolioSpec:
    portfolio_id: str
    bargaining_weight: int
    prestige: int
    risk: int
    resource_effects_per_turn: dict[str, float]
    theme_effects_per_turn: dict[str, float]
    territorial_effects_per_turn: dict[str, float]
    scandal_profile: str
    ideal_party_tags: tuple[str, ...]
    failure_sensitivity: float


@dataclass(slots=True)
class MinisterAssignment:
    portfolio_id: str
    party_id: str
    holder_quality: float


@dataclass(slots=True)
class PortfolioRuntimeState:
    portfolio_id: str
    effectiveness: float = 50.0
    stress: float = 30.0
    scandal_risk: float = 20.0
    current_pressure: float = 30.0
    recent_failures: int = 0
    territory_modifiers: dict[str, float] = field(default_factory=dict)
    theme_modifiers: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class CabinetPhaseSignals:
    minister_failure_penalty: float = 0.0
    budget_cycle_penalty: float = 0.0
    portfolio_satisfaction_bonus: float = 0.0
    pm_strength_bonus: float = 0.0


@dataclass(slots=True)
class CabinetState:
    exists: bool = False
    pm_party: str | None = None
    pm_strength: float = 50.0
    start_stability: float = 60.0
    current_stability: float = 60.0
    partner_satisfaction: dict[str, float] = field(default_factory=dict)
    budget_load: float = 30.0
    prime_minister_wear: float = 10.0
    competence_image: float = 50.0
    assignments: list[MinisterAssignment] = field(default_factory=list)
    runtime_by_portfolio: dict[str, PortfolioRuntimeState] = field(default_factory=dict)
    problem_queue: list[str] = field(default_factory=list)
    reshuffle_history: list[str] = field(default_factory=list)
    cabinet_performance: float = 50.0
    last_phase_signals: CabinetPhaseSignals = field(default_factory=CabinetPhaseSignals)


PORTFOLIO_LIBRARY: dict[str, PortfolioSpec] = {
    "finance": PortfolioSpec(
        portfolio_id="finance",
        bargaining_weight=5,
        prestige=5,
        risk=5,
        resource_effects_per_turn={"agenda_control": 1.4, "brand_wear": 1.0, "trust": 0.4},
        theme_effects_per_turn={"economy": 1.2, "services": -0.3},
        territorial_effects_per_turn={"service_stress": 0.3},
        scandal_profile="austerity_backlash",
        ideal_party_tags=("technocrats", "system_center"),
        failure_sensitivity=1.4,
    ),
    "regional_development": PortfolioSpec(
        portfolio_id="regional_development",
        bargaining_weight=4,
        prestige=3,
        risk=3,
        resource_effects_per_turn={"org_network": 1.2, "trust": 0.3},
        theme_effects_per_turn={"regions": 1.1},
        territorial_effects_per_turn={"network_boost": 0.8},
        scandal_profile="procurement",
        ideal_party_tags=("regionalists",),
        failure_sensitivity=1.0,
    ),
    "transport": PortfolioSpec(
        portfolio_id="transport",
        bargaining_weight=3,
        prestige=3,
        risk=4,
        resource_effects_per_turn={"org_network": 0.8, "trust": 0.2, "brand_wear": 0.4},
        theme_effects_per_turn={"services": 0.7, "regions": 0.4},
        territorial_effects_per_turn={"network_boost": 0.5, "service_stress": 0.4},
        scandal_profile="infrastructure_delay",
        ideal_party_tags=("regionalists", "pragmatists"),
        failure_sensitivity=1.2,
    ),
    "health": PortfolioSpec(
        portfolio_id="health",
        bargaining_weight=3,
        prestige=4,
        risk=5,
        resource_effects_per_turn={"trust": 1.0, "brand_wear": 0.6},
        theme_effects_per_turn={"welfare": 1.2, "services": 0.8},
        territorial_effects_per_turn={"service_stress": 0.7},
        scandal_profile="system_overload",
        ideal_party_tags=("progressive", "social"),
        failure_sensitivity=1.6,
    ),
}


def ensure_runtime(cabinet: CabinetState) -> None:
    for assignment in cabinet.assignments:
        cabinet.runtime_by_portfolio.setdefault(
            assignment.portfolio_id,
            PortfolioRuntimeState(portfolio_id=assignment.portfolio_id),
        )


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def apply_cabinet_operating_effects(
    cabinet: CabinetState,
    parties_by_name: dict[str, Party],
    nation_state: NationState,
) -> CabinetPhaseSignals:
    if not cabinet.exists:
        return CabinetPhaseSignals()

    ensure_runtime(cabinet)
    minister_failure_penalty = 0.0

    for assignment in cabinet.assignments:
        spec = PORTFOLIO_LIBRARY.get(assignment.portfolio_id)
        if spec is None:
            continue
        party = parties_by_name.get(assignment.party_id)
        if party is None:
            continue

        runtime = cabinet.runtime_by_portfolio[assignment.portfolio_id]
        runtime.effectiveness = _clamp((runtime.effectiveness * 0.7) + (assignment.holder_quality * 0.3))
        runtime.current_pressure = _clamp(runtime.current_pressure + cabinet.budget_load * 0.05 + spec.risk * 0.4)
        runtime.stress = _clamp(runtime.stress + runtime.current_pressure * 0.04)
        runtime.scandal_risk = _clamp(
            runtime.scandal_risk + (100 - assignment.holder_quality) * 0.05 + spec.failure_sensitivity * 0.7
        )

        eff = (runtime.effectiveness / 100.0)
        for key, delta in spec.resource_effects_per_turn.items():
            if hasattr(party.resources, key):
                current = getattr(party.resources, key)
                setattr(party.resources, key, _clamp(current + delta * eff))

        for theme, delta in spec.theme_effects_per_turn.items():
            nation_state.national_theme_pressure[theme] = nation_state.national_theme_pressure.get(theme, 50.0) + (delta * eff)

        network_boost = spec.territorial_effects_per_turn.get("network_boost", 0.0)
        service_stress = spec.territorial_effects_per_turn.get("service_stress", 0.0)
        for m in nation_state.municipalities.values():
            m.party_network_strength[party.name] = _clamp(m.party_network_strength.get(party.name, 0.0) + network_boost * 0.08)
            m.protest_base = _clamp(m.protest_base + service_stress * 0.05)

        if runtime.scandal_risk > 65 or runtime.stress > 70:
            runtime.recent_failures += 1
            minister_failure_penalty += 1.5
            cabinet.problem_queue.append(assignment.portfolio_id)
            cabinet.partner_satisfaction[party.name] = _clamp(cabinet.partner_satisfaction.get(party.name, 50.0) - 2.0)
        else:
            cabinet.partner_satisfaction[party.name] = _clamp(cabinet.partner_satisfaction.get(party.name, 50.0) + 0.5)

    cabinet.prime_minister_wear = _clamp(cabinet.prime_minister_wear + cabinet.budget_load * 0.06)
    avg_satisfaction = 50.0
    if cabinet.partner_satisfaction:
        avg_satisfaction = sum(cabinet.partner_satisfaction.values()) / len(cabinet.partner_satisfaction)

    cabinet.cabinet_performance = _clamp(
        cabinet.pm_strength * 0.25
        + avg_satisfaction * 0.2
        + (100 - cabinet.prime_minister_wear) * 0.2
        + (100 - (len(cabinet.problem_queue) * 8)) * 0.2
        + (100 - cabinet.budget_load) * 0.15
    )
    cabinet.competence_image = _clamp((cabinet.competence_image * 0.7) + (cabinet.cabinet_performance * 0.3))

    signals = CabinetPhaseSignals(
        minister_failure_penalty=minister_failure_penalty,
        budget_cycle_penalty=cabinet.budget_load * 0.03,
        portfolio_satisfaction_bonus=(avg_satisfaction - 50.0) * 0.05,
        pm_strength_bonus=cabinet.pm_strength * 0.03,
    )
    cabinet.last_phase_signals = signals
    return signals
