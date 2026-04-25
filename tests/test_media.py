import unittest

from latvia_party_sim import (
    Archetype,
    AudienceProfile,
    BackgroundType,
    CabinetState,
    CareerState,
    EventEngineState,
    EventOriginType,
    EventStage,
    EventType,
    Gender,
    Leader,
    MediaEngine,
    MediaEngineState,
    MediaFormatType,
    MediaLine,
    MediaSlot,
    NationState,
    Party,
    PartyRole,
    ParliamentaryFaction,
    Personality,
    PersonalityArchetype,
    PoliticalEvent,
    RoleType,
    build_default_territory,
)


class MediaEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        municipalities, districts = build_default_territory()
        self.nation = NationState(turn=5, stage="mid", districts=districts, municipalities=municipalities)
        self.engine = MediaEngine()
        self.media_state = MediaEngineState()

    def _person(self, pid: str, debate: float, stress: float, burnout: float, trust: float = 55.0, growth: float = 55.0) -> Personality:
        return Personality(
            id=pid,
            first_name="A",
            last_name="B",
            full_name="A B",
            gender=Gender.MALE,
            age=42,
            district_affinity="RIGA",
            municipality_affinity=None,
            background_type=BackgroundType.MEDIA,
            role_type=RoleType.MINISTER,
            archetype=PersonalityArchetype.PUBLIC_LEADER,
            recognition=60,
            trust=trust,
            charisma=62,
            competence=58,
            debate=debate,
            loyalty=55,
            ambition=60,
            discipline=54,
            regional_power=60,
            coalition_acceptability=52,
            corruption_affinity=40,
            leak_risk=35,
            stress_tolerance=stress,
            betrayal_risk=30,
            media_hunger=60,
            ideological_rigidity=40,
            scandal_resilience=58,
            growth_potential=growth,
            burnout=burnout,
            scandal_load=30,
            career_state=CareerState.STABLE,
            party_fit=55,
            faction_alignment="core",
        )

    def test_hostile_format_rewards_debate_and_stress(self) -> None:
        slot = MediaSlot(
            id="m1", format_type=MediaFormatType.HARD_INTERVIEW, topic="scandal", pressure_level=70,
            audience_profile=AudienceProfile.NATIONAL_BROAD, hostility_level=80, target_actor_id=None,
            target_party_id="Gov", stage_context="mid", linked_scandal_id="s1", linked_issue="corruption",
            timing_importance=80,
        )
        party = Party("Gov", Archetype("a"), PartyRole.GOVERNMENT, Leader("L"), faction=ParliamentaryFaction(seats=30, in_coalition=True))
        strong = self._person("p1", debate=85, stress=80, burnout=20)
        weak = self._person("p2", debate=35, stress=30, burnout=70)
        good = self.engine.resolve_slot(slot, party, strong, MediaLine.RATIONAL_EXPLAIN, "mid", "government_lead")
        bad = self.engine.resolve_slot(slot, party, weak, MediaLine.RATIONAL_EXPLAIN, "mid", "government_lead")
        self.assertGreater(good.trust_figure_delta, bad.trust_figure_delta)

    def test_same_line_diff_context_changes_result(self) -> None:
        slot = MediaSlot(
            id="m2", format_type=MediaFormatType.BUDGET_EXPLAINER, topic="budget", pressure_level=50,
            audience_profile=AudienceProfile.MODERATE_TAXPAYERS, hostility_level=45, target_actor_id=None,
            target_party_id="Gov", stage_context="budget", linked_scandal_id=None, linked_issue="budget",
            timing_importance=70,
        )
        party = Party("Gov", Archetype("a"), PartyRole.GOVERNMENT, Leader("L"), faction=ParliamentaryFaction(seats=30, in_coalition=True))
        person = self._person("p1", debate=60, stress=60, burnout=20)
        same = self.engine.resolve_slot(slot, party, person, MediaLine.RATIONAL_EXPLAIN, "budget", "government_lead")
        mismatch = self.engine.resolve_slot(slot, party, person, MediaLine.RATIONAL_EXPLAIN, "mid", "government_lead")
        self.assertGreater(same.credibility_delta, mismatch.credibility_delta)

    def test_damage_control_reduces_scandal_heat(self) -> None:
        slot = MediaSlot(
            id="m3", format_type=MediaFormatType.CRISIS_BRIEFING, topic="scandal", pressure_level=60,
            audience_profile=AudienceProfile.NATIONAL_BROAD, hostility_level=70, target_actor_id=None,
            target_party_id="Gov", stage_context="mid", linked_scandal_id="scandal_1", linked_issue="corruption",
            timing_importance=85,
        )
        party = Party("Gov", Archetype("a"), PartyRole.GOVERNMENT, Leader("L"), faction=ParliamentaryFaction(seats=30, in_coalition=True))
        person = self._person("p1", debate=80, stress=85, burnout=10)
        res = self.engine.resolve_slot(slot, party, person, MediaLine.PARTIAL_ADMIT_FIX, "mid", "government_lead")
        self.assertLess(res.scandal_heat_delta, 0.0)

    def test_extra_parliamentary_gets_higher_visibility_upside(self) -> None:
        slot = MediaSlot(
            id="m4", format_type=MediaFormatType.NEW_FACE_LAUNCH, topic="entry", pressure_level=30,
            audience_profile=AudienceProfile.YOUTH_URBAN, hostility_level=25, target_actor_id=None,
            target_party_id="New", stage_context="mid", linked_scandal_id=None, linked_issue="visibility",
            timing_importance=60,
        )
        person = self._person("p1", debate=70, stress=70, burnout=10, growth=80)
        sys_party = Party("Sys", Archetype("a"), PartyRole.PARLIAMENTARY_OPPOSITION, Leader("S"), faction=ParliamentaryFaction(seats=20))
        new_party = Party("New", Archetype("a"), PartyRole.EXTRA_PARLIAMENTARY, Leader("N"), faction=ParliamentaryFaction(seats=0))
        res_sys = self.engine.resolve_slot(slot, sys_party, person, MediaLine.MOBILIZE_CORE, "mid", "parliamentary_opposition")
        res_new = self.engine.resolve_slot(slot, new_party, person, MediaLine.MOBILIZE_CORE, "mid", "extra_parliamentary")
        self.assertGreater(res_new.visibility_breakthrough_delta, res_sys.visibility_breakthrough_delta)

    def test_junior_partner_distancing_drives_distinctiveness(self) -> None:
        slot = MediaSlot(
            id="m5", format_type=MediaFormatType.HARD_INTERVIEW, topic="coalition", pressure_level=55,
            audience_profile=AudienceProfile.NATIONAL_BROAD, hostility_level=60, target_actor_id=None,
            target_party_id="Junior", stage_context="mid", linked_scandal_id=None, linked_issue="coalition",
            timing_importance=72,
        )
        person = self._person("p1", debate=70, stress=65, burnout=15)
        party = Party("Junior", Archetype("a"), PartyRole.GOVERNMENT, Leader("J"), faction=ParliamentaryFaction(seats=10, in_coalition=True))
        res = self.engine.resolve_slot(slot, party, person, MediaLine.DISTANCE, "mid", "government_junior")
        self.assertGreater(res.distinctiveness_delta, 0.0)

    def test_regional_affinity_impacts_territorial_resolution(self) -> None:
        slot = MediaSlot(
            id="m6", format_type=MediaFormatType.REGIONAL_BROADCAST, topic="transport", pressure_level=40,
            audience_profile=AudienceProfile.REGIONAL_PUBLIC, hostility_level=35, target_actor_id=None,
            target_party_id="Reg", stage_context="mid", linked_scandal_id=None, linked_issue="services",
            timing_importance=55, territorial_relevance={"district": ["LATGALE"]},
        )
        party = Party("Reg", Archetype("a"), PartyRole.PARLIAMENTARY_OPPOSITION, Leader("R"), faction=ParliamentaryFaction(seats=12))
        person = self._person("p1", debate=68, stress=66, burnout=12)
        res = self.engine.resolve_slot(slot, party, person, MediaLine.RATIONAL_EXPLAIN, "mid", "parliamentary_opposition")
        self.assertIn("LATGALE", res.territorial_mood_delta_map)

    def test_no_direct_polling_shift_only_intermediate_deltas(self) -> None:
        party = Party("Gov", Archetype("a"), PartyRole.GOVERNMENT, Leader("L"), faction=ParliamentaryFaction(seats=30, in_coalition=True))
        slot = MediaSlot(
            id="m7", format_type=MediaFormatType.SOFT_PROGRAM, topic="program", pressure_level=20,
            audience_profile=AudienceProfile.NATIONAL_BROAD, hostility_level=20, target_actor_id=None,
            target_party_id="Gov", stage_context="mid", linked_scandal_id=None, linked_issue="program",
            timing_importance=40,
        )
        person = self._person("p1", debate=65, stress=60, burnout=10)
        res = self.engine.resolve_slot(slot, party, person, MediaLine.MORAL_HIGH_GROUND, "mid", "government_lead")
        before_rating = party.memory_markers.get("national_rating")
        self.engine.apply_resolution(slot, res, party, self.nation, CabinetState(exists=True, pm_party="Gov"), EventEngineState(), self.media_state)
        after_rating = party.memory_markers.get("national_rating")
        self.assertEqual(before_rating, after_rating)
        self.assertIn("media_credibility", party.memory_markers)

    def test_slots_spawn_from_events_and_opportunities(self) -> None:
        cabinet = CabinetState(exists=True, pm_party="Gov")
        gov = Party("Gov", Archetype("a"), PartyRole.GOVERNMENT, Leader("L"), faction=ParliamentaryFaction(seats=30, in_coalition=True))
        extra = Party("New", Archetype("a"), PartyRole.EXTRA_PARLIAMENTARY, Leader("N"), faction=ParliamentaryFaction(seats=0))
        extra.resources.activist_energy = 70
        event_state = EventEngineState(active_events=[PoliticalEvent(
            id="sc1", event_type=EventType.CORRUPTION_SCANDAL, origin_type=EventOriginType.ENDOGENOUS,
            severity=70, scope="cabinet", source_actor_id="Gov", target_actor_ids=["Gov"], trigger_conditions={"x": 1},
            current_stage=EventStage.SIGNAL, heat=65, visibility=0.7,
        )])
        self.engine.generate_slots(5, "mid", cabinet, [gov, extra], event_state, self.media_state)
        self.assertTrue(any(slot.linked_scandal_id == "sc1" for slot in self.media_state.active_slots))
        self.assertTrue(any(slot.target_party_id == "New" for slot in self.media_state.active_slots))


if __name__ == "__main__":
    unittest.main()
