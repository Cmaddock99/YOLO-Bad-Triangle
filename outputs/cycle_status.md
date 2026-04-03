# Auto-cycle status

cycle_id   : cycle_20260402_133001
phase      : 3/4 complete
updated_at : 2026-04-03T03:53:41.274687

top_attacks  : ['square', 'deepfool', 'dispersion_reduction']
top_defenses : ['jpeg_preprocess', 'bit_depth', 'c_dog']

best_attack_params:
  square: {'attack.params.eps': 0.3, 'attack.params.n_queries': 450}
  deepfool: {'attack.params.epsilon': 0.1, 'attack.params.steps': 50}
  dispersion_reduction: {'attack.params.epsilon': 0.15, 'attack.params.steps': 20}
best_defense_params:
  jpeg_preprocess: {'defense.params.quality': 40}
  bit_depth: {'defense.params.bits': 5}
  c_dog: {'defense.params.timestep': 25.0, 'defense.params.sharpen_alpha': 0.55}

P1=True  P2=True  P3=True  P4=False

*** PARTIAL — phases 4–4 still pending ***
