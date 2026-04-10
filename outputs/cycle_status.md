# Auto-cycle status

cycle_id   : cycle_20260407_193440
phase      : 4/4 complete
updated_at : 2026-04-09T20:53:59.937635

top_attacks  : ['square', 'deepfool', 'dispersion_reduction']
top_defenses : ['jpeg_preprocess', 'median_preprocess', 'bit_depth', 'c_dog']

best_attack_params:
  square: {'attack.params.eps': 0.3, 'attack.params.n_queries': 450}
  deepfool: {'attack.params.epsilon': 0.07625, 'attack.params.steps': 200}
  dispersion_reduction: {'attack.params.epsilon': 0.15, 'attack.params.steps': 20}
best_defense_params:
  jpeg_preprocess: {'defense.params.quality': 40}
  median_preprocess: {'defense.params.kernel_size': 5}
  bit_depth: {'defense.params.bits': 3}
  c_dog: {'defense.params.timestep': 10.0, 'defense.params.sharpen_alpha': 0.0}

P1=True  P2=True  P3=True  P4=True

*** CYCLE COMPLETE ***
