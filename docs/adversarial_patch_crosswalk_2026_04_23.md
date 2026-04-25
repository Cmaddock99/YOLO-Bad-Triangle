# Adversarial_Patch Research Crosswalk

Date: 2026-04-23

Scope reviewed:
- `/Users/lurch/Desktop/Adversarial_Patch/docs/research/*`
- `/Users/lurch/Desktop/Adversarial_Patch/docs/notes/*`
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/*`
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/nuc_handoff/*`
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/colab_runs/*`

This file answers one question: what from `Adversarial_Patch` is directly useful to `YOLO-Bad-Triangle` right now, and what should stay in the sibling repo until it produces better artifacts.

## 1. Directly Usable Right Now

### Imported patch artifacts already fit this repo's ingestion path

`YOLO-Bad-Triangle` can already consume `Adversarial_Patch` outputs via imported-patch evaluation:

- Attack adapter: `src/lab/plugins/extra/attacks/pretrained_patch_adapter.py`
- Patch profile: `configs/pipeline_profiles.yaml` (`yolo11n_patch_eval_v1`)
- Matrix config example: `configs/patch_artifacts.yaml`

Important compatibility detail:
- `pretrained_patch_adapter.py` accepts either `patch_artifact.json` or a legacy `results.json` sidecar when the artifact is `patches/patch.png`.
- `Adversarial_Patch` currently ships `results.json` but usually does not ship `patch_artifact.json`.
- That means the external artifacts are still ingestible today.

External artifacts worth evaluating immediately:
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/yolov8n_patch_v2/patches/patch.png`
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/yolo11n_patch_v2/patches/patch.png`
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/yolo26n_patch_v2/patches/patch.png`

Prebuilt handoff configs already exist:
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/nuc_handoff/nuc_handoff_20260423T201433Z/patch_matrix_yolov8n_patch_v2.yaml`
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/nuc_handoff/nuc_handoff_20260423T201433Z/patch_matrix_yolo11n_patch_v2.yaml`
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/nuc_handoff/nuc_handoff_20260423T201433Z/patch_matrix_yolo26n_patch_v2.yaml`

These are already shaped for `scripts/run_unified.py patch-matrix`.

### The repos already share useful mechanics

There is already one explicit cross-repo borrow in-tree:
- `scripts/training/train_dpc_unet_local.py` copies the DePatch-style perturbation block erase from `Adversarial_Patch`.

That means cross-pollination is not hypothetical; the seam already exists.

## 2. Highest-Value Attack-Side Findings

### A. Larger source models should be treated as a top diagnostic, not an optional polish pass

Strongest evidence:
- `docs/notes/bayer2024_network_transferability.md`
- `docs/notes/gala2025_yolo_adversarial_patches.md`

Why it matters here:
- Bayer's main result is that `YOLOv8n/s` are weak transfer sources.
- The current `Adversarial_Patch` matrix is still dominated by nano-source experiments.
- Before any more nano-only tuning, the project needs a larger-source row.

Concrete queued artifact already prepared:
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/colab_runs/colab_runs_20260423T212740Z/handoff/colab_jobs/v8m_source_transfer_v1.json`

Best use in this repo:
- Do not reimplement patch training here.
- Let `Adversarial_Patch` finish the `yolov8m` source run.
- Import the resulting patch into `YOLO-Bad-Triangle` and evaluate it across the current defense matrix.

### B. Self-ensemble plus patch cutout is the cleanest short-path transfer upgrade

Strongest evidence:
- `docs/notes/huang2022_tsea_transfer.md`
- `docs/research/full_note_repo_benefit_refresh_2026_04_23.md`

Why it matters here:
- T-SEA is the most actionable transfer-improvement method in the reviewed corpus.
- `Adversarial_Patch` already has the ablation queue prepared.

Queued jobs:
- `v8n_transfer_baseline_v1`
- `v8n_transfer_cutout_only_v1`
- `v8n_transfer_self_ensemble_only_v1`
- `v8n_transfer_cutout_self_ensemble_v1`

Paths:
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/colab_runs/colab_runs_20260423T212740Z/handoff/colab_jobs/v8n_transfer_baseline_v1.json`
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/colab_runs/colab_runs_20260423T212740Z/handoff/colab_jobs/v8n_transfer_cutout_only_v1.json`
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/colab_runs/colab_runs_20260423T212740Z/handoff/colab_jobs/v8n_transfer_self_ensemble_only_v1.json`
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/colab_runs/colab_runs_20260423T212740Z/handoff/colab_jobs/v8n_transfer_cutout_self_ensemble_v1.json`

Best use in this repo:
- Consume the winning artifact here, not the training code.
- Make this repo the canonical defense-and-reporting surface for those imported results.

### C. YOLO26 is not a tuning problem; it is an objective mismatch problem

Strongest evidence:
- `docs/notes/wang2024_yolov10_end_to_end.md`
- `docs/research/full_note_repo_benefit_refresh_2026_04_23.md`

First-party evidence from `Adversarial_Patch` outputs:
- `yolo26n_patch_v2` (`one2many_scores`): `16.3%` suppression
- `yolo26n_patch_v3_one2one` (`one2one_scores`): `11.6%` suppression
- `yolo26n_patch_v4_logsumexp` (`one2many_scores` + logsumexp): `20.9%` suppression
- `yolo26n_patch_v2_warmstart`: `14.0%` suppression

Interpretation:
- Warm-start does not solve it.
- Pure one-to-one does not solve it.
- Logsumexp improves but does not break through.
- The next honest step is the queued hybrid objective, not more parameter nibbling.

Queued job:
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/colab_runs/colab_runs_20260423T212740Z/handoff/colab_jobs/yolo26n_hybrid_loss_v1.json`

Best use in this repo:
- Treat YOLO26 imported patches as difficult black-box stress tests for defenses.
- Keep objective research in the sibling repo until it produces a materially better artifact.

### D. Keep torso-centered and off-object patch regimes separate

Strongest evidence:
- `docs/notes/liu2019_dpatch.md`
- `docs/notes/thys2019_fooling_surveillance.md`
- `docs/research/full_note_repo_benefit_refresh_2026_04_23.md`

Why it matters here:
- This repo already supports both `largest_person_torso` and `off_object_fixed`.
- Those are different threat models and should not be summarized as one number.

Current good news:
- The imported patch path already records `placement_mode`.
- `configs/patch_artifacts.yaml` already exposes both placement modes.

Needed follow-through:
- Keep per-placement reporting explicit in summaries and dashboards.

### E. Naturalistic GAN/diffusion patches should stay a comparator lane, not the main direction

Strongest evidence:
- `docs/notes/huang2025_advreal_physical.md`
- `docs/notes/wu2024_NAPGuard.md`
- `docs/notes/hu2021_naturalistic_patch.md`
- `docs/notes/diffnat2026_AAAI.md`

Conclusion:
- Naturalistic appearance repeatedly trades away attack strength.
- Naturalistic patches are also exactly where detector-side defenses such as NAPGuard are becoming strongest.
- For `YOLO-Bad-Triangle`, these are worth benchmarking as imported artifacts, not centering as the main research bet.

## 3. Highest-Value Defense Imports For This Repo

### A. SAR-style blind segment-and-recover is the best next defense to add

Strongest evidence:
- `docs/notes/gu2025_SAR_segment_recover.md`

Why it fits `YOLO-Bad-Triangle` well:
- This repo already has the perfect upper-bound baseline in `src/lab/plugins/extra/defenses/oracle_patch_recover_adapter.py`.
- SAR is the natural non-oracle follow-up: localize patch, inpaint patch, rerun detector.
- The defense uses preprocessing hooks, which align with the repo's defense interface.

Why this should be first:
- Strong direct YOLO11 evidence exists in the paper.
- It is closer to the current repo architecture than retraining the detector head.
- It upgrades the repo from oracle inpainting to blind inpainting.

### B. Patch-class retraining is the strongest detector-integrated baseline

Strongest evidence:
- `docs/notes/ji2021_adversarial_yolo_defense.md`

Why it matters here:
- If this repo wants a detector-side retraining baseline, this is the cleanest one.
- It complements rather than replaces SAR and DPC-UNet.
- It uses attacked-object AP as the metric that matters, not patch-mask accuracy.

Best fit in this repo:
- A future learned defense or training lane, not a preprocessing adapter.

### C. NutNet is the best lightweight online defense comparator

Strongest evidence:
- `docs/notes/lin2024_nutnet_defense.md`

Why it matters here:
- It is patch-agnostic.
- It is lighter than segmentation-heavy defenses.
- It generalizes across one-stage, two-stage, and transformer detectors.

Best fit in this repo:
- As an additional preprocess defense plugin or a medium-complexity comparison baseline after SAR.

### D. Use APDE's evaluation lesson even if none of its code lands here

Strongest evidence:
- `docs/notes/shen2025_revisiting_patch_defenses_detectors.md`

Lesson to import:
- Evaluate defenses by attacked-object AP / recovery, not by whether the patch was "detected."
- Naturalistic patches and adaptive attacks reorder defense rankings.
- Unified evaluation matters more than isolated one-paper win claims.

This repo is already closer to the right metric than most patch papers; keep leaning into that.

### E. Classical preprocessing should remain the floor, not the roadmap

First-party evidence from `Adversarial_Patch`:
- `/Users/lurch/Desktop/Adversarial_Patch/outputs/defense_eval/defense_report.md`
- `jpeg` and `blur` mostly make suppression worse or destroy clean performance.
- `crop_resize` is the only classical family that sometimes helps, and even then it is highly parameter-sensitive.

Implication for this repo:
- `bit_depth`, `jpeg_preprocess`, `median_preprocess`, and `random_resize` are still worth keeping as cheap baselines.
- They are not where the main defense investment should go.

## 4. Physical And Reporting Upgrades To Borrow

### A. Physical reporting should be sector-based, not pooled into one number

Strongest evidence:
- `docs/notes/schack2024_real_world_challenges.md`
- `docs/notes/huang2025_advreal_physical.md`
- `docs/notes/xu2020_adversarial_tshirt.md`
- `docs/notes/delacruz2026_physical_attacks_surveillance.md`

Recommended reporting axes:
- distance
- yaw / angle
- lighting
- patch size / occupancy

Why it matters here:
- This repo should not quote a single physical robustness number once imported physical evaluation gets serious.

### B. Add a digital failure grid if physical runs are expensive

Strongest evidence:
- `docs/notes/schack2024_real_world_challenges.md`
- `docs/notes/bagley2025_dynamically_optimized_clusters.md`

Minimum useful grid:
- rotation
- brightness
- hue
- size / occupancy

Reason:
- This is the cheapest way to stop over-claiming physical robustness before a full physical benchmark exists.

### C. If attack-side physical training continues externally, cloth deformation is the first real upgrade

Strongest evidence:
- `docs/notes/guesmi2024_DAP_dynamic_adversarial_patch.md`
- `docs/notes/huang2025_advreal_physical.md`
- `docs/notes/bagley2025_dynamically_optimized_clusters.md`

Practical takeaway:
- Rigid rotation EoT is not enough.
- Non-rigid cloth deformation is the highest-value physical augmentation upgrade.
- Superpixel or coarse-structure regularization is worth testing after the deformation lane is in place.

This belongs mainly in `Adversarial_Patch`, then flows back here as imported artifacts.

## 5. Recommended Priorities For YOLO-Bad-Triangle

### P0 - Do now

1. Run imported patch-matrix evaluation on:
   - `yolov8n_patch_v2`
   - `yolo11n_patch_v2`
   - `yolo26n_patch_v2`
2. Add SAR-style blind patch localization + inpainting as the first new defense baseline.
3. Keep placement-mode reporting separated for torso vs off-object.

### P1 - Next

1. Add digital failure-grid reporting for imported patch artifacts.
2. Add a detector-integrated patch-class retraining baseline.
3. Add a NutNet-like lightweight blind defense comparator.

### P2 - Leave in Adversarial_Patch until the artifacts are better

1. `yolov8m` larger-source transfer training
2. T-SEA-style self-ensemble ablations
3. YOLO26 hybrid loss research
4. cloth-EoT / non-rigid physical training improvements

These are attack-generation research lanes. This repo should mainly consume their outputs and compare them against defenses.

## 6. Bottom Line

The most important things `Adversarial_Patch` gives `YOLO-Bad-Triangle` are:

1. A ready-to-ingest patch artifact stream and handoff configs
2. Strong evidence that transfer improvements should focus on source size and self-ensemble, not more nano-only tuning
3. Strong evidence that YOLO26 needs a hybrid objective, not just more hyperparameter search
4. A much stronger defense roadmap than the current classical-preprocess floor:
   - SAR first
   - patch-class retraining second
   - NutNet as the lightweight comparator
5. A cleaner reporting standard for imported patch evaluation:
   - separate placement regimes
   - sector physical reporting
   - digital failure grids

The biggest thing to avoid is spending more time on weak classical preprocessing or naturalistic-patch aesthetics before the larger-source, self-ensemble, SAR, and hybrid-loss lanes are resolved.
