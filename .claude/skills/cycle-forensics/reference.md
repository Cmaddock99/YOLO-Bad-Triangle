# cycle-forensics reference

## Scope
- Focus on framework cycle report artifacts, not ad-hoc logs.
- Prefer evidence from `outputs/framework_reports/<sweep_id>/`.

## Ranking intent
- `attack_damage`: higher damage means stronger attack impact.
- `defense_recovery`: higher recovery means stronger defense response against the paired attack.

## Anomaly classes
- `missing_pair`: baseline, attack-only, or attack+defense rows are missing for a comparison.
- `image_count_mismatch`: rows being compared do not share equivalent image counts.
- `outlier_shift`: large metric jump that is unsupported by nearby runs in the same cycle.

## Status guidance
- `ok`: enough evidence to produce ranked outputs.
- `partial`: usable but incomplete evidence (for example one attack missing a pair).
- `insufficient_data`: cannot produce meaningful rankings.

## Notes
- Keep this skill read-only.
- Do not claim causal explanations that are not directly supported by artifacts.
- TODO: If additional canonical report filenames are standardized, add them here.
