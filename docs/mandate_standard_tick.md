# Standard Mandate Tick (Implementation Order)

This file fixes one baseline inter-election tick where rating is a **late output**, not the driver.

## Fixed order (must not be reordered)

1. `national context`
2. `territorial update`
3. `district aggregation`
4. `government/party actions selection`
5. `parliamentary/action resolution`
6. `government + portfolio operating effects`
7. `budget/resource pressure resolution`
8. `coalition stability`
9. `public opinion update`
10. `long party resources update`
11. `alerts/events for next turn`

## Input bundle

- `NationState`
- 5 `District`
- 42 `Municipality`
- parties + resources
- cabinet state (if exists)
- mandate stage
- national pulse
- memory markers
- pending events

## Output bundle

- updated nation, districts, municipalities
- updated party states
- coalition stability deltas
- district alerts + headlines
- reactive flags for next turn

## Rule

Rating is computed only after territorial and parliamentary effects are resolved.
