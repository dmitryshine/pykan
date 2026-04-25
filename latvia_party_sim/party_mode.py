from __future__ import annotations

from dataclasses import dataclass

from .cabinet import CabinetState
from .models import MAX_SCORE, Party, PartyMode


@dataclass(frozen=True, slots=True)
class ModeProfile:
    resource_weights: dict[str, float]
    action_weights: dict[str, float]
    risk_weights: dict[str, float]
    success_metrics: dict[str, float]
    failure_metrics: dict[str, float]
    distinctiveness_pressure: float
    blame_pressure: float
    entry_pressure: float
    allowed_action_tags: tuple[str, ...]


MODE_PROFILES: dict[PartyMode, ModeProfile] = {
    PartyMode.GOVERNMENT_LEAD: ModeProfile(
        resource_weights={
            "cabinet_performance": 1.35,
            "trust": 1.25,
            "coalition_stability": 1.35,
            "budget_leverage": 1.4,
            "agenda_control": 1.1,
            "distinctiveness": 0.7,
        },
        action_weights={
            "budget": 1.25,
            "crisis": 1.15,
            "minister_defense": 1.1,
            "discipline": 1.1,
            "rebrand": 0.7,
            "entry": 0.5,
        },
        risk_weights={
            "brand_wear": 1.35,
            "blame": 1.35,
            "ministerial_exposure": 1.2,
            "budget_toxicity": 1.3,
        },
        success_metrics={"coalition_stability": 0.45, "agenda_control": 0.25, "trust": 0.2, "support_trend": 0.1},
        failure_metrics={"brand_wear": 0.5, "toxicity": 0.3, "protest": 0.2},
        distinctiveness_pressure=0.35,
        blame_pressure=1.35,
        entry_pressure=0.0,
        allowed_action_tags=("budget", "crisis", "discipline", "minister_defense", "general"),
    ),
    PartyMode.GOVERNMENT_JUNIOR: ModeProfile(
        resource_weights={
            "portfolio_value": 1.3,
            "distinctiveness": 1.35,
            "coalition_leverage": 1.2,
            "regional_payoff": 1.1,
            "trust": 1.05,
        },
        action_weights={
            "distance": 1.3,
            "portfolio": 1.2,
            "district": 1.15,
            "budget": 0.9,
            "investigation": 0.4,
            "entry": 0.5,
        },
        risk_weights={"absorption": 1.4, "humiliation": 1.25, "late_exit": 1.2, "shared_blame": 1.1},
        success_metrics={"distinctiveness": 0.4, "trust": 0.2, "org_network": 0.2, "support_trend": 0.2},
        failure_metrics={"brand_wear": 0.35, "toxicity": 0.25, "coalition_stability": 0.4},
        distinctiveness_pressure=1.4,
        blame_pressure=1.0,
        entry_pressure=0.1,
        allowed_action_tags=("distance", "portfolio", "district", "coalition", "general"),
    ),
    PartyMode.PARLIAMENTARY_OPPOSITION: ModeProfile(
        resource_weights={
            "agenda_control": 1.3,
            "trust": 1.2,
            "issue_ownership": 1.3,
            "new_faces": 1.2,
            "protest_access": 1.1,
        },
        action_weights={
            "investigation": 1.35,
            "issue": 1.25,
            "attack": 1.15,
            "constructive": 1.0,
            "budget": 0.45,
            "entry": 0.7,
        },
        risk_weights={"noise": 1.3, "fragmentation": 1.2, "over_negativity": 1.1},
        success_metrics={"agenda_control": 0.35, "trust": 0.35, "support_trend": 0.2, "cadres": 0.1},
        failure_metrics={"toxicity": 0.4, "brand_wear": 0.2, "discipline": 0.4},
        distinctiveness_pressure=1.0,
        blame_pressure=0.6,
        entry_pressure=0.2,
        allowed_action_tags=("investigation", "issue", "attack", "constructive", "district", "general"),
    ),
    PartyMode.EXTRA_PARLIAMENTARY: ModeProfile(
        resource_weights={
            "brand_freshness": 1.4,
            "org_network": 1.35,
            "protest_access": 1.35,
            "new_faces": 1.25,
            "trust": 0.9,
        },
        action_weights={
            "rebrand": 1.35,
            "entry": 1.4,
            "district": 1.2,
            "absorb": 1.15,
            "investigation": 0.6,
            "budget": 0.0,
        },
        risk_weights={"invisibility": 1.4, "burnout": 1.2, "weak_structure": 1.25},
        success_metrics={"org_network": 0.35, "cadres": 0.2, "support_trend": 0.25, "activist_energy": 0.2},
        failure_metrics={"discipline": 0.3, "toxicity": 0.2, "brand_wear": 0.5},
        distinctiveness_pressure=1.25,
        blame_pressure=0.25,
        entry_pressure=1.4,
        allowed_action_tags=("rebrand", "entry", "district", "absorb", "general"),
    ),
}


def _metric_value(party: Party, metric: str) -> float:
    if metric == "coalition_stability":
        return party.memory_markers.get("coalition_stability", 50.0)
    if metric == "support_trend":
        return party.support_trend
    if metric == "cabinet_performance":
        return party.memory_markers.get("cabinet_performance", 50.0)
    if metric == "portfolio_value":
        return party.memory_markers.get("portfolio_value", 50.0)
    if metric == "issue_ownership":
        return party.memory_markers.get("issue_ownership", party.resources.agenda_control)
    if metric == "new_faces":
        return party.memory_markers.get("new_faces", party.resources.cadres)
    if metric == "protest":
        return party.memory_markers.get("protest_pressure", 50.0)
    if metric == "distinctiveness":
        return party.memory_markers.get("distinctiveness", 50.0)
    if metric == "brand_freshness":
        return MAX_SCORE - party.resources.brand_wear
    if metric == "budget_leverage":
        return party.memory_markers.get("budget_leverage", 50.0)
    if metric == "coalition_leverage":
        return party.memory_markers.get("coalition_leverage", 50.0)
    if metric == "regional_payoff":
        return party.memory_markers.get("regional_payoff", party.resources.org_network)
    if metric == "trust_growth":
        return party.memory_markers.get("trust_growth", 0.0)
    if hasattr(party.resources, metric):
        return float(getattr(party.resources, metric))
    return party.memory_markers.get(metric, 50.0)


def determine_party_mode(party: Party, cabinet: CabinetState) -> PartyMode:
    if party.faction.seats <= 0:
        return PartyMode.EXTRA_PARLIAMENTARY
    if cabinet.exists and party.name == cabinet.pm_party:
        return PartyMode.GOVERNMENT_LEAD
    if cabinet.exists:
        in_assignments = any(assignment.party_id == party.name for assignment in cabinet.assignments)
        if in_assignments or party.faction.in_coalition or party.role.value == "government":
            return PartyMode.GOVERNMENT_JUNIOR
    return PartyMode.PARLIAMENTARY_OPPOSITION


def profile_for_mode(mode: PartyMode) -> ModeProfile:
    return MODE_PROFILES[mode]


def action_allowed(mode: PartyMode, action_tags: tuple[str, ...]) -> bool:
    if not action_tags:
        return True
    allowed = set(MODE_PROFILES[mode].allowed_action_tags)
    return any(tag in allowed for tag in action_tags)


def action_priority_multiplier(mode: PartyMode, action_tags: tuple[str, ...]) -> float:
    if not action_tags:
        return 1.0
    weights = MODE_PROFILES[mode].action_weights
    return max((weights.get(tag, 1.0) for tag in action_tags), default=1.0)


def evaluate_mode_cycle(party: Party, mode: PartyMode) -> float:
    profile = MODE_PROFILES[mode]
    success = sum(_metric_value(party, metric) * weight for metric, weight in profile.success_metrics.items())
    failure = sum(_metric_value(party, metric) * weight for metric, weight in profile.failure_metrics.items())
    score = success - failure + 50.0 - (profile.blame_pressure * 2.0) + (profile.entry_pressure * 2.0)
    return max(0.0, min(MAX_SCORE, score))
