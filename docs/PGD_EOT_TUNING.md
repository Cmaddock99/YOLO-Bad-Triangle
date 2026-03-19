# PGD + EOT-PGD Power Tuning

This note documents strong defaults and a reproducible tuning protocol for maximum white-box attack strength under explicit `L_inf` bounds.

## Attack defaults

Use these as starting points in `configs/experiment_lab.yaml`:

- `pgd`
  - `epsilon: 0.016`
  - `alpha: 0.002`
  - `steps: 20`
  - `random_start: true`
  - `restarts: 1`
- `eot_pgd`
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

## Matched-budget quick matrix

Run this first to sanity-check that baseline, PGD, and EOT-PGD diverge at the same budget:

```bash
./.venv/bin/python scripts/run_framework.py --config configs/pgd_eot_quick_matrix.yaml
```

Expected outcome: PGD and EOT-PGD rows are both worse than baseline on at least one primary metric (`mAP50`, `mAP50-95`, `recall`), and EOT-PGD is often stronger than PGD at the same `epsilon`.

## Maximum-strength protocol

Keep YOLO and evaluation fixed while tuning:

- model: `yolo26` (or fixed weights path)
- confidence: `conf=0.25`
- fixed seed: `seed=42`
- same dataset split and same validation flow

### 1) Calibrate PGD first

Sweep:

- `epsilon`: `0.008`, `0.012`, `0.016`, `0.024`
- `steps`: `10`, `20`, `40`
- `alpha`: roughly from `epsilon/steps` to `2*epsilon/steps`

Pick the strongest setting that is numerically stable and still within your threat model.

### 2) Tune EOT-PGD at fixed PGD budget

Lock `epsilon` and `steps`, then sweep:

- `eot_samples`: `2`, `4`, `8`
- transform magnitudes:
  - `scale_jitter`
  - `translate_frac`
  - `brightness_jitter`
  - `contrast_jitter`
  - `blur_prob`

Goal: further lower `mAP50`, `mAP50-95`, and `recall` versus PGD at the same `epsilon`.

### 3) Increase restarts for stronger white-box optimization

Raise `restarts` to `3-5` and keep the worst-case solution per image.
This improves attack strength at the cost of runtime.

## Metrics to track each run

Primary:

- `mAP50`
- `mAP50-95`
- `recall`

Secondary:

- `images_with_detections`
- `total_detections`
- runtime per run

## Practical guardrails

- EOT cost scales roughly with `steps * eot_samples * restarts`.
- Start with a small subset for tuning, then scale to full validation.
- Use moderate transform magnitudes. Overly aggressive transforms can make optimization unstable and weaken attack quality.
