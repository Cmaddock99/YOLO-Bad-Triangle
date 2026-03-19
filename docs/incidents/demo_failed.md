# Demo Failed Playbook

Use this playbook when demo CI gate fails.

## 1) Re-run demo gate exactly

```bash
PYTHONPATH=src ./.venv/bin/python scripts/ci/check_demo_gate.py --profile week1-demo --output-root outputs/demo-gate-ci
```

## 2) Re-run demo package manually

```bash
bash scripts/demo/run_demo_package.sh fast --profile week1-demo --output-root outputs/demo-gate-ci
```

## 3) Validate required outputs

Expected files:
- `outputs/demo-gate-ci/metrics_summary.csv`
- `outputs/demo-gate-ci/experiment_table.md`

## 4) Inspect fallback execution path

Demo runs should remain framework-first through wrappers/adapters.  
If incident requires rollback, run:

```bash
./.venv/bin/python scripts/run_framework.py --legacy --config configs/week1_stabilization_demo_matrix.yaml --output_root outputs/demo-gate-ci
```

## 5) Post-incident action

- File an issue with failing command + stderr.
- Attach artifact directory and gate output logs.
- Re-run `scripts/ci/run_migration_gates.py` before closing incident.
