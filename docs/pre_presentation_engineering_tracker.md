# Pre-Presentation Engineering Tracker

This tracker is the implementation handoff for the final hardening pass before presentation building. It is intentionally narrow. Do the smallest safe change that satisfies the acceptance commands. Do not widen scope into cleanup or redesign.

## Priority Order

- [x] `A0` Codex: fix `run_training_ritual.py` export wrapper bug and lock it with regression coverage.
- [ ] `B1` External: reconcile dependency contract.
- [ ] `B2` External: make `c_dog` readiness consistent between environment check and demo preflight.
- [ ] `B3` External: fix dashboard mypy blocker without changing output.
- [ ] `B4` External: validate imported patch workflow end to end.
- [ ] `B5` External: validate offline training story as a real workflow.

## A0 — Done by Codex

**Goal**

Fix the export handoff in `scripts/training/run_training_ritual.py` so it passes the correct CLI shape to `export_training_data.py`.

**Files changed**

- `scripts/training/run_training_ritual.py`
- `tests/test_training_ritual.py`

**Acceptance commands**

```bash
./.venv/bin/python -m pytest -q tests/test_training_ritual.py tests/test_training_script_compat.py
PYTHONPATH=src ./.venv/bin/python scripts/training/run_training_ritual.py --dry-run --max-age-hours 1000
```

**Expected result**

- the export command now includes both `--from-signal` and `--signal-path`
- targeted tests pass

**Status**

- complete

## B1 — External Engineer

**Goal**

Make `requirements.txt`, `scripts/check_environment.py`, and `tests/test_check_environment.py` agree on one supported dependency stack.

**Source of truth**

- `ultralytics==8.4.23`
- `torch==2.5.1`
- `torchvision==0.20.1`

**Files to touch**

- `requirements.txt`
- `scripts/check_environment.py`
- `tests/test_check_environment.py`

**Do not do**

- no package upgrades
- no version-range loosening
- no unrelated environment-check refactor

**Acceptance commands**

```bash
PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py
./.venv/bin/python -m pytest -q tests/test_check_environment.py
```

**Done when**

- a fresh environment built from `requirements.txt` passes the checker
- the test expectations match the same versions
- no user-facing file still advertises a second official version set

**Status**

- pending external

## B2 — External Engineer

**Goal**

Use one DPC-UNet checkpoint readiness rule in both the environment checker and demo preflight.

**Required behavior**

- accept explicit checkpoint path when provided
- accept `DPC_UNET_CHECKPOINT_PATH`
- accept existing common default local checkpoint filenames
- align `run_demo.py` to the broader existing checker behavior

**Files to touch**

- `scripts/demo/run_demo.py`
- optionally factor shared resolution logic from `scripts/check_environment.py` into a helper if that is the smallest clean change

**Do not do**

- no new CLI surface unless blocked
- no behavior change outside checkpoint readiness

**Acceptance commands**

```bash
PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py --require-cdog
PYTHONPATH=src ./.venv/bin/python scripts/demo/run_demo.py --defenses c_dog --dry-run
```

**Done when**

- both commands pass or fail together on the same machine state
- a default local checkpoint file works even without the env var

**Status**

- pending external

## B3 — External Engineer

**Goal**

Fix the mypy failure in the dashboard formatting helpers without changing generated HTML.

**Files to touch**

- `src/lab/reporting/aggregate/dashboard.py`

**Do not do**

- no report redesign
- no unrelated typing cleanup
- no HTML/content changes unless absolutely required to satisfy typing

**Acceptance commands**

```bash
PYTHONPATH=src ./.venv/bin/python scripts/ci/run_repo_quality_gate.py --lane fast
```

**Stretch acceptance after B1**

```bash
PYTHONPATH=src ./.venv/bin/python scripts/ci/run_repo_quality_gate.py --lane ci
```

**Done when**

- fast lane passes
- CI lane is expected to pass once the dependency contract is reconciled

**Status**

- pending external

## B4 — External Engineer

**Goal**

Make the imported patch workflow presentation-ready using the existing patch profile and matrix config.

**Required setup**

- set `ADV_PATCH_ARTIFACT_PATH` to one canonical patch artifact
- set `DPC_UNET_CHECKPOINT_PATH` if `c_dog` is in the defense list

**Commands**

```bash
export ADV_PATCH_ARTIFACT_PATH=/absolute/path/to/canonical_patch_artifact
export DPC_UNET_CHECKPOINT_PATH=/absolute/path/to/dpc_unet_checkpoint.pt
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py patch-matrix --matrix-config configs/patch_artifacts.yaml
PYTHONPATH=src ./.venv/bin/python scripts/reporting/generate_framework_report.py --runs-root outputs/patch_matrix --output-dir outputs/framework_reports/patch_matrix
PYTHONPATH=src ./.venv/bin/python scripts/reporting/generate_dashboard.py --report-dir outputs/framework_reports/patch_matrix --output outputs/framework_reports/patch_matrix/dashboard.html --no-pages
```

**Do not do**

- do not redesign patch placement logic
- do not change the profile unless a blocker makes the workflow impossible
- fix execution blockers only

**Done when**

- both placement modes run
- listed defenses run
- report assets exist for presentation

**Status**

- pending external

## B5 — External Engineer

**Goal**

Validate the learned-defense training story as a real manual workflow without `--profile`.

**Required command chain**

```bash
PYTHONPATH=src ./.venv/bin/python scripts/training/export_training_data.py --from-signal --signal-path outputs/cycle_training_signal.json
PYTHONPATH=src ./.venv/bin/python scripts/training/train_from_signal.py --signal-path outputs/cycle_training_signal.json
PYTHONPATH=src ./.venv/bin/python scripts/training/run_training_ritual.py --max-age-hours 1000
```

**Required output files**

- `outputs/training_runs/<cycle_id>/training_manifest.json`
- `outputs/training_runs/<cycle_id>/clean_gate_result.json`
- `outputs/training_runs/<cycle_id>/attack_gate_result.json`

**Do not do**

- do not change profile trainability
- do not present the training path as canonical profile behavior

**Done when**

- one real manifest exists
- both gate result JSON files exist
- the presenter can explain that profiled training remains intentionally blocked by current policy

**Status**

- pending external

## Global Exit Gate

Do not switch fully into presentation building until all of the following are true:

- [ ] `A0` through `B5` are complete
- [ ] one frozen artifact pack exists for each story: core demo, auto-cycle, training, patch
- [ ] no demo-day step depends on “latest run” discovery
- [ ] the presenter has a written Known Limitations slide
