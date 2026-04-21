from __future__ import annotations

import importlib
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Wrappers under scripts/*.py that re-publish a moved implementation via
# `sys.modules[__name__] = _load_module()`. Add new entries here when adding
# a new wrapper; the meta-test below guards against omissions.
WRAPPER_ALIASES: tuple[tuple[str, str], ...] = (
    ("scripts.auto_cycle", "scripts.automation.auto_cycle"),
    ("scripts.cleanup_stale_runs", "scripts.automation.cleanup_stale_runs"),
    ("scripts.watch_cycle", "scripts.automation.watch_cycle"),
    ("scripts.run_demo", "scripts.demo.run_demo"),
    ("scripts.evaluate_checkpoint", "scripts.training.evaluate_checkpoint"),
    ("scripts.export_training_data", "scripts.training.export_training_data"),
    ("scripts.run_training_ritual", "scripts.training.run_training_ritual"),
    ("scripts.train_dpc_unet_local", "scripts.training.train_dpc_unet_local"),
    ("scripts.train_dpc_unet_feature_loss", "scripts.training.train_dpc_unet_feature_loss"),
    ("scripts.train_from_signal", "scripts.training.train_from_signal"),
    ("scripts.print_summary", "scripts.reporting.print_summary"),
    ("scripts.generate_auto_summary", "scripts.reporting.generate_auto_summary"),
    ("scripts.generate_cycle_report", "scripts.reporting.generate_cycle_report"),
    ("scripts.generate_dashboard", "scripts.reporting.generate_dashboard"),
    ("scripts.generate_failure_gallery", "scripts.reporting.generate_failure_gallery"),
    ("scripts.generate_framework_report", "scripts.reporting.generate_framework_report"),
    ("scripts.generate_team_summary", "scripts.reporting.generate_team_summary"),
)

# Old flat adapter paths under src/lab/{attacks,defenses,models}/ that
# re-publish their plugin-tree implementation via the same sys.modules pattern.
ADAPTER_SHIM_ALIASES: tuple[tuple[str, str], ...] = (
    ("lab.attacks.blur_adapter", "lab.plugins.core.attacks.blur_adapter"),
    ("lab.attacks.cw_adapter", "lab.plugins.extra.attacks.cw_adapter"),
    ("lab.attacks.deepfool_adapter", "lab.plugins.core.attacks.deepfool_adapter"),
    ("lab.attacks.dispersion_reduction_adapter", "lab.plugins.core.attacks.dispersion_reduction_adapter"),
    ("lab.attacks.eot_pgd_adapter", "lab.plugins.core.attacks.eot_pgd_adapter"),
    ("lab.attacks.fgsm_adapter", "lab.plugins.core.attacks.fgsm_adapter"),
    ("lab.attacks.fgsm_center_mask_adapter", "lab.plugins.extra.attacks.fgsm_center_mask_adapter"),
    ("lab.attacks.fgsm_edge_mask_adapter", "lab.plugins.extra.attacks.fgsm_edge_mask_adapter"),
    ("lab.attacks.jpeg_attack_adapter", "lab.plugins.extra.attacks.jpeg_attack_adapter"),
    ("lab.attacks.pgd_adapter", "lab.plugins.core.attacks.pgd_adapter"),
    ("lab.attacks.pretrained_patch_adapter", "lab.plugins.extra.attacks.pretrained_patch_adapter"),
    ("lab.attacks.square_adapter", "lab.plugins.core.attacks.square_adapter"),
    ("lab.defenses.confidence_filter_adapter", "lab.plugins.extra.defenses.confidence_filter_adapter"),
    ("lab.defenses.none_adapter", "lab.plugins.core.defenses.none_adapter"),
    ("lab.defenses.preprocess_bitdepth_adapter", "lab.plugins.core.defenses.preprocess_bitdepth_adapter"),
    ("lab.defenses.preprocess_dpc_unet_adapter", "lab.plugins.extra.defenses.preprocess_dpc_unet_adapter"),
    ("lab.defenses.preprocess_jpeg_adapter", "lab.plugins.core.defenses.preprocess_jpeg_adapter"),
    ("lab.defenses.preprocess_median_blur_adapter", "lab.plugins.core.defenses.preprocess_median_blur_adapter"),
    ("lab.defenses.preprocess_random_resize_adapter", "lab.plugins.extra.defenses.preprocess_random_resize_adapter"),
    ("lab.models.torchvision_adapter", "lab.plugins.extra.models.torchvision_adapter"),
    ("lab.models.yolo_adapter", "lab.plugins.core.models.yolo_adapter"),
)

_SHIM_TARGET_RE = re.compile(r'import_module\(["\']([\w.]+)["\']\)')


def _discover_wrapper_scripts() -> dict[str, str]:
    """Return {old_module: new_module} for every scripts/*.py that uses the
    sys.modules-replacement compat pattern.
    """
    found: dict[str, str] = {}
    for path in sorted((REPO_ROOT / "scripts").glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if "sys.modules[__name__] = _load_module()" not in text:
            continue
        match = _SHIM_TARGET_RE.search(text)
        if match is None:
            continue
        found[f"scripts.{path.stem}"] = match.group(1)
    return found


def _discover_adapter_shims() -> dict[str, str]:
    """Return {old_module: new_module} for every flat adapter shim under
    src/lab/{attacks,defenses,models}/ that uses the sys.modules pattern.
    """
    found: dict[str, str] = {}
    for subdir in ("attacks", "defenses", "models"):
        for path in sorted((REPO_ROOT / "src" / "lab" / subdir).glob("*_adapter.py")):
            text = path.read_text(encoding="utf-8")
            if "sys.modules[__name__] = import_module(" not in text:
                continue
            match = _SHIM_TARGET_RE.search(text)
            if match is None:
                continue
            found[f"lab.{subdir}.{path.stem}"] = match.group(1)
    return found


class RepoStructureCompatTest(unittest.TestCase):
    def test_root_wrappers_alias_to_moved_modules(self) -> None:
        for old_name, new_name in WRAPPER_ALIASES:
            with self.subTest(old_name=old_name):
                old_mod = importlib.import_module(old_name)
                new_mod = importlib.import_module(new_name)
                self.assertIs(old_mod, new_mod)

    def test_old_adapter_shims_alias_to_moved_modules(self) -> None:
        for old_name, new_name in ADAPTER_SHIM_ALIASES:
            with self.subTest(old_name=old_name):
                old_mod = importlib.import_module(old_name)
                new_mod = importlib.import_module(new_name)
                self.assertIs(old_mod, new_mod)

    def test_reporting_umbrella_still_exports_render_markdown_report(self) -> None:
        from lab.reporting import render_markdown_report
        from lab.reporting.framework import render_markdown_report as framework_render_markdown_report

        self.assertIs(render_markdown_report, framework_render_markdown_report)

    def test_wrapper_alias_table_matches_filesystem(self) -> None:
        # Any script that ships the wrapper pattern must appear in
        # WRAPPER_ALIASES, otherwise the alias contract goes untested.
        discovered = _discover_wrapper_scripts()
        declared = dict(WRAPPER_ALIASES)
        self.assertEqual(
            declared,
            discovered,
            msg=(
                "WRAPPER_ALIASES drift vs scripts/*.py. Update the table when "
                "adding or removing a wrapper script."
            ),
        )

    def test_adapter_shim_alias_table_matches_filesystem(self) -> None:
        discovered = _discover_adapter_shims()
        declared = dict(ADAPTER_SHIM_ALIASES)
        self.assertEqual(
            declared,
            discovered,
            msg=(
                "ADAPTER_SHIM_ALIASES drift vs src/lab/{attacks,defenses,models}/. "
                "Update the table when adding or removing a flat-path shim."
            ),
        )


if __name__ == "__main__":
    unittest.main()
