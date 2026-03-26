# Attack Module Template

Use this template to add a new attack in `src/lab/attacks/`.

## 1) Create a new file

Create `src/lab/attacks/<your_attack>_adapter.py` and start from this:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .base_attack import BaseAttack
from .framework_registry import register_attack_plugin
from lab.eval.prediction_utils import adapter_stage_metadata


@dataclass
@register_attack_plugin("your_attack_name", "optional_alias")
class YourAttack(BaseAttack):
    # Parameters settable from YAML (attack.params.*) go here.
    strength: float = 0.1
    name: str = "your_attack_name"

    def __post_init__(self) -> None:
        if self.strength <= 0:
            raise ValueError("strength must be > 0")

    def apply(
        self,
        image: np.ndarray,
        model: Any | None = None,
        **kwargs: Any,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        del model, kwargs
        # TODO: apply attack to image (uint8 HWC, BGR)
        attacked = image.copy()
        meta = adapter_stage_metadata("your_attack_name", "apply", strength=self.strength)
        return attacked, meta
```

## 2) How registration works

- `@register_attack_plugin("your_attack_name", "optional_alias")` makes the class discoverable.
- The registry is `src/lab/attacks/framework_registry.py` — you do not need to edit any central list.
- Plugins are loaded lazily on first use.

## 3) YAML usage example

Params set in the config or via `--set` go under `attack.params.*`:

```yaml
attack:
  name: your_attack_name
  params:
    strength: 0.2
```

Or inline with `--set`:
```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=your_attack_name \
  --set attack.params.strength=0.2
```

## 4) Expected behavior contract

- Input: `image` — single `np.ndarray`, shape `(H, W, 3)`, dtype `uint8`, BGR channel order.
- Output: `(attacked_image, metadata_dict)` — same shape/dtype as input; `metadata_dict` from `adapter_stage_metadata`.
- The `model` argument is available if your attack needs a differentiable loss (e.g. FGSM, PGD). Pass `del model` if unused.
- Determinism: use the seeded RNG passed in via `**kwargs` if your attack has randomness.

## 5) Quick validation checklist

- [ ] File created in `src/lab/attacks/` with `_adapter.py` suffix.
- [ ] Class subclasses `BaseAttack`.
- [ ] `apply(self, image, model=None, **kwargs)` returns `(np.ndarray, dict)`.
- [ ] Uses `@register_attack_plugin(...)` with at least one name.
- [ ] Works with a quick smoke test:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=your_attack_name \
  --set runner.max_images=4
```

## 6) Current registered attacks

Run `scripts/sweep_and_report.py --list-plugins` for the live list. Current attacks in the auto-cycle:

| Name | Type |
|---|---|
| `fgsm` | Gradient — fast, single-step L∞ |
| `pgd` | Gradient — iterative L∞ |
| `deepfool` | Gradient — minimal perturbation |
| `eot_pgd` | Gradient — expectation over transformations |
| `blur` | Non-gradient — Gaussian blur |
| `jpeg_attack` | Non-gradient — JPEG compression |
| `square` | Query-based black-box L∞ |
