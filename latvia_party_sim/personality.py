from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import random


class Gender(str, Enum):
    FEMALE = "female"
    MALE = "male"


class BackgroundType(str, Enum):
    MUNICIPAL = "municipal"
    PARTY_APPARATUS = "party_apparatus"
    STATE_ADMIN = "state_admin"
    BUSINESS = "business"
    MEDIA = "media"
    NGO = "ngo"
    ACADEMIA = "academia"
    SECURITY = "security"
    LEGAL = "legal"
    SOCIAL = "social"


class PersonalityArchetype(str, Enum):
    PUBLIC_LEADER = "public_leader"
    TECHNOCRAT = "technocrat"
    APPARATCHIK = "apparatchik"
    REGIONAL_PATRON = "regional_patron"
    IDEOLOGUE = "ideologue"
    COALITION_NEGOTIATOR = "coalition_negotiator"
    YOUNG_REFORMER = "young_reformer"
    MEDIA_POPULIST = "media_populist"
    CRISIS_MANAGER = "crisis_manager"
    SHADOW_BROKER = "shadow_broker"
    CAREERIST = "careerist"
    SECOND_NUMBER = "second_number"


class CareerState(str, Enum):
    RISING = "rising"
    STABLE = "stable"
    OVEREXPOSED = "overexposed"
    BURNED_OUT = "burned_out"
    COMPROMISED = "compromised"
    EMBOLDENED = "emboldened"
    MARGINALISED = "marginalised"
    REBELLIOUS = "rebellious"


class RoleType(str, Enum):
    PARTY_LEADER = "party_leader"
    MINISTER = "minister"
    FACTION_OPERATOR = "faction_operator"
    REGIONAL_CARRIER = "regional_carrier"
    CAMPAIGN_FACE = "campaign_face"


OPEN_KEYS = (
    "recognition",
    "trust",
    "charisma",
    "competence",
    "debate",
    "loyalty",
    "ambition",
    "discipline",
    "regional_power",
    "coalition_acceptability",
)

HIDDEN_KEYS = (
    "corruption_affinity",
    "leak_risk",
    "stress_tolerance",
    "betrayal_risk",
    "media_hunger",
    "ideological_rigidity",
    "scandal_resilience",
    "growth_potential",
)


@dataclass(slots=True)
class ArchetypePreset:
    id: PersonalityArchetype
    display_name: str
    open_stat_ranges: dict[str, tuple[int, int]]
    hidden_stat_ranges: dict[str, tuple[int, int]]
    preferred_roles: dict[RoleType, int]
    typical_backgrounds: tuple[BackgroundType, ...]
    typical_quirks: tuple[str, ...]
    party_affinity_weights: dict[str, float]
    career_state_bias: tuple[CareerState, ...]
    corruption_profile: str
    scandal_profile: str


@dataclass(slots=True)
class Personality:
    id: str
    first_name: str
    last_name: str
    full_name: str
    gender: Gender
    age: int
    district_affinity: str
    municipality_affinity: str | None
    background_type: BackgroundType
    role_type: RoleType
    archetype: PersonalityArchetype

    recognition: float
    trust: float
    charisma: float
    competence: float
    debate: float
    loyalty: float
    ambition: float
    discipline: float
    regional_power: float
    coalition_acceptability: float

    corruption_affinity: float
    leak_risk: float
    stress_tolerance: float
    betrayal_risk: float
    media_hunger: float
    ideological_rigidity: float
    scandal_resilience: float
    growth_potential: float

    burnout: float
    scandal_load: float
    career_state: CareerState
    party_fit: float
    faction_alignment: str
    quirks: list[str] = field(default_factory=list)
    relations: dict[str, float] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self.first_name

    @property
    def surname(self) -> str:
        return self.last_name

    @property
    def region_affinity(self) -> str:
        return self.district_affinity


LATVIAN_MALE_NAMES = ["Jānis", "Andris", "Mārtiņš", "Edgars", "Artūrs", "Rihards"]
LATVIAN_FEMALE_NAMES = ["Agnese", "Ilze", "Liene", "Elīna", "Inese", "Marta"]
LATVIAN_SURNAMES = ["Bērziņš", "Kalniņš", "Ozols", "Liepiņš", "Balodis", "Krūmiņa", "Aboltiņa", "Lapiņa", "Vilks", "Siliņš"]


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def _r(rng: random.Random, lo: int, hi: int) -> float:
    return float(rng.randint(lo, hi))


def _mk_preset(arch: PersonalityArchetype, open_mid: dict[str, tuple[int, int]], hidden_mid: dict[str, tuple[int, int]], quirks: tuple[str, ...], bgs: tuple[BackgroundType, ...], roles: dict[RoleType, int], corruption_profile: str, scandal_profile: str) -> ArchetypePreset:
    return ArchetypePreset(
        id=arch,
        display_name=arch.value,
        open_stat_ranges=open_mid,
        hidden_stat_ranges=hidden_mid,
        preferred_roles=roles,
        typical_backgrounds=bgs,
        typical_quirks=quirks,
        party_affinity_weights={"technocratic": 1.0, "protest": 1.0, "regional": 1.0},
        career_state_bias=(CareerState.STABLE, CareerState.RISING),
        corruption_profile=corruption_profile,
        scandal_profile=scandal_profile,
    )


ARCHETYPE_PRESETS: dict[PersonalityArchetype, ArchetypePreset] = {
    PersonalityArchetype.PUBLIC_LEADER: _mk_preset(
        PersonalityArchetype.PUBLIC_LEADER,
        {"recognition": (70, 95), "trust": (45, 80), "charisma": (70, 95), "competence": (40, 75), "debate": (65, 90), "loyalty": (35, 75), "ambition": (60, 90), "discipline": (35, 70), "regional_power": (25, 60), "coalition_acceptability": (35, 75)},
        {"corruption_affinity": (20, 60), "leak_risk": (25, 60), "stress_tolerance": (35, 70), "betrayal_risk": (30, 65), "media_hunger": (70, 95), "ideological_rigidity": (25, 65), "scandal_resilience": (35, 70), "growth_potential": (35, 70)},
        ("magnet_for_cameras", "says_too_much", "crowd_instinct"),
        (BackgroundType.MEDIA, BackgroundType.BUSINESS, BackgroundType.NGO),
        {RoleType.PARTY_LEADER: 5, RoleType.CAMPAIGN_FACE: 5, RoleType.MINISTER: 2, RoleType.FACTION_OPERATOR: 1, RoleType.REGIONAL_CARRIER: 2},
        "opportunistic", "overexposure",
    ),
    PersonalityArchetype.TECHNOCRAT: _mk_preset(
        PersonalityArchetype.TECHNOCRAT,
        {"recognition": (30, 70), "trust": (60, 90), "charisma": (20, 55), "competence": (75, 95), "debate": (35, 70), "loyalty": (45, 80), "ambition": (30, 65), "discipline": (60, 90), "regional_power": (15, 45), "coalition_acceptability": (55, 90)},
        {"corruption_affinity": (15, 45), "leak_risk": (10, 35), "stress_tolerance": (55, 85), "betrayal_risk": (15, 40), "media_hunger": (15, 45), "ideological_rigidity": (25, 60), "scandal_resilience": (45, 80), "growth_potential": (25, 55)},
        ("strong_in_numbers", "cabinet_style", "bad_showman"),
        (BackgroundType.STATE_ADMIN, BackgroundType.ACADEMIA, BackgroundType.LEGAL),
        {RoleType.PARTY_LEADER: 4, RoleType.CAMPAIGN_FACE: 2, RoleType.MINISTER: 5, RoleType.FACTION_OPERATOR: 3, RoleType.REGIONAL_CARRIER: 1},
        "controlled", "performance_failure",
    ),
    PersonalityArchetype.APPARATCHIK: _mk_preset(
        PersonalityArchetype.APPARATCHIK,
        {k: (20, 80) for k in OPEN_KEYS},
        {k: (20, 80) for k in HIDDEN_KEYS},
        ("list_keeper", "remembers_everything", "loyal_machine"),
        (BackgroundType.PARTY_APPARATUS, BackgroundType.MUNICIPAL),
        {RoleType.PARTY_LEADER: 1, RoleType.CAMPAIGN_FACE: 1, RoleType.MINISTER: 2, RoleType.FACTION_OPERATOR: 5, RoleType.REGIONAL_CARRIER: 2},
        "clientelist", "internal_leak",
    ),
}
# Fill remaining archetypes using balanced fallback ranges.
for arch in PersonalityArchetype:
    if arch not in ARCHETYPE_PRESETS:
        ARCHETYPE_PRESETS[arch] = _mk_preset(
            arch,
            {k: (30, 75) for k in OPEN_KEYS},
            {k: (20, 75) for k in HIDDEN_KEYS},
            ("adaptive", "volatile"),
            (BackgroundType.PARTY_APPARATUS, BackgroundType.MEDIA, BackgroundType.STATE_ADMIN),
            {r: 3 for r in RoleType},
            "mixed",
            "mixed",
        )


def _apply_background_modifiers(person: Personality) -> None:
    bg = person.background_type
    if bg == BackgroundType.MUNICIPAL:
        person.regional_power = _clamp(person.regional_power + 10)
        person.recognition = _clamp(person.recognition - 5)
    elif bg == BackgroundType.PARTY_APPARATUS:
        person.discipline = _clamp(person.discipline + 8)
        person.charisma = _clamp(person.charisma - 5)
    elif bg == BackgroundType.STATE_ADMIN:
        person.competence = _clamp(person.competence + 8)
    elif bg == BackgroundType.BUSINESS:
        person.corruption_affinity = _clamp(person.corruption_affinity + 8)
    elif bg == BackgroundType.MEDIA:
        person.recognition = _clamp(person.recognition + 10)
        person.media_hunger = _clamp(person.media_hunger + 8)


def _apply_age_modifiers(person: Personality) -> None:
    if person.age <= 32:
        person.growth_potential = _clamp(person.growth_potential + 10)
        person.stress_tolerance = _clamp(person.stress_tolerance - 8)
    elif person.age >= 61:
        person.recognition = _clamp(person.recognition + 5)
        person.burnout = _clamp(person.burnout + 8)


def compute_party_fit(person: Personality, party_profile: str = "balanced") -> float:
    if party_profile == "technocratic":
        fit = person.competence * 0.4 + person.discipline * 0.3 + person.coalition_acceptability * 0.3
    elif party_profile == "protest":
        fit = person.charisma * 0.4 + person.debate * 0.3 + person.media_hunger * 0.3
    elif party_profile == "regional":
        fit = person.regional_power * 0.5 + person.loyalty * 0.3 + person.discipline * 0.2
    else:
        fit = (person.competence + person.charisma + person.loyalty) / 3
    return _clamp(fit)


def generate_personality(
    uid: int,
    region_affinity: str,
    role_type: RoleType,
    archetype: PersonalityArchetype,
    seed: int = 0,
    party_profile: str = "balanced",
) -> Personality:
    """Fixed pipeline:
    1) gender
    2) name/surname
    3) age
    4) district affinity
    5) background
    6) archetype
    7) open stats
    8) background+age modifiers
    9) hidden stats
    10) quirks
    11) relations/faction
    12) party fit
    13) start role/career state
    """
    rng = random.Random(seed + uid)
    preset = ARCHETYPE_PRESETS[archetype]

    gender = rng.choice([Gender.MALE, Gender.FEMALE])
    first_name = rng.choice(LATVIAN_MALE_NAMES if gender == Gender.MALE else LATVIAN_FEMALE_NAMES)
    last_name = rng.choice(LATVIAN_SURNAMES)
    if rng.random() < 0.18:
        second = rng.choice(LATVIAN_SURNAMES)
        if second != last_name:
            last_name = f"{last_name}-{second}"

    age = rng.randint(24, 68)
    background_type = rng.choice(preset.typical_backgrounds)

    stats: dict[str, float] = {}
    for k, (lo, hi) in preset.open_stat_ranges.items():
        stats[k] = _r(rng, lo, hi)
    for k, (lo, hi) in preset.hidden_stat_ranges.items():
        stats[k] = _r(rng, lo, hi)

    quirk1 = rng.choice(preset.typical_quirks)
    quirks = [quirk1]
    if rng.random() < 0.35:
        quirks.append(rng.choice(preset.typical_quirks))

    person = Personality(
        id=f"pers_{uid}",
        first_name=first_name,
        last_name=last_name,
        full_name=f"{first_name} {last_name}",
        gender=gender,
        age=age,
        district_affinity=region_affinity,
        municipality_affinity=None,
        background_type=background_type,
        role_type=role_type,
        archetype=archetype,
        recognition=stats["recognition"],
        trust=stats["trust"],
        charisma=stats["charisma"],
        competence=stats["competence"],
        debate=stats["debate"],
        loyalty=stats["loyalty"],
        ambition=stats["ambition"],
        discipline=stats["discipline"],
        regional_power=stats["regional_power"],
        coalition_acceptability=stats["coalition_acceptability"],
        corruption_affinity=stats["corruption_affinity"],
        leak_risk=stats["leak_risk"],
        stress_tolerance=stats["stress_tolerance"],
        betrayal_risk=stats["betrayal_risk"],
        media_hunger=stats["media_hunger"],
        ideological_rigidity=stats["ideological_rigidity"],
        scandal_resilience=stats["scandal_resilience"],
        growth_potential=stats["growth_potential"],
        burnout=_r(rng, 5, 30),
        scandal_load=_r(rng, 0, 20),
        career_state=rng.choice(preset.career_state_bias),
        party_fit=50.0,
        faction_alignment=rng.choice(["ideological", "apparatus", "regional", "youth", "pragmatic"]),
        quirks=quirks,
        relations={"leader": _r(rng, 20, 80), "patron": _r(rng, 0, 70), "rival": _r(rng, 0, 70)},
    )

    _apply_background_modifiers(person)
    _apply_age_modifiers(person)
    person.party_fit = compute_party_fit(person, party_profile)
    return person


def holder_quality_for_portfolio(personality: Personality, portfolio_id: str) -> float:
    quality = (
        personality.competence * 0.30
        + personality.discipline * 0.18
        + personality.stress_tolerance * 0.18
        + (100 - personality.burnout) * 0.12
        + personality.trust * 0.10
        + personality.loyalty * 0.07
        + (100 - personality.scandal_load) * 0.05
    )

    if portfolio_id in {"finance", "economy"}:
        quality += (personality.competence - 50) * 0.20
    if portfolio_id in {"regional_development", "transport"}:
        quality += (personality.regional_power - 50) * 0.22
    if portfolio_id in {"health", "welfare"}:
        quality += (personality.trust - 50) * 0.15
    if portfolio_id in {"justice", "culture"}:
        quality += (personality.debate - 50) * 0.10

    return _clamp(quality)
