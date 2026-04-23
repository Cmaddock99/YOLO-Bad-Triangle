# Gate 0 Decision Record: Canonical Attack Set v1

**Status:** ACCEPTED — written 2026-04-22
**Scope:** Historical Direction A / archived cycle evidence only. This record
does not change the current `yolo11n_lab_v1` runtime profile catalogs.

---

## Purpose

Freeze the baseline, comparison surface, and evidence hierarchy used for
archived Direction A claims so follow-on docs and repo edits stop re-litigating
those inputs.

## Gate 0 Decisions

### 1. Authoritative baseline

- Baseline value: `mAP50 = 0.6001591766396535`
- Baseline run: `validate_baseline`
- Authoritative cycle: `cycle_20260407_193440` (started 2026-04-07, finished
  2026-04-09)
- Required source artifacts:
  - `outputs/cycle_history/cycle_20260407_193440.json`
  - `outputs/framework_reports/cycle_20260407_193440/framework_run_summary.csv`

The exact baseline value must come from the two source artifacts above, not
from memory, summaries, or later restatements.

### 2. Authoritative metric

- Use `mAP50` for baseline and recovery comparisons.
- Treat `mAP50-95` as diagnostic output only; it must not replace `mAP50` in
  archived Direction A gate decisions.

### 3. Comparison surface

The historical comparison surface for this record is the set captured by
`cycle_20260407_193440`:

- Attacks: `square`, `deepfool`, `dispersion_reduction`
- Defenses: `jpeg_preprocess`, `median_preprocess`, `bit_depth`, `c_dog`

This comparison surface is evidence governance for archived analysis. It is not
a claim that every item above is part of the current `yolo11n_lab_v1` runtime
profile.

### 4. Exclusions

- `0.5765` and other memory-only baseline values are non-authoritative.
- Manual patch artifacts, patch demos, physical benchmark notes, and ad hoc
  sweeps are not Gate 0 authority unless they are promoted into the source
  artifacts above.
- Current execution behavior still comes from the repo runtime contracts,
  especially `configs/pipeline_profiles.yaml`, not from this archival record.

## Evidence Hierarchy

When sources disagree, use this precedence order:

1. `outputs/cycle_history/cycle_20260407_193440.json`
2. `outputs/framework_reports/cycle_20260407_193440/framework_run_summary.csv`
3. Derived analysis docs such as `docs/analysis/direction_a_closure_20260409.md`
4. Notes, memory entries, summaries, and informal restatements

## Consequences

- No separate Workstream 1 remains after this record; baseline selection is
  closed by this document.
- Future archival Direction A edits must cite the baseline above and stay
  within the comparison surface above, or explicitly mark themselves as
  diagnostic or out of scope.
- Any later governance record that supersedes this one must name the
  replacement artifact set and the exact replacement baseline value.
