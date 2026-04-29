# Pre-Presentation Messaging Notes

Use this note to stay accurate under questioning. The goal is not to sound perfect. The goal is to sound precise and honest.

## Do Not Say

- Do not say “the repo is fully green” unless the quality gate and the scoped workflows really are green on the frozen environment.
- Do not say “training is part of the canonical profile flow.” It is not. The shipped profiles currently mark learned-defense training as non-trainable.
- Do not say “we run auto-cycle or training live in the demo.” The plan is artifact-led.
- Do not say “patch evaluation is the same as the gradient attack workflow.” It is a separate imported-artifact workflow.
- Do not say “the model is being retrained” when describing the training story. The training path is for the learned preprocessing defense, not YOLO itself.
- Do not hide historical repo issues if asked. Mention them clearly and explain what was fixed versus what remained policy-limited.

## Do Say

- Say “the core runtime is unified: config/profile -> attack -> defense preprocess -> model -> defense postprocess -> metrics/reporting.”
- Say “the repo uses structured artifacts and provenance so runs are reproducible and comparable.”
- Say “profiles define the canonical experiment surface, and manual workflows exist outside that policy boundary.”
- Say “the learned-defense story is currently presented as a manual/profileless workflow because profile policy intentionally blocks trainable learned-defense operation.”
- Say “the demo is artifact-led on purpose so the presentation depends on frozen evidence, not on long-running live jobs.”
- Say “imported patch evaluation is a separate benchmarking path using `patch-matrix` and the patch profile.”

## Known Limitations Slide: Required Topics

Include these topics explicitly:

- dependency contract mismatch existed between `requirements.txt` and the environment checker
- dashboard typing issue blocked the quality gate until repaired
- learned-defense training is not enabled inside the shipped canonical profiles
- any workflow that still requires manual execution or manual promotion

## One Safe High-Level Summary

Use this when you need one accurate short framing statement:

> The repo’s presentation-ready story is built around frozen artifacts from four paths: the core benchmark demo, auto-cycle automation, manual learned-defense retraining with A/B gating, and imported patch evaluation. The live portion is intentionally minimal so the claims rely on reproducible outputs instead of risky long-running runtime behavior.
