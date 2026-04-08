# Full-Repo Audit — Domain Partitions

Domains are ordered by blast radius (highest risk first). Audit in order 1→7.

---

## Domain 1 — Core Orchestration

**Rationale:** Bugs here affect every run. Two P0s were fixed in PRs #68/#69;
verify fixes landed and check for anything missed.

**Files:**
- `scripts/auto_cycle.py`
- `scripts/sweep_and_report.py`
- `scripts/run_unified.py`
- `src/lab/runners/run_experiment.py`
- `src/lab/runners/run_intent.py`
- `src/lab/runners/cli_utils.py`

---

## Domain 2 — Signal-Driven Training & Gate Logic

**Rationale:** Deployment-critical. Gate threshold P0 just fixed in PR #69;
verify solid and audit adjacent training scripts for similar issues.

**Files:**
- `scripts/train_from_signal.py`
- `scripts/evaluate_checkpoint.py`
- `scripts/export_training_data.py`
- `scripts/train_dpc_unet_local.py`
- `scripts/train_dpc_unet_feature_loss.py`

---

## Domain 3 — Evaluation & Metrics

**Rationale:** Scientific correctness. If metrics are wrong, all downstream
conclusions (comparability, attack ranking, defense recovery) are invalid.

**Files:**
- `src/lab/eval/` (use Glob to resolve all .py files)
- `src/lab/config/contracts.py`
- `schemas/v1/` (use Glob to resolve all .json files)

---

## Domain 4 — Reporting & Summaries

**Rationale:** Comparability and authority selection. One P2 (silent provenance
gap) already found; look for more silent mis-reporting.

**Files:**
- `src/lab/reporting/` (use Glob to resolve all .py files)
- `scripts/generate_auto_summary.py`
- `scripts/generate_framework_report.py`
- `scripts/generate_team_summary.py`
- `scripts/generate_cycle_report.py`
- `scripts/generate_dashboard.py`
- `scripts/generate_failure_gallery.py`
- `scripts/generate_slide_tables.py`
- `scripts/print_summary.py`
- `scripts/analyze_per_class.py`

---

## Domain 5 — Attack Plugins

**Rationale:** Registration, objective correctness, determinism, output
shape/dtype. Largest single area (19 files).

**Files:**
- `src/lab/attacks/` (use Glob to resolve all .py files)

---

## Domain 6 — Defense Plugins & Models

**Rationale:** Checkpoint provenance, routing policy, training losses,
clean-image degradation risk.

**Files:**
- `src/lab/defenses/` (use Glob to resolve all .py files, including routing/ and training/)
- `src/lab/models/` (use Glob to resolve all .py files)

---

## Domain 7 — Infrastructure, Contracts & Tests

**Rationale:** Lowest blast radius for runtime behavior. Check schema alignment,
plugin registry correctness, health check coverage, CI validity, and test
coverage gaps across all high-risk surfaces.

**Files:**
- `src/lab/core/` (use Glob to resolve all .py files)
- `src/lab/health_checks/` (use Glob to resolve all .py files)
- `scripts/ci/` (use Glob to resolve all .py files)
- `tests/` (use Glob to resolve all test_*.py files — audit for coverage gaps, not just correctness)
