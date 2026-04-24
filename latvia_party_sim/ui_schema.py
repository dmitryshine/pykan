from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CycleStage(str, Enum):
    FORMATION = "formation"
    EARLY_MANDATE = "early_mandate"
    MID_MANDATE = "mid_mandate"
    LATE_MANDATE = "late_mandate"
    PRE_ELECTION = "pre_election"
    HOT_CAMPAIGN = "hot_campaign"
    ELECTION_DAY = "election_day"


@dataclass(slots=True)
class ZoneEmphasis:
    top_bar: int
    parliament: int
    map_panel: int
    segments_panel: int
    party_panel: int
    portfolios_panel: int
    agenda_pulse: int
    bottom_actions: int


def default_emphasis(stage: CycleStage) -> ZoneEmphasis:
    if stage in {CycleStage.EARLY_MANDATE, CycleStage.MID_MANDATE, CycleStage.LATE_MANDATE}:
        return ZoneEmphasis(3, 5, 3, 3, 4, 5, 4, 4)
    if stage == CycleStage.PRE_ELECTION:
        return ZoneEmphasis(3, 3, 4, 5, 5, 3, 4, 5)
    if stage == CycleStage.HOT_CAMPAIGN:
        return ZoneEmphasis(3, 2, 5, 5, 5, 2, 4, 5)
    return ZoneEmphasis(3, 4, 3, 3, 4, 3, 3, 4)
