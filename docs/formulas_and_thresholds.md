# Formulas and Thresholds (v1)

## 1) Resource update

`resource_next = clamp(resource_prev + action_delta + event_delta + role_delta - decay, 0, 100)`

## 2) Support trend

`support = clamp(w_trust*trust + w_agenda*agenda + w_org*org + w_cadres*cadres + w_energy*energy - w_toxic*toxicity - w_wear*brand_wear + event_shock + random_shock, 0, 100)`

## 3) Brand wear effects

Brand wear influences:
- growth ceiling
- soft voter retention
- rebranding probability
- refresh cost multiplier

## 4) Toxicity vs acceptability

Toxicity and coalition acceptability are related but not identical:
- toxicity can increase base mobilization;
- acceptability depends on strategic arithmetic and partner scarcity.

## 5) 5% threshold sensitivity

For parties in 4–6% zone, late-campaign shocks are amplified.

Suggested multipliers:
- baseline shock multiplier: `1.0`
- 4–6% zone: `1.8`
- below 4%: `2.2`

## 6) Lifecycle thresholds

Suggested status boundaries (evaluated each turn):
- `ACTIVE`: death_pressure < 70
- `DYING`: 70 <= death_pressure < 85
- `DEAD`: death_pressure >= 85
- `REBRANDING`: brand_wear >= 75 and death_pressure < 85
