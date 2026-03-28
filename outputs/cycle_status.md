# Auto-cycle status

cycle_id   : cycle_20260327_212809
phase      : 3/4 complete
updated_at : 2026-03-27T23:21:36.912895

top_attacks  : ['deepfool', 'eot_pgd', 'blur']
top_defenses : ['jpeg_preprocess', 'bit_depth', 'median_preprocess']

best_attack_params:
  deepfool: {'attack.params.epsilon': 0.1, 'attack.params.steps': 50}
  eot_pgd: {'attack.params.epsilon': 0.25, 'attack.params.eot_samples': 8}
  blur: {'attack.params.kernel_size': 29}
best_defense_params:
  jpeg_preprocess: {'defense.params.quality': 60}
  bit_depth: {'defense.params.bits': 5}
  median_preprocess: {'defense.params.kernel_size': 5}

P1=True  P2=True  P3=True  P4=False

*** PARTIAL — phases 4–4 still pending ***
