# Personality System (MVP Spec)

## Purpose

Personalities are runtime political actors (not decorative portraits).
They affect campaigns, cabinet performance, coalition behavior, territorial network, corruption, leaks, and party crises.

## Core layers

1. identity (name, surname, age, region affinity)
2. political archetype
3. open stats
4. hidden traits
5. relation/faction layer
6. dynamic state (burnout/scandal/career state)

## MVP required fields

- `name`, `surname`, `age`, `region_affinity`, `role_type`
- open: `recognition`, `trust`, `charisma`, `competence`, `debate`, `loyalty`, `ambition`, `discipline`, `regional_power`
- hidden: `corruption_affinity`, `leak_risk`, `stress_tolerance`, `growth_potential`
- dynamic: `burnout`, `scandal_load`, `career_state`, `faction_alignment`

## Generation pipeline

1. Latvian name + surname generation (double surname optional)
2. role + archetype
3. stat sampling by archetype ranges
4. region/faction alignment
5. quirks

## Cabinet integration

Minister assignment can point to a concrete `personality_id`.
Holder quality is computed from personality stats + portfolio fit.

Effects:
- strong fit -> better ministry effectiveness
- weak but loyal -> short-term discipline stability, higher long-term failure risk
- corruption/leak traits feed corruption runtime pressure/exposure.

## Archetype preset data format

Each archetype preset must provide:
- `id`
- `display_name`
- `open_stat_ranges`
- `hidden_stat_ranges`
- `preferred_roles`
- `typical_backgrounds`
- `typical_quirks`
- `party_affinity_weights`
- `career_state_bias`
- `corruption_profile`
- `scandal_profile`

## Fixed generation pipeline

1. gender
2. first/last name
3. age layer
4. district affinity
5. background type
6. archetype
7. open stats
8. background + age modifiers
9. hidden stats
10. quirks
11. relations + faction alignment
12. party fit
13. role/career state finalize
