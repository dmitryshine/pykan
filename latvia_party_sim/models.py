from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


MIN_SCORE = 0.0
MAX_SCORE = 100.0


class PartyRole(str, Enum):
    GOVERNMENT = "government"
    PARLIAMENTARY_OPPOSITION = "parliamentary_opposition"
    EXTRA_PARLIAMENTARY = "extra_parliamentary"


class PartyLifecycleState(str, Enum):
    ACTIVE = "active"
    DYING = "dying"
    DEAD = "dead"
    REBRANDING = "rebranding"


class PartyMode(str, Enum):
    GOVERNMENT_LEAD = "government_lead"
    GOVERNMENT_JUNIOR = "government_junior"
    PARLIAMENTARY_OPPOSITION = "parliamentary_opposition"
    EXTRA_PARLIAMENTARY = "extra_parliamentary"


@dataclass(slots=True)
class Archetype:
    """Template coefficients shared by parties of the same type."""

    name: str
    governance: float = 50.0
    mobilization: float = 50.0
    coalition_bias: float = 50.0
    volatility: float = 50.0


@dataclass(slots=True)
class Leader:
    name: str
    recognition: float = 50.0
    trust: float = 50.0
    burnout: float = 0.0
    debate_power: float = 50.0


@dataclass(slots=True)
class ParliamentaryFaction:
    seats: int = 0
    cohesion: float = 50.0
    in_coalition: bool = False


@dataclass(slots=True)
class PartyWallets:
    operations: float = 0.0
    campaign: float = 0.0
    public_funding: float = 0.0
    private_donations: float = 0.0


@dataclass(slots=True)
class PartyResources:
    org_network: float = 50.0
    cadres: float = 50.0
    trust: float = 50.0
    agenda_control: float = 50.0
    toxicity: float = 0.0
    coalition_acceptability: float = 50.0
    discipline: float = 50.0
    activist_energy: float = 50.0
    brand_wear: float = 0.0


@dataclass(slots=True)
class Party:
    name: str
    archetype: Archetype
    role: PartyRole
    leader: Leader
    faction: ParliamentaryFaction = field(default_factory=ParliamentaryFaction)
    wallets: PartyWallets = field(default_factory=PartyWallets)
    resources: PartyResources = field(default_factory=PartyResources)
    lifecycle_state: PartyLifecycleState = PartyLifecycleState.ACTIVE
    mode: PartyMode = PartyMode.EXTRA_PARLIAMENTARY
    support_trend: float = 0.0
    memory_markers: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class ActionEffect:
    org_network: float = 0.0
    cadres: float = 0.0
    trust: float = 0.0
    agenda_control: float = 0.0
    toxicity: float = 0.0
    coalition_acceptability: float = 0.0
    discipline: float = 0.0
    activist_energy: float = 0.0
    brand_wear: float = 0.0
    operations_wallet: float = 0.0
    campaign_wallet: float = 0.0


@dataclass(slots=True)
class TurnAction:
    key: str
    effect: ActionEffect
    target_district_id: str | None = None
    tags: tuple[str, ...] = ()


@dataclass(slots=True)
class StageContext:
    turn: int
    stage: str
    event_shock: float = 0.0
    coalition_shock: float = 0.0
    rng_seed: int = 42
