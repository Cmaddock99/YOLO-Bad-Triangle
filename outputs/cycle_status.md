# Auto-cycle status

cycle_id   : cycle_20260328_064948
phase      : 3/4 complete
updated_at : 2026-03-28T08:42:54.739208

top_attacks  : ['deepfool', 'blur', 'eot_pgd']
top_defenses : ['bit_depth', 'jpeg_preprocess', 'median_preprocess', 'c_dog']

best_attack_params:
  deepfool: {'attack.params.epsilon': 0.1, 'attack.params.steps': 50}
  blur: {'attack.params.kernel_size': 29}
  eot_pgd: {'attack.params.epsilon': 0.25, 'attack.params.alpha': 0.0015, 'attack.params.eot_samples': 8}
best_defense_params:
  bit_depth: {'defense.params.bits': 6}
  jpeg_preprocess: {'defense.params.quality': 75}
  median_preprocess: {'defense.params.kernel_size': 9}
  c_dog: {'defense.params.timestep': 50.0, 'defense.params.sharpen_alpha': 0.0}

P1=True  P2=True  P3=True  P4=False

*** PARTIAL — phases 4–4 still pending ***
