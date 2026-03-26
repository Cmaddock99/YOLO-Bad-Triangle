# Auto-cycle status

cycle_id   : cycle_20260324_094635
phase      : 4/4 complete
updated_at : 2026-03-25T22:38:49.664521

top_attacks  : ['deepfool', 'eot_pgd', 'blur']
top_defenses : ['jpeg_preprocess', 'bit_depth', 'random_resize']

best_attack_params:
  deepfool: {'attack.params.epsilon': 0.1, 'attack.params.steps': 50}
  eot_pgd: {'attack.params.epsilon': 0.25, 'attack.params.eot_samples': 8}
  blur: {'attack.params.kernel_size': 29}
best_defense_params:
  jpeg_preprocess: {'defense.params.quality': 60}
  bit_depth: {'defense.params.bits': 5}
  random_resize: {'defense.params.scale_factor_low': 0.85}

P1=True  P2=True  P3=True  P4=True

*** CYCLE COMPLETE ***
