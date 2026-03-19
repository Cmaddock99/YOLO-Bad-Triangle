# Parity Failed Playbook

Use this playbook when the parity CI gate fails.

## 1) Re-run parity gate exactly

```bash
PYTHONPATH=src ./.venv/bin/python scripts/ci/check_parity_gate.py --config configs/parity_test.yaml
```

## 2) Re-run full paired shadow parity for debug artifacts

```bash
PYTHONPATH=src ./.venv/bin/python run_shadow_parity.py --config configs/parity_test.yaml
```

## 3) Inspect parity deltas

```bash
python -m json.tool outputs/shadow_parity/<latest_run_id>/parity_report.json
```

Focus on:
- `metadata_mismatches`
- `delta_summary.detection_worst_relative_pct`
- `delta_summary.confidence_worst_relative_pct`
- `validation_gate_errors`

## 4) Compare paired CSV rows

```bash
python -m json.tool outputs/shadow_parity/<latest_run_id>/parity_report.json
```

Then inspect:
- `outputs/shadow_parity/<latest_run_id>/metrics_summary.csv`
- `outputs/shadow_parity/<latest_run_id>/shadow_summary.md`

## 5) Rollback instructions

- Temporary rollback surface:
  - Single-run: `python run_experiment.py --legacy ...`
  - Batch: `./.venv/bin/python scripts/run_framework.py --legacy --config <legacy_config> --output_root <dir>`
- Keep framework-first as default; rollback is for incident containment only.
