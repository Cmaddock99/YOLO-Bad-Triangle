# AGENTS.md

## Cursor Cloud specific instructions

### Overview

YOLO-Bad-Triangle is a Python 3.11 adversarial-ML experiment lab for YOLO object detection. It is a fully self-contained local application with no external services (no Docker, no databases, no web servers). See `README.md` for canonical workflows and `CLAUDE.md` for project-wide rules.

### Environment

- **Python 3.11** is required (enforced by `scripts/check_environment.py`). The VM has it installed via `deadsnakes/ppa`.
- Virtual environment lives at `.venv/`. Activate with `source .venv/bin/activate`.
- `PYTHONPATH` must include both `src` (for the `lab` package) and `.` (for `scripts` module imports in tests). Use `PYTHONPATH=src:.` or export it.

### Quality gates

```bash
source .venv/bin/activate
.venv/bin/ruff check src tests scripts      # lint
.venv/bin/mypy                               # type check (scoped to eval/reporting/runners)
PYTHONPATH=src:. .venv/bin/pytest -q          # unit tests (integration tests skipped by default)
```

### Running experiments

Before running an experiment, create a demo image if using `ci_demo.yaml`:

```bash
PYTHONPATH=src python -c "
from pathlib import Path; import cv2, numpy as np
out = Path('outputs/ci_demo/images'); out.mkdir(parents=True, exist_ok=True)
cv2.imwrite(str(out / 'ci.jpg'), np.full((128,128,3), 127, dtype=np.uint8))"
```

Then run:

```bash
PYTHONPATH=src python scripts/run_unified.py run-one --config configs/ci_demo.yaml --dry-run
PYTHONPATH=src python scripts/run_unified.py run-one --config configs/ci_demo.yaml
```

### Non-obvious gotchas

- **PYTHONPATH for tests**: `pyproject.toml` sets `pythonpath = ["src"]`, but several tests do `from scripts import ...` which requires the repo root on `PYTHONPATH`. Always use `PYTHONPATH=src:.` when running pytest locally. CI works because GitHub Actions' working directory is implicitly on the path.
- **COCO dataset not required for basic runs**: The `check_environment.py` script reports "Dataset missing" for `coco/val2017_subset500/`, but the CI demo config uses `outputs/ci_demo/images` instead. Full validation sweeps do need the COCO subset.
- **YOLO weights auto-download**: Model weights (e.g. `yolo26n.pt`) are automatically downloaded by ultralytics on first use. No manual download needed.
- **No GPU required**: CPU mode works for all experiments. GPU (CUDA/MPS) only needed for performance in large sweeps.
