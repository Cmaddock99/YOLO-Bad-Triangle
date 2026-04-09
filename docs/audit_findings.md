# Full-Repo Audit Findings

Systematic domain-by-domain audit of the YOLO-Bad-Triangle codebase.
Each domain is audited using `/full-repo-audit <N>`. Findings accumulate here.

See `.claude/skills/full-repo-audit/domains.md` for the full file list per domain.

Status update (verified 2026-04-08):

- Historical inline status bullets below are point-in-time audit snapshots, not the current repo state.
- Current closure check:
  `./.venv/bin/pytest -q` -> `288 passed, 1 deselected`
- The WS1-WS7 remediation slices are now covered by focused regression tests in `tests/`.
- Remaining notes in this file that explicitly say "No fix required" should be read as documented residual risk, not open correctness blockers.

---

## Domain 1 — Core Orchestration (audited 2026-04-07)

### P2 — `run_single` skips on `metrics.json` alone; partial runs silently re-skipped

**File/line:** `scripts/auto_cycle.py` lines 475–478

**Why it matters:** `run_single` (used for all Phase 1–4 tune/validate runs inside `auto_cycle.py`) skips a run directory if `metrics.json` exists, without checking for `run_summary.json` or `predictions.jsonl`. In `run_experiment.py` the write sequence is: `predictions.jsonl` (line 723), `metrics.json` (line 755), `run_summary.json` (line 756). A crash or OOM kill between lines 755 and 756 leaves a valid `metrics.json` on disk with no `run_summary.json`. The next `run_single` call for that run will log "skip (exists)" and return True, silently using a partial artifact. Downstream consumers that read `run_summary.json` (provenance, resume fingerprinting, cycle history) will silently get empty or missing data for that run. This is a silent corruption risk on Phase 4 validate runs, which are the authoritative source for mAP50.

**Evidence:** `auto_cycle.py` line 476 checks only `(run_dir / "metrics.json").exists()`. `sweep_and_report.py` lines 182–184 uses `_required_run_artifacts_status` which checks all three required artifacts. The two callers use inconsistent partial-completion guards.

**Smallest fix:** Replace the `metrics.json`-only check in `run_single` with the same three-artifact check used by `_required_run_artifacts_status` (or import and reuse that function). Only skip if all three required artifacts are present.

---

### P2 — `metrics.json` and `run_summary.json` are written non-atomically, no tmp/replace

**File/line:** `src/lab/runners/run_experiment.py` lines 755–756

**Why it matters:** Both `metrics_file.write_text(...)` and `summary_file.write_text(...)` are plain synchronous writes with no tmp+`os.replace` pattern. The comment on line 739 notes that a "prior double-write" was fixed, but the current single-pass still writes two separate files sequentially. A crash between the two writes leaves `metrics.json` written but `run_summary.json` absent or zero-length. Combined with the P2 above (`run_single` skips on metrics.json alone), this leaves a corrupt run directory that is permanently skipped by auto_cycle. Even without P2, `sweep_and_report.py`'s `_check_resume` would then classify the run as `reran_partial` and re-run it, so at least one path catches it — but only when sweep is the caller.

**Evidence:** Lines 755–756 use `.write_text()` directly. All other persisted state in auto_cycle.py (cycle_state, warm_start, training_signal, cycle history) use `tmp.write_text(...); os.replace(tmp, target)`.

**Smallest fix:** Write both `metrics.json` and `run_summary.json` via tmp files and `os.replace`. Write `metrics.json` last (after summary) so that the presence of `metrics.json` is the reliable completion sentinel that `run_single` already uses.

---

### P3 — Phase 4 tqdm progress bar overflows by one when dashboard step is included

**File/line:** `scripts/sweep_and_report.py` lines 888, 891, 927–939

**Why it matters:** `report_steps = 3 if args.team_summary else 2`. The tqdm bar is declared with `total=report_steps` and receives 3 `update(1)` calls when `team_summary=True` (framework report, team summary, failure gallery — lines 902, 913, 925). However, the dashboard generation (lines 929–939) runs outside the `with tqdm(...)` block but passes `bar=bar4` to `_run_command`, and then calls `bar4.set_description(...)` on the already-closed bar. The dashboard is a fourth report step not counted in `report_steps`. The bar shows 100% after the gallery step, then dashboard output still routes through the closed bar object. This is cosmetically broken (operator sees 3/3 complete before dashboard finishes) and could mask dashboard failures in terminal output.

**Evidence:** `report_steps` is 2 or 3 (line 888). `bar4.update(1)` is called 3 times unconditionally when `team_summary=True` (lines 902, 913, 925). Dashboard command runs after the `with` block closes (lines 927+). `bar=bar4` is still passed to `_run_command` for the dashboard at line 937. `bar4.set_description()` at line 939 is called on a closed bar.

**Smallest fix:** Include the dashboard step inside the `with tqdm(...)` block and add it to `report_steps`. Change `report_steps = 4 if args.team_summary else 3` and add `bar4.update(1)` after the dashboard command.

---

### P3 — `run_single` skip check does not validate run intent; stale artifacts from changed params are silently reused

**File/line:** `scripts/auto_cycle.py` lines 475–478

**Why it matters:** `run_single` skips any run directory where `metrics.json` exists, regardless of whether the run was produced with different parameters. If a tuning run was executed with old params (e.g., from a warm-start), and `carry_forward_params` updates the init values, the Phase 4 validate run that reuses the same `run_name` will be skipped even if the effective overrides changed. The `sweep_and_report.py` path avoids this with a full run-intent fingerprint comparison (`_check_resume`). `auto_cycle`'s `run_single` has no equivalent.

**Evidence:** Line 476 checks only file existence. No fingerprint or intent comparison is performed. `sweep_and_report.py` lines 250–274 implement `_check_resume` with full intent fingerprinting. `auto_cycle.run_single` does not call this.

**Smallest fix:** Add a `--resume` equivalent: compute the intended run fingerprint and compare it to the existing run's `run_summary.json`. If they differ, remove the stale directory and re-run. This is a contained change to `run_single` and would not affect `sweep_and_report.py`.

---

### P3 — `git_commit_phase` commits directly to the default branch on the NUC

**File/line:** `scripts/auto_cycle.py` lines 1864–1876

**Why it matters:** `git_commit_phase` commits `cycle_status.md` and `report_root` directly to whatever branch `HEAD` is on — in practice, `main`. The project memory rule states "Always work on feature branches; never commit directly to main." This is violated on every phase completion in loop mode. `_push_state_to_branch` (lines 1879–1907) partially mitigates this by pushing a separate nuc/sweep-results branch, but the primary commit still lands on main.

**Evidence:** Lines 1864–1873 run `git commit` then `git pull --rebase origin main` then `git push` with no branch specification. The push target is whatever `HEAD` tracks, which in normal operation is `main`.

**Smallest fix:** Either (a) commit/push to a dedicated `nuc/cycle-snapshots` branch in `git_commit_phase`, mirroring the pattern already used in `_push_state_to_branch`, or (b) document explicitly that NUC direct-to-main commits are intentionally exempted from the feature-branch rule.

---

### Open questions / missing tests

1. There are no unit tests for `run_single`, `_compute_phase4_demotions`, `_write_training_signal`, `_coordinate_descent`, or `carry_forward_params`. These are the highest-value orchestration paths and they are entirely untested. A crash or wrong result in any of them silently misroutes training signal or corrupt warm-start state.

2. `_validate_param_spaces()` runs at import time and validates hardcoded init values — but `carry_forward_params` and `load_warm_start` mutate `init` values at runtime without re-running validation. A warm-start value that drifts outside `[min, max]` bounds will never be caught. This is low-risk given the bounds guards in `_clamp`, but the invariant is not enforced continuously.

3. The `TUNE_TOLERANCE_ABS` constant is described as an "absolute floor" for the commit threshold, but it is only used in the diminishing-returns guard (line 1058), not in the per-step commit condition (lines 992–994). The comment is misleading.

4. `git_pull`'s `os.execv` self-restart: the inherited lock fd from the original process is never explicitly closed in the new process before the new lock fd is opened. The old fd is orphaned for the lifetime of the new process. On Linux, all fds for a PID are released on exit, so this is not a lock-leak in practice, but it is unclean and could complicate debugging if the lock file is inspected externally.

5. The `save_cycle_history` function (lines 1357–1428) silently swallows `Exception` on `json.loads` of run artifacts (line 1383). A malformed `run_summary.json` (e.g., partial write) is skipped without logging, so it will not appear in cycle history and the resulting gap in `validation_results` will propagate to training signal and demotions without any warning.

---

domain complete

---

## Domain 1 — Core Orchestration (re-audit 2026-04-08)

Re-audit pass to verify whether prior findings were fixed and to catch anything new.
All six Domain 1 files were read in full.

### Status of prior findings (from 2026-04-07)

- **P2 — `run_single` skips on `metrics.json` alone**: **FIXED.** `auto_cycle.run_single` now uses the shared three-artifact completion contract and run-intent resume checks.
- **P2 — non-atomic `metrics.json` / `run_summary.json` writes**: **FIXED.** `run_experiment.py` now writes canonical artifacts via tmp files and `os.replace`, with `metrics.json` last.
- **P3 — tqdm bar overflows by one (dashboard outside `with` block)**: **FIXED.** `sweep_and_report.py` now counts dashboard generation in the report step flow.
- **P3 — `run_single` skip does not validate run intent**: **FIXED.** `auto_cycle.run_single` now reruns on partial or mismatched fingerprints.
- **P3 — `git_commit_phase` commits directly to main**: **FIXED.** `git_commit_phase` now pushes snapshots to `nuc/cycle-snapshots`.
- **Open Question #5 — `save_cycle_history` bare `except Exception: pass`**: Promoted to finding below.

---

### P2 — `save_cycle_history` silently drops Phase 4 runs on any JSON or I/O error

**File/line:** `scripts/auto_cycle.py` line 1382 (`except Exception: pass`)

**Why it matters:** For each `validate_*/metrics.json` found, `save_cycle_history` reads both `metrics.json` and `run_summary.json`. If either file is malformed (e.g., due to the non-atomic write bug noted above) or any other exception occurs, the bare `except Exception: pass` drops that run from `validation_results` without emitting any log entry. Downstream effects:
1. The dropped run does not appear in cycle history, so `_write_training_signal` and `_compute_phase4_demotions` both operate on incomplete data.
2. The demotion decision in `carry_forward_params` may incorrectly pass or fail a defense because the missing run is treated as absent rather than errored.
3. The missing run leaves a silent provenance gap in `cycle_history/<cycle_id>.json` — operators cannot distinguish "run was never produced" from "run was produced but couldn't be read."

**Evidence:** Lines 1365–1383: the glob yields each `validate_*/metrics.json`; the `try/except` around the entire inner block (including `json.loads` of both files and `_infer_pipeline_semantics`) catches all exceptions and passes silently. No log statement inside the except clause.

**Smallest fix:** Replace `except Exception: pass` with `except Exception as exc: log(f"[warn] save_cycle_history: skipping {mf.parent.name} — {exc}")`. This surfaces the error without changing recovery behavior.

---

### P2 — `_compute_phase4_demotions` silently skips a defense recovery entry when either mAP50 is None

**File/line:** `scripts/auto_cycle.py` lines 655–656

**Why it matters:** When the inner `for defense in ALL_DEFENSES` loop finds a suffix match but either `atk_map50` or `def_map50` is `None`, line 656 does `break`. This exits the defense-scan loop without adding any recovery entry for that attack-defense pair and without logging. The defense's average recovery in `recovery_by_defense` will be computed from fewer data points than expected. If the missing run is the only one for a defense, its average is never computed and it cannot be demoted — a defense that genuinely degraded mAP50 may re-enter Phase 2 next cycle.

**Evidence:** Line 655 checks `if atk_map50 is None or def_map50 is None: break`. No log statement precedes the break. The `recovery_by_defense` dict for that defense is left unchanged. Compare to the matching mAP50-path guard in `_write_training_signal` lines 1562–1563, which uses `continue` (not `break`) and does not log the skip either, but is inside a flat outer loop rather than a nested suffix-match loop.

**Smallest fix:** Replace `break` with `continue` and add a log: `log(f"  [phase4-demotion] missing mAP50 for {key} — skipping recovery entry")`. Using `continue` is semantically correct here because the suffix match was already found; the defense-scan loop has served its purpose and should not check other defenses for this key.

**Note:** The `break` on the success path (line 662) is correct and must remain — it exits the defense-scan after the match is consumed.

---

### Open questions / missing tests (re-audit additions)

1. None of the five open questions from the 2026-04-07 audit have been addressed. They carry forward.
2. `_write_cycle_status` (line 1812) writes `cycle_status.md` via plain `.write_text()`. This file is git-tracked and committed by `git_commit_phase`. A crash mid-write leaves a truncated `cycle_status.md` on disk that gets staged and committed. Impact is cosmetic (tracking file only), but it is inconsistent with the atomic-write pattern used for all other state files.
3. `git_pull`'s self-restart via `os.execv` (line 1775) re-executes the full `sys.argv`, which may include `--reset` or `--status` flags. If the process was invoked with `--reset`, a self-restart after a pull would delete cycle state. In practice, `git_pull` is only called inside the loop body after `STATE_FILE.unlink()`, so `--reset` isn't usually in argv here — but it is worth noting as a flag-ordering hazard.

---

domain complete

---

## Domain 2 — Signal-Driven Training & Gate Logic (audited 2026-04-08)

**Files read:** all five domain files.

---

### P1 — `_gate_passed` dead-codes its tolerance band: effective gate is `-0.001`, not `-0.005`

**File/line:** `scripts/train_from_signal.py` lines 97–119; `scripts/evaluate_checkpoint.py` line 214

**Why it matters:** The tolerance band is the spec correction introduced in PR #69. `_gate_passed` requires both `returncode == 0` AND `delta >= _GATE_THRESHOLD (-0.005)`. The exit-code check already enforces a stricter threshold: `evaluate_checkpoint.py` line 214 exits 0 only when `delta >= -0.001`. For any delta in `[-0.005, -0.001)` the subprocess exits 1, the `result.returncode != 0` guard at line 111 returns False before the threshold check on line 117 runs, and the gate fails. The comment "Our spec allows a -0.005 tolerance band" is correct as intent but wrong as implementation. A candidate with delta = -0.003 is silently rejected when the spec says it should pass.

**Failure mode direction:** False-negative (good candidate rejected).

**Evidence:**
- `evaluate_checkpoint.py` line 214: `return 0 if delta >= -0.001 else 1`
- `train_from_signal.py` line 111: `if result is None or result.returncode != 0: return False` — fires before line 117's `_GATE_THRESHOLD` check
- For delta in `[-0.005, -0.001)`: subprocess exits 1 → returncode guard fires → returns False. The `_GATE_THRESHOLD` check is unreachable for this range.

**Smallest fix (pick one):**
1. Change `evaluate_checkpoint.py` line 214 to `return 0 if delta >= -0.005 else 1` — align the subprocess exit-code threshold to the spec. One-line change.
2. Remove the `result.returncode != 0` guard from `_gate_passed` and rely solely on `delta >= _GATE_THRESHOLD` — but requires verifying the result JSON is always written even on failure.

Option 1 is safer.

---

### P2 — `export_training_data.py` exits 0 on no usable attacks; stale zip at same path silently passes into training

**File/line:** `scripts/export_training_data.py` lines 213–219; `scripts/train_from_signal.py` lines 280–286

**Why it matters:** When `--from-signal` mode finds no usable adversarial image dirs, `export_training_data.py` prints a warning and calls `sys.exit(0)`. Back in `train_from_signal.py`, the returncode guard at line 281 does not trigger. The subsequent zip-existence guard at line 284 catches the missing zip and aborts — but only if the zip was not already on disk from a prior run with the same `cycle_id`. If a stale zip exists at the expected path, the export step silently re-uses old adversarial images, training proceeds on stale data, and the manifest records the correct `signal_path` but incorrect image content. No provenance warning is emitted.

**Failure mode direction:** False-positive (stale artifact passes into training).

**Evidence:**
- `export_training_data.py` lines 213–219: `sys.exit(0)` on no usable attacks — no error file written.
- `train_from_signal.py` line 281: returncode check only; line 284: catches missing zip but not a stale zip.
- Zip path is `outputs/training_exports/<cycle_id>_training_data.zip` — deterministic from cycle_id, so a stale file from a prior run with the same id will be reused silently.

**Smallest fix:** Change `export_training_data.py` line 219 from `sys.exit(0)` to `sys.exit(2)` when no usable attacks are found. Exit 0 is the wrong contract when called from an automated pipeline.

---

### P2 — `train_dpc_unet_local.py` reuses stale extracted training data when zip filename is unchanged

**File/line:** `scripts/train_dpc_unet_local.py` lines 335–343

**Why it matters:** The extraction guard at line 336 checks only `if not extract_dir.exists()`. A new zip with updated adversarial images at the same filename will silently reuse the old extracted data. Any automated signal-driven training that produces the same zip filename across reruns (same `cycle_id` or same preset) will train on old images. The operator sees `Training data already extracted` and may not notice.

**Failure mode direction:** False-positive (stale training data used without warning).

**Evidence:** Lines 335–343: no mtime comparison, no checksum, no zip manifest. The extraction dir name is `outputs/training_data/<zip_path.stem>`, deterministic from the zip filename.

**Smallest fix:** Add a mtime comparison before the skip: if `zip_path.stat().st_mtime > extract_dir.stat().st_mtime`, delete `extract_dir` and re-extract. Two-line addition to the extraction guard.

---

### P2 — `evaluate_checkpoint.py` subprocess always uses hardcoded `.venv/bin/python`; caller's `--python-bin` is not propagated

**File/line:** `scripts/evaluate_checkpoint.py` line 45; `scripts/train_from_signal.py` lines 224–241

**Why it matters:** `evaluate_checkpoint.py` defines `PYTHON = REPO / ".venv" / "bin" / "python"` at line 45 and uses it for the inner `run_unified.py` subprocess. `train_from_signal.py` passes `args.python_bin` when invoking `evaluate_checkpoint.py` itself via `build_repo_python_command`, but there is no mechanism to pass that python bin further into the inner subprocess. If the venv is not at `.venv/` (e.g., on a remote machine with a different layout), the inner run silently uses the wrong interpreter or fails.

**Failure mode direction:** Loud failure (interpreter not found) if venv path differs; silent wrong-interpreter use if another Python exists at that path.

**Evidence:** Line 45: `PYTHON = REPO / ".venv" / "bin" / "python"` — no `--python` CLI argument exposed. `train_from_signal.py` lines 224–241 pass `python_bin=args.python_bin` to the outer invocation only.

**Smallest fix:** Expose `--python` as a CLI argument in `evaluate_checkpoint.py` (defaulting to `.venv/bin/python`) and use it instead of the module-level constant.

---

### P3 — `train_dpc_unet_local.py` detector alignment pass leaves YOLO running-stats updating during fine-tuning

**File/line:** `scripts/train_dpc_unet_local.py` lines 426–427

**Why it matters:** `yolo_inner.train()` is called at line 426, then `p.requires_grad_(False)` is applied at line 427. `requires_grad=False` prevents weight-gradient accumulation but does not stop BatchNorm/GroupNorm running-stat updates in train mode. YOLO's internal normalization layers will accumulate running mean/variance from the purified denoiser outputs during fine-tuning, causing their statistics to drift from what was observed during pretraining. This affects the feature activations used for the detector alignment loss, potentially making the loss signal less accurate over time.

**Evidence:** Line 426: `yolo_inner.train()`. Line 427: `p.requires_grad_(False)` — does not prevent running-stat updates. No `yolo_inner.eval()` call after the freeze.

**Smallest fix:** Replace line 426 `yolo_inner.train()` with `yolo_inner.eval()` (or add `yolo_inner.eval()` immediately after line 427). The YOLO model is used only for loss computation, not for its own training.

---

### P3 — `train_from_signal.py` manifest omits `attack_params` used by the attack gate; evaluation is not reproducible from the manifest alone

**File/line:** `scripts/train_from_signal.py` lines 188–191

**Why it matters:** The manifest `attack_gate` key records `attack`, `result_path`, `delta_mAP50`, and `verdict` — but not the `--attack-params` passed to `evaluate_checkpoint.py`. If `worst_attack_params` from the signal is non-empty, the gate evaluation used non-default params that are not recorded anywhere in the manifest. Operators reading the manifest cannot reproduce the gate result without cross-referencing the signal file.

**Evidence:** Lines 188–191: no `params` field in `manifest["attack_gate"]`. Lines 257–262: `worst_attack_params` entries are passed as `--attack-params` args but never written to manifest.

**Smallest fix:** Add `"attack_params": worst_attack_params` to `manifest["attack_gate"]` at line 188. One-line dict addition.

---

### P3 — `export_training_data.py` checkpoint filename in zip is hardcoded on extraction; non-default `--checkpoint` silently falls back to repo root

**File/line:** `scripts/export_training_data.py` line 240; `scripts/train_dpc_unet_local.py` lines 357, 370–374

**Why it matters:** `export_training_data.py` packs the checkpoint as `checkpoint/<checkpoint.name>`. `train_dpc_unet_local.py` reads it back at the hardcoded path `extract_dir / "checkpoint" / "dpc_unet_final_golden.pt"`. If `--checkpoint` is set to a non-default name, the zip will contain `checkpoint/<other_name>.pt`, the hardcoded path will not exist, and the fallback at line 372 silently uses `ROOT / "dpc_unet_final_golden.pt"` without any distinguishing warning. The training run proceeds with a different checkpoint than was exported.

**Evidence:** `train_dpc_unet_local.py` line 357: literal `"dpc_unet_final_golden.pt"` regardless of zip contents. Lines 370–374: fallback with identical print format to non-fallback path.

**Smallest fix:** In `train_dpc_unet_local.py`, replace the hardcoded filename with `list((extract_dir / "checkpoint").glob("*.pt"))` and take the first match. Log explicitly when falling back to the repo root.

---

### Open questions / missing tests

1. **No unit test for `_gate_passed` tolerance-band behavior.** A test with a mocked `CompletedProcess(returncode=1)` and `delta=-0.003` would have caught the P1 immediately.

2. **No test for `export_training_data.py` exit contract.** The `sys.exit(0)` on no usable attacks is the wrong contract for a pipeline-facing script and is untested.

3. **`train_dpc_unet_local.py` has no test coverage.** Dataset pair-building, oversampling, preset defaults application, and checkpoint path resolution are all untested. These determine what data the model trains on.

4. **`train_dpc_unet_feature_loss.py` is a smoke-path stub** using random tensors (lines 70–71). It cannot catch any real training bug. Its purpose is structural import validation only; the docstring should state this explicitly.

5. **`signal_driven` preset sets `fresh=True`** (line 67 of `train_dpc_unet_local.py`). An interrupted signal-driven training cannot resume. No comment explains this intentional behavior.

6. **`evaluate_checkpoint.py` clean sentinel write** (`CLEAN_VALIDATION_SENTINEL`, lines 209–210) is non-atomic. Concurrent clean evals would silently overwrite each other.

---

domain complete

---

---

## Domain 3 — Evaluation & Metrics (audited 2026-04-08)

**High-risk surface contact:** `src/lab/eval/` and `src/lab/config/contracts.py` are explicitly listed as high-risk surfaces in CLAUDE.md.

---

### P2 — `write_predictions_jsonl` writes non-atomically; a mid-write crash produces a silently truncated `predictions.jsonl`

**File/line:** `src/lab/eval/prediction_utils.py` lines 18–23

**Why it matters:** `predictions.jsonl` is a required run artifact. The function opens the file with `open("w")` and writes records line-by-line with no tmp-then-rename pattern. A crash or OOM kill between the first and last write leaves a truncated file at the canonical path. Any subsequent reader (`_load_predictions` in `bootstrap.py`, `run_single` in `auto_cycle.py`, downstream reporting) will silently process a partial file. The existing `run_single` skip-check (Domain 1 P2 finding) checks only `metrics.json`, so a truncated `predictions.jsonl` will not cause a re-run. This is the third leg of the artifact-write trilogy already identified in Domains 1 and 2.

**Evidence:** `prediction_utils.py` lines 20–23: `output_path.open("w") ... handle.write(...)` with no tmp. `auto_cycle.py` line 476 checks only `metrics.json`. `bootstrap.py` lines 10–27 silently skip unparseable lines — a truncated final line will be silently dropped with no indication.

**Smallest fix:** Write to `output_path.with_suffix(".jsonl.tmp")` first, flush and close, then `os.replace(tmp, output_path)`. One-line addition.

---

### P2 — `_load_predictions` silently drops corrupt JSONL lines; bootstrap CI `n_images` count is misleading when lines are skipped

**File/line:** `src/lab/eval/bootstrap.py` lines 22–26

**Why it matters:** `_load_predictions` catches `json.JSONDecodeError` and continues without logging, without incrementing any counter, and without setting any flag in the result dict. The returned `result["n_images"]` reflects only successfully-paired records. If a `predictions.jsonl` is corrupt or truncated, the bootstrap CI is computed over a reduced population with no indication. A caller presenting this result cannot distinguish a 100-image run from a 90-image run where 10 lines were silently dropped. The CI bounds will be narrower than they should be (overclaiming precision), which directly undermines the scientific validity of the CI output.

**Evidence:** `bootstrap.py` line 22: `except json.JSONDecodeError: continue` — no log, no counter. `result["n_images"]` is set at line 103 from `len(common_ids)`, which is the intersection of successfully-parsed IDs, not the expected run image count.

**Smallest fix:** Add a `skipped` counter inside `_load_predictions`; return `(records, skipped_count)` and propagate `skipped_lines` into the result dict. Add a `note` field when `skipped_count > 0`. Alternatively, at minimum, log a warning with the count when nonzero.

---

### P2 — Four schema IDs declared in `contracts.py` have no corresponding `.schema.json` file; two schema files exist with no `contracts.py` entry

**File/line:** `src/lab/config/contracts.py` lines 9–12, 19–22; `schemas/v1/`

**Why it matters:** `contracts.py` declares `cycle_summary/v1`, `warnings/v1`, `headline_metrics_csv/v1`, and `per_class_vulnerability_csv/v1` as schema IDs (lines 9–12) with corresponding entries in `SCHEMA_IDS` (lines 19–22), but none of these have `.schema.json` files in `schemas/v1/`. Conversely, `schemas/v1/system_health_summary.schema.json` and `schemas/v1/demo_manifest.schema.json` exist but have no entries in `SCHEMA_IDS`. Any code that uses `SCHEMA_IDS` to look up a schema path for validation will silently fail to find the file, or will be unable to discover the health/manifest schemas by their ID. Schema validation tools and CI checks that enumerate `schemas/v1/` cannot cross-check against `SCHEMA_IDS`.

**Evidence:**
- Declared in `SCHEMA_IDS` but no file: `cycle_summary`, `warnings`, `headline_metrics_csv`, `per_class_vulnerability_csv`.
- Files exist but no `SCHEMA_IDS` entry: `system_health_summary.schema.json`, `demo_manifest.schema.json`.
- Confirmed by directory listing: `schemas/v1/` contains exactly five files, none of which are the four missing ones.

**Smallest fix:** For each schema ID declared in `contracts.py` without a file, either (a) create a minimal `schemas/v1/<name>.schema.json` or (b) remove the `SCHEMA_IDS` entry if the schema is genuinely unused. For `system_health_summary` and `demo_manifest`, add entries to `SCHEMA_IDS` so they are discoverable. Do not bundle both directions into one PR.

---

### P3 — `validation_status` returns a fixed set of four string constants but the schema does not constrain the `status` field to those values

**File/line:** `src/lab/eval/framework_metrics.py` lines 11–20, 28–34; `schemas/v1/framework_metrics.schema.json` lines 36–41

**Why it matters:** `framework_metrics.py` defines four named status constants (`missing`, `partial`, `complete`, `error`) and `validation_status()` only returns three of them. The `error` constant is declared but `validation_status()` never returns it; it is only set by `run_experiment.py` directly when validation throws. The schema's `validation` object requires `status` and `enabled` but does not enumerate allowed `status` values. A consumer implementing the schema cannot validate correctness without reading the code. A bug that emits an arbitrary string as `status` would pass schema validation and all existing tests.

**Evidence:** `framework_metrics.py` line 12: `VALIDATION_STATUS_ERROR = "error"` declared. Lines 28–34: `validation_status()` never returns `"error"`. `schemas/v1/framework_metrics.schema.json` line 38: `"required": ["status", "enabled"]` with no `enum` constraint. `test_framework_metrics.py`: no test for the `error` status path.

**Smallest fix:** Add `"enum": ["missing", "partial", "complete", "error"]` to the `status` property in `framework_metrics.schema.json`. One-field schema addition with no behavioral change.

---

### P3 — `bootstrap_paired_ci` confidence CI resamples from a non-paired subset without documenting the pairing break

**File/line:** `src/lab/eval/bootstrap.py` lines 116–118, 141–157

**Why it matters:** The detection CI resamples paired `(baseline_det[idx], attack_det[idx])` using the same index vector, preserving per-image pairing. The confidence CI discards images where either baseline or attack had zero detections. The surviving arrays remain aligned by construction (same mask applied to both), but the alignment is implicit and undocumented. If the mask logic is modified to allow one-sided masking, the CI becomes unpaired without any obvious failure. The docstring says "paired bootstrap" with no mention of the image-exclusion rule.

**Evidence:** Lines 116–118: mask computed as `b is not None and a is not None`; both arrays compressed with the same mask — alignment is structural but undocumented. Line 67 docstring: "Paired bootstrap CI" with no mention of the image-exclusion rule.

**Smallest fix:** Add a comment at line 116: `# Exclude image pairs where either side has no detections (avg_conf is None); arrays remain paired.` No code change required.

---

### Open questions / missing tests

1. **No unit tests for `bootstrap_paired_ci`.** The function is non-trivial (2000-iteration loop, two distinct resampling paths, nan-handling, early-exit conditions at n<4 and det_valid<0.9). It is used in `auto_summary.py` to produce CI bounds that appear in team summaries. There is no test that exercises the nan path, the early-exit path, or verifies the bounds are monotone (`lower <= point <= upper`).

2. **No unit tests for `compute_per_class_detection_drop`, `compute_confidence_drop`, or `compute_normalized_defense_recovery`.** Only `compute_detection_drop` and `compute_defense_recovery` are exercised in `test_e2e_pipeline.py`. The normalized recovery function is entirely untested — including its documented edge case (returns `None` when `|degradation| < 1e-9`).

3. **`write_predictions_jsonl` accepts `Iterable[PredictionRecord]`, not `list`.** If a caller passes a lazy generator that raises mid-iteration, the output file will contain a partial JSONL at the canonical path. The current call site in `run_experiment.py` passes a fully-materialized list, but the type signature does not enforce this. Consider tightening the signature to `list[PredictionRecord]`.

4. **`summarize_prediction_metrics` counts detections from `boxes` but `bootstrap.py` counts from `scores`.** `framework_metrics.py` line 43 uses `len(record.get("boxes", []))`. `bootstrap.py` line 31 uses `len(scores)`. Both should be equivalent post-validation, but the inconsistency is a latent risk if either is ever used on unvalidated records.

5. **`system_health_summary.schema.json` uses both `id` and `schema_id` fields (lines 2–3)** — redundant and inconsistent with all other schemas which use only `id`. No blocking finding, but should be normalized when the schema is next touched.

6. **`framework_metrics.schema.json` does not require `images_without_detections` or `detections_per_image_mean`** even though `summarize_prediction_metrics` always emits them. Consumers relying on those fields cannot validate their presence via the schema.

---

domain complete

## Unreviewed files

All domain files reviewed.

---

## Domain 4 — Reporting & Summaries (audited 2026-04-08)

**Files read:** all files in the domain list (6 reporting module files + 9 scripts).
**High-risk surface contact:** `src/lab/reporting/` is explicitly listed in CLAUDE.md.

---

### P1 — `_merge_effectiveness_and_recovery` keys on `(model, seed, attack)` without attack signature; cross-product merge when multiple attack configs share a name

**File/line:** `src/lab/reporting/auto_summary.py` lines 512–534

**Why it matters:** `_merge_effectiveness_and_recovery` builds a lookup keyed by `(model, seed, attack)` (line 514). `build_comparison_rows` (called earlier) can emit multiple rows with the same `(model, seed, attack)` name but different `attack_run`, `objective_mode`, `target_class`, or `attack_roi` — for example `deepfool` with `target_class=0` and `deepfool` with `target_class=3`. The merge loop iterates over every attack row and looks up `recovery_lookup.get(key)`, which returns ALL defense rows for that `(model, seed, attack)` tuple. The result is a cross-product: `deepfool+target_class=0` gets merged with defense rows that matched the signature of `deepfool+target_class=3`. The merged rows will carry incorrect `defended_mAP50`, `detection_recovery_normalized`, and `mAP50_recovery_normalized` for the wrong attack variant. These values flow directly into `write_headline_csv`, which is the machine-parseable output consumed by downstream analysis.

**Evidence:** Line 514: `key = (r.get("model"), r.get("seed"), r.get("attack"))` — no `attack_signature`. `build_comparison_rows` (framework_comparison.py line 346) passes `attack_signature` as a row field but does not include it in the merge key. `build_defense_recovery_rows` similarly emits `attack_signature` (line 429) but it is not used in the merge lookup.

**Smallest fix:** Change line 514 to key on `(model, seed, attack, attack_signature)` — where `attack_signature` is read as `r.get("attack_signature") or ""` — and change line 519 to `key = (arow.get("model"), arow.get("seed"), arow.get("attack"), arow.get("attack_signature") or "")`. This is a two-line change. The fallback to `""` preserves backward compatibility when `attack_signature` is absent.

---

### P2 — `write_summary_csv` and `write_team_summary` write output files non-atomically

**File/line:** `src/lab/reporting/framework_comparison.py` line 302; `src/lab/reporting/team_summary.py` lines 384–385

**Why it matters:** `write_summary_csv` uses `output_csv.open("w", ...)` (line 302) — a plain direct write with no tmp+`os.replace`. `write_team_summary` uses `json_path.write_text(...)` and `md_path.write_text(...)` (lines 384–385) — also direct writes. A crash or signal mid-write leaves a truncated file at the canonical path (`framework_run_summary.csv`, `team_summary.json`, `team_summary.md`). `framework_run_summary.csv` is the primary input to `generate_team_summary.py` and `generate_dashboard.py`. A truncated CSV will be silently parsed by `csv.DictReader`, which will process whatever rows were written before the crash — downstream comparison tables and dashboard cards will be computed from incomplete data with no error.

**Evidence:** `framework_comparison.py` line 302: `output_csv.open("w", ...)` — no tmp. Contrast with `auto_summary.py` lines 547–553, 563–565, which correctly use `tmp = path.with_suffix(".tmp"); os.replace(tmp, path)`. `team_summary.py` lines 384–385: plain `.write_text()` on both outputs.

**Smallest fix:** In `write_summary_csv`, write to `output_csv.with_suffix(".csv.tmp")` and `os.replace(tmp, output_csv)`. In `write_team_summary`, apply the same pattern to both `json_path` and `md_path`. This matches the pattern already used in `write_auto_summary`.

---

### P2 — `_parse_validation` in `generate_cycle_report.py` silently overwrites defended runs with no authority or phase selection

**File/line:** `scripts/generate_cycle_report.py` lines 85–89

**Why it matters:** For attack-only rows, `_parse_validation` deduplicates by keeping the entry with more detections (line 82). For defended rows, line 87 performs an unconditional `defended_map[(str(atk), str(dfn))] = v` — last-seen wins with no comparability check, no authority preference, and no phase preference. If a cycle's `validation_results` contains two defended entries for the same `(attack, defense)` pair — which can happen when both Phase 1 smoke and Phase 4 validate runs appear — the last entry encountered during dict iteration determines the reported `mAP50`, `recovery_pct`, and the "best defended" executive summary value. The cycle report may attribute Phase 1 smoke metrics as the authoritative defended result.

**Evidence:** Line 87: `defended_map[(str(atk), str(dfn))] = v` — no comparison against existing entry. Compare to the attack-only dedup at lines 81–83 which at least applies a `detections` comparison.

**Smallest fix:** Mirror the attack-only dedup pattern: keep the existing entry if `(v.get("detections") or 0) <= (defended_map[(atk, dfn)].get("detections") or 0)` (prefer higher detections as a proxy for the more complete run), or preferably read `source_phase` from `v` and apply `_PHASE_PRIORITY` to select Phase 4 over Phase 1. A two-line addition.

---

### P2 — `WARN_HIGH_CONFIDENCE_FLOOR` fires when confidence is LOW, not high; code name is inverted relative to behavior

**File/line:** `src/lab/reporting/warnings.py` lines 106–115

**Why it matters:** The warning code is named `WARN_HIGH_CONFIDENCE_FLOOR` (line 18), and its message says "Baseline avg_confidence is below 0.5; model may be under-confident." The code fires when `baseline_conf < 0.5` — i.e., when confidence is below the threshold, not above it. The name implies the floor is high (concern: model is over-confident or filtering too aggressively), but the behavior flags under-confidence. Operators reading `HIGH_CONFIDENCE_FLOOR` in logs or warning outputs will expect an inflated-confidence warning. This is a silent mis-labeling: the right condition may trigger the wrong remediation.

**Evidence:** Line 106: `if baseline_conf is not None and float(baseline_conf) < 0.5:` — fires when confidence is *below* 0.5. Line 18: `WARN_HIGH_CONFIDENCE_FLOOR = "HIGH_CONFIDENCE_FLOOR"`. The word "floor" suggests the floor value is high, not the current value.

**Smallest fix:** Rename the constant and code to `WARN_LOW_BASELINE_CONFIDENCE` / `"LOW_BASELINE_CONFIDENCE"`. Update the one declaration and the one usage. Update `warnings.json` schema if it enumerates valid codes.

---

### P2 — `evaluate_warnings` applies `_prefer_authoritative_rows` before the `NO_VALIDATION` check; suppresses the warning if authoritative smoke rows have no mAP50

**File/line:** `src/lab/reporting/warnings.py` lines 80–95

**Why it matters:** `evaluate_warnings` first filters `attack_rows` to authoritative-only via `_prefer_authoritative_rows` (line 80), then checks `has_validation` — whether any of those rows has `is_validation_success(validation_status)` (lines 84–87). If all authoritative rows are Phase 1 smoke runs (no mAP50, `validation_status != "complete"`), `has_validation` is False. The subsequent guard at line 88 checks `not attack_rows_are_diagnostic_only` — but these are authoritative rows, not diagnostic, so `attack_rows_are_diagnostic_only` is False. The warning fires. So far so good. However, if there are no authoritative rows but diagnostic rows do have `validation_status == "complete"`, `_prefer_authoritative_rows` falls back to all rows (line 45), `has_validation` is True, and the warning does not fire. This path is correct. The real problem is the inverted case: if authoritative rows exist but none have `validation_status == "complete"`, the warning fires — even if Phase 4 rows in the full payload would have succeeded. This matches the documented `auto_summary false-positive warning` in CLAUDE.md. The warning is not a false-positive per se; it fires accurately given the filtered row set. But the filtering discards Phase 4 authoritative rows that may carry `validation_status == "complete"` if they come from a different `authority` value than the authoritative rows already seen.

**Evidence:** Line 80: `_prefer_authoritative_rows(attack_rows)` before `has_validation` check. CLAUDE.md `auto_summary false-positive warning` section documents the Phase 1/Phase 4 shadowing issue at the payload level, not at the warnings level.

**Smallest fix:** Before applying `_prefer_authoritative_rows`, check if any row in the full (unfiltered) `attack_rows` has `is_validation_success(...)`. If yes, set `has_validation = True` regardless of the filtered set. This preserves the filter for LOW_ATTACK_COUNT and ATTACK_BELOW_NOISE while not suppressing the validation-success information that exists in the payload.

---

### P3 — `generate_dashboard.py` writes unconditionally to `docs/index.html` regardless of `--output` flag; no atomic write on either output

**File/line:** `scripts/generate_dashboard.py` lines 584–587

**Why it matters:** Lines 584–587 always resolve and write `docs/index.html` regardless of the `--output` argument. If the dashboard is generated for a debug or staging purpose with a non-default `--output`, it still overwrites the live GitHub Pages file. This is a silent side-effect of every dashboard invocation. Additionally, both the primary output (line 582) and the Pages output (line 587) use `output.write_text(...)` / `pages_out.write_text(...)` — plain non-atomic writes. A crash mid-write corrupts the live GitHub Pages file.

**Evidence:** Line 584: `pages_out = Path("docs/index.html").resolve()` — hardcoded, not derived from `output`. Lines 582 and 587: `.write_text(html, ...)` — no tmp+replace.

**Smallest fix (two independent sub-fixes):** (1) Add a `--no-pages` flag (default False) and gate lines 584–587 on `not args.no_pages`; or expose `--pages-output` as a CLI argument. (2) Write both outputs via tmp files and `os.replace`. These can be separate PRs.

---

### P3 — `generate_cycle_report.py` computes `drop_pct` incorrectly when `baseline_dets` is falsy but non-zero

**File/line:** `scripts/generate_cycle_report.py` line 139

**Why it matters:** Line 139: `if baseline_dets and atk_dets is not None:` — uses `baseline_dets` in a boolean context. If `baseline_dets` is `0`, the condition is False and `drop_pct` stays `None`. This is correct: zero baseline means drop is undefined. But if `baseline_dets` is `0.0` (a float zero from JSON), it is also falsy, which is correct. However if `baseline_dets` is any other falsy value that is not truly zero (e.g., an empty string that slipped through a `dict.get` call without a numeric cast), the condition silently skips the computation. The issue is cosmetically similar to Domain 1's `not baseline_dets` patterns. More importantly, lines 166 and 451 use `if baseline_dets and atk_dets is not None` with no explicit zero-guard comment, making the behavior non-obvious to maintainers.

**Evidence:** Lines 139, 166, 451: `if baseline_dets and ...` — truthiness check on a numeric value with no explicit comparison operator.

**Smallest fix:** Replace `if baseline_dets and` with `if baseline_dets is not None and baseline_dets != 0 and` (or `if baseline_dets:` with an inline comment `# falsy covers 0 and None — both mean drop is undefined`). The behavior is correct for numeric types; the fix is documentation/clarity only unless the source can produce non-numeric falsy values.

---

### P3 — `generate_slide_tables.py` raises `ValueError` instead of printing a user-facing error when CSV outputs are empty

**File/line:** `scripts/generate_slide_tables.py` lines 463–466

**Why it matters:** `_write_csv` raises `ValueError(f"No rows available for output: {path}")` when `rows` is empty (line 463). All four callers in `main()` (lines 587–590) let this exception propagate unhandled. The user sees a Python traceback from `ValueError` rather than a clean `ERROR:` message and a non-zero exit code. While this fails loudly (good), the error format is inconsistent with the rest of the script which uses `raise SystemExit(f"ERROR: ...")` (lines 513, 529). On a CI system, the distinction between `ValueError` and `SystemExit` may affect error-log parsing.

**Evidence:** `_write_csv` line 463: `raise ValueError(...)`. Other early-exit paths in `main()` (lines 513, 529) use `SystemExit`. No `try/except` wraps the four `_write_csv` calls.

**Smallest fix:** Change `raise ValueError(...)` to `raise SystemExit(f"ERROR: no rows available for output: {path}")` — consistent with the rest of the script.

---

### Open questions / missing tests

1. **No unit tests for `build_comparison_rows`, `build_defense_recovery_rows`, or `build_per_class_rows`.** These are the core authority-selection and comparability functions. The P1 finding above (cross-product merge) would be immediately caught by a test that creates two attack records with the same name but different `attack_signature` values.

2. **No unit tests for `evaluate_warnings`.** The `NO_VALIDATION` false-positive path (Phase 1 shadowing Phase 4) is documented in CLAUDE.md as a known issue, but there is no regression test that exercises the conditions under which it fires or suppresses correctly.

3. **`generate_cycle_report.py` imports no project library code.** It re-implements baseline/attack classification with its own `_is_baseline`/`_is_attack_only` helpers that use `in (None, "none", "")` rather than the shared `is_none_like` from `framework_comparison.py`. These two implementations can diverge. Minimum fix: import and use `is_none_like`.

4. **`analyze_per_class.py` merges multiple baseline run counts by summing them** (line 123: `merged_baseline[cid]["count"] += ...`). If multiple baseline runs with different image counts are present (e.g., smoke + full), the summed count inflates the baseline denominator and makes detection drops appear smaller than they are. No warning is emitted when more than one baseline run is found.

5. **`_build_markdown_provenance` in `team_summary.py` resolves `eval_ab_clean.json` relative to `report_root.parents[1]`** (line 287). If the report root is nested differently than `outputs/framework_reports/<sweep_id>`, this path silently resolves to the wrong location and `clean_gate_text` is "not evaluated" with no warning. The CLAUDE.md canonical path for A/B eval artifacts is `outputs/eval_ab_*.json` — which is one level up from `outputs/framework_reports/`, so `parents[1]` is correct for the canonical layout. But it is not validated.

6. **`generate_failure_gallery.py` does not filter for `attack_then_defense` semantic order when selecting defended records.** `_select_records` uses `discover_framework_runs` and groups all defended runs regardless of `semantic_order`. A legacy `defense_then_attack` defended run will appear in the gallery alongside current-era runs with no comparability warning.

---

domain complete

## Unreviewed files
All domain files reviewed.

---

## Domain 5 — Attack Plugins (audited 2026-04-08)

### P1 — `SquareAttack`: CPU generator passed to `torch.randint` with non-CPU `device` arg; crashes on GPU/MPS

**File/line:** `src/lab/attacks/square_adapter.py` lines 97–98

**Why it matters:** `_apply_to_tensor` creates a `torch.Generator(device="cpu")` (square_adapter.py line 168 via `apply()`; or directly in tests). At line 97–98 it calls:
```python
sign = torch.randint(0, 2, (...), generator=generator, device=device).float() * 2.0 - 1.0
```
where `device = x_padded.device`. PyTorch requires that the generator's device matches the output tensor's device. If `device` is anything other than `"cpu"` (e.g. `"cuda"` or `"mps"`), PyTorch raises a `RuntimeError` at runtime. The `apply()` method always converts the image to CPU via `torch.from_numpy(...)` so this path is safe when called through `apply()`. However `_apply_to_tensor` is part of the class interface and callers (including tests or future defenses that move tensors to GPU before calling) will crash silently. The companion `torch.randint` calls at lines 93–94 do not pass `device=` at all (they default to CPU), which avoids the crash but breaks reproducibility: the `top`/`left` values are always drawn from a CPU generator regardless of `device`, which is inconsistent with the `sign` tensor.

**Evidence:** Line 168: `generator = torch.Generator(device="cpu")`. Lines 93–94: no `device=` arg. Lines 97–98: `device=device` on a CPU generator. The `SquareAttackAdapter.device` field defaults to `"cpu"` (line 133) but is not used to move the input tensor in `apply()` (line 172 calls `_image_to_tensor` which always produces a CPU tensor).

**Smallest fix:** Remove `device=device` from the `torch.randint` at lines 97–98 (generate on CPU, then move: `sign = torch.randint(..., generator=generator).float() * 2.0 - 1.0; sign = sign.to(device)`). Alternatively, keep the generator on CPU and always generate on CPU then `.to(device)`. Do not change lines 93–94 — those are already CPU-only and correct.

---

### P2 — `DeepFoolAttack._detection_confidence` uses raw string literals for objective modes instead of contract constants

**File/line:** `src/lab/attacks/deepfool_adapter.py` lines 76, 78

**Why it matters:** `_detection_confidence` compares `self.objective.mode` against hardcoded string literals `"target_class_misclassification"` and `"class_conditional_hiding"` rather than `ATTACK_OBJECTIVE_TARGET_CLASS` and `ATTACK_OBJECTIVE_CLASS_HIDE` from `contracts.py`. The same bug appears in `FGSMAttack._compute_loss` (fgsm_adapter.py lines 90, 94), which is the shared parent. If the canonical constant values are ever changed in `contracts.py`, the comparisons in these two methods will silently stop matching, causing `_detection_confidence` to fall through to the untargeted heuristic path (lines 85–96) and `_compute_loss` to raise `ValueError("Unsupported objective mode: ...")` — two different failure modes for the same root cause. The failure in `_compute_loss` is loud; the failure in `_detection_confidence` is silent (wrong objective, wrong attack direction, no error).

**Evidence:** `contracts.py` line 68: `ATTACK_OBJECTIVE_TARGET_CLASS = "target_class_misclassification"`. Line 69: `ATTACK_OBJECTIVE_CLASS_HIDE = "class_conditional_hiding"`. `deepfool_adapter.py` lines 76, 78 and `fgsm_adapter.py` lines 90, 94: direct string literals without import or reference to these constants.

**Smallest fix:** In `deepfool_adapter.py` import `ATTACK_OBJECTIVE_TARGET_CLASS, ATTACK_OBJECTIVE_CLASS_HIDE` from `lab.config.contracts` and replace the literal strings at lines 76 and 78. Do the same in `fgsm_adapter.py` lines 90 and 94 (both already import `ATTACK_OBJECTIVE_UNTARGETED` from contracts, so only two additional names need to be added to the existing import).

---

### P2 — `_extract_class_logits` has ambiguous branch priority for square tensors where both `shape[1] > 6` and `shape[-1] > 6`

**File/line:** `src/lab/attacks/fgsm_adapter.py` lines 144–150 (inherited by PGD, DeepFool, EOT-PGD, CW, DR)

**Why it matters:** For a 3-D tensor where both `shape[1] > 6` and `shape[-1] > 6` are true (e.g. shape `(1, 84, 84)` from a YOLO variant that outputs a square anchor grid), the function returns from the first branch (treating axis 1 as channels) and never reaches the second branch. The two branches make opposite layout assumptions: the first assumes `(batch, channels, anchors)` and slices `out[:, 4:, :]`; the second assumes `(batch, anchors, channels)` and slices `out[..., 5:]`. An incorrect layout assumption produces wrong class logit indices — the attack optimises the wrong channels and the objective loss is meaningless. There is no guard, warning, or assertion to detect the ambiguity. The comment on line 145 says "Common raw YOLO path" but does not document the disambiguation criterion.

**Evidence:** Lines 146–147 check `out.shape[1] > 6` first. A tensor of shape `(1, 84, 84)` satisfies this condition, but is processed as channel-major. If it is actually anchor-major, the resulting class logit slice `out[:, 4:, :]` contains box coordinates and random positional data rather than class logits.

**Smallest fix:** Add an explicit shape heuristic comment and, where possible, prefer a non-ambiguous discriminant (e.g. `shape[1] < shape[2]` as a tiebreaker: fewer channels than anchors is the canonical raw-YOLO layout). Also add a `LOGGER.debug` warning when both conditions are true simultaneously so the ambiguity is at least visible in debug output.

---

### P2 — `DispersionReductionAdapter`: no seed / determinism support; randomised start is unreproducible across runs

**File/line:** `src/lab/attacks/dispersion_reduction_adapter.py` lines 60–61

**Why it matters:** `_DispersionReductionCore.apply_to_tensor` initialises the adversarial start with `torch.empty_like(x0).uniform_(-self.epsilon, self.epsilon)` (line 60) using no generator and no seed. The global PyTorch RNG state at the time of the call determines the start. Other iterative gradient attacks in this codebase (PGD, EOT-PGD, Square) all accept a `seed` kwarg or `generator` argument and plumb it through to every stochastic operation, enabling exact reproducibility. The Dispersion Reduction adapter does not accept `seed` and the `apply()` method does not pass `kwargs.get("seed")` to the core. This means DR runs on the same image with identical parameters will produce different adversarial outputs when the global RNG state differs — which breaks experiment reproducibility guarantees documented in CLAUDE.md ("introduce nondeterminism without explicit seed plumbing and documentation").

**Evidence:** `apply_to_tensor` line 60: `torch.empty_like(x0).uniform_(...)` with no generator argument. `DispersionReductionAdapter.apply()` (line 162) ignores `**kwargs` — there is no `seed = kwargs.get("seed")` line.

**Smallest fix:** Accept an optional `seed` parameter in `apply_to_tensor`, create a `torch.Generator` seeded with it (or with the global state if None), and pass it to `uniform_`. In `apply()`, read `seed = kwargs.get("seed")` and forward it. Add `seed` to the returned metadata dict.

---

### P3 — `PGDAttack._random_generator`: unseeded path calls `torch.seed()` which advances the global RNG, causing non-obvious cross-run interference

**File/line:** `src/lab/attacks/pgd_adapter.py` lines 88–91

**Why it matters:** When `seed is None`, `_random_generator` calls `torch.seed()` (line 90) to generate a fresh seed for the local generator. `torch.seed()` is a global call that (a) uses entropy to seed the global PyTorch RNG and (b) returns the resulting seed. Calling it as a seed source for a local generator is an unusual pattern: it advances global state, which can affect any subsequent call that relies on the global RNG (e.g. PyTorch dropout, data loaders, other plugins). The more typical pattern for "seeded locally, random globally" is `torch.randint(0, 2**31, (1,)).item()` (which draws from the global RNG without re-seeding it). The behaviour is not wrong for a single-process run, but it is surprising and can cause hard-to-debug non-reproducibility in multi-plugin sweeps.

**Evidence:** Line 90: `generator.manual_seed(torch.seed() if seed is None else int(seed))`. `torch.seed()` is documented to "sets and returns a new seed for the global generator". This is different from reading from the global RNG.

**Smallest fix:** Replace `torch.seed()` with `int(torch.randint(0, 2**31, (1,)).item())` to draw a random seed from the global RNG without re-seeding it.

---

### P3 — `CWAttackAdapter`: `confidence` field is stored and passed to `CWAttack.__init__` but never used in the optimisation loop

**File/line:** `src/lab/attacks/cw_adapter.py` lines 200–203, 37–53

**Why it matters:** The C&W adapter exposes a `confidence` parameter (line 200, default `0.0`) which matches the standard C&W formulation (a margin added to the attack loss to enforce a detection-confidence gap). `CWAttack.__init__` stores it (`self.confidence = float(confidence)`, line 49). However, nowhere in `_apply_to_tensor` is `self.confidence` used. The inner optimisation at line 134 calls `self._compute_loss(outputs, image=x_adv)` which inherits the untargeted confidence suppression from `FGSMAttack._compute_loss`, with no confidence margin term. The field is dead code. A user setting `confidence > 0` expecting stronger suppression pressure gets the same result as `confidence = 0`. This is a provenance / metadata correctness issue: the `confidence` parameter is not returned in the metadata dict (line 172 does not include it), so callers cannot even detect that it was ignored.

**Evidence:** `CWAttack.__init__` line 49: `self.confidence = float(confidence)`. `_apply_to_tensor` lines 117–163: no reference to `self.confidence`. The metadata dict at line 172 does not include `confidence`.

**Smallest fix (documentation):** Add a comment in `__init__` and `_apply_to_tensor` stating that `confidence` is currently unused. Remove it from the adapter's public interface or mark it as reserved. If implementing it: the standard C&W confidence margin adds `max(0, f(x) - κ)` to the attack loss where κ=confidence.

---

### P3 — `SquareAttack._score` uses hardcoded threshold `> 0.1`; inconsistent with the rest of the codebase and not configurable

**File/line:** `src/lab/attacks/square_adapter.py` lines 53–57; also `cw_adapter.py` lines 62–66

**Why it matters:** `_score` filters detection confidences with `conf > 0.1` (line 56). `CWAttack._count_detections` uses the same `conf > 0.1` threshold (line 65). These thresholds control which detections are considered "alive" for the purpose of the attack's scoring function. The YOLO framework's default confidence threshold is typically `0.25` (and can be configured in run configs). Using `0.1` means the attack continues trying to suppress low-confidence detections that the model would not report in its normal output, potentially wasting queries/iterations on sub-threshold blips. More importantly, if the threshold is raised to match production settings, the score function would terminate early (fewer effective detections to suppress), changing attack effectiveness. The hardcoded value is undocumented and not exposed as a parameter. It is also inconsistent between the `_untargeted_loss` path in `FGSMAttack` (which has no threshold — it uses raw mean confidence) and these two scoring helpers.

**Evidence:** `square_adapter.py` line 56: `conf[conf > 0.1]`. `cw_adapter.py` line 65: `conf > 0.1`. No parameter exposes this threshold. `FGSMAttack._untargeted_loss` uses `.mean()` with no threshold (line 109).

**Smallest fix:** Promote `0.1` to a named module-level constant or a constructor parameter with a default of `0.1` so it can be documented and adjusted. Add a comment explaining the choice (below YOLO's production threshold to ensure all active predictions are captured).

---

### Open questions / missing tests

1. **No tests exercise `_extract_class_logits` with tensors where both `shape[1] > 6` and `shape[-1] > 6` are simultaneously true.** The P2 ambiguity above is untestable from the current test suite.

2. **No tests verify that PGD, EOT-PGD, DeepFool produce identical outputs given the same seed across two separate calls.** The `seed` plumbing exists for PGD/EOT-PGD but is not regression-tested for exact reproducibility.

3. **Dispersion Reduction is not smoke-tested anywhere.** The DR adapter's fallback to `[2, 4, 6]` when no C2f blocks are found is exercised only at runtime. A test that passes a minimal model with non-C2f blocks would confirm this path doesn't silently corrupt outputs.

4. **`DeepFoolAttack._detection_confidence` early-termination condition (`f_scalar < 1e-6`, line 142) uses a fixed threshold.** There is no test for the case where confidence is genuinely near-zero at step 0 vs at a later step. Early termination at step 0 would return the unperturbed image; there is no metadata flag for this case.

5. **`CWAttack` effectiveness note in the docstring (line 188–193) states "0% detection suppression" across all parameter settings.** This known failure is not reflected in a warning emitted when the attack is used, and there is no test asserting that it produces at least some perturbation (it does — `best_success` can be `False` but the image is still perturbed). The metadata `success` field conveys this, but callers that ignore metadata will silently accept a no-op attack result.

6. **`BlurAttackAdapter` and `JPEGAttackAdapter` do not validate that the output image has the same shape and dtype as the input.** `cv2.GaussianBlur` and `cv2.imdecode` can return `None` on failure (e.g. empty buffer from `imencode`). Neither adapter checks for `None` before returning, which would propagate a `None` image downstream with no error.

---

domain complete

## Unreviewed files
All domain files reviewed.

---

## Domain 6 — Defense Plugins & Models (audited 2026-04-08)

### Findings

---

**P1 — `run_wrapper_multipass_on_bgr_image` runs an extra undocumented final pass**

- File: `src/lab/defenses/dpc_unet_wrapper.py`, lines 245–260
- The loop on line 245 iterates over every element of `timestep_schedule`, including the last. After the loop completes, line 260 runs the model again at `timestep_schedule[-1]`. For any N-element schedule the model is called N+1 times, with the final timestep applied twice.
- For the default `EnsembleCDogDefenseAdapter` schedule of `"50"` (1 element), the model runs at t=50 twice. For `"75,50,25"`, it runs at 75, 50, 25, 25.
- The stat `"passes": len(timestep_schedule)` (line 268) reports N, hiding the actual N+1 call count. Downstream metadata is incorrect.
- Why it matters: the extra pass is an undocumented behavior change that alters defense output. It silently doubles cost on single-element schedules and diverges from the documented "progressively cleaning coarse to fine" description. Provenance is wrong.
- Evidence: loop body updates `current` from model output; line 260 calls `model(current, timestep=float(timestep_schedule[-1]))` outside the loop.
- Fix: capture the last loop `output` as `last_output` and remove line 260. Use `last_output` for stats and `model_tensor_to_image_bgr`. `"passes"` will then correctly equal `len(timestep_schedule)`.

---

**P1 — Intermediate NaN in multipass silently corrupts output rather than raising**

- File: `src/lab/defenses/dpc_unet_wrapper.py`, lines 245–261
- Within the loop, intermediate model outputs are not checked for finiteness. A NaN in an intermediate pass is silently clipped to 0.0 by `np.clip(arr, 0.0, 1.0)` at line 255, producing a mostly-black intermediate image. This black image is fed into the next pass and the final output — which contains only 0.0 values — passes the `isfinite` check on line 261 (0.0 is finite).
- Result: a corrupted black image passes the finiteness guard and is used for inference. The adapter's `RuntimeError("DPC-UNet defense produced non-finite output.")` is never triggered. The run completes silently with incorrect detection results.
- Why it matters: this is a silent correctness failure on a high-risk defense. The output is wrong but no error is raised and no warning is logged.
- Evidence: `np.clip(arr, 0.0, 1.0)` at line 255 converts NaN to 0.0; `torch.isfinite(final_output).all()` at line 261 returns True for an all-zeros tensor.
- Fix: add an immediate per-pass finiteness check after line 246: `if not torch.isfinite(output).all(): raise RuntimeError(f"DPC-UNet multipass produced non-finite output at timestep {t}.")`

---

**P2 — `CDogDefenseAdapter` emits misleading `timestep` in metadata when multipass is active**

- File: `src/lab/defenses/preprocess_dpc_unet_adapter.py`, lines 189–199
- When `timestep_schedule` is set and the multipass path is taken, the returned metadata still includes `timestep=float(self.timestep)` (line 192) — the single-pass default, not the actual schedule used.
- `timestep_schedule` is also emitted (line 193), so both keys coexist. An analyst reading `metadata["timestep"]=25.0` on a multipass run will reach incorrect conclusions about which timestep governed the output.
- Why it matters: provenance is the canonical record for auditing defense decisions. A conflicting `timestep` field is a provenance gap.
- Evidence: line 172–180 shows the branch choice; line 192 emits `self.timestep` unconditionally.
- Fix: emit `timestep=float(self.timestep) if not schedule else None` so the field is unambiguous.

---

**P2 — `YOLOModelAdapter.validate` silently maps missing box attributes to `0.0`**

- File: `src/lab/models/yolo_adapter.py`, lines 51–54
- `getattr(box, "map50", 0.0)` returns `0.0` when the attribute is absent. A genuine mAP50 of 0.0 (complete model failure) and a missing attribute (unexpected schema or evaluation error) are indistinguishable in the returned dict.
- Why it matters: the CLAUDE.md evidence integrity rule requires missing evidence to be reported as `None`/unknown, not filled with `0.0`. A `0.0` mAP50 propagated into downstream comparisons can appear to be a valid catastrophic result or trigger false alarms.
- Evidence: lines 51–54 use `getattr(..., 0.0)` not `getattr(..., None)`.
- Fix: replace the three `getattr(box, ..., 0.0)` defaults with `None` and guard the `float()` cast: `float(v) if v is not None else None`.

---

**P3 — `strict_load_with_report` is dead code**

- File: `src/lab/defenses/dpc_unet_wrapper.py`, lines 129–145
- Defined but never called. The actual load path (`_BaseCDogAdapter._ensure_loaded`, line 84 of `preprocess_dpc_unet_adapter.py`) calls `model.load_state_dict` directly. The fallback-to-relaxed behavior and `StrictLoadReport` type are unreachable.
- Fix: delete or wire into `_ensure_loaded` with logging.
- Status: fixed in current repo state. `_BaseCDogAdapter._ensure_loaded` now routes checkpoint loading through `strict_load_with_report` and raises a detailed incompatibility error when strict loading fails.

---

**P3 — `checkpoint_provenance` SHA256 reflects the on-disk file at call time, not at load time**

- File: `src/lab/defenses/preprocess_dpc_unet_adapter.py`, lines 96–106
- `_sha256_file` is called on every `checkpoint_provenance` invocation. If the checkpoint file is replaced after `_ensure_loaded` completes (e.g. training overwrites the path mid-sweep), `run_summary.json` records the SHA256 of the new file, not what was loaded into memory.
- Fix: compute and store the SHA256 inside `_ensure_loaded` and return the cached value from `checkpoint_provenance`.

---

**P3 — Routing policy silently falls through to `median_only` for unknown attack hints**

- File: `src/lab/defenses/routing/policy.py`, lines 15–32
- When routing is enabled and `attack_hint` is not in the known hint sets, the function falls through to signal-only logic. `"square"` and `"cw"` — both used by this repo's attack plugins — are not in the dispatch table and silently route as if the hint were absent.
- Routing is disabled by default, limiting blast radius.
- Fix: add `"square"`, `"cw"`, and other repo attack names to the hint dispatch, or raise on unrecognized non-empty hints when routing is enabled.

---

### Open questions / missing tests

1. No test for `run_wrapper_multipass_on_bgr_image` — the double-last-pass bug (P1) is not caught by any existing test. A smoke test with a 2-element schedule that asserts `stats["passes"] == 2` and output shape is unchanged would catch it.
2. No test for intermediate NaN propagation — the silent corruption path (P1) is untested. A test injecting NaN on an intermediate pass should assert `RuntimeError`, not silent success.
3. No test for `CDogDefenseAdapter` multipass metadata — the P2 provenance gap is untested.
4. `FasterRCNNAdapter.validate` always returns a stub (`mAP50: None, _status: not_supported`). If used in a sweep, Phase 4 validation rows will have `mAP50=None` with no error and may trigger `NO_VALIDATION` false positives in `generate_auto_summary.py`. Not tested.
5. `model_label_from_path` has no case for `"yolo26"` stems despite `DEFAULT_YOLO_MODEL = "yolo26n.pt"`. Label falls back to the raw stem, potentially breaking `<model>__<attack>__<defense>` matrix key consistency across runs.

---

domain complete

## Unreviewed files

All domain files reviewed.

---

## Domain 7 — Infrastructure, Contracts & Tests (audited 2026-04-08)

### P2 — `resolve_latest_dir` sorts by name, not mtime; lexicographic tie-breaking is fragile for non-ISO directory names

**File/line:** `src/lab/health_checks/execution.py:121`

**Why it matters:** `resolve_latest_dir` is exported in `__all__` and is the basis for `resolve_latest_framework_run`. It selects the "latest" directory with `sorted(..., key=lambda p: p.name)[-1]`. This works correctly for ISO-8601 timestamp names (e.g. `sweep_20260326T094116Z`, `cycle_20260330_115004`) because lexicographic order matches chronological order. However any directory name that does not strictly sort in creation order — a renamed run, a test directory, or an alphanumeric name like `sweep_training_round2` — will silently return the wrong directory. The failure is silent: callers receive a valid `Path` and produce outputs attributed to the wrong run.

**Evidence:** `execution.py:121` — `candidates = sorted(..., key=lambda p: p.name)[-1]`. No mtime fallback, no assertion that the returned name is timestamp-shaped.

**Smallest viable fix:** Document the naming contract in the function docstring, and add an optional `warn_if_non_timestamp=True` flag that emits a warning when the returned name does not match an ISO-timestamp pattern. Alternatively, change `key` to `lambda p: (p.stat().st_mtime, p.name)` for deterministic mtime-then-name ordering. Note: this is a health-check helper; runtime impact is confined to callers of `resolve_latest_framework_run`.

---

### P2 — `_runtime_profiles_payload` is `@lru_cache(maxsize=1)` at module level; tests that create or modify `configs/runtime_profiles.yaml` will see stale cached data

**File/line:** `src/lab/health_checks/regression.py:39-47`

**Why it matters:** `_runtime_profiles_payload` is decorated with `@lru_cache(maxsize=1)`. The cache is process-scoped and is never invalidated. Any test that calls `resolve_runtime_profile` (which includes `validate_profile_expectations`, `choose_attack_name`, and any caller downstream) after another test has already loaded the profiles file will use the cached payload from the first call. If the profiles file changes between tests — or if tests run in an order where a different profile set is expected — the function silently returns stale data. No test currently flushes the cache between test cases.

**Evidence:** `regression.py:39` — `@lru_cache(maxsize=1)` on `_runtime_profiles_payload`. `preflight.py:81` calls `resolve_runtime_profile` from `validate_profile_expectations`. No test calls `_runtime_profiles_payload.cache_clear()`.

**Smallest viable fix:** Add `_runtime_profiles_payload.cache_clear()` in test teardown wherever `validate_profile_expectations` or `resolve_runtime_profile` is called with a modified profiles file. In production this is not an issue because the YAML is read once per process; the risk is test isolation only.

---

### P2 — `PluginRegistry.register` silently overwrites an existing alias; duplicate registration goes undetected

**File/line:** `src/lab/core/plugin_registry.py:31-37`

**Why it matters:** When two `_adapter.py` modules register themselves under the same alias (e.g. both call `@register_attack_plugin("fgsm")`), the second decorator silently replaces the first in `_store`. The module-level `_loaded` flag prevents re-discovery, so whichever adapter happened to be loaded last wins. This is a silent corruption risk: the wrong plugin class runs with no error, warning, or log message.

**Evidence:** `plugin_registry.py:34-35` — `self._store[key] = cls` with no collision check. `adapter_loader.py:39-42` — modules are loaded in `iter_modules` order with no deduplication guard.

**Smallest viable fix:**
```python
if key in self._store:
    raise ValueError(
        f"{self._label} plugin alias '{key}' already registered "
        f"by {self._store[key].__name__}; cannot re-register with {cls.__name__}."
    )
self._store[key] = cls
```

---

### P3 — `validate_legacy_csv_file` only checks schema_version on rows it iterates; a zero-row CSV passes silently

**File/line:** `src/lab/health_checks/schema.py:77-81`

**Why it matters:** `validate_legacy_csv_file` reads `required_columns` from the schema, checks headers, then iterates rows to validate `schema_version_column`. A zero-data CSV (headers present, no data rows) passes all checks without any content validation. This is a false-positive gate: a newly created empty CSV is treated as valid by `validate_output_bundle` and `scripts/ci/validate_outputs.py`.

**Evidence:** `schema.py:77` — `for idx, row in enumerate(reader, start=2):` — if no rows exist, the loop body never executes. No `assert len(rows) > 0` guard exists.

**Smallest viable fix:** After reading fieldnames, assert at least one row was produced before returning success, or add a `require_nonempty: bool = True` parameter. The schema validation fixture tests in `test_schema_contracts.py` do not include a zero-row CSV case, so this gap is currently undetected by tests.

---

### P3 — Several exported `regression.py` functions are dead code: no caller outside `health_checks/` or `tests/`

**File/line:** `src/lab/health_checks/regression.py` and `__init__.py`

**Why it matters:** `run_metrics_integrity_checks`, `run_fgsm_sanity_checks`, `assert_no_fingerprint_collision`, `assert_attack_sweeps_not_flat`, `assert_attack_sweep_nonflat_strict`, `append_rolling_baseline_history`, `load_rolling_baseline`, `resolve_latest_dir`, and `resolve_latest_framework_run` are all exported in `__all__` but are called from no script outside the module or its tests. These functions are load-bearing in the API surface (they are tested), but the actual orchestration and CI scripts (`auto_cycle.py`, `sweep_and_report.py`, `scripts/ci/validate_outputs.py`) do not invoke them. This is a coverage gap: the health checks exist but are not wired into the pipeline paths they were built to guard.

**Evidence:** Grepping all `.py` files under `scripts/` and `src/` for `run_metrics_integrity_checks`, `run_fgsm_sanity_checks`, `append_rolling_baseline_history`, and `load_rolling_baseline` returns zero matches outside `health_checks/` itself.

**No fix required for correctness.** Residual risk: if these functions are not called by the pipeline, the regression and rolling-baseline guards they implement provide no protection. Either wire them into the pipeline or document their expected call sites so the gap is intentional.

---

### P3 — `check_tracked_outputs.py` policy does not cover `outputs/framework_reports/**` subdirectory content; raw sub-artifacts inside a report dir would be accepted

**File/line:** `scripts/ci/check_tracked_outputs.py:18-30`

**Why it matters:** `DISALLOWED_PATTERNS` blocks `outputs/framework_runs/**`, `outputs/training_data/**`, etc., but explicitly does not restrict content inside `outputs/framework_reports/<sweep_id>/`. The test in `test_tracked_output_policy.py` confirms `outputs/framework_reports/sweep_001/summary_blur.txt` is allowed. There is no upper bound on what a framework_reports subdirectory may contain, meaning large binary artifacts or raw run outputs placed inside a reports subdirectory would pass the policy check.

**Evidence:** `check_tracked_outputs.py:18-30` — no `outputs/framework_reports/**/*.pt`, `*.csv.gz`, etc. exclusion. `test_tracked_output_policy.py:17-18` — the test affirms that `.txt` files inside framework_reports are allowed.

**Smallest viable fix:** Not necessarily a blocker, but add a comment to the policy file documenting what is allowed inside `framework_reports/` subdirectories, and optionally add patterns to block binary artifacts (`.pt`, `.onnx`, `.zip`, `.gz`).

---

### Open questions and missing tests

1. `validate_system_health_summary_payload` is exported in `__init__.py` and the schema file exists (`schemas/v1/system_health_summary.schema.json`), but no test calls this function and no script appears to call it either. Unknown whether it is invoked at runtime. Coverage gap.

2. No test covers `resolve_latest_dir` behavior for non-timestamp-shaped directory names. The `test_export_training_data.py` test for `_resolve_runs_root` does exercise mtime-based selection, but that is in `export_training_data.py` (which uses its own `os.stat` logic), not `resolve_latest_dir`.

3. `validate_framework_json_file` only checks top-level key presence and `schema_version`; it does not validate nested required keys or types. No test checks partial inner payloads. Validation depth is shallow.

4. `_runtime_profiles_payload` returns `{}` silently if `configs/runtime_profiles.yaml` is missing (`regression.py:43-44`). `resolve_runtime_profile` then falls back to hardcoded defaults. This silent fallback is not surfaced to callers. Missing-profiles-file condition has no test.

5. No test exercises `AdapterLoader._load` when zero `*_adapter.py` modules exist (the `RuntimeError` path at line 44-47 of `adapter_loader.py`).

---

domain complete

## Unreviewed files

All domain files reviewed.

---

## Cross-cutting summary (pending)

_To be written after all 7 domains complete. Will capture patterns that span
multiple domains and any systemic risks not visible within a single domain._
