# Fix Spec — YOLO-Bad-Triangle

Generated: 2026-03-26

---

## BUGS (broken, producing wrong results)

**B1 — Training signal `None vs "none"` string comparison** *(fixed in PR #45)*
`_write_training_signal()` was comparing `attack == "none"` against a Python `None` value, so baseline was never detected and the function returned early with no signal written. Every training signal in cycles 1–7 was generated from a broken baseline. Fixed in PR #45 but worth auditing what Colab was actually trained on.

**B2 — CW attack produces zero detection drop**
`initial_drop=0.0000`, `best_score=0.0000`, zero recovery across all defenses after a full tuning run. CW is a classifier-logit attack and the YOLO adaptation is targeting the wrong output layer or loss. The detection head has many anchor outputs; optimising against a single class confidence or wrong tensor is likely the cause. Needs a minimal repro: run CW on 1 image, check if raw YOLO logits change at all pre/post attack.

**B3 — jpeg_attack is a no-op**
Produces 21 smoke detections = clean baseline across two cycles. Default quality parameter is almost certainly too high (e.g. 95) to produce adversarial compression artefacts. Has been in `ALL_ATTACKS` for two full cycles consuming phase 1 characterize slots with zero signal.

**B4 — Dashboard showing `21` as baseline detections instead of `1437`**
Smoke run data is leaking into the dashboard summary card. The dashboard generator is picking up the most recent baseline run (which is the 8-image smoke run) instead of the phase 4 full-dataset baseline. `validate_baseline` result (1437 dets) should be the authoritative source for that card.

**B5 — Dashboard showing CW as strongest attack at `-0.0%`**
Downstream consequence of B2. CW's zero drop makes it appear as the "strongest" attack in the dashboard because the sort logic may not handle zero-drop edge cases. Should filter zero-drop attacks from the strongest-attack card.

**B6 — Duplicate log lines in `auto_cycle.log`**
Every log entry appears twice. The `--loop` process and something else (possibly a second instance attempt or the subprocess inheriting the log fd) are both writing to the same file. Makes the log twice as long and harder to read.

---

## DESIGN ISSUES (working but producing misleading or suboptimal results)

**D1 — Worst-attack selection uses smoke composite score, not phase 4 mAP50**
The training signal selected `eot_pgd` as worst attack in cycle 6 despite deepfool having materially lower phase 4 mAP50 (0.2184 vs 0.2529). The composite score from 8-image smoke runs is noisy and doesn't agree with full-dataset ground truth. `_write_training_signal()` should prefer phase 4 mAP50 when available, falling back to smoke composite only when phase 4 data is absent.

**D2 — Composite scoring metric is effectively just detection count**
The 50/50 avg_conf + normalised detection count composite is meant to capture both dimensions. But avg_conf is flat across all conditions (0.73–0.85 regardless of attack, defense, or image count). The metric degenerates to detection count only. Either avg_conf isn't the right signal here, or the formula needs rethinking — e.g. using recall or mAP50 directly when available.

**D3 — Smoke sample size (8 images) too small for reliable defense ranking**
jpeg_preprocess ranked top-3 in phase 2 smoke but actively hurt recovery at full scale (deepfool: -15.9% vs attack, eot_pgd: -9.7%). Eight images isn't enough to distinguish signal from noise for defense ranking. `TUNE_MAX_IMAGES` is already set separately; the smoke phase should use a larger minimum, probably 32–50 images, before committing a defense to phase 3 tuning slots.

**D4 — Attack param space exhausted at warm-start**
All three attack tuners converged at warm-start values in a single iteration for cycle 8 (deepfool eps=0.1/steps=50, eot_pgd eps=0.25/samples=8, blur k=29). The tuner has nothing to explore. Current search ranges are too narrow around carried-forward values. Needs widening: deepfool should explore eps 0.005–0.3, steps 10–200; blur kernel up to 41+; eot_pgd eot_samples up to 16, plus step_size as a new parameter.

**D5 — c_dog_ensemble consistently worse than single c_dog**
Across every smoke run and every attack in cycles 6 and 7, c_dog_ensemble produces fewer detections than single c_dog — significantly worse against deepfool (3 vs 5 dets on smoke). The ensemble combination method is introducing artefacts that outweigh any benefit from multiple passes. Should be investigated or removed from `ALL_DEFENSES` until the combination method is fixed. Running it is wasting phase 2 matrix slots.

**D6 — eot_pgd validation gap with no assigned owner**
eot_pgd is in `SLOW_ATTACKS` so NUC skips all phase 4 eot_pgd runs. The intent is for Mac to handle these. But Mac has been running CW tuning (which is producing zero signal, B2) and no mechanism assigns or tracks the eot_pgd phase 4 runs to Mac. Cycle 7 has a blank column for eot_pgd in the trend table. Needs either: (a) Mac explicitly runs `validate_eot_pgd_*` after each NUC cycle, or (b) a flag in the cycle state that marks which runs are delegated to Mac.

**D7 — No loop auto-pause on checkpoint update**
Cycle 8 started and ran phases 1–3 before PR #45 landed with the new checkpoint. The loop will complete cycle 8 on the old checkpoint, then cycle 9 will get the new one via `git pull`. There's no mechanism to detect a new checkpoint mid-cycle and pause/restart. Low priority but means one cycle is always "wasted" after each checkpoint deployment.

---

## MISSING FEATURES (gaps in observability or control)

**F1 — No per-run timeout in phase 4**
If a validate run hangs (OOM, deadlock, infinite loop), it blocks the entire phase 4 indefinitely. `subprocess.run()` in `run_single()` has no `timeout=` argument. A per-run timeout (e.g. 2× the expected time based on preset + attack) would let the cycle skip stuck runs and continue.

**F2 — No smoke→full consistency check before phase 3 tuning**
The pipeline goes straight from phase 2 smoke ranking to phase 3 tuning with no gate. A quick 50-image pre-validation of the top-ranked defenses before committing to full phase 3 tuning would catch jpeg_preprocess-style false positives early and save hours.

**F3 — warm_start carries stale `random_resize` params**
`outputs/cycle_warm_start.json` still contains `random_resize: {scale_factor_low: 0.85}` even though `random_resize` was removed from `ALL_DEFENSES`. These params will never be used but silently persist. `carry_forward_params()` should filter out params for attacks/defenses no longer in the catalogue.

**F4 — No validation that delegated Mac runs (eot_pgd) were actually completed**
When the loop archives a cycle and generates the cycle report, it doesn't check whether the eot_pgd phase 4 runs that were delegated to Mac are present. The cycle history JSON just omits them silently. Should log a warning when expected validate runs are missing from the history.

**F5 — `cycle_report.md` trend table polluted by pre-catalogue-change cycles**
Cycles 1–5 used different attacks and defenses (gaussian_blur, confidence_filter, pgd) that are no longer in the catalogue. They appear as rows with mostly `n/a` in the trend tables, obscuring the actual trend for current attacks. The report should either split pre/post catalogue sections or annotate which cycles are comparable.

---

## HOUSEKEEPING

**H1 — git commit identity misconfigured**
All NUC commits show `Committer: lurch migurch <lurch@lurch>`. `git config --global user.name` and `user.email` are not set. Not blocking anything but makes the git history harder to read and will fail any hooks that validate email format.

**H2 — jpeg_attack should be removed from `ALL_ATTACKS` until B3 is fixed**
Two cycles of zero signal. It's consuming a phase 1 characterize slot and a phase 2 matrix row (× all defenses) every cycle for no return.

**H3 — c_dog_ensemble should be removed from `ALL_DEFENSES` until D5 is investigated**
Same reasoning — two cycles of being worse than single c_dog, consuming phase 2 and potentially phase 3 slots.
