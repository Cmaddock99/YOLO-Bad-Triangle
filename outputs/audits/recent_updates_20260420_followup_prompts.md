# Follow-up Prompts: 2026-04-20 Audit

One self-contained prompt per actionable finding from
[recent_updates_20260420.md](recent_updates_20260420.md). Each prompt is
written to be pasted into a fresh session (no prior context required).
Standards: CODE_QUALITY_STANDARD.md + CLAUDE.md.

Suggested workflow: each prompt → its own worktree → its own PR.
Definition of done is at the bottom of each prompt.

---

## P1-1 — Fix silent fallback in `pretrained_patch` adapter

```text
Fix a P1 silent-fallback bug in the pretrained_patch attack adapter.

File: src/lab/plugins/extra/attacks/pretrained_patch_adapter.py:100-110

The current code:

    try:
        results = yolo.predict(
            source=clean_rgb, save=False, verbose=False,
            conf=self.clean_detect_conf, iou=self.clean_detect_iou,
            classes=[self.person_class_id],
        )
    except Exception:
        return []

returns an empty list on ANY exception. Callers treat empty boxes as "no
person found" and fall back to `placement_mode="center"`. The run is then
recorded as a successful pretrained_patch attack with the original
`largest_person_torso` intent — operators have no signal that the
placement actually used was different.

Per CLAUDE.md merge-blockers: "hide failures behind broad exception
handling or fallback behavior that changes experiment meaning" is a
blocker.

Required fix (smallest viable):
1. Narrow the except to (RuntimeError, ValueError, torch.cuda.OutOfMemoryError)
   — anything that legitimately can come out of ultralytics .predict().
   KeyboardInterrupt and SystemExit must propagate.
2. Log the exception with the run name and the exception type/message via
   the project's logger (or print to stderr if the adapter has no logger
   plumbed; check the rest of the file for the existing pattern).
3. When the fallback path triggers, record the actual placement used in
   the per-image attack metadata so cross-run comparisons can detect it.
   Look at how other attack adapters write per-image metadata (grep for
   `placement_mode` or for what gets surfaced in metrics.json /
   predictions.jsonl) — re-use the existing channel rather than inventing
   a new one.

Verification:
- Add a unit test that mocks `yolo.predict` to raise RuntimeError and
  asserts (a) the adapter does not crash, (b) the fallback placement is
  recorded somewhere observable (metadata field, log line, etc).
- Add a second test that asserts a non-suppressible exception
  (KeyboardInterrupt) does propagate.
- Run: PYTHONPATH=src ./.venv/bin/python -m pytest -q
  tests/test_framework_attack_plugins.py
- Run: PYTHONPATH=src ./.venv/bin/python -m ruff check
  src/lab/plugins/extra/attacks/pretrained_patch_adapter.py

Out of scope: refactoring placement_mode logic, changing the public
adapter signature, touching other attack adapters.

Definition of done: tests green, ruff clean, PR description names the
behavior change explicitly (CLAUDE.md "do not weaken existing errors")
and notes any change to the per-image metadata schema.
```

---

## P1-2 — Parametrize wrapper compat tests to cover ALL wrappers

```text
Close a P1 verification gap in the repo-structure compat tests.

File: tests/test_repo_structure_compat.py

The test `test_root_wrappers_alias_to_moved_modules` currently spot-checks
4 wrappers (auto_cycle, run_training_ritual, run_demo,
generate_auto_summary). PR #91 introduced ~17 wrapper scripts; the other
~13 are unverified despite CODE_QUALITY_STANDARD.md §"Wrapper and shim
changes" requiring "explicit compatibility tests" and AGENTS.md repeating
that requirement.

Same problem in `test_old_adapter_shims_alias_to_moved_modules` — covers
4 of 15+ adapter shims under src/lab/{attacks,defenses,models}/*.

Required fix:

1. Build the full list of wrappers programmatically. The pattern is: any
   file directly under scripts/ that ends with one of the
   "Compatibility wrapper" docstring lines (or that does
   `sys.modules[__name__] = _load_module()` in its `else:` branch). At the
   time of writing, that's:
   - scripts.auto_cycle           → scripts.automation.auto_cycle
   - scripts.cleanup_stale_runs   → scripts.automation.cleanup_stale_runs
   - scripts.watch_cycle          → scripts.automation.watch_cycle
   - scripts.run_demo             → scripts.demo.run_demo
   - scripts.evaluate_checkpoint  → scripts.training.evaluate_checkpoint
   - scripts.export_training_data → scripts.training.export_training_data
   - scripts.run_training_ritual  → scripts.training.run_training_ritual
   - scripts.train_dpc_unet_local → scripts.training.train_dpc_unet_local
   - scripts.train_dpc_unet_feature_loss → scripts.training.train_dpc_unet_feature_loss
   - scripts.train_from_signal    → scripts.training.train_from_signal
   - scripts.print_summary        → scripts.reporting.print_summary
   - scripts.generate_auto_summary    → scripts.reporting.generate_auto_summary
   - scripts.generate_cycle_report    → scripts.reporting.generate_cycle_report
   - scripts.generate_dashboard       → scripts.reporting.generate_dashboard
   - scripts.generate_failure_gallery → scripts.reporting.generate_failure_gallery
   - scripts.generate_framework_report → scripts.reporting.generate_framework_report
   - scripts.generate_team_summary    → scripts.reporting.generate_team_summary

   Verify the list against the current tree with:
   `for f in scripts/*.py; do grep -l "Compatibility wrapper" "$f"; done`

2. Same exercise for adapter shims under src/lab/{attacks,defenses,models}/.
   Pattern: any file in those flat directories that contains
   `sys.modules[__name__] = import_module("lab.plugins.…")`. Build the
   list programmatically.

3. Use `subTest` per case so a failure tells you exactly which wrapper
   broke. Don't catch and silently skip missing imports — let them fail.

4. Add a meta-test that asserts the test list matches the actual set of
   wrappers in scripts/ (so adding a new wrapper without a test fails
   loudly).

Verification:
- PYTHONPATH=src ./.venv/bin/python -m pytest -q tests/test_repo_structure_compat.py -v
- The test count for both methods should grow by ~13× and ~11× respectively.

Out of scope: refactoring the wrappers themselves; the standardization in
P3-1 is a separate task.

Definition of done: every wrapper currently in scripts/ that uses the
sys.modules pattern is covered; meta-test guards future additions; ruff
and mypy clean.
```

---

## P2-1 — Make dashboard output deterministic

```text
Fix a P2 non-determinism finding in the reporting layer.

File: src/lab/reporting/aggregate/dashboard.py:432

Current code:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

The value is rendered into the output HTML. Two consecutive runs with
identical input data produce different output bytes, breaking
CI-cacheability and PR-diffability. CLAUDE.md "Reporting or summary code"
required-checks call for "deterministic machine-parseable outputs."

Required fix (pick one — discuss in PR description which and why):
A. Derive the timestamp from the input data — e.g. the max mtime of the
   sweep manifests being aggregated, or the latest sweep_id timestamp.
   This keeps a meaningful "last data point" indicator without
   wall-clock dependence.
B. Drop the timestamp from the rendered HTML and put it in a separate
   `dashboard_meta.json` sidecar that's allowed to vary.
C. Keep wall-clock but ALSO emit a stable content hash near the top of
   the HTML so diff tools can detect actual content changes.

Recommendation: option A. Cleanest, no new artifacts.

Verification:
- New test: run the dashboard generator twice on the same fixture
  framework_reports/ tree, assert the byte-for-byte output is identical.
- Existing tests in tests/test_framework_reporting.py must still pass.
- Run ruff + mypy on the changed file.

Out of scope: touching team_summary, failure_gallery, or any other
reporting module unless they have the same bug (verify with grep first;
if they do, mention in PR but split into separate PR).

Definition of done: deterministic test passes; PR description names the
chosen approach (A/B/C) and the trade-off.
```

---

## P2-2 — Add tests for `team_summary.py` semantic-status logic

```text
Close a P2 testability gap in the reporting layer.

File: src/lab/reporting/team_summary.py

PR #91 added ~130 lines of new logic in this file:
- Helpers: _shared_value, _context_value, _is_ranked_row,
  _derive_semantic_status, _build_local_context, _build_external_provenance
- New row fields: _dataset_scope, _pipeline_profile, _authoritative_metric
- New keyword arg: external_clean_gate_path
- Markdown payload now branches on semantic_status (ranked / mixed /
  diagnostic) and renders distinct "Local" vs "External" sections.

Currently no test exercises _derive_semantic_status directly, and the
overall payload schema is not pinned. CODE_QUALITY_STANDARD.md
non-negotiable #6 forbids "silent contract weakening" for output paths,
and the team summary is a downstream consumer contract.

Required tests (add to tests/test_framework_reporting.py):

1. Unit tests for _derive_semantic_status — one per branch
   (ranked_result, mixed, diagnostic, anything else). Use the smallest
   possible fixture row dict.
2. A snapshot/golden test for build_team_summary_payload + render_team_summary_markdown
   on a fixed fixture: ranked rows + diagnostic rows + an external clean-gate
   file. Pin the JSON shape and a markdown excerpt.
3. A test that calls write_team_summary(report_root) WITHOUT
   external_clean_gate_path and asserts the output still validates as a
   valid v1 schema instance (whatever that means in this repo — check
   schemas/v1/ for the relevant schema; if there isn't one for team summary,
   add one in a separate PR rather than scope-creeping).
4. A test asserting the new private-prefixed row fields (_dataset_scope
   etc.) do NOT leak into the public Markdown rendering, OR if they DO
   appear (e.g. as a debug section), pin the rendering.

Verification:
- PYTHONPATH=src ./.venv/bin/python -m pytest -q tests/test_framework_reporting.py -v
- ruff + mypy on touched files (team_summary is in mypy's scope, so type
  errors will surface).

Out of scope: changing team_summary behavior, refactoring helpers,
schema additions (separate PR).

Definition of done: all four tests added and passing; PR description
states "no behavior change, test coverage only."
```

---

## P2-3 — Enforce Phase 4 / authority filtering in dashboard aggregation

```text
Close a P2 comparability gap in the dashboard.

File: src/lab/reporting/aggregate/dashboard.py

The dashboard reads framework reports (sweep outputs) and renders charts
across cycles. CLAUDE.md "mAP50 source rule" requires Phase 4 validate_*
rows as the authoritative source for mAP50. The "auto_summary
false-positive warning" notes that Phase 1 smoke can shadow Phase 4
rows. The current dashboard does not filter by source_phase / authority,
so a Phase 1 (32-image, confidence-only) point can render in the same
series as a Phase 4 mAP50 point with no visual warning.

Required fix:
1. Identify where dashboard ingests rows. Trace from main(...) through
   any aggregate/groupby steps.
2. Add a filter: when computing mAP50-bearing series, drop rows where
   `source_phase != "phase4"` OR `authority != "primary"` (whichever
   field carries the contract — check src/lab/runners/run_intent.py and
   schemas/v1/ for the canonical name).
3. Track the count of rows excluded per chart and render a small footer
   note ("N rows excluded as non-authoritative; see audit log") so the
   elision is visible.
4. Do NOT silently change which rows feed the confidence-metric series
   (Phase 1 is fine for confidence; mAP50 specifically is the contract).

Verification:
- New test in tests/test_framework_reporting.py: feed a fixture with
  mixed Phase 1 / Phase 4 rows; assert mAP50 chart series only contain
  Phase 4 data; assert the footer note correctly reports the excluded
  count.
- Existing dashboard tests must still pass.

Out of scope: changing how upstream runs are tagged with source_phase;
modifying auto_summary's false-positive warning logic (separate concern).

Definition of done: filter active, test green, PR description quotes the
relevant CLAUDE.md rule.
```

---

## P2-4 — Stop swallowing warm-start failures silently in `auto_cycle`

```text
Fix a P2 silent-failure bug in the cycle orchestrator.

File: scripts/automation/auto_cycle.py:1367-1369

Current code:
    try:
        warm = json.loads(WARM_START_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass

A corrupted warm-start file (truncated write, partial JSON, missing key)
silently disables the warm-start optimization. An operator looking at why
a cycle is unexpectedly slow has no signal. CLAUDE.md "Stateful or
resumable code" required-checks include "interruption safety" — silent
fallback fails that.

Required fix:
1. Narrow the except to (OSError, json.JSONDecodeError) — anything else
   should propagate (e.g. a RuntimeError from a config-shape mismatch is
   a real bug we want to see).
2. log() the failure with: the file path, the exception type, and a
   one-line message. Use the existing `log()` helper in this file
   (search the file for its definition / usage pattern).
3. After the log line, set warm to whatever the existing fallback is
   (probably {} or None — check the code immediately after the
   try/except).

Verification:
- Add a unit test that writes a truncated JSON file to the warm-start
  path (use tmp_path fixture or monkeypatch the path constant) and
  asserts (a) the function does not crash, (b) something log-worthy was
  emitted (capture stdout/stderr), (c) the cycle continues.
- Run: PYTHONPATH=src ./.venv/bin/python -m pytest -q
  tests/test_auto_cycle_and_dashboard.py

Out of scope: any other broad-except in this file; full audit of warm
start (separate big-brother-auditor pass).

Definition of done: ≤15 line change, test added, ruff clean. Note in PR
that auto_cycle is on the high-risk surfaces list (CLAUDE.md) and that
this fix doesn't change cycle semantics.
```

---

## P2-5 — Document mypy scope honestly in CODE_QUALITY_STANDARD.md

```text
Doc-only fix for a P2 honesty gap.

File: CODE_QUALITY_STANDARD.md (and possibly README.md)

Current state: pyproject.toml configures mypy against only
src/lab/{eval,reporting,runners} — 24 files of >150 in src/lab/. The
2.5k-line scripts/automation/auto_cycle.py (high-risk surface),
src/lab/plugins/, src/lab/attacks/, src/lab/defenses/ are NOT
type-checked. CODE_QUALITY_STANDARD.md §"Retroactive Audit Commands"
presents the `--lane full` audit as the broad audit but mypy coverage
is far narrower than that reads, and non-negotiable #7 says "comments
and docs must be honest."

Required fix:
1. In CODE_QUALITY_STANDARD.md §"Retroactive Audit Commands", add a
   note immediately after the `--lane full` block: "Current mypy scope:
   src/lab/{eval,reporting,runners}. Other src/lab/ subpackages and
   scripts/ are not type-checked — see pyproject.toml [tool.mypy] for
   the authoritative list."
2. In CODE_QUALITY_STANDARD.md §"Verification Matrix", soften
   "mypy when the change touches typed orchestration or contracts" to
   include an explicit pointer to the configured surface so contributors
   know when mypy will and won't run on their code.
3. Open a tracking issue (or add a TODO at the top of pyproject.toml's
   mypy block) listing the planned expansion order. Recommended order:
   src/lab/runners (already in scope; verify), src/lab/plugins/ (high
   value, mostly typed already), src/lab/config/, src/lab/attacks/,
   src/lab/defenses/, scripts/automation/auto_cycle.py last.

Verification:
- PYTHONPATH=src ./.venv/bin/python scripts/ci/run_repo_standards_audit.py --lane full
  (must still pass — this is doc-only)
- Read the updated CODE_QUALITY_STANDARD.md end-to-end and confirm no
  remaining claims of broader coverage than is implemented.

Out of scope: actually expanding mypy coverage. That's a series of
separate PRs, one per subpackage, because each will surface real
type-debt that needs addressing.

Definition of done: doc PR, no code changed, no test runs needed beyond
the audit lane.
```

---

## P2-6 — Add module-identity AND `--help` smoke tests for the remaining wrappers

```text
Close the testability twin of P1-2 in the per-area compat test files.

Files:
- tests/test_training_script_compat.py
- tests/test_reporting_and_demo_script_compat.py
- tests/test_cli_wrapper_entrypoints.py

Untested for module-identity (7): evaluate_checkpoint, generate_dashboard,
generate_failure_gallery, generate_team_summary, print_summary,
train_dpc_unet_local, train_dpc_unet_feature_loss.

Untested for --help (6): same set minus evaluate_checkpoint.

This is a finer-grained version of P1-2: that fix covers the umbrella
test in tests/test_repo_structure_compat.py; this fix covers the per-area
test files that should have caught it locally.

NOTE: do P1-2 first. After P1-2 lands, this fix may collapse into a few
parametrize() additions — review what's still needed against the new
state of test_repo_structure_compat.py and don't double-cover.

Required fix (after P1-2 is merged):
1. For each of the three test files, parametrize over the relevant
   wrapper subset (training files in test_training_script_compat,
   reporting+demo files in test_reporting_and_demo_script_compat, all
   CLI smoke in test_cli_wrapper_entrypoints).
2. The --help smoke should run `subprocess.run([sys.executable,
   "scripts/X.py", "--help"], capture_output=True, timeout=10)` and
   assert returncode == 0. Skip on Windows if any of the wrappers are
   POSIX-only (none are at time of writing — verify).
3. Don't shell out via shell=True; build the arg list explicitly.

Verification:
- PYTHONPATH=src ./.venv/bin/python -m pytest -q
  tests/test_training_script_compat.py
  tests/test_reporting_and_demo_script_compat.py
  tests/test_cli_wrapper_entrypoints.py -v

Out of scope: the umbrella test covered by P1-2 (do first).

Definition of done: every wrapper that exists at scripts/X.py is
exercised by at least one --help smoke and one module-identity check.
```

---

## P3 batch — fold these into the next PR that touches the file

P3s aren't worth their own session. Drop these into whatever PR
naturally touches the file.

- **P3-1 — wrapper main pattern:** standardize all of scripts/*.py
  wrappers on `_run_main()` (5 already use it). Whoever does P1-2 can
  also do this — same mental cache.
- **P3-2 — explicit `framework_comparison` re-export:** in
  src/lab/reporting/__init__.py, add `from . import framework_comparison`
  + `"framework_comparison"` to `__all__`. Whoever does P2-2 will be in
  this file anyway.
- **P3-3 — `pgd_adapter` shim docstring:** add the standard
  "Compatibility shim for …" docstring to
  src/lab/attacks/pgd_adapter.py. ≤5 lines. Drop into any PR that
  touches the attacks directory.

---

## Granular follow-up audit (separate, not a fix)

```text
Run a deep big-brother-auditor pass on scripts/automation/auto_cycle.py.

Why: the 2026-04-20 broad triage scored PR #91 modularization 10/12
overall but only spot-checked auto_cycle.py despite it being the
highest-blast-radius file in the repo (2.5k lines, on the CLAUDE.md
high-risk-surfaces list, post-extraction from the PR #91 split).

How:
1. Use the .claude/skills/big-brother-auditor/ skill with scope
   "scripts/automation/auto_cycle.py and its phase 1-4 helpers". The
   skill knows the project conventions and the merge-blocker list.
2. Pay particular attention to:
   - state-corruption risk on resume (_phase4_validation_defenses
     supplementation logic, warm_start, lock cleanup)
   - process-group kill (PR #82) — verify the SIGKILL second-wait can't
     deadlock
   - phase 4 deepfool cap (PR #83) — confirm the cap is recorded in
     run provenance so cycle-over-cycle comparability isn't silently
     broken
   - subprocess timeout / exit-code propagation across phases
   - the broad except at line 1367 (already flagged P2-4; may surface
     others)
3. Output: standard big-brother-auditor findings (P0-P3, file:line,
   evidence, minimal fix).

Out of scope: fixing anything found. This is audit-only; spin off
fix PRs from the findings.
```
