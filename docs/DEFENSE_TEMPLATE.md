# Defense Module Template

Use this template to add a new defense in `src/lab/defenses/`.

## 1) Create a new file

Create `src/lab/defenses/<your_defense>_adapter.py` and start from this:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .base_defense import BaseDefense
from .framework_registry import register_defense_plugin
from lab.eval.prediction_schema import PredictionRecord
from lab.eval.prediction_utils import adapter_stage_metadata


@dataclass
@register_defense_plugin("your_defense_name", "optional_alias")
class YourDefense(BaseDefense):
    # Parameters settable from YAML (defense.params.*) go here.
    kernel_size: int = 3
    name: str = "your_defense_name"

    def __post_init__(self) -> None:
        if self.kernel_size < 3 or self.kernel_size % 2 == 0:
            raise ValueError("kernel_size must be odd and >= 3")

    def preprocess(
        self,
        image: np.ndarray,
        **kwargs: Any,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        del kwargs
        # TODO: apply defense to image (uint8 HWC, BGR)
        defended = image.copy()
        meta = adapter_stage_metadata(
            "your_defense_name", "preprocess", kernel_size=self.kernel_size
        )
        return defended, meta

    def postprocess(
        self,
        predictions: list[PredictionRecord],
        **kwargs: Any,
    ) -> tuple[list[PredictionRecord], dict[str, Any]]:
        del kwargs
        # Most defenses are preprocess-only — leave this as identity.
        return predictions, adapter_stage_metadata(
            "your_defense_name", "postprocess", note="identity"
        )
```

## 2) How registration works

- `@register_defense_plugin("your_defense_name", "optional_alias")` makes the class discoverable.
- The registry is `src/lab/defenses/framework_registry.py` — you do not need to edit any central list.
- Plugins are loaded lazily on first use.

## 3) YAML usage example

Params go under `defense.params.*`:

```yaml
defense:
  name: your_defense_name
  params:
    kernel_size: 5
```

Or inline with `--set`:
```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=blur \
  --set defense.name=your_defense_name \
  --set defense.params.kernel_size=5
```

## 4) Expected behavior contract

**`preprocess(image, **kwargs) -> (image, metadata)`**
- Input: `image` — single `np.ndarray`, shape `(H, W, 3)`, dtype `uint8`, BGR.
- Output: cleaned image (same shape/dtype) + metadata dict from `adapter_stage_metadata`.
- Called before the YOLO model sees the image.

**`postprocess(predictions, **kwargs) -> (predictions, metadata)`**
- Input: list of `PredictionRecord` objects from YOLO.
- Output: filtered/modified predictions + metadata.
- Most defenses leave this as identity — only implement if you need to filter by confidence or boxes.

## 5) Quick validation checklist

- [ ] File created in `src/lab/defenses/` with `_adapter.py` suffix.
- [ ] Class subclasses `BaseDefense`.
- [ ] Implements both `preprocess(image, **kwargs)` and `postprocess(predictions, **kwargs)`.
- [ ] Uses `@register_defense_plugin(...)` with at least one name.
- [ ] Works with a quick smoke test:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=blur \
  --set defense.name=your_defense_name \
  --set runner.max_images=4
```

## 6) Current registered defenses

Run `scripts/sweep_and_report.py --list-plugins` for the live list. Current defenses in the auto-cycle:

| Name | Description |
|---|---|
| `c_dog` | DPC-UNet learned denoiser |
| `c_dog_ensemble` | Median blur → DPC-UNet → sharpen |
| `median_preprocess` | Median blur preprocessing |
| `jpeg_preprocess` | JPEG re-encode preprocessing |
| `bit_depth` | Bit-depth reduction preprocessing |
