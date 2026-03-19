# Attack Module Template

Use this template to add a new attack in `src/lab/attacks/`.

## 1) Create a new file

Create `src/lab/attacks/<your_attack>.py` and start from this:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .base import Attack, register_attack
from .utils import iter_images


@dataclass
@register_attack("your_attack_name", "optional_alias")
class YourAttack(Attack):
    # Parameters you want to set from YAML go here.
    strength: float = 0.1
    name: str = "your_attack_name"

    def __post_init__(self) -> None:
        if self.strength <= 0:
            raise ValueError("strength must be > 0")

    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        rng = np.random.default_rng(seed)
        output_dir.mkdir(parents=True, exist_ok=True)

        for image_path in iter_images(source_dir):
            image = cv2.imread(str(image_path))
            if image is None:
                continue

            # TODO: replace with your attack logic
            attacked = image.copy()

            relative = image_path.relative_to(source_dir)
            out_path = output_dir / relative
            out_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_path), attacked)

        return output_dir
```

## 2) How registration works

- `@register_attack("your_attack_name", "optional_alias")` makes the class discoverable.
- You do not need to edit a central list; `lab.attacks.registry` auto-imports modules in `src/lab/attacks`.

## 3) YAML usage example

Add to an experiment config:

```yaml
experiments:
  - name: my_new_attack_run
    attack: your_attack_name
    attack_params:
      strength: 0.2
    defense: none
    run_name_template: my_new_attack_conf{conf_token}
```

## 4) Expected behavior contract

- Input: `source_dir` containing images.
- Output: write transformed images into `output_dir`, preserving relative file paths.
- Return: `output_dir`.
- Determinism: use `seed` for any randomness.

## 5) Quick validation checklist

- File exists in `src/lab/attacks/`.
- Class subclasses `Attack`.
- Has `apply(...)` method with the exact signature.
- Uses `@register_attack(...)` with at least one name.
- Works with a tiny test run:
  - `source .venv/bin/activate`
  - `python run_experiment.py attack=blur conf=0.25`

## 6) Current variant examples (strength + spatial behavior)

- `fgsm_center_mask`
  - Effect: medium-strength FGSM focused on central region.
  - Params: `epsilon=0.008`, `radius_fraction=0.35`.
- `fgsm_edge_mask`
  - Effect: medium-strength FGSM focused on edges/textures.
  - Params: `epsilon=0.008`, `edge_threshold=40`, `edge_dilate=1`.
- `blur_anisotropic`
  - Effect: directional blur (strong horizontal smear, weak vertical).
  - Params: `kernel_x=17`, `kernel_y=3`, `sigma_x=0.0`, `sigma_y=0.0`.
- `noise_blockwise`
  - Effect: blockwise spatially-varying noise (medium-strong).
  - Params: `stddev=10.0`, `block_size=32`, `scale_jitter=0.5`.
- `deepfool_band_limited`
  - Effect: structured stripe-limited iterative perturbation (strong).
  - Params: `epsilon=0.9`, `steps=3`, `stripe_period=32`, `stripe_width=12`, `blur_kernel=7`.

Example command:

- `./.venv/bin/python run_experiment.py attack=fgsm_edge_mask attack.edge_threshold=35 conf=0.25 validate=true`
