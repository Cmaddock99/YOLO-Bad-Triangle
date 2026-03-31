# experiment-planner reference

## Planning objective
- Recommend only the next 3-5 experiments.
- Prioritize decisions that reduce uncertainty and improve defense recovery.

## Evidence prerequisites
- Evidence should come from framework report artifacts.
- Comparability requires baseline + attack-only + defended context where possible.
- If prerequisites fail, record blockers instead of fabricating rankings.

## Queue guidance
- `priority` starts at 1 and increments by 1.
- `params` should be explicit enough to execute later through canonical scripts.
- `stop_condition` should specify when to stop running a path (for example diminishing returns).

## Risk handling
- Use `risk_note` to capture confounders (budget mismatch, missing pairs, unstable outcomes).
- Use `blocked_by` when insufficient evidence prevents reliable planning.

## Notes
- Keep this skill read-only and strategic.
- TODO: Add a canonical budget token format if the project standardizes one.
