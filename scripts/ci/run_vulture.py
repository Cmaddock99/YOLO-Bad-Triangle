#!/usr/bin/env python3
"""Run vulture dead-code scan with a whitelist for the plugin system.

Plugin adapter classes and their bootstrap constants are dynamically loaded by
AdapterLoader and therefore appear unused to static analysis. This script generates
a whitelist that suppresses those false positives before running vulture.

Exit code: always 0 — this scan is informational, not a hard gate.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Vulture whitelist entries for the dynamic plugin system.
# AdapterLoader discovers adapters by name at runtime; none of them appear
# in static import chains.
_WHITELIST = """\
from lab.plugins.core.attacks.blur_adapter import BlurAttackAdapter
from lab.plugins.core.attacks.deepfool_adapter import DeepFoolAttackAdapter
from lab.plugins.core.attacks.fgsm_adapter import FGSMAttackAdapter
from lab.plugins.core.attacks.pgd_adapter import PGDAttackAdapter
from lab.plugins.core.attacks.square_adapter import SquareAttackAdapter
from lab.plugins.core.defenses.none_adapter import NoneDefenseAdapter
from lab.plugins.core.defenses.preprocess_bitdepth_adapter import BitDepthDefenseAdapter
from lab.plugins.core.defenses.preprocess_jpeg_adapter import JPEGDefenseAdapter
from lab.plugins.core.defenses.preprocess_median_blur_adapter import MedianBlurDefenseAdapter
from lab.plugins.core.models.yolo_adapter import YOLOModelAdapter
from lab.plugins.extra.attacks.cw_adapter import CWAttackAdapter
from lab.plugins.extra.attacks.pretrained_patch_adapter import PretrainedPatchAttackAdapter
from lab.plugins.extra.defenses.blind_patch_recover_adapter import BlindPatchRecoverAdapter
from lab.plugins.extra.defenses.confidence_filter_adapter import ConfidenceFilterAdapter
from lab.plugins.extra.defenses.oracle_patch_recover_adapter import OraclePatchRecoverAdapter
from lab.plugins.extra.defenses.preprocess_dpc_unet_adapter import CDogDefenseAdapter
from lab.plugins.extra.defenses.preprocess_dpc_unet_adapter import EnsembleCDogDefenseAdapter
from lab.plugins.extra.defenses.preprocess_random_resize_adapter import RandomResizeDefenseAdapter

# Bootstrap module lists are read by AdapterLoader, not by import
_.ADAPTER_MODULES
"""


def main() -> int:
    python_bin = sys.executable

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", prefix="vulture_whitelist_", delete=False
    ) as f:
        f.write(_WHITELIST)
        whitelist_path = f.name

    print("Running vulture dead-code scan (informational — not a hard gate)...")
    result = subprocess.run(
        [
            python_bin, "-m", "vulture",
            "src", "scripts",
            whitelist_path,
            "--min-confidence", "70",
        ],
        cwd=REPO_ROOT,
        capture_output=False,
    )

    Path(whitelist_path).unlink(missing_ok=True)

    if result.returncode == 0:
        print("vulture: no dead code found.")
    else:
        print(
            "\nvulture: potential dead code found (see above). "
            "Review before acting — plugin adapters should be whitelisted."
        )

    return 0  # informational — always exits 0


if __name__ == "__main__":
    raise SystemExit(main())
