# Territorial Model (MVP, 2026 baseline)

## 1) Administrative baseline

For 2026 baseline data, model uses **42 municipalities** grouped into 5 Saeima districts.

Gameplay is two-layer:
- background local layer: municipalities (state containers, auto-updated);
- public strategic layer: 5 districts (player-facing map and most actions).

## 2) Data hierarchy

- `NationState` -> national pressure and cycle stage
- `District` (5) -> visible aggregates and alerts
- `Municipality` (42) -> local mood/network/support/volatility memory

Signal flow each turn:
1. nation pressure down to districts/municipalities;
2. local updates per municipality;
3. aggregation up to district indicators;
4. district outputs feed player-facing strategy.

## 3) Municipality update intent

Municipality is a lightweight state unit (not a full micro-governance mini-game).
The engine updates each municipality automatically every turn.

Core local update targets:
- local mood to government;
- party local support tendency;
- turnout tendency;
- protest heat;
- network drift.

## 4) Interaction model

Player mostly acts at district/hotspot level.
Municipality drill-down is informational by default and only occasionally action-enabled.

## 5) Included territorial set

Current implementation stores district-to-municipality mapping for:
- Rīga
- Vidzeme
- Latgale
- Kurzeme
- Zemgale

with 42 total municipalities.
