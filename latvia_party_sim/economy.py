from __future__ import annotations

from dataclasses import dataclass

from .cabinet import CabinetState
from .models import Party
from .territory import NationState


@dataclass(slots=True)
class PartyEconomyState:
    operating_cash: float = 0.0
    campaign_cash: float = 0.0
    state_funding: float = 0.0
    private_funding_flow: float = 0.0
    fundraising_capacity: float = 50.0
    network_upkeep_cost: float = 2.0
    cadre_upkeep_cost: float = 1.5
    media_cost_pressure: float = 1.0
    crisis_response_cost: float = 0.0
    rebrand_cost_pressure: float = 0.0


@dataclass(slots=True)
class GovernmentEconomyState:
    budget_stress: float = 40.0
    fiscal_room: float = 55.0
    spending_pressure_social: float = 50.0
    spending_pressure_regions: float = 50.0
    spending_pressure_security: float = 45.0
    spending_pressure_services: float = 50.0
    infrastructure_commitment: float = 45.0
    public_tolerance_for_austerity: float = 45.0
    pre_election_spending_temptation: float = 30.0


@dataclass(slots=True)
class GovernmentEconomicSignals:
    coalition_budget_penalty: float = 0.0
    trust_penalty: float = 0.0
    network_penalty: float = 0.0
    economic_strain: float = 0.0


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def update_party_economy(party: Party, econ: PartyEconomyState) -> None:
    income = econ.state_funding + econ.private_funding_flow + (econ.fundraising_capacity * 0.08)
    upkeep = econ.network_upkeep_cost + econ.cadre_upkeep_cost + econ.media_cost_pressure + econ.crisis_response_cost

    econ.operating_cash += income - upkeep
    party.wallets.operations += income - upkeep

    if econ.rebrand_cost_pressure > 0:
        econ.campaign_cash -= econ.rebrand_cost_pressure
        party.wallets.campaign -= econ.rebrand_cost_pressure


def resolve_government_budget_pressure(
    cabinet: CabinetState,
    gov_econ: GovernmentEconomyState,
    parties: list[Party],
    nation_state: NationState,
) -> GovernmentEconomicSignals:
    spending_bundle = (
        gov_econ.spending_pressure_social
        + gov_econ.spending_pressure_regions
        + gov_econ.spending_pressure_security
        + gov_econ.spending_pressure_services
        + gov_econ.infrastructure_commitment
    ) / 5

    gov_econ.budget_stress = _clamp(
        gov_econ.budget_stress + spending_bundle * 0.08 + gov_econ.pre_election_spending_temptation * 0.06 - gov_econ.fiscal_room * 0.07
    )

    gov_econ.fiscal_room = _clamp(gov_econ.fiscal_room - gov_econ.budget_stress * 0.05 + gov_econ.public_tolerance_for_austerity * 0.03)

    economic_strain = _clamp(
        gov_econ.budget_stress * 0.45
        + (100 - gov_econ.fiscal_room) * 0.30
        + gov_econ.pre_election_spending_temptation * 0.15
        + len(cabinet.problem_queue) * 2.0
    )

    # Budget strain flows to cabinet, territories, and ruling parties.
    for p in parties:
        if p.role.value == "government":
            p.resources.trust = _clamp(p.resources.trust - economic_strain * 0.04)
            p.resources.brand_wear = _clamp(p.resources.brand_wear + economic_strain * 0.03)

    for municipality in nation_state.municipalities.values():
        municipality.government_mood = _clamp(municipality.government_mood - economic_strain * 0.05)
        municipality.protest_base = _clamp(municipality.protest_base + economic_strain * 0.03)

    cabinet.current_stability = _clamp(cabinet.current_stability - economic_strain * 0.05)

    return GovernmentEconomicSignals(
        coalition_budget_penalty=economic_strain * 0.08,
        trust_penalty=economic_strain * 0.05,
        network_penalty=economic_strain * 0.03,
        economic_strain=economic_strain,
    )
