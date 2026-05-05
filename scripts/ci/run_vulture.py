#!/usr/bin/env python3
"""Run vulture dead-code scan with a whitelist for the plugin system.

Plugin adapter classes and their bootstrap constants are dynamically loaded by
AdapterLoader and therefore appear unused to static analysis. This script generates
a whitelist that suppresses those false positives before running vulture.

Exit code mapping:
- 0: no dead code found
- 3: dead code found (reported, but treated as informational)
- 1/2/other non-zero: execution/setup failure and must fail the lane
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_EXIT_OK = 0
_EXIT_INVALID_INPUT = 1
_EXIT_INVALID_ARGUMENTS = 2
_EXIT_DEAD_CODE_FOUND = 3

# Vulture whitelist entries for the dynamic plugin system.
# AdapterLoader discovers adapters by name at runtime; none of them appear
# in static import chains.
_WHITELIST = """\
from lab.plugins.core.attacks.blur_adapter import BlurAttackAdapter
BlurAttackAdapter
from lab.plugins.core.attacks.deepfool_adapter import DeepFoolAttackAdapter
DeepFoolAttackAdapter
from lab.plugins.core.attacks.fgsm_adapter import FGSMAttackAdapter
FGSMAttackAdapter
from lab.plugins.core.attacks.pgd_adapter import PGDAttackAdapter
PGDAttackAdapter
from lab.plugins.core.attacks.square_adapter import SquareAttackAdapter
SquareAttackAdapter
from lab.plugins.core.defenses.none_adapter import NoneDefenseAdapter
NoneDefenseAdapter
from lab.plugins.core.defenses.preprocess_bitdepth_adapter import BitDepthDefenseAdapter
BitDepthDefenseAdapter
from lab.plugins.core.defenses.preprocess_jpeg_adapter import JPEGDefenseAdapter
JPEGDefenseAdapter
from lab.plugins.core.defenses.preprocess_median_blur_adapter import MedianBlurDefenseAdapter
MedianBlurDefenseAdapter
from lab.plugins.core.models.yolo_adapter import YOLOModelAdapter
YOLOModelAdapter
from lab.plugins.extra.attacks.cw_adapter import CWAttackAdapter
CWAttackAdapter
from lab.plugins.extra.attacks.pretrained_patch_adapter import PretrainedPatchAttackAdapter
PretrainedPatchAttackAdapter
from lab.plugins.extra.defenses.blind_patch_recover_adapter import BlindPatchRecoverAdapter
BlindPatchRecoverAdapter
from lab.plugins.extra.defenses.confidence_filter_adapter import ConfidenceFilterAdapter
ConfidenceFilterAdapter
from lab.plugins.extra.defenses.oracle_patch_recover_adapter import OraclePatchRecoverAdapter
OraclePatchRecoverAdapter
from lab.plugins.extra.defenses.preprocess_dpc_unet_adapter import CDogDefenseAdapter
CDogDefenseAdapter
from lab.plugins.extra.defenses.preprocess_dpc_unet_adapter import EnsembleCDogDefenseAdapter
EnsembleCDogDefenseAdapter
from lab.plugins.extra.defenses.preprocess_random_resize_adapter import RandomResizeDefenseAdapter
RandomResizeDefenseAdapter

# Bootstrap module lists are read by AdapterLoader, not by import
from lab.plugins.core.attacks.bootstrap_adapter import ADAPTER_MODULES as CORE_ATTACK_MODULES
CORE_ATTACK_MODULES
from lab.plugins.core.defenses.bootstrap_adapter import ADAPTER_MODULES as CORE_DEFENSE_MODULES
CORE_DEFENSE_MODULES
from lab.plugins.core.models.bootstrap_adapter import ADAPTER_MODULES as CORE_MODEL_MODULES
CORE_MODEL_MODULES
from lab.plugins.extra.attacks.bootstrap_adapter import ADAPTER_MODULES as EXTRA_ATTACK_MODULES
EXTRA_ATTACK_MODULES
from lab.plugins.extra.defenses.bootstrap_adapter import ADAPTER_MODULES as EXTRA_DEFENSE_MODULES
EXTRA_DEFENSE_MODULES
from lab.plugins.extra.models.bootstrap_adapter import ADAPTER_MODULES as EXTRA_MODEL_MODULES
EXTRA_MODEL_MODULES
"""


def main() -> int:
    python_bin = sys.executable
    whitelist_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", prefix="vulture_whitelist_", delete=False
        ) as f:
            f.write(_WHITELIST)
            whitelist_path = Path(f.name)

        print("Running vulture dead-code scan (informational — not a hard gate)...")
        try:
            result = subprocess.run(
                [
                    python_bin,
                    "-m",
                    "vulture",
                    "src",
                    "scripts",
                    str(whitelist_path),
                    "--min-confidence",
                    "70",
                ],
                cwd=REPO_ROOT,
                capture_output=False,
            )
        except OSError as exc:
            print(
                "\nvulture: failed to launch vulture. "
                f"This is an execution/setup error, not a dead-code report: {exc}"
            )
            return _EXIT_INVALID_INPUT

        if result.returncode == _EXIT_OK:
            print("vulture: no dead code found.")
            return _EXIT_OK

        if result.returncode == _EXIT_DEAD_CODE_FOUND:
            print(
                "\nvulture: potential dead code found (see above). "
                "Review before acting — plugin adapters should be whitelisted."
            )
            return _EXIT_OK

        if result.returncode in {_EXIT_INVALID_INPUT, _EXIT_INVALID_ARGUMENTS}:
            print(
                "\nvulture: execution/setup error while running the scan "
                f"(exit code {result.returncode}). This is not a dead-code report."
            )
            return result.returncode

        print(
            "\nvulture: unexpected non-zero exit "
            f"({result.returncode}). This is an execution/setup error, not a dead-code report."
        )
        return result.returncode
    finally:
        if whitelist_path is not None:
            whitelist_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
