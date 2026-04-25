# Interview & Media Appearances

Media appearances are modeled as a dedicated runtime political system, not a direct polling button.

## Core object

`MediaSlot` carries contextual fields:

- `id`, `format_type`, `topic`, `pressure_level`
- `audience_profile`, `hostility_level`
- `target_actor_id`, `target_party_id`
- `stage_context`, `linked_scandal_id`, `linked_issue`
- `timing_importance`, `territorial_relevance`
- `resolution_window`, `visibility`, `upside_potential`, `downside_risk`

## Formats

- hard interview
- soft program interview
- crisis briefing
- budget explainer
- debate
- regional broadcast
- new face launch

## Resolution model

A slot is resolved by combining:

1. context fit (slot stage/topic)
2. response line fit (`MediaLine`)
3. personality profile fit (trust/recognition/debate/competence/stress/burnout/media-hunger)
4. pressure/hostility/scandal context
5. party mode
6. audience profile

Output is a vector of intermediate deltas (issue ownership, scandal heat, momentum, credibility, coalition tension, territorial mood, distinctiveness, visibility breakthrough, follow-up risk), not immediate polling shift.

## Tick integration

Media phase is integrated into mandate tick after events escalation and before coalition/public-opinion updates.
