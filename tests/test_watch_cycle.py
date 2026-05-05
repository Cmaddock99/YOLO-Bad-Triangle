from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

# watch_cycle.py depends on `rich` for its TUI output. Stub it out so tests
# can exercise the pure-logic helpers without requiring the package.
from unittest.mock import MagicMock  # noqa: E402

for _mod in (
    "rich", "rich.box", "rich.columns", "rich.console", "rich.live",
    "rich.panel", "rich.table", "rich.text", "rich.theme",
):
    if _mod not in sys.modules:
        _m = types.ModuleType(_mod)
        # Allow any attribute access on the stub
        _m.__getattr__ = lambda name, _m=_m: MagicMock()  # type: ignore[attr-defined]
        sys.modules[_mod] = _m
        # Patch common rich names that are imported directly
        for _name in ("Console", "Group", "Live", "Panel", "Table", "Text",
                       "Theme", "Columns", "box", "SIMPLE", "ROUNDED"):
            setattr(_m, _name, MagicMock)

from scripts import watch_cycle  # noqa: E402


class WatchCycleTest(unittest.TestCase):
    def test_expected_validate_runs_expand_attack_defense_grid(self) -> None:
        state = {
            "top_attacks": ["square", "deepfool"],
            "top_defenses": ["jpeg_preprocess", "c_dog"],
        }

        self.assertEqual(
            watch_cycle._expected_validate_runs(state),
            [
                "validate_baseline",
                "validate_atk_square",
                "validate_atk_deepfool",
                "validate_square_jpeg_preprocess",
                "validate_square_c_dog",
                "validate_deepfool_jpeg_preprocess",
                "validate_deepfool_c_dog",
            ],
        )

    def test_parse_progress_snapshot_reads_latest_run_and_eta(self) -> None:
        log_text = """
2026-04-08T23:42:17 [run-unified] INFO: $ python scripts/run_experiment.py --set runner.run_name=validate_atk_square
[2026-04-08 17:27:48]   run: validate_atk_deepfool
\rPreparing images:   9%|▉         | 45/500 [35:55<5:33:19, 43.95s/img]
"""

        progress = watch_cycle._parse_progress_snapshot(log_text)

        self.assertIsNotNone(progress)
        assert progress is not None
        self.assertEqual(progress["run_name"], "validate_atk_deepfool")
        self.assertEqual(progress["done"], 45)
        self.assertEqual(progress["total"], 500)
        self.assertEqual(progress["remaining"], "5:33:19")
        self.assertEqual(progress["elapsed"], "35:55")
        self.assertAlmostEqual(progress["secs_per_image"], 43.95)

    def test_parse_process_snapshot_prefers_worker_over_loop(self) -> None:
        repo_root = Path("/home/lurch/YOLO-Bad-Triangle")
        ps_output = """
563684 01:00  0.1  0.2 ./.venv/bin/python scripts/auto_cycle.py --loop
704341 37:03 199.0  7.9 /home/lurch/YOLO-Bad-Triangle/.venv/bin/python /home/lurch/YOLO-Bad-Triangle/src/lab/runners/run_experiment.py --config configs/default.yaml --set attack.name=deepfool --set defense.name=none --set runner.run_name=validate_atk_deepfool
"""

        process = watch_cycle._parse_process_snapshot(ps_output, repo_root)

        self.assertIsNotNone(process)
        assert process is not None
        self.assertEqual(process["kind"], "run_experiment")
        self.assertEqual(process["run_name"], "validate_atk_deepfool")
        self.assertEqual(process["attack"], "deepfool")
        self.assertEqual(process["defense"], "none")

    def test_parse_process_snapshot_accepts_idle_auto_cycle_without_repo_path(self) -> None:
        repo_root = Path("/home/lurch/YOLO-Bad-Triangle")
        ps_output = "563684 01:00  0.1  0.2 ./.venv/bin/python scripts/auto_cycle.py --loop\n"

        process = watch_cycle._parse_process_snapshot(ps_output, repo_root)

        self.assertIsNotNone(process)
        assert process is not None
        self.assertEqual(process["kind"], "auto_cycle")
        self.assertIsNone(process["run_name"])

    def test_parse_thermals_filters_invalid_temperature(self) -> None:
        sensors_output = """
iwlwifi_1-virtual-0
Adapter: Virtual device
temp1:        +59.0°C

pch_skylake-virtual-0
Adapter: Virtual device
temp1:        +74.5°C

acpitz-acpi-0
Adapter: ACPI interface
temp1:       -263.2°C
"""

        thermals = watch_cycle._parse_thermals(sensors_output)

        self.assertEqual(len(thermals), 2)
        self.assertEqual(thermals[0]["chip"], "pch_skylake-virtual-0")
        self.assertEqual(thermals[0]["temp_c"], 74.5)
        self.assertEqual(thermals[1]["chip"], "iwlwifi_1-virtual-0")
        self.assertEqual(thermals[1]["temp_c"], 59.0)


if __name__ == "__main__":
    unittest.main()
