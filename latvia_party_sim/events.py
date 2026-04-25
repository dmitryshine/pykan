from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .cabinet import CabinetState
from .models import Party
from .party_mode import determine_party_mode
from .personality import Personality
from .territory import District, NationState


class EventType(str, Enum):
    GOVERNANCE_CRISIS = "governance_crisis"
    CORRUPTION_SCANDAL = "corruption_scandal"
    PERSONALITY_CRISIS = "personality_crisis"
    COALITION_CRISIS = "coalition_crisis"
    INTRA_PARTY_CRISIS = "intra_party_crisis"
    POSITIVE_WINDOW = "positive_window"


class EventOriginType(str, Enum):
    ENDOGENOUS = "endogenous"
    EXOGENOUS = "exogenous"
    ACTOR_TRIGGERED = "actor_triggered"


class EventStage(str, Enum):
    LATENT = "latent"
    SIGNAL = "signal"
    ESCALATION = "escalation"
    RESOLUTION = "resolution"
    MEMORY = "memory"


@dataclass(slots=True)
class PoliticalEvent:
    id: str
    event_type: EventType
    origin_type: EventOriginType
    severity: float
    scope: str
    source_actor_id: str | None
    target_actor_ids: list[str]
    trigger_conditions: dict[str, float]
    current_stage: EventStage = EventStage.LATENT
    heat: float = 0.0
    controllability: float = 50.0
    territorial_footprint: dict[str, list[str]] = field(default_factory=dict)
    theme_links: tuple[str, ...] = ()
    memory_effects: dict[str, float] = field(default_factory=dict)
    resolution_options: tuple[str, ...] = (
        "ignore",
        "localize",
        "sacrifice",
        "counter_attack",
        "reframe",
        "procedural_freeze",
        "shift_blame",
        "capitalize",
        "distance",
        "dramatize",
    )
    visibility: float = 0.0
    expires_after: int | None = None
    created_turn: int = 0
    last_updated_turn: int = 0


@dataclass(slots=True)
class EventEngineState:
    active_events: list[PoliticalEvent] = field(default_factory=list)
    event_memory: dict[str, float] = field(default_factory=dict)
    unresolved_tensions: dict[str, float] = field(default_factory=dict)


class EventEngine:
    def generate_latent_tensions(
        self,
        turn: int,
        nation_state: NationState,
        cabinet: CabinetState,
        parties: list[Party],
        personalities: dict[str, Personality],
        state: EventEngineState,
    ) -> None:
        self._add_tension(state, "budget_stress", cabinet.budget_load * 0.6)
        self._add_tension(state, "corruption_pressure", (cabinet.corruption_load + cabinet.corruption_memory) * 0.5)
        if cabinet.partner_satisfaction:
            self._add_tension(state, "coalition_resentment", max(0.0, 55 - min(cabinet.partner_satisfaction.values())) * 1.2)
        if cabinet.problem_queue:
            self._add_tension(state, "ministerial_strain", len(cabinet.problem_queue) * 10.0)
        municipal_heat = sum(max(0.0, m.protest_base - 50.0) for m in nation_state.municipalities.values())
        self._add_tension(state, "territorial_anger", municipal_heat / max(1, len(nation_state.municipalities)))
        if personalities:
            personality_stress = max((p.burnout + p.scandal_load + (100 - p.stress_tolerance)) / 3 for p in personalities.values())
            self._add_tension(state, "personality_crack", personality_stress * 0.5)

        self._spawn_endogenous(turn, nation_state, cabinet, parties, state)
        self._spawn_positive_window(turn, cabinet, parties, state)

    def emit_signals(self, turn: int, state: EventEngineState) -> None:
        for event in state.active_events:
            if event.current_stage == EventStage.LATENT and event.heat >= 30:
                event.current_stage = EventStage.SIGNAL
                event.visibility = min(1.0, event.visibility + 0.35)
                event.last_updated_turn = turn

    def advance_active_events(
        self,
        turn: int,
        state: EventEngineState,
        parties: list[Party],
        nation_state: NationState,
        cabinet: CabinetState,
        planned_actions: dict[str, list[str]] | None = None,
    ) -> None:
        actions = planned_actions or {}
        for event in state.active_events:
            for party in parties:
                party.mode = determine_party_mode(party, cabinet)
            if event.current_stage == EventStage.SIGNAL:
                pressure = 0.0
                for tags in actions.values():
                    if any(tag in {"attack", "investigation", "dramatize"} for tag in tags):
                        pressure += 3.0
                    if any(tag in {"crisis", "localize", "reframe"} for tag in tags):
                        pressure -= 2.0
                event.heat = max(0.0, min(100.0, event.heat + pressure))
                if event.heat >= 50:
                    event.current_stage = EventStage.ESCALATION
                    event.visibility = min(1.0, event.visibility + 0.25)
            if event.current_stage == EventStage.ESCALATION:
                delta_heat, delta_control = self._escalation_dynamics(event, parties, actions)
                event.heat = max(0.0, min(100.0, event.heat + delta_heat))
                event.controllability = max(0.0, min(100.0, event.controllability + delta_control))
                if event.heat >= 65 or turn - event.created_turn >= 2:
                    event.current_stage = EventStage.RESOLUTION
            if event.current_stage == EventStage.RESOLUTION:
                self._resolve_event(event, parties, nation_state, cabinet, state)
                event.current_stage = EventStage.MEMORY
                event.expires_after = turn + 3
            if event.current_stage == EventStage.MEMORY and event.expires_after is not None and turn >= event.expires_after:
                event.visibility = max(0.0, event.visibility - 0.2)
            event.last_updated_turn = turn

    def build_player_signals(self, state: EventEngineState) -> tuple[list[str], list[str], list[str]]:
        headlines: list[str] = []
        warnings: list[str] = []
        opportunities: list[str] = []
        for event in state.active_events:
            if event.visibility < 0.3:
                continue
            summary = f"{event.event_type.value}: {event.current_stage.value}"
            if event.event_type == EventType.POSITIVE_WINDOW:
                opportunities.append(summary)
            elif event.current_stage in (EventStage.SIGNAL, EventStage.ESCALATION):
                warnings.append(summary)
            else:
                headlines.append(summary)
        return headlines, warnings, opportunities

    def _resolve_event(
        self,
        event: PoliticalEvent,
        parties: list[Party],
        nation_state: NationState,
        cabinet: CabinetState,
        state: EventEngineState,
    ) -> None:
        success = event.controllability >= event.heat
        event.memory_effects = {
            "scandal_memory": event.heat * (0.06 if not success else 0.03),
            "competence_bonus": event.severity * (0.12 if success and event.event_type == EventType.POSITIVE_WINDOW else 0.0),
            "protest_residue": event.heat * (0.05 if event.event_type != EventType.POSITIVE_WINDOW else -0.04),
        }
        state.event_memory[event.id] = sum(event.memory_effects.values())

        target_set = set(event.target_actor_ids)
        for party in parties:
            mode_mult = {
                "government_lead": 1.25,
                "government_junior": 1.0,
                "parliamentary_opposition": 0.7,
                "extra_parliamentary": 0.85,
            }.get(party.mode.value, 1.0)
            if target_set and party.name not in target_set:
                mode_mult *= 0.6
            trust_hit = event.severity * (0.35 if not success else -0.2)
            if event.event_type == EventType.POSITIVE_WINDOW:
                trust_hit = -event.severity * 0.35
            party.resources.trust = max(0.0, min(100.0, party.resources.trust - trust_hit * mode_mult))
            party.resources.brand_wear = max(0.0, min(100.0, party.resources.brand_wear + event.severity * 0.2 * mode_mult))
            party.memory_markers[f"event_{event.id}_impact"] = trust_hit * mode_mult

        for district_id in event.territorial_footprint.get("district", []):
            district = nation_state.districts.get(district_id)
            if district:
                district.district_protest = max(0.0, min(100.0, district.district_protest + event.memory_effects["protest_residue"]))
                district.alerts.append(f"event:{event.event_type.value}")
        for municipality_id in event.territorial_footprint.get("municipality", []):
            municipality = nation_state.municipalities.get(municipality_id)
            if municipality:
                municipality.protest_base = max(0.0, min(100.0, municipality.protest_base + event.memory_effects["protest_residue"]))
                municipality.last_events.append(event.id)

        if event.event_type in (EventType.COALITION_CRISIS, EventType.CORRUPTION_SCANDAL):
            cabinet.current_stability = max(0.0, min(100.0, cabinet.current_stability - event.severity * (0.6 if not success else 0.25)))

    def _escalation_dynamics(
        self,
        event: PoliticalEvent,
        parties: list[Party],
        actions: dict[str, list[str]],
    ) -> tuple[float, float]:
        heat_delta = 4.0
        control_delta = -2.0
        for party in parties:
            tags = actions.get(party.name, [])
            if any(tag in {"crisis", "localize", "reframe"} for tag in tags):
                if party.mode.value in {"government_lead", "government_junior"}:
                    heat_delta -= 2.8
                    control_delta += 3.8
            if any(tag in {"attack", "dramatize", "investigation"} for tag in tags):
                heat_delta += 2.3
                if party.mode.value in {"parliamentary_opposition", "extra_parliamentary"}:
                    control_delta -= 0.8
            if any(tag in {"distance", "shift_blame"} for tag in tags) and party.mode.value == "government_junior":
                heat_delta += 1.2
                control_delta += 1.4
        return heat_delta, control_delta

    def _spawn_endogenous(
        self,
        turn: int,
        nation_state: NationState,
        cabinet: CabinetState,
        parties: list[Party],
        state: EventEngineState,
    ) -> None:
        if state.unresolved_tensions.get("budget_stress", 0.0) >= 35:
            self._ensure_event(
                state,
                PoliticalEvent(
                    id=f"gov_crisis_{turn}",
                    event_type=EventType.GOVERNANCE_CRISIS,
                    origin_type=EventOriginType.ENDOGENOUS,
                    severity=min(100.0, state.unresolved_tensions["budget_stress"]),
                    scope="cabinet",
                    source_actor_id=cabinet.pm_party,
                    target_actor_ids=[p.name for p in parties if p.role.value == "government"],
                    trigger_conditions={"budget_stress": state.unresolved_tensions["budget_stress"]},
                    heat=state.unresolved_tensions["budget_stress"],
                    controllability=55.0,
                    territorial_footprint={"district": list(nation_state.districts.keys())[:2]},
                    theme_links=("services", "economy"),
                    visibility=0.1,
                    created_turn=turn,
                ),
            )
        if state.unresolved_tensions.get("corruption_pressure", 0.0) >= 30:
            self._ensure_event(
                state,
                PoliticalEvent(
                    id=f"scandal_{turn}",
                    event_type=EventType.CORRUPTION_SCANDAL,
                    origin_type=EventOriginType.ENDOGENOUS,
                    severity=min(100.0, state.unresolved_tensions["corruption_pressure"]),
                    scope="cabinet",
                    source_actor_id=cabinet.pm_party,
                    target_actor_ids=[p.name for p in parties if p.role.value == "government"],
                    trigger_conditions={"corruption_pressure": state.unresolved_tensions["corruption_pressure"]},
                    heat=state.unresolved_tensions["corruption_pressure"],
                    controllability=40.0,
                    territorial_footprint={"national": ["LV"]},
                    theme_links=("corruption",),
                    visibility=0.0,
                    created_turn=turn,
                ),
            )

    def _spawn_positive_window(self, turn: int, cabinet: CabinetState, parties: list[Party], state: EventEngineState) -> None:
        avg_trust = sum(p.resources.trust for p in parties) / max(1, len(parties))
        if cabinet.cabinet_performance >= 62 and avg_trust >= 55:
            self._ensure_event(
                state,
                PoliticalEvent(
                    id=f"positive_window_{turn}",
                    event_type=EventType.POSITIVE_WINDOW,
                    origin_type=EventOriginType.ENDOGENOUS,
                    severity=min(100.0, (cabinet.cabinet_performance + avg_trust) / 2),
                    scope="national",
                    source_actor_id=cabinet.pm_party,
                    target_actor_ids=[p.name for p in parties if p.role.value == "government"],
                    trigger_conditions={"cabinet_performance": cabinet.cabinet_performance, "avg_trust": avg_trust},
                    heat=32.0,
                    controllability=65.0,
                    territorial_footprint={"national": ["LV"]},
                    theme_links=("governance",),
                    visibility=0.25,
                    created_turn=turn,
                ),
            )

    def _add_tension(self, state: EventEngineState, key: str, delta: float) -> None:
        state.unresolved_tensions[key] = max(0.0, min(100.0, state.unresolved_tensions.get(key, 0.0) * 0.7 + delta))

    def _ensure_event(self, state: EventEngineState, event: PoliticalEvent) -> None:
        if any(existing.id == event.id or (existing.event_type == event.event_type and existing.current_stage != EventStage.MEMORY) for existing in state.active_events):
            return
        state.active_events.append(event)
