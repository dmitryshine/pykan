from __future__ import annotations

from dataclasses import dataclass, field

from .cabinet import CabinetPhaseSignals, CabinetState, apply_cabinet_operating_effects
from .coalition import CoalitionEngine, CoalitionStabilityInputs
from .engine import SimulationEngine
from .models import Party, StageContext, TurnAction
from .territory import NationState, aggregate_district_metrics


@dataclass(slots=True)
class PendingEvent:
    key: str
    district_id: str | None = None
    pressure_delta: dict[str, float] = field(default_factory=dict)
    protest_delta: float = 0.0


@dataclass(slots=True)
class MandateTickInput:
    nation_state: NationState
    parties: list[Party]
    context: StageContext
    planned_actions: dict[str, list[TurnAction]]
    pending_events: list[PendingEvent] = field(default_factory=list)
    cabinet: CabinetState = field(default_factory=CabinetState)


@dataclass(slots=True)
class MandateTickResult:
    nation_state: NationState
    phase_log: list[str]
    headlines: list[str]
    district_alerts: dict[str, list[str]]


class MandateTickEngine:
    """Standard mandate-stage tick in fixed 10-phase order."""

    def __init__(self) -> None:
        self.sim_engine = SimulationEngine()
        self.coalition_engine = CoalitionEngine()

    def run_tick(self, tick_input: MandateTickInput) -> MandateTickResult:
        ns = tick_input.nation_state
        phase_log: list[str] = []

        self._phase_1_update_national_context(ns, tick_input.pending_events)
        phase_log.append("phase_1_national_context")

        self._phase_2_update_territories(ns, tick_input.pending_events)
        phase_log.append("phase_2_territorial_update")

        self._phase_3_aggregate_districts(ns, tick_input.parties)
        phase_log.append("phase_3_district_aggregation")

        self._phase_4_actions_selection(phase_log)

        self._phase_5_resolve_actions(ns, tick_input.parties, tick_input.context, tick_input.planned_actions)
        phase_log.append("phase_5_action_resolution")

        cabinet_signals = self._phase_6_update_government_and_portfolios(ns, tick_input.cabinet, tick_input.parties)
        phase_log.append("phase_6_portfolio_ops")

        self._phase_7_update_coalition_stability(tick_input.parties, tick_input.context, cabinet_signals)
        phase_log.append("phase_7_coalition_stability")

        self._phase_8_update_public_opinion(ns, tick_input.parties, tick_input.cabinet)
        phase_log.append("phase_8_public_opinion")

        self._phase_9_update_long_resources(tick_input.parties)
        phase_log.append("phase_9_long_resources")

        headlines, district_alerts = self._phase_10_generate_signals(ns, tick_input.cabinet)
        phase_log.append("phase_10_signals")

        return MandateTickResult(ns, phase_log, headlines, district_alerts)

    def _phase_1_update_national_context(self, nation_state: NationState, pending_events: list[PendingEvent]) -> None:
        for event in pending_events:
            for k, v in event.pressure_delta.items():
                nation_state.national_theme_pressure[k] = nation_state.national_theme_pressure.get(k, 50.0) + v

    def _phase_2_update_territories(self, nation_state: NationState, pending_events: list[PendingEvent]) -> None:
        protest_pressure = nation_state.national_theme_pressure.get("protest", 0.0) * 0.03
        for municipality in nation_state.municipalities.values():
            municipality.protest_base = max(0.0, min(100.0, municipality.protest_base + protest_pressure - 0.4))
            municipality.government_mood = max(0.0, min(100.0, municipality.government_mood - protest_pressure * 0.5))

        for event in pending_events:
            if event.district_id is None:
                continue
            for m in nation_state.municipalities.values():
                if m.district_id == event.district_id:
                    m.protest_base = max(0.0, min(100.0, m.protest_base + event.protest_delta))

    def _phase_3_aggregate_districts(self, nation_state: NationState, parties: list[Party]) -> None:
        for district in nation_state.districts.values():
            district.alerts = []
            for party in parties:
                aggregate_district_metrics(district, nation_state.municipalities, party.name)
            if district.district_protest > 55:
                district.alerts.append("protest_risk")

    def _phase_4_actions_selection(self, phase_log: list[str]) -> None:
        phase_log.append("phase_4_actions_selected")

    def _phase_5_resolve_actions(
        self,
        nation_state: NationState,
        parties: list[Party],
        context: StageContext,
        planned_actions: dict[str, list[TurnAction]],
    ) -> None:
        by_name = {p.name: p for p in parties}
        for party_name, actions in planned_actions.items():
            party = by_name[party_name]
            for action in actions:
                self.sim_engine.apply_action(party, action)
                if action.target_district_id:
                    for m in nation_state.municipalities.values():
                        if m.district_id == action.target_district_id:
                            m.party_network_strength[party_name] = m.party_network_strength.get(party_name, 0.0) + 1.0

        for party in parties:
            self.sim_engine.apply_decay(party.resources, party.role.value)
            shock = self.sim_engine.resolve_stochastic_shocks(party, context)
            party.support_trend = self.sim_engine.compute_support_trend(party, context, shock)

    def _phase_6_update_government_and_portfolios(
        self,
        nation_state: NationState,
        cabinet: CabinetState,
        parties: list[Party],
    ) -> CabinetPhaseSignals:
        parties_by_name = {p.name: p for p in parties}
        return apply_cabinet_operating_effects(cabinet, parties_by_name, nation_state)

    def _phase_7_update_coalition_stability(
        self,
        parties: list[Party],
        context: StageContext,
        cabinet_signals: CabinetPhaseSignals,
    ) -> None:
        for party in parties:
            if party.role.value != "government":
                continue
            prev = party.memory_markers.get("coalition_stability", 60.0)
            inputs = CoalitionStabilityInputs(
                discipline_bonus=party.resources.discipline * 0.03,
                compatibility_bonus=party.resources.coalition_acceptability * 0.02,
                seat_buffer_bonus=2.0,
                portfolio_satisfaction_bonus=max(0.0, cabinet_signals.portfolio_satisfaction_bonus),
                pm_strength_bonus=cabinet_signals.pm_strength_bonus,
                toxicity_penalty=party.resources.toxicity * 0.03,
                rivalry_penalty=context.coalition_shock,
                scandal_penalty=0.5,
                minister_failure_penalty=cabinet_signals.minister_failure_penalty,
                poll_divergence_penalty=0.3,
                election_pressure_penalty=0.2,
                budget_cycle_penalty=cabinet_signals.budget_cycle_penalty,
            )
            party.memory_markers["coalition_stability"] = self.coalition_engine.update_stability(prev, inputs)

    def _phase_8_update_public_opinion(self, nation_state: NationState, parties: list[Party], cabinet: CabinetState) -> None:
        cabinet_competence_bonus = (cabinet.competence_image - 50.0) * 0.05 if cabinet.exists else 0.0
        for party in parties:
            local_mean = 0.0
            if nation_state.municipalities:
                local_mean = sum(
                    m.party_local_support.get(party.name, party.support_trend) for m in nation_state.municipalities.values()
                ) / len(nation_state.municipalities)
            party.memory_markers["national_rating"] = round((party.support_trend * 0.6) + (local_mean * 0.4) + cabinet_competence_bonus, 2)

    def _phase_9_update_long_resources(self, parties: list[Party]) -> None:
        for party in parties:
            party.resources.org_network = min(100.0, party.resources.org_network + 0.2)
            party.resources.cadres = min(100.0, party.resources.cadres + 0.1)
            party.resources.activist_energy = max(0.0, party.resources.activist_energy - 0.1)
            self.sim_engine.update_lifecycle_state(party)

    def _phase_10_generate_signals(self, nation_state: NationState, cabinet: CabinetState) -> tuple[list[str], dict[str, list[str]]]:
        headlines: list[str] = []
        district_alerts: dict[str, list[str]] = {}
        for district in nation_state.districts.values():
            alerts = list(district.alerts)
            if district.district_protest > 65:
                alerts.append("hotspot_protest")
            if district.district_turnout < 50:
                alerts.append("turnout_risk")
            district_alerts[district.id] = alerts
            if alerts:
                headlines.append(f"{district.name}: {', '.join(alerts)}")

        if cabinet.exists and cabinet.problem_queue:
            headlines.append(f"Cabinet pressure: {cabinet.problem_queue[-1]} at risk")

        return headlines, district_alerts
