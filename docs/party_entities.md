# Party Entities (Implementation Spec)

## 1) Standard scales

All hidden simulation stats use **0–100** scale.
- 0 = minimum state
- 100 = maximum state
- Clamp after each turn-phase operation.

Money fields are absolute numeric values (float, non-negative).

## 2) Core entity split

## Archetype (template)
Defines default coefficients and behavior priors.
- `name`
- `governance`
- `mobilization`
- `coalition_bias`
- `volatility`

## Party (runtime organism)
Persistent actor across cycles.
- identity: `name`, `archetype`
- runtime state: `role`, `lifecycle_state`
- subsystems: `leader`, `faction`, `wallets`, `resources`
- dynamic outputs: `support_trend`, `memory_markers`

## Leader
- `recognition`, `trust`, `burnout`, `debate_power`

## ParliamentaryFaction
- `seats`
- `cohesion`
- `in_coalition`

## 3) Financial model

Party has four wallets:
- `operations` (apparatus costs)
- `campaign` (campaign spending)
- `public_funding` (stable stream)
- `private_donations` (volatile stream)

Primary spending buckets:
- network maintenance
- media and messaging
- talent retention
- crisis management
- campaign field operations

## 4) Lifecycle states

- `ACTIVE`
- `DYING`
- `DEAD`
- `REBRANDING`

Threshold checks are computed at end of each mandate turn.
