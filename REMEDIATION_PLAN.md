# YOLO-Bad-Triangle — Safe Remediation Plan
_Generated: 2026-03-29 from full repository audit_
_Status updated: 2026-04-09 — all Phase 1 (P0) and Phase 2 (P1) items verified CLOSED in code_

## Status Summary (2026-04-09)

All high-priority items have been applied in prior commits. The plan below reflects original
wording; verified current code state is noted per item.

| Item | Severity | Code Status |
|---|---|---|
| 1.1 save_state() atomic write | P0 | **DONE** — `os.replace()` at auto_cycle.py:321 |
| 1.2 per_class key documentation | P0 | **DONE** — contracts.py documents str keys |
| 2.1 Lock FD close on BlockingIOError | P1 | **DONE** — `lock_fd.close()` at auto_cycle.py:2219 |
| 2.2 Training signal: trainable-only filter | P1 | **DONE** — `_trainable_pool()` at auto_cycle.py:1565 |
| 2.3 EOT-PGD: assert → RuntimeError | P1 | **DONE** — RuntimeError at eot_pgd.py:182 |
| 2.4 DR: hook registration validation | P1 | **DONE** — ValueError at dispersion_reduction_adapter.py:53 |
| 2.5 _recovery() None propagation guard | P1 | **DONE** — returns None explicitly; callers handle it |
| 3.1–3.3 Structural/P2 items | P2 | Deferred — no active bug risk |
| 4.1–4.2 NUC ops | P3 | Deferred — NUC operator decision |

---

## Guiding Principles

1. **Smallest possible diff per fix** — no drive-by refactors
2. **No behavioral changes to the ML pipeline** — inference, training signal, and mAP50 numbers must not change except where a fix explicitly corrects a documented bug
3. **Tests must still pass after every phase** — run `pytest -q` between phases
4. **Phases are ordered by risk and dependency** — Phase 1 (Critical) → Phase 2 (High) → Phase 3 (Structural)
5. **All changes on `fix/remediation` branch** — never commit directly to `main`

---

## Phase 1 — Critical: Data Integrity Fixes

These have silent data corruption potential. Fix before any new cycles run.

### Fix 1.1 — `save_state()`: Atomic write to prevent state corruption

**File:** `scripts/auto_cycle.py:272–274`
**Risk if skipped:** Process kill / cron restart mid-write corrupts `cycle_state.json` permanently; cycle cannot resume.
**Behavior change:** None (same JSON written, same path). Atomicity is transparent to readers.

**Current code:**
```python
def save_state(state: dict) -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))
```

**Fix:**
```python
import tempfile

def save_state(state: dict) -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    os.replace(tmp, STATE_FILE)
```

`import tempfile` is already imported or add `import os` (already present at line 48).
`os.replace()` is atomic on POSIX (rename syscall). No temp file left on crash.

**Verification:** Run `pytest -q` — no test touches `save_state` directly so all pass.

---

### Fix 1.2 — `per_class` key type: Standardize to `str` throughout

**Files:** `src/lab/eval/framework_metrics.py:70` (writer), `src/lab/reporting/framework_comparison.py:299–302` and `:310–313` (reader)
**Risk if skipped:** Any new reporting path that reads `per_class` without `int(k)` conversion silently drops all per-class data.
**Behavior change:** Zero change to existing CSV output; the `int(k)` conversion in `framework_comparison.py` already corrects for the writer writing `str`. The fix eliminates the structural mismatch so future readers don't need to know about it.

**Strategy:** The safest fix is to standardize the *reader* side fully rather than changing the writer (changing the writer risks breaking any reader not yet audited). Both reader sites already do `int(k)` — confirm they are the only two.

```bash
grep -rn "per_class" src/ --include="*.py" | grep -v "\.pyc"
```

If only `framework_comparison.py` reads `per_class` from JSON, document in `contracts.py`:

**Add to `src/lab/config/contracts.py`** (as a comment near the metrics schema section):
```python
# NOTE: framework_metrics.py writes per_class keys as str(int) e.g. "0", "42".
# All readers must cast: int(k) or str(k) as appropriate.
# Do NOT change the writer — existing metrics.json files on disk use str keys.
```

This is a documentation fix only — no code changed, risk zero.

**If** a future audit reveals a reader missing the `int(k)` cast, add it at that time.

---

## Phase 2 — High: Reliability and Correctness Fixes

These cause silent wrong behavior, resource leaks, or subtle ML pipeline errors.

### Fix 2.1 — Lock FD resource leak on `BlockingIOError`

**File:** `scripts/auto_cycle.py:1771–1776`
**Risk if skipped:** File descriptor leaked to OS on every blocked invocation (cron fires every 30 min). On long-running NUC sessions this accumulates.
**Behavior change:** None — the process exits immediately after, but proper FD cleanup is correct.

**Current code (lines 1771–1776):**
```python
lock_fd = open(LOCK_FILE, "w")
try:
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    print("Another cycle instance is already running. Exiting.")
    sys.exit(0)
```

**Fix:**
```python
lock_fd = open(LOCK_FILE, "w")
try:
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    lock_fd.close()
    print("Another cycle instance is already running. Exiting.")
    sys.exit(0)
```

One line added: `lock_fd.close()` before `sys.exit(0)`.

**Verification:** `pytest -q` — not tested by unit tests, but trivially correct.

---

### Fix 2.2 — Training signal filter: Only select from trainable defenses

**File:** `scripts/auto_cycle.py` — `_write_training_signal()`, two code paths
**Risk if skipped:** Signal selects `jpeg_preprocess` as weakest defense; Colab training targets JPEG compression, which DPC-UNet cannot learn to counteract. Wasted GPU training time.
**Behavior change:** `weakest_defense` in `cycle_training_signal.json` changes — but only when a non-DPC-UNet defense would have been selected. The ML pipeline behavior is _corrected_, not broken.

**Code path A — mAP50 path (lines 1299–1301):**

Current:
```python
if defense_recovery.get(worst_attack):
    weakest_defense = min(defense_recovery[worst_attack], key=lambda d: defense_recovery[worst_attack][d])
    weakest_recovery = defense_recovery[worst_attack][weakest_defense]
```

Fix:
```python
_TRAINABLE_DEFENSES = {"c_dog", "c_dog_ensemble"}

if defense_recovery.get(worst_attack):
    trainable = {d: v for d, v in defense_recovery[worst_attack].items()
                 if d in _TRAINABLE_DEFENSES}
    _pool = trainable if trainable else defense_recovery[worst_attack]
    weakest_defense = min(_pool, key=lambda d: _pool[d])
    weakest_recovery = _pool[weakest_defense]
```

Fallback to full pool if no trainable defenses present in results (smoke runs may not include all defenses).

**Code path B — detection fallback path (lines 1361–1364):**

Current:
```python
worst_attack = atk_avg[0][1]
rmap = defense_recovery[worst_attack]
weakest_defense = min(rmap, key=lambda d: rmap[d])
weakest_recovery = rmap[weakest_defense]
```

Fix:
```python
worst_attack = atk_avg[0][1]
rmap = defense_recovery[worst_attack]
_TRAINABLE_DEFENSES = {"c_dog", "c_dog_ensemble"}
trainable_rmap = {d: v for d, v in rmap.items() if d in _TRAINABLE_DEFENSES}
_pool = trainable_rmap if trainable_rmap else rmap
weakest_defense = min(_pool, key=lambda d: _pool[d])
weakest_recovery = _pool[weakest_defense]
```

**Implementation note:** Define `_TRAINABLE_DEFENSES` once as a module-level constant near the top of `_write_training_signal()` or as a file-level constant, not duplicated in both branches.

**Verification:** `pytest -q`. Consider adding a unit test for `_write_training_signal()` that verifies `jpeg_preprocess` is NOT selected when `c_dog` results are present.

---

### Fix 2.3 — EOT-PGD: Replace `assert` with `RuntimeError`

**File:** `src/lab/attacks/eot_pgd.py:181`
**Risk if skipped:** `assert loss_sum is not None` is silently disabled when Python runs with `-O` (optimized flag). If `eot_samples=0` or all model calls fail silently, `.backward()` is called on `None`, producing a cryptic `AttributeError` instead of a clear error.
**Behavior change:** None under normal execution. Only changes the error type under pathological conditions.

**Current (line 181):**
```python
assert loss_sum is not None
```

**Fix:**
```python
if loss_sum is None:
    raise RuntimeError(
        "EOT-PGD: loss_sum is None after EOT loop — "
        "check that eot_samples > 0 and the model returns valid outputs"
    )
```

**Verification:** `pytest -q` — existing EOT-PGD tests should still pass (they use valid models).

---

### Fix 2.4 — DR attack: Validate hook registration

**File:** `src/lab/attacks/dispersion_reduction_adapter.py:47–51`
**Risk if skipped:** If all `layer_indices` exceed `len(torch_model.model)`, zero hooks register. The attack runs all `steps` iterations, captures nothing, and returns a randomly-initialized epsilon-ball image — silently wrong, no error raised. Calling code logs this as a "successful" attack result.
**Behavior change:** Raises `ValueError` early instead of returning noisy garbage. This is a corrective behavior change — garbage output is worse than a clear error.

**Current (lines 47–54):**
```python
handles = []
try:
    for idx in self.layer_indices:
        if idx < len(torch_model.model):
            handles.append(torch_model.model[idx].register_forward_hook(hook_fn))

    # Random start within epsilon ball
    x_adv = (x0 + torch.empty_like(x0).uniform_(-self.epsilon, self.epsilon)).clamp(0, 1)
```

**Fix — add validation after the hook loop:**
```python
handles = []
try:
    for idx in self.layer_indices:
        if idx < len(torch_model.model):
            handles.append(torch_model.model[idx].register_forward_hook(hook_fn))

    if not handles:
        raise ValueError(
            f"DispersionReduction: no hooks registered — all layer_indices "
            f"{self.layer_indices} exceed model depth {len(torch_model.model)}. "
            f"Valid range: 0–{len(torch_model.model) - 1}."
        )

    # Random start within epsilon ball
    x_adv = (x0 + torch.empty_like(x0).uniform_(-self.epsilon, self.epsilon)).clamp(0, 1)
```

**Verification:** Add a unit test with a 2-layer toy model and `layer_indices=[999]` — should raise `ValueError`. `pytest -q` should pass for existing DR tests (they use valid indices).

---

### Fix 2.5 — `_recovery()` None propagation: Guard downstream `min()` calls

**File:** `src/lab/reporting/framework_comparison.py` and `scripts/auto_cycle.py`
**Risk if skipped:** `_recovery()` returns `None` when attack has no effect (`degradation ≈ 0`). In `auto_cycle.py`, `defense_recovery[worst_attack][d]` values fed into `min(..., key=lambda d: ...)` can be `None`, causing `TypeError: '<' not supported between instances of 'NoneType' and 'float'`.
**Behavior change:** None values are now treated as "no recovery" (0.0) for the purposes of the `min()` selector. This is semantically correct — a defense with unmeasured recovery is maximally concerning.

**Location in `auto_cycle.py`:** The `defense_recovery` dict is populated from Phase 2/Phase 4 results. Trace the population site to confirm None can arrive:

```bash
grep -n "defense_recovery\[" scripts/auto_cycle.py | head -30
```

**Fix pattern** (apply wherever `min(rmap, ...)` or `min(defense_recovery[attack], ...)` is called):
```python
# Replace:
weakest_defense = min(_pool, key=lambda d: _pool[d])

# With:
weakest_defense = min(_pool, key=lambda d: (_pool[d] if _pool[d] is not None else 0.0))
```

This combines naturally with Fix 2.2 — apply both to the same lines.

**Verification:** Add a unit test calling `_write_training_signal()` with a `defense_recovery` dict containing `None` values — should not raise.

---

## Phase 3 — Structural: Code Quality

These are low urgency but reduce cognitive load and prevent future bugs.

### Fix 3.1 — Atomic write for cycle history and warm-start files

**File:** `scripts/auto_cycle.py:1196`, `1319`, `1377`, `1482`, `1686`
**Same pattern as Fix 1.1** — `write_text()` calls on important state files.
**Priority:** Lower than `save_state()` since these files are written once at phase completion, not mid-iteration. But history files should also be atomic.

Apply `os.replace()` pattern to:
- `out.write_text(json.dumps(summary, indent=2))` (cycle history, line 1196)
- `sig_path.write_text(json.dumps(signal, indent=2))` (training signal, lines 1319 and 1377)
- `WARM_START_FILE.write_text(json.dumps(warm, indent=2))` (warm-start, line 1686)

`status_file.write_text(...)` at line 1482 is low-stakes (regenerated on next status call) — skip.

---

### Fix 3.2 — `_recovery()` call-site documentation

**File:** `src/lab/reporting/framework_comparison.py:120–131`
Add a one-line comment explaining why None is returned for zero-degradation case, so the next reader doesn't try to "fix" the early return:

```python
def _recovery(...) -> float | None:
    """defense_recovery = (defended - attacked) / (baseline - attacked)
    Returns None when attack had no measurable effect (degradation < 1e-9),
    making recovery undefined. Callers must handle None explicitly.
    """
```

---

### Fix 3.3 — DR `layer_indices` default validation in adapter

**File:** `src/lab/attacks/dispersion_reduction_adapter.py` — the `DispersionReductionAdapter` dataclass
After Fix 2.4 raises on zero hooks, consider also validating `layer_indices` is non-empty at adapter construction time (in `__post_init__` or similar) to surface misconfiguration before any model is needed.

This is optional — Fix 2.4 already catches the failure at runtime with a clear message.

---

## Phase 4 — Optional: NUC Operations

Low urgency housekeeping, schedule during next maintenance window.

### Fix 4.1 — NUC: Cron :00/:30 spurious restarts

**Context:** Cron is set to trigger at :00 and :30; the lock prevents double-runs but each trigger still opens a FD (fixed by 2.1 but FD is still opened then immediately closed).
**Option A:** Change cron to fire at :01 and :31 (offset from natural restart times).
**Option B:** Lower cron frequency to every 60 min since average cycle is ~45 min.
**Decision:** Defer to NUC operator preference.

### Fix 4.2 — NUC: Remove old checkpoint

**File on NUC:** `dpc_unet_adversarial_finetuned.pt` (pre-cycle-7 checkpoint)
**Action:** Archive to `checkpoints/archive/` or delete after confirming `dpc_unet_final_golden.pt` is the active checkpoint everywhere.
**Risk:** None — `dpc_unet_final_golden.pt` is the active path in `.env`.

---

## Implementation Order & Checklist

```
Phase 1 (do first — before next cycle)
[ ] 1.1  save_state() atomic write     scripts/auto_cycle.py:272-274
[ ] 1.2  per_class key documentation   src/lab/config/contracts.py

Phase 2 (do before next full-dataset run)
[ ] 2.1  Lock FD close on exit         scripts/auto_cycle.py:1774-1776
[ ] 2.2  Training signal filter        scripts/auto_cycle.py:1299-1301, 1361-1364
[ ] 2.3  EOT assert → RuntimeError     src/lab/attacks/eot_pgd.py:181
[ ] 2.4  DR hook validation            src/lab/attacks/dispersion_reduction_adapter.py:47-54
[ ] 2.5  _recovery() None guard        scripts/auto_cycle.py (all min() call sites)

Phase 3 (schedule for next PR after Phase 2 is merged)
[ ] 3.1  Atomic writes (history/signal/warm-start)
[ ] 3.2  _recovery() docstring
[ ] 3.3  DR adapter __post_init__ validation (optional)

Phase 4 (NUC maintenance window)
[ ] 4.1  Cron frequency review
[ ] 4.2  Old checkpoint archive
```

---

## Risk Matrix

| Fix | Severity | Behavior Change? | Can Break Tests? | Rollback Cost |
|-----|----------|-----------------|-----------------|---------------|
| 1.1 save_state atomic | Critical | No | No | Trivial |
| 1.2 per_class docs | Critical | No | No | Trivial |
| 2.1 lock FD close | High | No | No | Trivial |
| 2.2 training signal filter | High | Yes (corrective) | No (no test) | Low |
| 2.3 EOT assert→RuntimeError | High | No (error path only) | No | Trivial |
| 2.4 DR hook validation | High | Yes (raises instead of garbage) | No | Low |
| 2.5 _recovery() None guard | High | Yes (None→0.0 in min) | No | Low |
| 3.1 atomic history writes | Structural | No | No | Trivial |
| 3.2 docstring | Structural | No | No | Trivial |

---

## Verification Commands

After each phase:
```bash
# Lint
ruff check src tests scripts

# Tests
PYTHONPATH=src pytest -q

# Smoke run (confirms ML pipeline is intact)
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/ci_demo.yaml \
  --set runner.output_root=outputs/framework_runs/remediation_smoke \
  --set runner.run_name=smoke_$(date +%s)
```

Final gate before merge:
```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=fgsm \
  --set runner.run_name=remediation_gate
# Check: outputs/framework_runs/remediation_gate/metrics.json exists and mAP50 is finite
```
