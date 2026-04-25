# Mandate Turn Loop (One Tick Spec)

This document is the execution order for one inter-election turn.

## Deterministic order

1. **Apply public context** (macro pressure, stage modifiers).
2. **Apply ministerial load** (if party is in government and has portfolios).
3. **Resolve chosen actions** (all parties).
4. **Resolve parliament conflicts** (committee/cabinet/opposition clashes).
5. **Update resources** (hard + soft resources, clamped 0–100).
6. **Update segment mood** (segment-level shifts).
7. **Update support trend** (derived, not stored as resource).
8. **Update coalition stability** (government block only).
9. **Check thresholds**:
   - split risk
   - death risk
   - rebranding unlock
   - role transition markers
10. **Write memory markers** and close turn.

## Deterministic vs stochastic

- Deterministic: resource deltas, budget flows, baseline support formula.
- Stochastic: crisis events, scandal triggers, late-stage shock multipliers.

RNG must be seeded by `(global_seed + turn + party_id_hash)` for reproducibility.

## Transition rules

- Parliamentary to extra-parliamentary transition is processed after election day.
- During mandate phase, parties can become `DYING` / `REBRANDING` but keep role until election resolution.
- Emergency split event can spawn a child party if discipline + cohesion are below thresholds.
