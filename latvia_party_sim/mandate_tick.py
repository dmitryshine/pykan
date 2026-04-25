from __future__ import annotations

from dataclasses import dataclass, field

from .cabinet import CabinetPhaseSignals, CabinetState, apply_cabinet_operating_effects
from .coalition import CoalitionEngine, CoalitionStabilityInputs
from .engine import SimulationEngine
from .models import ActionEffect, Party, StageContext, TurnAction
from .economy import GovernmentEconomicSignals, GovernmentEconomyState, PartyEconomyState, resolve_government_budget_pressure, update_party_economy
from .budget_cycle import BudgetCycleOutput, BudgetFrame, run_budget_cycle
from .personality import Personality
from .territory import NationState, aggregate_district_metrics
from .party_mode import action_allowed, action_priority_multiplier, determine_party_mode, evaluate_mode_cycle, profile_for_mode
from .events import EventEngine, EventEngineState
from .media import MediaEngine, MediaEngineState, MediaLine


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
    personalities: dict[str, Personality] = field(default_factory=dict)
    government_economy: GovernmentEconomyState = field(default_factory=GovernmentEconomyState)
    party_economy: dict[str, PartyEconomyState] = field(default_factory=dict)
    budget_frame: BudgetFrame = BudgetFrame.BALANCED
    budget_interval: int = 12
    event_state: EventEngineState = field(default_factory=EventEngineState)
    media_state: MediaEngineState = field(default_factory=MediaEngineState)
    planned_media: dict[str, tuple[str, str | None, MediaLine]] = field(default_factory=dict)


@dataclass(slots=True)
class MandateTickResult:
    nation_state: NationState
    phase_log: list[str]
    headlines: list[str]
    district_alerts: dict[str, list[str]]


class MandateTickEngine:
    """Standard mandate-stage tick with integrated event/crisis pipeline."""

    def __init__(self) -> None:
        self.sim_engine = SimulationEngine()
        self.coalition_engine = CoalitionEngine()
        self.event_engine = EventEngine()
        self.media_engine = MediaEngine()

    def run_tick(self, tick_input: MandateTickInput) -> MandateTickResult:
        ns = tick_input.nation_state
        phase_log: list[str] = []

        self._phase_1_update_national_context(ns, tick_input.pending_events)
        phase_log.append("phase_1_national_context")

        self._phase_2_update_territories(ns, tick_input.pending_events)
        phase_log.append("phase_2_territorial_update")

        self._phase_3_aggregate_districts(ns, tick_input.parties)
        phase_log.append("phase_3_district_aggregation")

        self._phase_4_generate_latent_tensions(
            tick_input.context.turn,
            ns,
            tick_input.cabinet,
            tick_input.parties,
            tick_input.personalities,
            tick_input.event_state,
        )
        phase_log.append("phase_4_latent_tensions")

        adjusted_actions = self._phase_5_actions_selection(tick_input.parties, tick_input.cabinet, tick_input.planned_actions, phase_log)

        self._phase_6_resolve_actions(ns, tick_input.parties, tick_input.context, adjusted_actions)
        phase_log.append("phase_6_action_resolution")

        cabinet_signals = self._phase_7_update_government_and_portfolios(ns, tick_input.cabinet, tick_input.parties, tick_input.personalities)
        phase_log.append("phase_7_portfolio_ops")

        economic_signals, budget_output = self._phase_8_resolve_budget_and_resource_pressure(ns, tick_input.cabinet, tick_input.parties, tick_input.government_economy, tick_input.party_economy, tick_input.context.turn, tick_input.budget_frame, tick_input.budget_interval)
        phase_log.append("phase_8_budget_resource_pressure")

        self._phase_9_advance_events_and_crises(tick_input.context.turn, tick_input.event_state, tick_input.parties, ns, tick_input.cabinet, adjusted_actions)
        phase_log.append("phase_9_events_crises")

        self._phase_10_media_appearances(
            tick_input.context.turn,
            tick_input.context.stage,
            tick_input.parties,
            tick_input.personalities,
            ns,
            tick_input.cabinet,
            tick_input.event_state,
            tick_input.media_state,
            tick_input.planned_media,
        )
        phase_log.append("phase_10_media_appearances")

        self._phase_11_update_coalition_stability(tick_input.parties, tick_input.context, cabinet_signals, economic_signals)
        phase_log.append("phase_11_coalition_stability")

        self._phase_12_update_public_opinion(ns, tick_input.parties, tick_input.cabinet, economic_signals)
        phase_log.append("phase_12_public_opinion")

        self._phase_13_update_long_resources(tick_input.parties)
        phase_log.append("phase_13_long_resources")

        headlines, district_alerts = self._phase_14_generate_signals(ns, tick_input.cabinet, tick_input.event_state)
        phase_log.append("phase_14_signals")

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

    def _phase_4_generate_latent_tensions(
        self,
        turn: int,
        nation_state: NationState,
        cabinet: CabinetState,
        parties: list[Party],
        personalities: dict[str, Personality],
        event_state: EventEngineState,
    ) -> None:
        self.event_engine.generate_latent_tensions(turn, nation_state, cabinet, parties, personalities, event_state)
        self.event_engine.emit_signals(turn, event_state)

    def _phase_5_actions_selection(
        self,
        parties: list[Party],
        cabinet: CabinetState,
        planned_actions: dict[str, list[TurnAction]],
        phase_log: list[str],
    ) -> dict[str, list[TurnAction]]:
        adjusted_actions: dict[str, list[TurnAction]] = {}
        for party in parties:
            party.mode = determine_party_mode(party, cabinet)
            profile = profile_for_mode(party.mode)
            party.memory_markers["mode"] = party.mode.value
            party.memory_markers["distinctiveness_pressure"] = profile.distinctiveness_pressure
            party.memory_markers["blame_pressure"] = profile.blame_pressure
            party.memory_markers["entry_pressure"] = profile.entry_pressure
            for resource, weight in profile.resource_weights.items():
                party.memory_markers[f"mode_weight_{resource}"] = weight

        for party_name, actions in planned_actions.items():
            party = next((p for p in parties if p.name == party_name), None)
            if party is None:
                continue
            mode_actions: list[TurnAction] = []
            for action in actions:
                if not action_allowed(party.mode, action.tags):
                    continue
                multiplier = action_priority_multiplier(party.mode, action.tags)
                if multiplier == 1.0:
                    mode_actions.append(action)
                    continue
                effect = action.effect
                scaled_effect = ActionEffect(
                    org_network=effect.org_network * multiplier,
                    cadres=effect.cadres * multiplier,
                    trust=effect.trust * multiplier,
                    agenda_control=effect.agenda_control * multiplier,
                    toxicity=effect.toxicity,
                    coalition_acceptability=effect.coalition_acceptability * multiplier,
                    discipline=effect.discipline * multiplier,
                    activist_energy=effect.activist_energy * multiplier,
                    brand_wear=effect.brand_wear,
                    operations_wallet=effect.operations_wallet,
                    campaign_wallet=effect.campaign_wallet,
                )
                mode_actions.append(TurnAction(key=action.key, effect=scaled_effect, target_district_id=action.target_district_id, tags=action.tags))
            adjusted_actions[party_name] = mode_actions

        phase_log.append("phase_5_actions_selected")
        return adjusted_actions

    def _phase_6_resolve_actions(
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

    def _phase_7_update_government_and_portfolios(
        self,
        nation_state: NationState,
        cabinet: CabinetState,
        parties: list[Party],
        personalities: dict[str, Personality],
    ) -> CabinetPhaseSignals:
        parties_by_name = {p.name: p for p in parties}
        return apply_cabinet_operating_effects(cabinet, parties_by_name, nation_state, personalities)

    def _phase_8_resolve_budget_and_resource_pressure(
        self,
        nation_state: NationState,
        cabinet: CabinetState,
        parties: list[Party],
        gov_economy: GovernmentEconomyState,
        party_economy: dict[str, PartyEconomyState],
        turn: int,
        budget_frame: BudgetFrame,
        budget_interval: int,
    ) -> tuple[GovernmentEconomicSignals, BudgetCycleOutput]:
        for p in parties:
            econ = party_economy.setdefault(p.name, PartyEconomyState())
            update_party_economy(p, econ)
        budget_output = run_budget_cycle(turn, budget_frame, cabinet, gov_economy, parties, nation_state.districts, budget_interval)
        economic_signals = resolve_government_budget_pressure(cabinet, gov_economy, parties, nation_state)
        economic_signals.coalition_budget_penalty += budget_output.government_economic_strain_delta * 0.03
        economic_signals.trust_penalty += max(0.0, -budget_output.trust_delta * 0.02)
        return economic_signals, budget_output

    def _phase_9_advance_events_and_crises(
        self,
        turn: int,
        event_state: EventEngineState,
        parties: list[Party],
        nation_state: NationState,
        cabinet: CabinetState,
        planned_actions: dict[str, list[TurnAction]],
    ) -> None:
        action_tags = {
            party_name: [tag for action in actions for tag in action.tags]
            for party_name, actions in planned_actions.items()
        }
        self.event_engine.advance_active_events(turn, event_state, parties, nation_state, cabinet, action_tags)

    def _phase_10_media_appearances(
        self,
        turn: int,
        stage_context: str,
        parties: list[Party],
        personalities: dict[str, Personality],
        nation_state: NationState,
        cabinet: CabinetState,
        event_state: EventEngineState,
        media_state: MediaEngineState,
        planned_media: dict[str, tuple[str, str | None, MediaLine]],
    ) -> None:
        self.media_engine.generate_slots(turn, stage_context, cabinet, parties, event_state, media_state)
        by_party = {party.name: party for party in parties}
        if not planned_media:
            for slot in media_state.active_slots[:2]:
                if slot.target_party_id and slot.target_party_id in by_party and personalities:
                    planned_media[slot.target_party_id] = (slot.id, next(iter(personalities.keys())), MediaLine.RATIONAL_EXPLAIN)
        for party_name, slot_cfg in planned_media.items():
            if party_name not in by_party:
                continue
            slot_id, personality_id, line = slot_cfg
            slot = next((s for s in media_state.active_slots if s.id == slot_id), None)
            if slot is None:
                continue
            personality = personalities.get(personality_id) if personality_id else None
            if personality is None and personalities:
                personality = next(iter(personalities.values()))
            if personality is None:
                continue
            party = by_party[party_name]
            mode = determine_party_mode(party, cabinet).value
            resolution = self.media_engine.resolve_slot(slot, party, personality, line, stage_context, mode)
            self.media_engine.apply_resolution(slot, resolution, party, nation_state, cabinet, event_state, media_state)

    def _phase_11_update_coalition_stability(
        self,
        parties: list[Party],
        context: StageContext,
        cabinet_signals: CabinetPhaseSignals,
        economic_signals: GovernmentEconomicSignals,
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
                budget_cycle_penalty=cabinet_signals.budget_cycle_penalty + cabinet_signals.corruption_load_penalty + economic_signals.coalition_budget_penalty,
            )
            party.memory_markers["coalition_stability"] = self.coalition_engine.update_stability(prev, inputs)

    def _phase_12_update_public_opinion(self, nation_state: NationState, parties: list[Party], cabinet: CabinetState, economic_signals: GovernmentEconomicSignals) -> None:
        cabinet_competence_bonus = (cabinet.competence_image - 50.0) * 0.05 if cabinet.exists else 0.0
        for party in parties:
            local_mean = 0.0
            if nation_state.municipalities:
                local_mean = sum(
                    m.party_local_support.get(party.name, party.support_trend) for m in nation_state.municipalities.values()
                ) / len(nation_state.municipalities)
            party.memory_markers["national_rating"] = round((party.support_trend * 0.6) + (local_mean * 0.4) + cabinet_competence_bonus - economic_signals.trust_penalty, 2)

    def _phase_13_update_long_resources(self, parties: list[Party]) -> None:
        for party in parties:
            party.resources.org_network = min(100.0, party.resources.org_network + 0.2)
            party.resources.cadres = min(100.0, party.resources.cadres + 0.1)
            party.resources.activist_energy = max(0.0, party.resources.activist_energy - 0.1)
            party.memory_markers["mode_success_score"] = evaluate_mode_cycle(party, party.mode)
            self.sim_engine.update_lifecycle_state(party)

    def _phase_14_generate_signals(self, nation_state: NationState, cabinet: CabinetState, event_state: EventEngineState) -> tuple[list[str], dict[str, list[str]]]:
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
        if cabinet.exists and cabinet.scandal_hooks:
            headlines.append(f"Corruption hook: {cabinet.scandal_hooks[-1]}")

        event_headlines, warnings, opportunities = self.event_engine.build_player_signals(event_state)
        headlines.extend(event_headlines + warnings + opportunities)

        return headlines, district_alerts
