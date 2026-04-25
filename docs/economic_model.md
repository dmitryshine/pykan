# Economic Model (Party + Government)

## Core principle

Two linked but non-identical economies:
1. party economy (cashflow/survival/campaign machine)
2. government budget pressure economy (fiscal political constraints)

## Party economy variables

- `operating_cash`
- `campaign_cash`
- `state_funding`
- `private_funding_flow`
- `fundraising_capacity`
- `network_upkeep_cost`
- `cadre_upkeep_cost`
- `media_cost_pressure`
- `crisis_response_cost`
- `rebrand_cost_pressure`

## Government economy variables

- `budget_stress`
- `fiscal_room`
- `spending_pressure_social`
- `spending_pressure_regions`
- `spending_pressure_security`
- `spending_pressure_services`
- `infrastructure_commitment`
- `public_tolerance_for_austerity`
- `pre_election_spending_temptation`

## Tick placement

Budget/resource pressure is resolved after cabinet operating effects and before coalition stability/public opinion.

## Output signals

`GovernmentEconomicSignals`:
- coalition budget penalty
- trust penalty
- network penalty
- aggregate economic strain
