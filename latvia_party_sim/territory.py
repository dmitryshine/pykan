from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class MunicipalityType(str, Enum):
    CAPITAL = "capital"
    MAJOR_CITY = "major_city"
    MID_CITY = "mid_city"
    MIXED_NOVADS = "mixed_novads"
    PERIPHERAL_NOVADS = "peripheral_novads"
    BORDER_SENSITIVE_NOVADS = "border_sensitive_novads"


@dataclass(slots=True)
class Municipality:
    id: str
    name: str
    district_id: str
    municipality_type: MunicipalityType
    weight_population: float
    urbanity: float
    turnout_base: float
    protest_base: float
    government_mood: float = 50.0
    theme_profile: dict[str, float] = field(default_factory=dict)
    party_network_strength: dict[str, float] = field(default_factory=dict)
    party_local_support: dict[str, float] = field(default_factory=dict)
    local_elite_power: float = 50.0
    new_party_openness: float = 50.0
    crisis_risk: float = 20.0
    volatility: float = 40.0
    last_events: list[str] = field(default_factory=list)
    trend_vector: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class District:
    id: str
    name: str
    municipality_ids: list[str]
    seat_weight_proxy: float
    district_support: dict[str, float] = field(default_factory=dict)
    district_turnout: float = 0.0
    district_network_score: float = 0.0
    district_protest: float = 0.0
    dominant_themes: list[str] = field(default_factory=list)
    swing_index: float = 0.0
    government_penalty: float = 0.0
    opposition_window: float = 0.0
    campaign_heat: float = 0.0
    alerts: list[str] = field(default_factory=list)


@dataclass(slots=True)
class NationState:
    turn: int
    stage: str
    districts: dict[str, District]
    municipalities: dict[str, Municipality]
    national_theme_pressure: dict[str, float] = field(default_factory=dict)


def _mid(default: float = 50.0) -> dict[str, float]:
    return {
        "economy": default,
        "security": default,
        "identity": default,
        "welfare": default,
        "regions": default,
        "services": default,
        "corruption": default,
    }


def default_municipality(name: str, district_id: str, mtype: MunicipalityType) -> Municipality:
    return Municipality(
        id=name.lower().replace(" ", "_").replace("ē", "e").replace("ā", "a").replace("ū", "u").replace("ī", "i").replace("ķ", "k").replace("ģ", "g").replace("ļ", "l").replace("ņ", "n").replace("ž", "z").replace("č", "c").replace("š", "s").replace("ū", "u"),
        name=name,
        district_id=district_id,
        municipality_type=mtype,
        weight_population=1.0,
        urbanity=70.0 if "novads" not in name else 45.0,
        turnout_base=62.0,
        protest_base=35.0,
        theme_profile=_mid(),
        trend_vector={"support": 0.0, "turnout": 0.0, "protest": 0.0},
    )


DISTRICT_TO_MUNICIPALITIES: dict[str, list[str]] = {
    "RIGA": ["Rīga"],
    "VIDZEME": [
        "Jūrmala",
        "Alūksnes novads",
        "Ādažu novads",
        "Cēsu novads",
        "Gulbenes novads",
        "Ķekavas novads",
        "Limbažu novads",
        "Madonas novads",
        "Mārupes novads",
        "Ogres novads",
        "Olaines novads",
        "Ropažu novads",
        "Salaspils novads",
        "Saulkrastu novads",
        "Siguldas novads",
        "Smiltenes novads",
        "Valkas novads",
        "Valmieras novads",
    ],
    "LATGALE": [
        "Daugavpils",
        "Rēzekne",
        "Augšdaugavas novads",
        "Balvu novads",
        "Krāslavas novads",
        "Līvānu novads",
        "Ludzas novads",
        "Preiļu novads",
        "Rēzeknes novads",
    ],
    "KURZEME": [
        "Liepāja",
        "Ventspils",
        "Dienvidkurzemes novads",
        "Kuldīgas novads",
        "Saldus novads",
        "Talsu novads",
        "Ventspils novads",
    ],
    "ZEMGALE": [
        "Jelgava",
        "Aizkraukles novads",
        "Bauskas novads",
        "Dobeles novads",
        "Jelgavas novads",
        "Jēkabpils novads",
        "Tukuma novads",
    ],
}


def build_default_territory() -> tuple[dict[str, Municipality], dict[str, District]]:
    municipalities: dict[str, Municipality] = {}
    districts: dict[str, District] = {}

    for district_id, names in DISTRICT_TO_MUNICIPALITIES.items():
        m_ids: list[str] = []
        for name in names:
            if name == "Rīga":
                mtype = MunicipalityType.CAPITAL
            elif "novads" in name:
                mtype = MunicipalityType.MIXED_NOVADS
            else:
                mtype = MunicipalityType.MAJOR_CITY

            m = default_municipality(name, district_id, mtype)
            municipalities[m.id] = m
            m_ids.append(m.id)

        districts[district_id] = District(
            id=district_id,
            name=district_id.title(),
            municipality_ids=m_ids,
            seat_weight_proxy=float(len(m_ids)),
        )

    return municipalities, districts


def aggregate_district_metrics(
    district: District,
    municipalities: dict[str, Municipality],
    party_key: str,
) -> District:
    subset = [municipalities[mid] for mid in district.municipality_ids]
    total_weight = sum(max(0.1, m.weight_population) for m in subset)

    district.district_turnout = sum(m.turnout_base * m.weight_population for m in subset) / total_weight
    district.district_protest = sum(m.protest_base * m.weight_population for m in subset) / total_weight
    district.district_network_score = (
        sum(m.party_network_strength.get(party_key, 0.0) * m.weight_population for m in subset) / total_weight
    )
    district.district_support[party_key] = (
        sum(m.party_local_support.get(party_key, 0.0) * m.weight_population for m in subset) / total_weight
    )

    return district
