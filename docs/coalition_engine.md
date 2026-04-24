# Coalition Engine Spec

## 1) Data scales and normalization

All coalition variables use 0..100 scale unless noted.

| Variable | Scale |
| --- | --- |
| mandates | 0..100 seats |
| acceptability | 0..100 |
| legitimacy | 0..100 |
| cadres | 0..100 |
| agenda | 0..100 |
| toxicity | 0..100 |
| veto_count | integer |
| stability | 0..100 |

## 2) Formator eligibility

A party is eligible for first attempt if:
- it can theoretically assemble 51+ seats;
- `hard_isolation_flag == false`;
- `veto_count <= veto_wall_threshold`;
- `acceptability >= min_acceptability`.

## 3) Formator score

```text
formator_score =
    mandates*0.35 +
    acceptability*0.25 +
    legitimacy*0.15 +
    cadres*0.10 +
    agenda*0.10 -
    toxicity*0.15 -
    veto_count*veto_penalty_weight
```

Tie-breakers:
1. more mandates;
2. higher acceptability;
3. lower toxicity.

## 4) Coalition candidate generation

Algorithm:
1. enumerate all combinations of parliamentary parties;
2. filter by `seats >= 51`;
3. apply hard veto pair filter;
4. compute compatibility score;
5. apply optional ideological distance cap;
6. rank by `(blocked, seats desc, compatibility desc)`.

Round A output object (`CoalitionCandidate`):
- `member_names`
- `total_seats`
- `compatibility_score`
- `blocked`

## 5) Negotiation pipeline

- Round A: candidate coalition generation.
- Round B: PM + portfolio package and utility optimization.
- Round C: policy contract build.
- Round D: confidence vote simulation.

Round B output object:
- PM assignment
- portfolio assignment
- per-party utility score
- compensation flags

Round C output object:
- policy satisfaction
- discipline risk
- confidence probability

## 6) Portfolio utility

```text
portfolio_utility =
    ideological_fit +
    electoral_fit +
    institutional_fit +
    prestige_fit -
    cadre_stress -
    scandal_exposure
```

## 7) Portfolio operating effects (mandatory fields)

Each portfolio must define:
- `bargain_weight`
- `prestige`
- `risk`
- `resource_effects_per_turn`
- `segment_effects_per_turn`
- `scandal_profile`
- `ideal_party_tags`

## 8) Coalition stability

```text
stability_next =
    stability_prev +
    discipline_bonus +
    compatibility_bonus +
    seat_buffer_bonus +
    portfolio_satisfaction_bonus +
    pm_strength_bonus -
    toxicity_penalty -
    rivalry_penalty -
    scandal_penalty -
    minister_failure_penalty -
    poll_divergence_penalty -
    election_pressure_penalty -
    budget_cycle_penalty
```

Thresholds:
- below `warning_threshold` -> internal crisis;
- below `reshuffle_threshold` -> reshuffle routine unlock;
- below `collapse_threshold` -> collapse path check.

## 9) Crisis routine with branching

1. concession attempt (only if compensations are available);
2. reshuffle attempt (only if failure is localized);
3. PM replacement attempt;
4. collapse check (depends on electoral incentives and distance to elections).

Outcomes:
- coalition survives;
- coalition survives with reshuffle;
- PM replaced;
- coalition collapses and new formator selection starts.

## 10) Turn integration

Within each mandate turn:
1. update minister performance;
2. apply scandals;
3. update partner satisfaction;
4. update coalition stability;
5. if below thresholds -> run crisis routine;
6. if unresolved -> collapse/reformation sequence.
