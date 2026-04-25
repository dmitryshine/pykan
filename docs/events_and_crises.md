# Events and Crises System

MVP event layer models politics as a pipeline:

`latent buildup -> signal -> escalation -> resolution -> memory`

## Event classes

- `governance_crisis`
- `corruption_scandal`
- `personality_crisis`
- `coalition_crisis`
- `intra_party_crisis`
- `positive_window`

## Origins

- `endogenous`
- `exogenous`
- `actor_triggered`

## Runtime object

`PoliticalEvent` includes required runtime fields:

- id, type, origin, severity, scope
- source and target actors
- trigger conditions
- stage, heat, controllability
- territorial footprint and linked themes
- memory effects and resolution options
- visibility and expiry metadata

## Tick placement

Integrated into mandate tick phases:

1. national context
2. territory update
3. district aggregation
4. latent tension generation + signal emission
5. mode-aware action selection
6. action resolution
7. cabinet effects
8. budget/resource pressure
9. event escalation/resolution
10. coalition stability
11. public opinion
12. long resources + mode evaluation
13. player signals

## Outputs to player

The engine produces event-aware headlines/warnings/opportunities and updates district alerts with event marks.
