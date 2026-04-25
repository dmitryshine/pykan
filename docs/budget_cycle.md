# Budget Cycle Mechanic (MVP)

## Role

Budget cycle is a recurring mandate stress-test where coalition, ministries, territories, corruption pressure and public tolerance collide.

## Frequency

Runs every `budget_interval` turns (default: 12).

## Placement in mandate tick

1. National context
2. Territorial update
3. Party actions
4. Cabinet operating effects
5. **Budget cycle resolution**
6. Coalition stability
7. Public opinion
8. Resource update
9. Alerts/events

## Required inputs

- cabinet state and assignments
- government economy state
- ministry demand pressure
- coalition partner satisfaction
- territorial districts
- budget frame selection

## Budget frames

- austerity
- balanced
- social expansion
- regional push
- security first
- pre-election splurge
- patronage

## Required outputs

- `coalition_satisfaction_delta`
- `cabinet_performance_delta`
- `government_economic_strain_delta`
- `ministerial_strain_map`
- `district_budget_impact_map`
- `trust_delta`
- `protest_delta`
- `brand_wear_delta`
- `corruption_delta`
- `future_budget_pressure_delta`
