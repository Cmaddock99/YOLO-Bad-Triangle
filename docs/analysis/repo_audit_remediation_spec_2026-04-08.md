# Full-Repo Audit Remediation Spec

Generated: 2026-04-08

Primary input: `docs/audit_findings.md`
Related context: `docs/analysis/fix_spec.md`, `REMEDIATION_PLAN.md`

---

## Purpose

Convert the 2026-04-08 full-repo audit into an execution-ready fix plan that can be implemented in small, reviewable PRs.

This spec is intentionally stricter than the earlier March remediation docs:

- It covers the current audit backlog across orchestration, training, evaluation, reporting, plugins, defenses, and infrastructure.
- It treats silent corruption, provenance drift, and reproducibility gaps as blockers.
- It names the existing test files that should absorb each regression case.

---

## Guardrails

1. Smallest viable diff per fix. No opportunistic refactors.
2. No intentional ML behavior change except where the audit identified a correctness bug.
3. Every fix needs either:
   - a focused automated test, or
   - a documented reason the behavior is only practical to verify manually.
4. Prefer reusing existing helpers and tests before introducing new abstractions.
5. Do not run new unattended cycles until the blocker workstreams below are complete.

---

## Blocker Policy

Freeze new `auto_cycle.py --loop` and production `sweep_and_report.py` runs until these are complete:

- WS1 `Artifact Integrity And Resume Semantics`
- WS2 `Training Gate And Export Contracts`
- WS3 `Reporting Authority And Warning Correctness`

Reason: those workstreams contain the findings that can silently skip partial runs, reuse stale artifacts, merge the wrong attack rows, or reject valid checkpoints.

---

## Recommended PR Order

1. WS1 `Artifact Integrity And Resume Semantics`
2. WS2 `Training Gate And Export Contracts`
3. WS3 `Reporting Authority And Warning Correctness`
4. WS4 `Attack Plugin Correctness And Determinism`
5. WS5 `Defense Pipeline Correctness And Provenance`
6. WS6 `Contracts, Registry Safety, And CI Guardrails`
7. WS7 `Operator UX And Branch Safety`

Preferred rule: one workstream per PR unless two items touch the same files and share the same focused test slice.

---

## Workstream Summary

- WS1 `Artifact Integrity And Resume Semantics`
  Fix partial-run reuse, non-atomic artifact writes, silent history drops, and corrupt prediction handling.
- WS2 `Training Gate And Export Contracts`
  Fix the gate-threshold mismatch, stale export reuse, interpreter propagation, and training-manifest provenance.
- WS3 `Reporting Authority And Warning Correctness`
  Fix wrong attack-row merges, defended-row authority selection, warning semantics, and user-facing report failures.
- WS4 `Attack Plugin Correctness And Determinism`
  Fix the SquareAttack device crash, objective-mode constant drift, ambiguous logits extraction, and stochastic reproducibility gaps.
- WS5 `Defense Pipeline Correctness And Provenance`
  Fix DPC-UNet multipass correctness, NaN masking, metadata accuracy, and checkpoint provenance timing.
- WS6 `Contracts, Registry Safety, And CI Guardrails`
  Reconcile schema registration, harden registry collisions, fix empty CSV validation, and close health-check safety gaps.
- WS7 `Operator UX And Branch Safety`
  Fix progress reporting, dashboard side effects, and direct-to-main automation behavior.

---

## WS1 - Artifact Integrity And Resume Semantics

Severity: blocker

Audit findings covered:

- `scripts/auto_cycle.py` skips a run on `metrics.json` alone.
- `src/lab/runners/run_experiment.py` writes `metrics.json` and `run_summary.json` non-atomically.
- `scripts/auto_cycle.py` silently drops runs in `save_cycle_history`.
- `scripts/auto_cycle.py` breaks out of demotion recovery accumulation when `mAP50` is missing.
- `scripts/auto_cycle.py` reuses stale artifacts without validating run intent.
- `src/lab/eval/prediction_utils.py` writes `predictions.jsonl` non-atomically.
- `src/lab/eval/bootstrap.py` silently skips corrupt JSONL lines.
- `src/lab/reporting/framework_comparison.py` and `src/lab/reporting/team_summary.py` write report outputs non-atomically.
- `scripts/generate_dashboard.py` writes HTML non-atomically.

Required changes:

1. Define one canonical "complete run" check:
   `predictions.jsonl`, `run_summary.json`, and `metrics.json` must all exist and parse.
2. Update `run_single` to skip only when the full artifact set is present.
3. Reuse or extract the existing fingerprint logic from `sweep_and_report.py` so `run_single` refuses stale artifacts whose run intent no longer matches current params.
4. Write run artifacts in a safe order:
   `predictions.jsonl` first, `run_summary.json` second, `metrics.json` last.
   `metrics.json` remains the final completion sentinel, but only after the other two files are durably in place.
5. Convert every canonical report writer in this path to `tmp + os.replace`.
6. Replace bare `except Exception: pass` in `save_cycle_history` with a warning that names the skipped run.
7. Change `_compute_phase4_demotions` so missing `mAP50` skips that recovery entry without aborting the defense scan.
8. Surface bootstrap corruption:
   add `skipped_lines` or equivalent metadata to CI results when JSONL rows are dropped.

Implementation notes:

- Do not introduce a new persistence framework.
- Reuse the repo's current atomic-write pattern unless duplication becomes excessive inside a single file.
- "Parse" in the completion check should be minimal and cheap. It is enough to validate JSON syntax and required top-level keys.

Backfill after merge:

- Sweep `outputs/framework_runs/` for run dirs missing one of the three required artifacts and mark them for rerun or cleanup.
- Regenerate any report bundles built from truncated CSV or JSON outputs.

Tests to add or extend:

- `tests/test_auto_cycle_and_dashboard.py`
  Add coverage for `run_single` completion checks, intent mismatch reruns, demotion handling when `mAP50` is missing, and cycle-history warning behavior.
- `tests/test_framework_output_contract.py`
  Assert the required artifact set is complete before a run is treated as successful.
- `tests/test_framework_metrics.py`
  Add corrupt/truncated `predictions.jsonl` cases and verify skipped-line visibility.
- `tests/test_framework_reporting.py`
  Exercise report writers through their normal call sites so truncated-output regressions are caught.

Acceptance criteria:

- A directory with only `metrics.json` is never treated as a finished run.
- A truncated or corrupt `predictions.jsonl` is surfaced as degraded input, not silently treated as full data.
- A fingerprint mismatch forces rerun instead of stale reuse.
- Canonical report files are either old-good or new-good after a crash, never partially rewritten.

---

## WS2 - Training Gate And Export Contracts

Severity: blocker

Audit findings covered:

- `_gate_passed` effectively gates at `-0.001`, not the intended `-0.005`.
- `export_training_data.py` exits 0 on "no usable attacks", allowing stale zip reuse.
- `train_dpc_unet_local.py` reuses stale extracted data when the zip filename is unchanged.
- `evaluate_checkpoint.py` hardcodes `.venv/bin/python` and ignores the caller's interpreter.
- `train_dpc_unet_local.py` leaves YOLO running stats active during alignment-loss training.
- `train_from_signal.py` omits `attack_params` from the manifest.
- `train_dpc_unet_local.py` hardcodes the checkpoint filename when reading back an export zip.

Required changes:

1. Single-source the checkpoint gate threshold:
   `evaluate_checkpoint.py` and `train_from_signal.py` must use the same tolerance value.
   The repo should not allow "return code says fail, JSON delta says pass" divergence.
2. Change `export_training_data.py` so "no usable attacks" is a non-zero contract for automated callers.
3. Prevent stale zip reuse:
   build the archive at a temp path and replace the final zip only on success.
4. Make `train_dpc_unet_local.py` re-extract when the source zip is newer or otherwise changed.
5. Add a CLI path to propagate `--python-bin` all the way into `evaluate_checkpoint.py`'s inner subprocess.
6. Put the frozen YOLO loss model in eval mode during training so BatchNorm-style running stats do not drift.
7. Record the actual attack params used by the gate in the manifest.
8. When importing a checkpoint from the zip, discover the packaged `checkpoint/*.pt` file instead of assuming a fixed filename.

Implementation notes:

- Prefer correctness over backward compatibility for the gate exit code. The audit already proved the current behavior contradicts the intended spec.
- Re-extraction can use a simple freshness rule first.
  A checksum manifest can be deferred if the mtime-based fix is enough.

Optional backfill:

- Re-evaluate previously rejected checkpoints whose `delta_mAP50` fell in `[-0.005, -0.001)`.

Tests to add or extend:

- `tests/test_train_from_signal.py`
  Add tolerance-band coverage, manifest provenance coverage, and interpreter-propagation coverage.
- `tests/test_export_training_data.py`
  Add failure-contract coverage for "no usable attacks" and temp-output behavior.
- `tests/test_dpc_unet.py`
  Add zip re-extraction and checkpoint-discovery coverage if that logic stays close to the defense/training code.
- `tests/test_reproducibility.py`
  Add a focused assertion that the frozen detector path runs in eval mode during alignment training.

Acceptance criteria:

- A checkpoint with `delta_mAP50 = -0.003` passes the gate if the policy says the tolerance is `-0.005`.
- A failed export never leaves an old zip looking like fresh output.
- Signal-driven training uses the intended Python interpreter and the actual exported checkpoint.
- The training manifest alone is enough to reproduce the gate invocation.

---

## WS3 - Reporting Authority And Warning Correctness

Severity: blocker

Audit findings covered:

- `_merge_effectiveness_and_recovery` merges rows on `(model, seed, attack)` without attack signature.
- `generate_cycle_report.py` overwrites defended rows with last-seen wins.
- `WARN_HIGH_CONFIDENCE_FLOOR` is named opposite its behavior.
- `evaluate_warnings` can suppress or misfire `NO_VALIDATION` because it checks after authority filtering.
- `generate_cycle_report.py` uses truthiness checks where explicit numeric guards are clearer.
- `generate_slide_tables.py` raises raw `ValueError` for empty outputs.

Required changes:

1. Promote `attack_signature` to a first-class merge key wherever attack-only rows are joined to defense-recovery rows.
2. Define explicit precedence for duplicate validation rows:
   Phase 4 validate rows beat smoke and consistency rows.
   If phases tie, prefer authoritative rows.
3. Rename the low-confidence warning code to match its behavior and update any schema or tests that assert warning codes.
4. Compute validation presence from the full available row set before applying authority narrowing.
5. Replace ambiguous numeric truthiness checks with explicit guards for `None` and zero.
6. Convert user-facing CSV-empty failures in `generate_slide_tables.py` into `SystemExit("ERROR: ...")`.

Implementation notes:

- Do not redesign the report payload model in this pass.
- Keep the existing output columns stable unless a rename is required to correct a misleading warning code.

Tests to add or extend:

- `tests/test_framework_reporting.py`
  Add same-name different-signature attack rows, duplicate defended rows across phases, renamed warning-code expectations, and `NO_VALIDATION` coverage using mixed authority rows.
- `tests/test_cycle_report_generation.py`
  Add explicit phase-priority and numeric-guard coverage.

Acceptance criteria:

- Two attack rows with the same attack name but different signatures never cross-merge.
- Cycle report defended values come from the intended authoritative phase.
- Warning codes and warning messages point to the same underlying condition.
- Empty slide-table inputs fail cleanly with a user-facing error.

---

## WS4 - Attack Plugin Correctness And Determinism

Severity: high

Audit findings covered:

- `SquareAttack` crashes when a CPU generator is paired with non-CPU `torch.randint(..., device=...)`.
- `DeepFoolAttack` and `FGSMAttack` compare objective modes using raw string literals instead of contract constants.
- `_extract_class_logits` has ambiguous branch priority for square 3-D tensors.
- `DispersionReductionAdapter` has no seed plumbing.
- `PGDAttack` uses `torch.seed()` in a way that perturbs global RNG state.
- `CWAttackAdapter` exposes `confidence` but does not actually use it.
- `SquareAttack._score` hardcodes a confidence threshold with no documentation or config surface.

Required changes:

1. Make SquareAttack random draws device-safe:
   generate with the generator on CPU, then move tensors to the target device.
2. Replace raw objective-mode literals with imports from `lab.config.contracts`.
3. Make `_extract_class_logits` ambiguity explicit:
   document the layout heuristic, add a deterministic tiebreak rule, and emit a debug warning when both layouts are plausible.
4. Add optional `seed` plumbing to Dispersion Reduction and return the seed in metadata.
5. Replace `torch.seed()` in PGD's unseeded path with a random draw that does not reseed global state.
6. Make the CW `confidence` contract honest:
   either implement the margin term, or mark the field as reserved/unimplemented and include that fact in metadata.
7. Replace the Square/CW score threshold magic number with a named constant or constructor parameter.

Implementation notes:

- The CW item should default to the smaller diff.
  If implementing the full margin changes attack behavior materially, prefer marking the field as reserved now and opening a follow-up behavior PR later.
- For `_extract_class_logits`, the immediate goal is to eliminate silent ambiguity, not to redesign all YOLO tensor handling.

Tests to add or extend:

- `tests/test_framework_attack_plugins.py`
  Add non-CPU-safe SquareAttack coverage where the environment allows it, seed determinism for Dispersion Reduction, constant-backed objective-mode behavior, and threshold configurability.
- `tests/test_attack_objective_contract.py`
  Assert that plugin behavior tracks contract constants rather than literal strings.
- `tests/test_reproducibility.py`
  Add exact-output determinism tests for stochastic attacks that claim to support seeds.

Acceptance criteria:

- SquareAttack no longer crashes because of generator/device mismatch.
- Objective-mode renames in `contracts.py` cannot silently desync attack behavior.
- Stochastic attacks that expose a seed are reproducible across repeated calls.
- Attack metadata does not claim support for knobs that the implementation ignores.

---

## WS5 - Defense Pipeline Correctness And Provenance

Severity: high

Audit findings covered:

- `run_wrapper_multipass_on_bgr_image` performs an extra undocumented final pass.
- Intermediate NaN values are clipped away and silently propagated.
- `CDogDefenseAdapter` emits misleading `timestep` metadata during multipass runs.
- `YOLOModelAdapter.validate` maps missing metrics to `0.0` instead of `None`.
- `strict_load_with_report` is dead code.
- `checkpoint_provenance` hashes the file on disk at report time, not at load time.
- Routing policy falls through silently for unknown attack hints.

Required changes:

1. Remove the extra final multipass invocation and make `passes` equal the true number of model calls.
2. Add a per-pass finiteness check before any clip or image conversion.
3. When a timestep schedule is active, make the metadata unambiguous:
   `timestep` should be `None` or absent, and the schedule plus actual pass count should be present.
4. Return `None` for missing validation metrics rather than coercing them to `0.0`.
5. Keep `strict_load_with_report` honest:
   either wire it into `_ensure_loaded`, or remove it from the public path and tests.
   Preferred option: wire it into `_ensure_loaded` so the existing API surface remains meaningful.
6. Cache checkpoint SHA256 at load time and reuse that cached value in provenance.
7. Make routing-policy behavior explicit for unknown non-empty hints:
   either extend the known hint set to include repo attack names or raise/log when routing is enabled and the hint is unknown.

Tests to add or extend:

- `tests/test_dpc_unet.py`
  Add multipass call-count coverage, intermediate NaN failure coverage, metadata coverage, and load-report/provenance coverage.
- `tests/test_wrapper_checkpoint_contract.py`
  Confirm the checkpoint hash reflects the loaded artifact, not a later on-disk replacement.
- `tests/test_framework_defense_plugins.py`
  Add routing-hint behavior coverage if routing remains in active use.

Acceptance criteria:

- Multipass schedules run exactly the documented number of passes.
- A non-finite intermediate output fails loudly before a corrupted image reaches inference.
- Validation `None` and validation `0.0` are distinguishable in downstream payloads.
- Checkpoint provenance reflects what was actually loaded into memory.

---

## WS6 - Contracts, Registry Safety, And CI Guardrails

Severity: medium

Audit findings covered:

- `contracts.py` and `schemas/v1/` disagree about which schemas exist.
- `framework_metrics.schema.json` does not constrain validation status values.
- `resolve_latest_dir` sorts by name instead of modification time.
- `_runtime_profiles_payload` cache leaks between tests.
- `PluginRegistry.register` silently overwrites duplicate aliases.
- `validate_legacy_csv_file` accepts zero-row CSV files.
- Several exported health-check helpers are not wired into runtime paths.
- `check_tracked_outputs.py` allows arbitrary content inside `outputs/framework_reports/**`.

Required changes:

1. Reconcile schema registration in one direction per PR:
   either add the missing schema files for declared IDs, or remove unused IDs and register the existing schemas.
2. Add an enum for validation status values in `framework_metrics.schema.json`.
3. Change `resolve_latest_dir` to deterministic `mtime, name` ordering or add a timestamp-shape warning if behavior must stay name-based.
   Preferred option: switch to `mtime, name`.
4. Fix runtime-profile cache test isolation in `tests/conftest.py` or nearby fixtures by clearing the cache around tests that mutate profile inputs.
5. Make duplicate plugin registration a loud failure.
6. Make zero-row legacy CSV files invalid by default.
7. Decide whether the currently dead health-check exports are runtime guardrails or library helpers.
   If guardrails, wire them into CI or orchestration.
   If helpers, document that they are not currently enforced.
8. Tighten tracked-output policy for `framework_reports/` so binary or raw run artifacts do not pass simply because they are under a report directory.

Tests to add or extend:

- `tests/test_schema_contracts.py`
  Add zero-row CSV coverage and schema-registration consistency checks.
- `tests/test_framework_metrics.py`
  Validate the `status` enum contract.
- `tests/test_framework_attack_plugins.py` and `tests/test_framework_defense_plugins.py`
  Add duplicate-alias failure coverage through the registry path if practical.
- `tests/test_tracked_output_policy.py`
  Add blocked-artifact cases under `outputs/framework_reports/**`.

Acceptance criteria:

- Schema IDs and on-disk schema files are consistent and discoverable.
- Duplicate plugin aliases fail immediately.
- Empty legacy CSV files no longer pass validation.
- Test order no longer affects runtime-profile expectations.

---

## WS7 - Operator UX And Branch Safety

Severity: medium

Audit findings covered:

- `sweep_and_report.py` progress accounting omits the dashboard step.
- `git_commit_phase` in `auto_cycle.py` commits to the current branch, which is typically `main`.
- `generate_dashboard.py` always writes `docs/index.html` regardless of `--output`.
- Several low-risk clarity items remain open in report and health-check paths.

Required changes:

1. Keep the dashboard generation step inside the progress scope and count it explicitly.
2. Stop unattended loop commits from landing on `main`.
   Preferred option: use a dedicated branch for cycle snapshots and result pushes.
3. Make GitHub Pages output explicit:
   add `--pages-output` or `--no-pages` so `--output` does not silently rewrite `docs/index.html`.
4. Fold in the remaining low-risk clarity items that are not behaviorally risky:
   explicit comments for numeric truthiness where retained,
   documentation for non-runtime health-check helpers,
   small error-message consistency fixes.

Tests to add or extend:

- `tests/test_auto_cycle_and_dashboard.py`
  Cover dashboard progress accounting and pages-output behavior.
- `tests/test_sweep_and_report.py`
  Assert the report-step count includes dashboard generation when enabled.

Acceptance criteria:

- Terminal progress reaches 100 percent only after dashboard generation finishes.
- Dashboard debug runs no longer rewrite the live Pages file by accident.
- Unattended cycle commits do not target `main`.

---

## Verification Plan

Focused test slices by workstream:

- WS1:
  `pytest -q tests/test_auto_cycle_and_dashboard.py tests/test_framework_output_contract.py tests/test_framework_metrics.py tests/test_framework_reporting.py`
- WS2:
  `pytest -q tests/test_train_from_signal.py tests/test_export_training_data.py tests/test_dpc_unet.py tests/test_reproducibility.py`
- WS3:
  `pytest -q tests/test_framework_reporting.py tests/test_cycle_report_generation.py tests/test_auto_cycle_and_dashboard.py`
- WS4:
  `pytest -q tests/test_framework_attack_plugins.py tests/test_attack_objective_contract.py tests/test_reproducibility.py`
- WS5:
  `pytest -q tests/test_dpc_unet.py tests/test_wrapper_checkpoint_contract.py tests/test_framework_defense_plugins.py`
- WS6:
  `pytest -q tests/test_schema_contracts.py tests/test_framework_metrics.py tests/test_tracked_output_policy.py`
- WS7:
  `pytest -q tests/test_auto_cycle_and_dashboard.py tests/test_sweep_and_report.py`

Global gate after each merged workstream:

- `pytest -q`

Manual post-fix checks after WS1-WS3:

1. Run a representative local sweep or dry-run pipeline.
2. Confirm no partial run is skipped.
3. Confirm regenerated reports and dashboard reflect the corrected authority rules.
4. Confirm training-gate behavior matches the intended tolerance band.

---

## Finding To Workstream Map

Domain 1:

- `run_single` metrics-only skip -> WS1
- non-atomic `metrics.json` / `run_summary.json` writes -> WS1
- progress bar overflow -> WS7
- stale run-intent reuse -> WS1
- direct-to-main `git_commit_phase` -> WS7
- silent `save_cycle_history` drop -> WS1
- `_compute_phase4_demotions` break-on-missing-mAP50 -> WS1

Domain 2:

- `_gate_passed` tolerance-band mismatch -> WS2
- `export_training_data.py` exit contract / stale zip reuse -> WS2
- stale extracted training data reuse -> WS2
- hardcoded inner Python interpreter -> WS2
- YOLO running stats updating during fine-tuning -> WS2
- missing `attack_params` in manifest -> WS2
- hardcoded exported checkpoint filename on import -> WS2

Domain 3:

- non-atomic `predictions.jsonl` -> WS1
- silent corrupt JSONL line drop -> WS1
- schema ID / file mismatch -> WS6
- missing validation status enum in schema -> WS6
- undocumented confidence-CI pairing rule -> WS6

Domain 4:

- attack merge missing `attack_signature` -> WS3
- non-atomic summary/team-summary writes -> WS1
- defended-row overwrite in cycle report -> WS3
- inverted warning code name -> WS3
- `NO_VALIDATION` logic filtered too early -> WS3
- dashboard always rewriting Pages output -> WS7
- ambiguous `drop_pct` truthiness guards -> WS3
- raw `ValueError` in slide-table generation -> WS3

Domain 5:

- SquareAttack CPU-generator / device crash -> WS4
- objective-mode string literals -> WS4
- ambiguous `_extract_class_logits` branch priority -> WS4
- Dispersion Reduction seed gap -> WS4
- PGD global RNG reseed side effect -> WS4
- CW `confidence` contract drift -> WS4
- SquareAttack score threshold magic number -> WS4

Domain 6:

- multipass extra final pass -> WS5
- intermediate NaN masking -> WS5
- misleading multipass timestep metadata -> WS5
- missing validation metrics coerced to `0.0` -> WS5
- dead `strict_load_with_report` path -> WS5
- checkpoint provenance hashes current file instead of loaded file -> WS5
- routing policy unknown-hint fallthrough -> WS5

Domain 7:

- `resolve_latest_dir` name sort -> WS6
- runtime-profile cache leakage between tests -> WS6
- duplicate plugin alias overwrite -> WS6
- zero-row legacy CSV false pass -> WS6
- dead exported regression helpers -> WS6/WS7
- permissive tracked-output policy in `framework_reports/**` -> WS6

---

## Done Definition

This remediation is complete when:

- all audit findings in `docs/audit_findings.md` are either fixed or explicitly deferred with rationale,
- blocker workstreams are merged and verified before new unattended cycles begin,
- the focused regression tests named above exist and pass,
- `pytest -q` passes,
- regenerated reports and dashboards no longer rely on stale or cross-merged artifacts.
