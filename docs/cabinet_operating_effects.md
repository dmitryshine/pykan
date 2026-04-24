# Cabinet Operating Effects (Mandate Runtime Spec)

## Goal

Government is a permanent runtime mechanism inside each mandate tick, not a static coalition status.

## Tick placement (mandatory)

After party action resolution and before coalition stability + public opinion:
1. apply ministry operating effects
2. recalculate cabinet performance
3. register minister failures and budget load penalties
4. update partner satisfaction and PM wear
5. pass cabinet signals to coalition stability phase

## Cabinet runtime state

`CabinetState` stores:
- PM party and PM strength
- start/current stability
- partner satisfaction map
- budget load
- PM wear
- competence image
- portfolio assignments
- per-portfolio runtime state
- problem queue
- reshuffle history
- cabinet-wide performance

## Portfolio schema

Each ministry uses `PortfolioSpec`:
- `bargaining_weight`
- `prestige`
- `risk`
- `resource_effects_per_turn`
- `theme_effects_per_turn`
- `territorial_effects_per_turn`
- `scandal_profile`
- `ideal_party_tags`
- `failure_sensitivity`

Runtime per ministry uses `PortfolioRuntimeState`:
- effectiveness
- stress
- scandal risk
- current pressure
- recent failures
- territory/theme modifiers

## Cabinet-wide performance

Computed from weighted combination of:
- PM strength
- partner satisfaction
- PM wear
- number of problem ministries
- budget load

Used as downstream input to government mood and late public opinion.

## Testable invariants

- Better holder quality on same portfolio -> better effectiveness / fewer failures.
- High budget load -> higher coalition pressure and brand wear drift.
- Repeated failures in risky portfolios -> minister_failure_penalty grows.
- Regional/transport portfolios -> incremental network boost in territories.
