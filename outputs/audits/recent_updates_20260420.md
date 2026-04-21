# Audit: Recent Updates (PRs #80–#91 + interim commits)

Date: 2026-04-20
Branch: eloquent-snyder-b19618 (worktree)
Standards: [CODE_QUALITY_STANDARD.md](../../CODE_QUALITY_STANDARD.md) + [CLAUDE.md](../../CLAUDE.md)
Scope: broad triage; rank-ordered findings + per-PR rubric. No code changes.

---

## Executive summary

Counts: **0 P0** · **2 P1** · **6 P2** · **3 P3**

The recent work is in good shape mechanically — all configured gates pass on
this branch (ruff clean, mypy clean on the configured surface, 445+51 tests
green). The findings below are about scope of those gates, hidden behavior
changes, and verification debt that the new contract notionally requires but
isn't being enforced everywhere it claims to be.

Per-area headline (rubric scored 0–2 across 6 axes, max 12):

| Area | Score | Verdict |
|---|---|---|
| Plugin extraction (PR #91) | **12/12** | Clean. sys.modules shims + 54 passing tests. |
| Wrapper/shim layer (PR #91) | **8/12** | Works, but compat tests cover only ~60% of the wrappers they claim to enforce. |
| Reporting split (PR #91) | **8/12** | Behavior-preserving overall; non-determinism + new `team_summary` semantic logic under-tested. |
| Profile system (e28057f) | **10/12** | Schema + provenance fields wired correctly. |
| Phase 4 hardening (PRs #82/#83/#84) | **10/12** | Process-group kill is careful; deepfool cap is comparability-relevant but recorded in run config. |
| New attack `pretrained_patch` (PR #90) | **9/12** | Strong artifact provenance (sha256, resize validation), one P1 silent-fallback. |
| DPC-UNet feature loss (PR #89/#88) | **10/12** | Feature loss isolated behind `--feature-weight 0` default; deterministic given seed. |
| Quality contract itself (CODE_QUALITY_STANDARD.md, AGENTS.md) | **9/12** | Sound but mypy/audit scope is narrow vs what the doc implies. |

Recommendation: address P1s before the next merge, treat P2s as a one-week
follow-up sprint, leave P3s as-is unless someone is in the file anyway.

---

## Mechanical findings (Pass A — `scripts/ci/run_repo_standards_audit.py --lane full`)

```
$ ruff check src tests scripts                 → All checks passed!
$ mypy                                         → Success: no issues found in 24 source files
$ pytest -q                                    → 445 passed, 1 deselected
$ pytest -q tests/test_*_compat.py             → 51 passed
```

Gate is green. Two notes that aren't failures but are scope concerns:

- **mypy covers only `src/lab/{eval,reporting,runners}`** (24 files; see
  `pyproject.toml`). `scripts/`, `src/lab/{attacks,defenses,models,plugins,
  config,core,training}` get no static checking. The new
  CODE_QUALITY_STANDARD.md says "lint, type, and test gates" without
  qualification — the actual coverage is much narrower than that reads.
- **`scripts/ci/run_repo_standards_audit.py --lane compat`** runs only 51
  tests across 6 compat files. The `--lane full` adds the fast quality gate.
  Neither lane runs the full pytest suite, so the audit name overpromises.

---

## Findings (P1 → P3)

### P1-1 — `pretrained_patch` silently falls back to center placement on YOLO predict failure

- **File:** [src/lab/plugins/extra/attacks/pretrained_patch_adapter.py:100-110](../../src/lab/plugins/extra/attacks/pretrained_patch_adapter.py)
- **Evidence:**
  ```python
  try:
      results = yolo.predict(source=clean_rgb, save=False, verbose=False,
                             conf=self.clean_detect_conf,
                             iou=self.clean_detect_iou,
                             classes=[self.person_class_id])
  except Exception:
      return []      # ← caller treats empty boxes as "no person found"
  ```
- **Why it matters:** Per CLAUDE.md merge-blockers, "hide failures behind
  broad exception handling or fallback behavior that changes experiment
  meaning" is a blocker. A YOLO predict crash → empty boxes → adapter falls
  back to `placement_mode="center"`, but the run is recorded as a successful
  `pretrained_patch` attack with `largest_person_torso` placement intent.
  Cycle-over-cycle comparisons would silently mix two different attacks.
- **Minimal fix:** narrow the except (e.g. `except (RuntimeError,
  torch.cuda.OutOfMemoryError)`), log the fallback, and either record
  `placement_used="fallback_center_after_predict_error"` in run provenance or
  fail the run.

### P1-2 — Compat test coverage only spot-checks ~25% of the wrapper contract it claims to enforce

- **File:** [tests/test_repo_structure_compat.py](../../tests/test_repo_structure_compat.py)
- **Evidence:** `test_root_wrappers_alias_to_moved_modules` covers 4 of ~17
  wrappers (auto_cycle, run_training_ritual, run_demo,
  generate_auto_summary). `test_old_adapter_shims_alias_to_moved_modules`
  covers 4 of 15+ adapter shims. Untested wrappers include
  `evaluate_checkpoint`, `generate_dashboard`, `generate_failure_gallery`,
  `generate_team_summary`, `print_summary`,
  `train_dpc_unet_{local,feature_loss}`, `cleanup_stale_runs`,
  `watch_cycle`, `train_from_signal`, `export_training_data`,
  `generate_cycle_report`, `generate_framework_report`.
- **Why it matters:** CODE_QUALITY_STANDARD.md §"Wrapper and shim changes"
  explicitly requires "add explicit compatibility tests" — and the new
  `AGENTS.md` repeats it. A test file that proves 4 cases and is named
  `test_root_wrappers_alias_to_moved_modules` (plural) gives the impression
  of contract enforcement that doesn't exist. If someone deletes a `_load_module()`
  call from one of the untested wrappers, no test fails.
- **Minimal fix:** parametrize the test with the full list (one
  `subTest` per wrapper). ~10 lines.

### P2-1 — Dashboard output is non-deterministic (`datetime.now()`)

- **File:** [src/lab/reporting/aggregate/dashboard.py:432](../../src/lab/reporting/aggregate/dashboard.py)
- **Evidence:** `generated_at = datetime.now(timezone.utc).strftime(...)`
  is rendered into the HTML body.
- **Why it matters:** CLAUDE.md "Reporting or summary code" required-checks
  call for "deterministic machine-parseable outputs." The dashboard is
  HTML so determinism is less critical than for `metrics.json`, but
  CI-cacheability and PR-diffability suffer. Pre-existing in the legacy
  `scripts/generate_dashboard.py`, but the move was a chance to fix it.
- **Minimal fix:** derive timestamp from the latest sweep manifest's mtime
  (already deterministic per run), or accept the limitation and document it
  in a module-level comment.

### P2-2 — `team_summary.py` added ~130 lines of new semantic-status logic without dedicated regression tests

- **File:** [src/lab/reporting/team_summary.py:497+](../../src/lab/reporting/team_summary.py)
- **Evidence:** New helpers `_shared_value`, `_context_value`,
  `_is_ranked_row`, `_derive_semantic_status`, `_build_local_context`,
  `_build_external_provenance`. New row fields `_dataset_scope`,
  `_pipeline_profile`, `_authoritative_metric`. New `external_clean_gate_path`
  keyword arg. The Markdown payload now branches on `semantic_status`
  (ranked / mixed / diagnostic).
- **Why it matters:** Largest single semantics shift in the reporting layer;
  no test exercises `_derive_semantic_status` directly, no schema-pin test
  proves the JSON shape didn't drift for old consumers. This is exactly the
  kind of "silent contract weakening" CODE_QUALITY_STANDARD §6 forbids.
- **Minimal fix:** one unit test per branch of `_derive_semantic_status` (3-4
  cases), one snapshot/golden test of the rendered Markdown for a fixed
  input fixture.

### P2-3 — Authority/Phase-4 mAP50 rule not enforced in `dashboard.py` aggregation

- **File:** [src/lab/reporting/aggregate/dashboard.py](../../src/lab/reporting/aggregate/dashboard.py)
- **Evidence:** Dashboard reads framework reports (sweep outputs), not
  `cycle_history/`. CLAUDE.md "mAP50 source rule" requires Phase 4
  `validate_*` rows as authoritative; `auto_summary false-positive
  warning` notes that Phase 1 smoke can shadow Phase 4 rows. The dashboard
  does not filter on `source_phase` / `authority`.
- **Why it matters:** A dashboard built across cycles with mixed Phase
  1/2/4 data could plot a Phase 1 (32-image, confidence-only) point next to
  a Phase 4 mAP50 point with the same series color. There's no visual
  warning.
- **Minimal fix:** filter to rows where `authority == "primary"` (or
  source_phase == "phase4"), and emit a footer note listing any rows that
  were excluded so the elision is visible.

### P2-4 — `auto_cycle.py` warm-start swallows all exceptions silently

- **File:** [scripts/automation/auto_cycle.py:1367-1369](../../scripts/automation/auto_cycle.py)
- **Evidence:**
  ```python
  try:
      warm = json.loads(WARM_START_FILE.read_text(encoding="utf-8"))
  except Exception:
      pass    # warm stays unset; no log; continues without warm-start
  ```
- **Why it matters:** A corrupted warm-start file (truncated write, partial
  JSON) silently disables the optimization; an operator looking at why a
  cycle is slow has no signal. CLAUDE.md "Stateful or resumable code"
  required-checks include "interruption safety" — silent fallback fails
  that.
- **Minimal fix:** narrow to `(OSError, json.JSONDecodeError)` and `log()`
  the failure with the file path and the exception summary.

### P2-5 — `mypy` configured against only 3 directories despite repo-wide quality contract claims

- **File:** [pyproject.toml](../../pyproject.toml) (the `[tool.mypy] files = [...]` block)
- **Evidence:** mypy targets `src/lab/{eval,reporting,runners}` — 24 files
  out of >150 in `src/lab/` alone. `scripts/automation/auto_cycle.py`
  (2.5k lines, high-risk surface), `src/lab/plugins/`, `src/lab/attacks/`,
  `src/lab/defenses/` are not type-checked.
- **Why it matters:** CODE_QUALITY_STANDARD.md non-negotiable #7 says docs
  must be honest. The retroactive-audit commands in §"Retroactive Audit
  Commands" present `--lane full` as the broad audit; in practice it leaves
  85%+ of `src/lab/` unchecked. Either narrow the documentation or expand
  the mypy surface incrementally.
- **Minimal fix:** doc note in CODE_QUALITY_STANDARD.md §"Retroactive Audit
  Commands" explicitly stating the current mypy scope, plus a tracking
  issue for staged expansion (recommend `src/lab/plugins/` and
  `src/lab/runners/` next).

### P2-6 — 7 of 17 PR #91 wrappers have no module-identity test; 6 of 17 have no `--help` smoke test

- **Files:** [tests/test_training_script_compat.py](../../tests/test_training_script_compat.py),
  [tests/test_reporting_and_demo_script_compat.py](../../tests/test_reporting_and_demo_script_compat.py),
  [tests/test_cli_wrapper_entrypoints.py](../../tests/test_cli_wrapper_entrypoints.py)
- **Evidence:** Untested for module-identity: `evaluate_checkpoint`,
  `generate_dashboard`, `generate_failure_gallery`, `generate_team_summary`,
  `print_summary`, `train_dpc_unet_local`, `train_dpc_unet_feature_loss`.
  Untested for `--help`: same set minus `evaluate_checkpoint`.
- **Why it matters:** Same root cause as P1-2 but lower severity because
  this duplicates the issue across other compat test files. Ranked
  separately so it doesn't get lost when fixing P1-2.
- **Minimal fix:** parametrize both test files with the full wrapper
  list. ~20 lines total across the two files.

### P3-1 — Wrapper main-invocation pattern is inconsistent across PR #91 wrappers

- **Files:** [scripts/auto_cycle.py:23](../../scripts/auto_cycle.py),
  [scripts/watch_cycle.py:23](../../scripts/watch_cycle.py),
  vs [scripts/run_demo.py](../../scripts/run_demo.py),
  [scripts/cleanup_stale_runs.py](../../scripts/cleanup_stale_runs.py).
- **Evidence:** Three patterns in active use:
  - direct `_load_module().main()` (auto_cycle, watch_cycle)
  - `raise SystemExit(_load_module().main())` (cleanup_stale_runs)
  - `_run_main()` helper that conditionally raises SystemExit (run_demo)
- **Why it matters:** Functionally correct given current return types (some
  return `None`, some `int`), but if `auto_cycle.main()` ever starts
  returning a non-zero code on partial success, the wrapper would silently
  exit 0. Pure consistency / future-proofing.
- **Minimal fix:** standardize on the `_run_main()` pattern across all
  wrappers (5/7 already use it).

### P3-2 — `framework_comparison` is exposed via implicit module re-export

- **Files:** [src/lab/reporting/__init__.py](../../src/lab/reporting/__init__.py),
  [tests/test_framework_reporting.py:492](../../tests/test_framework_reporting.py).
- **Evidence:** Test does `from lab.reporting import framework_comparison`
  but `framework_comparison` is not in `__all__` and not explicitly
  re-exported — it works only because Python implicitly exposes submodule
  attributes after they have been imported once.
- **Why it matters:** Brittle. A future cleanup that drops the transitive
  import would break tests / external callers without warning.
- **Minimal fix:** either add `framework_comparison` to `__all__` (and a
  one-line re-export), or change the test/callers to
  `from lab.reporting.framework_comparison import ...`.

### P3-3 — `pgd_adapter` legacy shim is missing the docstring the other shims have

- **File:** [src/lab/attacks/pgd_adapter.py](../../src/lab/attacks/pgd_adapter.py)
- **Evidence:** 4 lines, no docstring. Compare to
  `src/lab/defenses/preprocess_dpc_unet_adapter.py` which has the standard
  "Compatibility shim for…" docstring.
- **Why it matters:** Pure consistency / discoverability for someone
  jumping into the file from grep.
- **Minimal fix:** add the standard docstring (5 lines).

---

## Per-PR rubric summary

Scored 0/1/2 on Correctness · Simplicity · Boundary hygiene · Testability ·
Compatibility · Doc honesty (max 12).

| PR | C | S | B | T | Cm | D | Total | Notes |
|---|---|---|---|---|---|---|---|---|
| #91 (modularization) | 2 | 2 | 2 | 1 | 2 | 1 | **10** | Excellent extraction; tests under-cover; PROJECT_STATE.md became enumerative. |
| #91 (wrapper layer subset) | 2 | 1 | 2 | 1 | 2 | 0 | **8** | Three invocation styles, ~40% wrappers untested. |
| #91 (reporting subset) | 1 | 1 | 2 | 1 | 2 | 1 | **8** | Non-determinism + 130 lines of new semantic logic without targeted tests. |
| #91 (plugins subset) | 2 | 2 | 2 | 2 | 2 | 2 | **12** | 54 passing tests, sys.modules shim pattern, alias stability proven. |
| #90 (pretrained_patch) | 1 | 2 | 2 | 1 | 2 | 1 | **9** | Strong artifact provenance; one silent-fallback (P1-1). |
| #89 (feature loss) | 2 | 2 | 2 | 1 | 2 | 1 | **10** | Default `--feature-weight 0` keeps blast radius small. |
| #88 (deepfool+DR preset) | 2 | 2 | 2 | 1 | 2 | 2 | **11** | Preset-style change; comparability narrative is honest. |
| #87 (sweep tests use sys.executable) | 2 | 2 | 2 | 2 | 2 | 2 | **12** | Tiny, correct. |
| #86 (restore re-export) | 2 | 2 | 2 | 2 | 2 | 2 | **12** | Tiny, correct. |
| #85 (ruff cleanup) | 2 | 2 | 2 | 2 | 2 | 2 | **12** | Mechanical; CI unblock. |
| #84 (phase4 second defense) | 2 | 2 | 2 | 2 | 2 | 2 | **12** | Supplementation logic guarded; tested. |
| #83 (deepfool phase4 cap) | 2 | 2 | 2 | 2 | 2 | 2 | **12** | Cap propagated via run config; comparability noted in commit. |
| #82 (kill phase4 process groups) | 2 | 2 | 2 | 2 | 2 | 2 | **12** | OS-aware, grace + escalation, correct PG semantics. |
| #81 (torch 2.6 / py3.13) | 2 | 2 | 2 | 1 | 2 | 2 | **11** | Dependency bump; relies on existing test surface. |
| #80 (YOLOv11 transition) | 2 | 2 | 2 | 1 | 2 | 2 | **11** | Heavy semantic change; evidence in cycle history. |
| e28057f (profile system) | 2 | 1 | 2 | 2 | 2 | 1 | **10** | 259 lines for one profile; schema fields wired through. |
| f3b8833 / efe8d0a (YOLO11 fixes) | 2 | 2 | 2 | 1 | 2 | 2 | **11** | Bug fixes for the feature-yolo discovery; no regression test added. |

---

## Open questions / verification gaps

1. **PR #83 deepfool cap → comparability:** The cap is set to 50 images, but
   the prior cycle (round 3, see CLAUDE.md) used the full eval set for
   deepfool. Are post-PR-#83 deepfool numbers comparable to pre-PR-#83
   cycle 22 (`cycle_20260407_193440`)? Cannot confirm from code alone — needs
   a side-by-side of two `metrics.json` files.
2. **PR #91 reporting move:** `dashboard.py` grew 623 → 684 lines. Pass B
   couldn't isolate which 60 lines are new behavior vs cleanup. Worth a
   `git diff 310c2e8 HEAD -- scripts/generate_dashboard.py
   src/lab/reporting/aggregate/dashboard.py` follow-up.
3. **Profile-driven sweeps:** Did anything break when a profile sets
   `learned_defense.trainable: false` and Phase 4 supplementation (PR #84)
   tries to add c_dog into a profile that excludes it? No test exercises
   that combination.
4. **`pretrained_patch` end-to-end:** No smoke test in the PR runs an
   actual sweep with the new attack to confirm the run_summary / metrics
   path. Tests cover the adapter in isolation only.

## Recommended next actions

- **Fix this week:** P1-1 (silent fallback in `pretrained_patch`) and P1-2
  (parametrize the wrapper compat test). Both <50 lines.
- **One-week follow-up sprint:** P2-1 through P2-4. Group into one PR per
  area (reporting determinism + auth filter; team_summary tests; auto_cycle
  warm-start log).
- **Doc-only PR:** P2-5 mypy scope clarification in CODE_QUALITY_STANDARD.md.
- **Defer:** all P3s unless someone is editing the file anyway.
- **Consider scheduling:** a follow-up granular audit of `auto_cycle.py`
  alone — it's 2.5k lines on the highest-risk surface and this triage only
  spot-checked it. The `.claude/skills/big-brother-auditor/` skill is the
  right tool.

## What this audit did NOT do

- No code changes (per request).
- No issues / PRs filed.
- No dynamic analysis (no `auto_cycle` end-to-end run, no live sweep, no
  GPU work).
- No re-verification of cycle history claims (CLAUDE.md memory facts about
  `dpc_unet_adversarial_finetuned.pt` were accepted as-is).
- No audit of pre-#80 history.
