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
  - `python scripts/run_experiment.py`
