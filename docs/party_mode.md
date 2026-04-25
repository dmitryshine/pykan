# Party Mode

`PartyMode` is a mandatory runtime state that changes strategy, action space, risks, and success evaluation per political status.

## Modes

- `government_lead`
- `government_junior`
- `parliamentary_opposition`
- `extra_parliamentary`

## Determination

`determine_party_mode(...)` assigns mode automatically each mandate tick using formal system state:

1. `seats == 0` -> `extra_parliamentary`
2. PM party in an active cabinet -> `government_lead`
3. In active cabinet without PM post (assignment / coalition flag / government role) -> `government_junior`
4. Otherwise -> `parliamentary_opposition`

Mode is recalculated before action selection to shape AI priorities and action availability.

## Mode profile

Each mode has a `ModeProfile`:

- `resource_weights`
- `action_weights`
- `risk_weights`
- `success_metrics`
- `failure_metrics`
- `distinctiveness_pressure`
- `blame_pressure`
- `entry_pressure`
- `allowed_action_tags`

## Tick integration

In `MandateTickEngine` phase 4:

1. determine and persist `party.mode`
2. write mode pressures and resource priorities into memory markers
3. filter actions by allowed mode tags
4. scale action effects by mode action weights

Phase 10 computes a mode-aware `mode_success_score` via `evaluate_mode_cycle(...)`.
