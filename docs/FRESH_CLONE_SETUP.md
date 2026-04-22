# Fresh Clone Setup

This file is the shortest accurate path from `git clone` to a working local machine.

## What `git clone` gives you

Tracked in Git:

- source code
- configs
- docs
- tests
- the COCO subset annotation JSON:
  `coco/val2017_subset500/instances_val2017_subset500.json`
- `.env.example`

Not tracked in Git:

- YOLO weights such as `yolo26n.pt`
- DPC-UNet checkpoints such as `dpc_unet_adversarial_finetuned.pt`
- COCO subset image files and label files under `coco/val2017_subset500/`
- your local `.env`

Reason: the repo intentionally keeps local model/data assets out of normal Git history.

## Recommended local layout

After setup, a working tree should look like this:

```text
YOLO-Bad-Triangle/
  yolo26n.pt
  dpc_unet_adversarial_finetuned.pt
  .env
  coco/
    val2017_subset500/
      images/
      labels/
      instances_val2017_subset500.json
```

The DPC checkpoint can live somewhere else, but putting it in the repo root is
the easiest local convention.

## Current recommended DPC checkpoint

Use:

`dpc_unet_adversarial_finetuned.pt`

If you have multiple local DPC checkpoints and just need the current default
one, start with that filename.

## Setup steps

```bash
git clone <repo-url>
cd YOLO-Bad-Triangle

python3.11 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

cp .env.example .env
```

Then place these local assets:

1. Put YOLO weights in the repo root:
   `yolo26n.pt`
2. Put the DPC checkpoint in the repo root:
   `dpc_unet_adversarial_finetuned.pt`
3. Populate the dataset directory:
   `coco/val2017_subset500/images/`
   `coco/val2017_subset500/labels/`

## Environment variables

Minimum recommended environment:

```bash
export PYTHONPATH=src
export DPC_UNET_CHECKPOINT_PATH=$PWD/dpc_unet_adversarial_finetuned.pt
```

If you keep the checkpoint outside the repo root, point `DPC_UNET_CHECKPOINT_PATH` at the absolute path instead.

## Verify the machine

For a full local setup that includes `c_dog`:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py --require-cdog
```

For a machine that only needs non-`c_dog` runs:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/check_environment.py
```

Then confirm the canonical entrypoint resolves:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --dry-run
```

And list the live plugins:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/sweep_and_report.py --list-plugins
```

## First smoke run

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=blur \
  --set runner.max_images=32 \
  --set runner.run_name=smoke_blur
```

If you want to verify `c_dog` specifically:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_unified.py run-one \
  --config configs/default.yaml \
  --set attack.name=none \
  --set defense.name=c_dog \
  --set runner.max_images=4 \
  --set runner.run_name=smoke_cdog
```

## Common failure modes

`c_dog` fails on startup:

- `DPC_UNET_CHECKPOINT_PATH` is unset or wrong
- fix: point it at `dpc_unet_adversarial_finetuned.pt`

`YOLO model missing` from `check_environment.py`:

- `yolo26n.pt` is not in the repo root
- fix: place the weights there or pass `--model-path`

`Dataset labels missing` from `check_environment.py`:

- images are present but `coco/val2017_subset500/labels/` is missing
- fix: add the matching YOLO-format label files

## Local asset persistence rule

When you bring up a new machine or replace your local workspace, make sure you
preserve or recopy:

- the repo URL and branch name
- `yolo26n.pt`
- `dpc_unet_adversarial_finetuned.pt`
- the `coco/val2017_subset500/` image + label folder

Do not assume a normal `git pull` will fetch those local assets.
