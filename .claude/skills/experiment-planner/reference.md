# experiment-planner reference

## Planning objective
- Recommend only the next 3–5 experiments.
- Prioritize decisions that reduce the most uncertainty or unblock the most consequential decision.
- The highest-priority item is always the one that, if run, would most change what we do next.

## Checkpoint context (current as of cycle_20260329_125124)

- `dpc_unet_final_golden.pt` — the production baseline checkpoint. Set via `DPC_UNET_CHECKPOINT_PATH` env var in `.env`.
- `dpc_unet_adversarial_finetuned.pt` — adversarially finetuned checkpoint at CONDITIONAL PASS status.
  - deepfool A/B (eps=0.1, steps=50, n=100): finetuned +0.006 mAP50 over golden (marginal)
  - square A/B (eps=0.3, n_queries=450, n=50): finetuned +0.027 mAP50 over golden (meaningful)
  - Clean (no-attack) A/B: **NOT YET RUN** — blocking full deployment decision
- Do not recommend deployment of `dpc_unet_adversarial_finetuned.pt` until clean validation completes.
- When clean A/B is absent: insert priority-1 run `yolo26n__none__c_dog` with both checkpoints and `runner.max_images=500`.

## Budget token format

Canonical forms accepted in `planning_basis.budget`:
- `"max_runs=N"` — total number of distinct framework runs
- `"max_images=N"` — total images across all runs
- `"wall_hours=N"` — NUC CPU wall-clock hours (approx 126s/image for square, 30s/image for deepfool, 15s/image for fgsm/pgd)

## Evidence prerequisites

- Evidence must come from Phase 4 `validation_results` in `outputs/cycle_history/<cycle_id>.json`.
- Phase 1/2 smoke runs are not comparable to Phase 4 full-dataset runs — do not use them as planning evidence.
- Comparability requires: baseline row present, compatible image counts, same model config.
- If square or dispersion_reduction validation used 50-image cap, flag this in `risk_note` for any runs that extend those results.

## Queue guidance

- `priority` starts at 1, increments by 1 — lower number = higher priority.
- `params` must be explicit enough to execute via `scripts/run_unified.py --set` or `scripts/sweep_and_report.py`.
- `stop_condition` specifies when to stop pursuing this path (e.g., diminishing returns, threshold met).
- `cost_estimate`: `"low"` (<1h NUC), `"medium"` (1–4h), `"high"` (>4h).

## Risk handling

- Use `risk_note` for confounders (image count mismatch, missing pairs, unstable outcomes, param bound hits).
- Use `blocked_by` when insufficient evidence prevents reliable planning.
- If `outputs/cycle_state.json` shows Phase 4 still active, note it in `risk_note` for any conflicting proposals.

## Notes

- Keep this skill read-only and strategic.
- Do not execute experiments or edit files.
