from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .cabinet import CabinetState
from .events import EventEngineState, EventStage, EventType
from .models import Party
from .party_mode import determine_party_mode
from .personality import Personality
from .territory import NationState


class MediaFormatType(str, Enum):
    HARD_INTERVIEW = "hard_interview"
    SOFT_PROGRAM = "soft_program"
    CRISIS_BRIEFING = "crisis_briefing"
    BUDGET_EXPLAINER = "budget_explainer"
    DEBATE = "debate"
    REGIONAL_BROADCAST = "regional_broadcast"
    NEW_FACE_LAUNCH = "new_face_launch"


class AudienceProfile(str, Enum):
    NATIONAL_BROAD = "national_broad"
    URBAN_CENTER = "urban_center"
    REGIONAL_PUBLIC = "regional_public"
    PROTEST_VIEWERS = "protest_viewers"
    MODERATE_TAXPAYERS = "moderate_taxpayers"
    CORE_VALUE_BASE = "core_value_base"
    YOUTH_URBAN = "youth_urban"


class MediaLine(str, Enum):
    RATIONAL_EXPLAIN = "rational_explain"
    PARTIAL_ADMIT_FIX = "partial_admit_fix"
    COUNTER_ATTACK = "counter_attack"
    PROCEDURALIZE = "proceduralize"
    SHIFT_BLAME = "shift_blame"
    MOBILIZE_CORE = "mobilize_core"
    DE_ESCALATE = "de_escalate"
    DISTANCE = "distance"
    MORAL_HIGH_GROUND = "moral_high_ground"
    PERSONALIZE_CONFLICT = "personalize_conflict"


@dataclass(slots=True)
class MediaSlot:
    id: str
    format_type: MediaFormatType
    topic: str
    pressure_level: float
    audience_profile: AudienceProfile
    hostility_level: float
    target_actor_id: str | None
    target_party_id: str | None
    stage_context: str
    linked_scandal_id: str | None
    linked_issue: str | None
    timing_importance: float
    territorial_relevance: dict[str, list[str]] = field(default_factory=dict)
    resolution_window: int = 1
    visibility: float = 0.5
    upside_potential: float = 50.0
    downside_risk: float = 50.0
    expires_on_turn: int = 0


@dataclass(slots=True)
class MediaResolution:
    issue_ownership_delta: float = 0.0
    scandal_heat_delta: float = 0.0
    trust_figure_delta: float = 0.0
    leader_momentum_delta: float = 0.0
    cabinet_credibility_delta: float = 0.0
    coalition_tension_delta: float = 0.0
    territorial_mood_delta_map: dict[str, float] = field(default_factory=dict)
    segment_fit_delta: float = 0.0
    distinctiveness_delta: float = 0.0
    credibility_delta: float = 0.0
    brand_freshness_delta: float = 0.0
    visibility_breakthrough_delta: float = 0.0
    media_followup_risk_delta: float = 0.0


@dataclass(slots=True)
class MediaEngineState:
    active_slots: list[MediaSlot] = field(default_factory=list)
    followup_flags: dict[str, float] = field(default_factory=dict)


_FORMAT_PROFILE: dict[MediaFormatType, tuple[float, float, str]] = {
    MediaFormatType.HARD_INTERVIEW: (1.3, 1.4, "debate"),
    MediaFormatType.SOFT_PROGRAM: (0.8, 0.9, "charisma"),
    MediaFormatType.CRISIS_BRIEFING: (1.2, 1.5, "stress_tolerance"),
    MediaFormatType.BUDGET_EXPLAINER: (1.0, 1.1, "competence"),
    MediaFormatType.DEBATE: (1.25, 1.35, "debate"),
    MediaFormatType.REGIONAL_BROADCAST: (0.9, 1.0, "regional_power"),
    MediaFormatType.NEW_FACE_LAUNCH: (1.1, 1.25, "growth_potential"),
}


class MediaEngine:
    def generate_slots(
        self,
        turn: int,
        stage_context: str,
        cabinet: CabinetState,
        parties: list[Party],
        event_state: EventEngineState,
        state: MediaEngineState,
    ) -> None:
        state.active_slots = [slot for slot in state.active_slots if slot.expires_on_turn >= turn]
        # forced appearances from events
        for event in event_state.active_events:
            if event.current_stage not in {EventStage.SIGNAL, EventStage.ESCALATION}:
                continue
            fmt = MediaFormatType.CRISIS_BRIEFING if event.event_type in {EventType.CORRUPTION_SCANDAL, EventType.GOVERNANCE_CRISIS} else MediaFormatType.HARD_INTERVIEW
            slot = MediaSlot(
                id=f"media_{event.id}_{turn}",
                format_type=fmt,
                topic=event.event_type.value,
                pressure_level=event.heat,
                audience_profile=AudienceProfile.NATIONAL_BROAD,
                hostility_level=min(100.0, event.heat + 15),
                target_actor_id=None,
                target_party_id=event.source_actor_id,
                stage_context=stage_context,
                linked_scandal_id=event.id if event.event_type == EventType.CORRUPTION_SCANDAL else None,
                linked_issue=event.event_type.value,
                timing_importance=event.visibility * 100,
                territorial_relevance=event.territorial_footprint,
                resolution_window=2,
                visibility=event.visibility,
                upside_potential=65,
                downside_risk=70,
                expires_on_turn=turn + 1,
            )
            self._add_unique_slot(state, slot)

        # opportunity slots
        for party in parties:
            party_mode = determine_party_mode(party, cabinet).value
            if party_mode == "extra_parliamentary" and party.resources.activist_energy > 55:
                self._add_unique_slot(
                    state,
                    MediaSlot(
                        id=f"media_breakthrough_{party.name}_{turn}",
                        format_type=MediaFormatType.NEW_FACE_LAUNCH,
                        topic="new_face",
                        pressure_level=35,
                        audience_profile=AudienceProfile.YOUTH_URBAN,
                        hostility_level=30,
                        target_actor_id=None,
                        target_party_id=party.name,
                        stage_context=stage_context,
                        linked_scandal_id=None,
                        linked_issue="visibility",
                        timing_importance=65,
                        territorial_relevance={},
                        resolution_window=1,
                        visibility=0.55,
                        upside_potential=75,
                        downside_risk=45,
                        expires_on_turn=turn,
                    ),
                )

    def resolve_slot(
        self,
        slot: MediaSlot,
        party: Party,
        personality: Personality,
        line: MediaLine,
        stage_context: str,
        party_mode: str,
    ) -> MediaResolution:
        volatility, risk_mult, key_stat = _FORMAT_PROFILE[slot.format_type]
        line_fit = self._line_fit(line, slot, party_mode)
        context_fit = 1.15 if stage_context == slot.stage_context else 0.9
        stat_value = float(getattr(personality, key_stat if key_stat != "debate" else "debate"))
        trust_base = (personality.trust + personality.recognition) / 2
        stress_score = (personality.stress_tolerance - personality.burnout * 0.7 + personality.scandal_resilience * 0.4)
        media_hunger_adjust = (personality.media_hunger - 50) * 0.08

        performance = (stat_value * 0.35 + trust_base * 0.25 + stress_score * 0.25 + media_hunger_adjust + line_fit * 20) * context_fit
        pressure_penalty = slot.pressure_level * 0.45 + slot.hostility_level * 0.35 + slot.downside_risk * 0.2 * risk_mult
        net = performance - pressure_penalty

        mode_upside = {"government_lead": 0.9, "government_junior": 1.0, "parliamentary_opposition": 1.05, "extra_parliamentary": 1.25}.get(party_mode, 1.0)
        mode_distinct = 1.2 if party_mode == "government_junior" and line == MediaLine.DISTANCE else 0.5

        resolution = MediaResolution()
        resolution.issue_ownership_delta = net * 0.08 * volatility
        resolution.trust_figure_delta = net * 0.06
        resolution.leader_momentum_delta = net * 0.07 * mode_upside
        resolution.segment_fit_delta = net * 0.05
        resolution.credibility_delta = net * 0.06
        resolution.distinctiveness_delta = net * 0.05 * mode_distinct
        resolution.brand_freshness_delta = net * 0.04 * (1.2 if party_mode == "extra_parliamentary" else 0.6)
        resolution.visibility_breakthrough_delta = net * 0.09 * (1.4 if party_mode == "extra_parliamentary" else 0.5)
        resolution.cabinet_credibility_delta = net * 0.05 if party_mode in {"government_lead", "government_junior"} else -net * 0.02
        resolution.coalition_tension_delta = (-net * 0.04) if line in {MediaLine.DE_ESCALATE, MediaLine.RATIONAL_EXPLAIN} else (net * 0.03 if line == MediaLine.DISTANCE else 0.0)

        if slot.linked_scandal_id:
            resolution.scandal_heat_delta = -max(0.0, net) * 0.12 + max(0.0, -net) * 0.1

        if net < -5:
            resolution.media_followup_risk_delta = abs(net) * 0.08
        else:
            resolution.media_followup_risk_delta = -net * 0.03

        if slot.audience_profile == AudienceProfile.REGIONAL_PUBLIC or slot.format_type == MediaFormatType.REGIONAL_BROADCAST:
            for district in slot.territorial_relevance.get("district", []):
                resolution.territorial_mood_delta_map[district] = net * 0.08

        return resolution

    def apply_resolution(
        self,
        slot: MediaSlot,
        resolution: MediaResolution,
        party: Party,
        nation_state: NationState,
        cabinet: CabinetState,
        event_state: EventEngineState,
        state: MediaEngineState,
    ) -> None:
        party.memory_markers["issue_ownership"] = party.memory_markers.get("issue_ownership", party.resources.agenda_control) + resolution.issue_ownership_delta
        party.memory_markers["leader_momentum"] = party.memory_markers.get("leader_momentum", 50.0) + resolution.leader_momentum_delta
        party.memory_markers["media_credibility"] = party.memory_markers.get("media_credibility", 50.0) + resolution.credibility_delta
        party.memory_markers["distinctiveness"] = party.memory_markers.get("distinctiveness", 50.0) + resolution.distinctiveness_delta
        party.memory_markers["visibility_breakthrough"] = party.memory_markers.get("visibility_breakthrough", 0.0) + resolution.visibility_breakthrough_delta
        party.resources.trust = max(0.0, min(100.0, party.resources.trust + resolution.trust_figure_delta * 0.25))

        cabinet.competence_image = max(0.0, min(100.0, cabinet.competence_image + resolution.cabinet_credibility_delta * 0.2))
        if cabinet.exists:
            cabinet.current_stability = max(0.0, min(100.0, cabinet.current_stability - resolution.coalition_tension_delta * 0.2))

        for event in event_state.active_events:
            if slot.linked_scandal_id and event.id == slot.linked_scandal_id:
                event.heat = max(0.0, min(100.0, event.heat + resolution.scandal_heat_delta))

        for district_id, delta in resolution.territorial_mood_delta_map.items():
            district = nation_state.districts.get(district_id)
            if district:
                district.district_protest = max(0.0, min(100.0, district.district_protest - delta * 0.1))

        state.followup_flags[f"followup_{slot.id}"] = state.followup_flags.get(f"followup_{slot.id}", 0.0) + resolution.media_followup_risk_delta

    def _line_fit(self, line: MediaLine, slot: MediaSlot, party_mode: str) -> float:
        if slot.format_type == MediaFormatType.BUDGET_EXPLAINER and line in {MediaLine.RATIONAL_EXPLAIN, MediaLine.PARTIAL_ADMIT_FIX}:
            return 1.4
        if slot.linked_scandal_id and line in {MediaLine.PARTIAL_ADMIT_FIX, MediaLine.DE_ESCALATE, MediaLine.RATIONAL_EXPLAIN}:
            return 1.3
        if party_mode == "government_junior" and line == MediaLine.DISTANCE:
            return 1.35
        if party_mode == "parliamentary_opposition" and line in {MediaLine.COUNTER_ATTACK, MediaLine.PERSONALIZE_CONFLICT}:
            return 1.3
        if party_mode == "extra_parliamentary" and line in {MediaLine.MOBILIZE_CORE, MediaLine.MORAL_HIGH_GROUND}:
            return 1.25
        return 1.0

    def _add_unique_slot(self, state: MediaEngineState, slot: MediaSlot) -> None:
        if any(existing.id == slot.id for existing in state.active_slots):
            return
        state.active_slots.append(slot)
