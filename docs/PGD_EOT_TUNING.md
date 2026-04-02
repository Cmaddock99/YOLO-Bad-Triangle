# PGD and EOT-PGD Tuning

This note records practical starting points for stronger white-box attack runs.

## Suggested defaults

### `pgd`

- `epsilon: 0.016`
- `alpha: 0.002`
- `steps: 20`
- `random_start: true`
- `restarts: 1`

### `eot_pgd`

- `epsilon: 0.016`
- `alpha: 0.0015`
- `steps: 20`
- `eot_samples: 4`
- `random_start: true`
- `restarts: 1`
- `scale_jitter: 0.1`
- `translate_frac: 0.03`
- `brightness_jitter: 0.08`
- `contrast_jitter: 0.08`
- `blur_prob: 0.25`

## Quick comparison command

Use the current sweep entrypoint, not removed legacy scripts:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py \
  --config configs/default.yaml \
  --attacks pgd,eot_pgd \
  --defenses none \
  --preset smoke \
  --validation-enabled \
  --workers 1
```

If you want to compare matched budgets, keep the same `epsilon`, `steps`, and
seed across both attacks.

## Tuning protocol

### 1. Calibrate PGD first

Sweep:

- `epsilon`: `0.008`, `0.012`, `0.016`, `0.024`
- `steps`: `10`, `20`, `40`
- `alpha`: roughly from `epsilon / steps` to `2 * epsilon / steps`

### 2. Tune EOT-PGD at fixed PGD budget

Hold `epsilon` and `steps` fixed, then sweep:

- `eot_samples`: `2`, `4`, `8`
- transform magnitudes such as `scale_jitter`, `translate_frac`,
  `brightness_jitter`, `contrast_jitter`, and `blur_prob`

### 3. Increase restarts only after the base setup is stable

Higher restart counts are stronger but much slower.

## Metrics worth tracking

- `mAP50`
- `mAP50-95`
- `recall`
- `images_with_detections`
- `total_detections`
- runtime per run

## Practical advice

- Tune on smoke-size runs first.
- Move to larger validation only after the parameter region looks sensible.
- Keep the comparison budget-matched so you learn whether EOT helped, not just
  whether you spent more compute.
