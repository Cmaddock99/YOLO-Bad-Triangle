# Defense Module Template

Use this template to add a new defense in `src/lab/defenses/`.

## 1) Create a new file

Create `src/lab/defenses/<your_defense>.py` and start from this:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2

from lab.attacks.utils import iter_images
from .base import Defense, register_defense


@dataclass
@register_defense("your_defense_name", "optional_alias")
class YourDefense(Defense):
    # Parameters you want to set from YAML go here.
    kernel_size: int = 3
    name: str = "your_defense_name"

    def __post_init__(self) -> None:
        if self.kernel_size < 3 or self.kernel_size % 2 == 0:
            raise ValueError("kernel_size must be odd and >= 3")

    def apply(self, source_dir: Path, output_dir: Path, *, seed: int | None = None) -> Path:
        del seed  # Keep if defense is deterministic.
        output_dir.mkdir(parents=True, exist_ok=True)

        for image_path in iter_images(source_dir):
            image = cv2.imread(str(image_path))
            if image is None:
                continue

            # TODO: replace with your defense logic
            defended = image.copy()

            relative = image_path.relative_to(source_dir)
            out_path = output_dir / relative
            out_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_path), defended)

        return output_dir
```

## 2) How registration works

- `@register_defense("your_defense_name", "optional_alias")` makes the class discoverable.
- You do not need to edit a central list; `lab.defenses.registry` auto-imports modules in `src/lab/defenses`.

## 3) YAML usage example

Add to an experiment config:

```yaml
experiments:
  - name: my_new_defense_run
    attack: blur
    attack_params:
      kernel_size: 9
    defense: your_defense_name
    defense_params:
      kernel_size: 5
    run_name_template: my_new_defense_conf{conf_token}
```

## 4) Expected behavior contract

- Input: attacked image directory from the attack stage.
- Output: write transformed images into `output_dir`, preserving relative file paths.
- Return: `output_dir`.
- Determinism: use `seed` if defense includes randomness.

## 5) Quick validation checklist

- File exists in `src/lab/defenses/`.
- Class subclasses `Defense`.
- Has `apply(...)` method with the exact signature.
- Uses `@register_defense(...)` with at least one name.
- Works with a tiny test run:
  - `source .venv/bin/activate`
  - `python run_experiment.py attack=blur defense=median conf=0.25`
