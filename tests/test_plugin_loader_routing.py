from __future__ import annotations

import unittest

from lab.attacks import framework_registry as attack_registry
from lab.defenses import framework_registry as defense_registry
from lab.models import framework_registry as model_registry
from lab.plugins.core.attacks import bootstrap_adapter as core_attack_bootstrap
from lab.plugins.core.defenses import bootstrap_adapter as core_defense_bootstrap
from lab.plugins.core.models import bootstrap_adapter as core_model_bootstrap
from lab.plugins.extra.attacks import bootstrap_adapter as extra_attack_bootstrap
from lab.plugins.extra.defenses import bootstrap_adapter as extra_defense_bootstrap
from lab.plugins.extra.models import bootstrap_adapter as extra_model_bootstrap


class PluginLoaderRoutingTest(unittest.TestCase):
    def test_attack_registry_loader_uses_core_and_extra_bootstrap_packages(self) -> None:
        self.assertEqual(
            attack_registry._loader.package_names,
            ("lab.plugins.core.attacks", "lab.plugins.extra.attacks"),
        )
        self.assertEqual(
            attack_registry._loader.core_package_names,
            ("lab.plugins.core.attacks",),
        )
        self.assertEqual(
            attack_registry._loader.extra_package_names,
            ("lab.plugins.extra.attacks",),
        )

    def test_defense_registry_loader_uses_core_and_extra_bootstrap_packages(self) -> None:
        self.assertEqual(
            defense_registry._loader.package_names,
            ("lab.plugins.core.defenses", "lab.plugins.extra.defenses"),
        )
        self.assertEqual(
            defense_registry._loader.core_package_names,
            ("lab.plugins.core.defenses",),
        )
        self.assertEqual(
            defense_registry._loader.extra_package_names,
            ("lab.plugins.extra.defenses",),
        )

    def test_model_registry_loader_uses_core_and_extra_bootstrap_packages(self) -> None:
        self.assertEqual(
            model_registry._loader.package_names,
            ("lab.plugins.core.models", "lab.plugins.extra.models"),
        )
        self.assertEqual(
            model_registry._loader.core_package_names,
            ("lab.plugins.core.models",),
        )
        self.assertEqual(
            model_registry._loader.extra_package_names,
            ("lab.plugins.extra.models",),
        )

    def test_core_attack_bootstrap_modules_match_contract(self) -> None:
        self.assertEqual(
            core_attack_bootstrap.ADAPTER_MODULES,
            (
                "lab.plugins.core.attacks.blur_adapter",
                "lab.plugins.core.attacks.deepfool_adapter",
                "lab.plugins.core.attacks.dispersion_reduction_adapter",
                "lab.plugins.core.attacks.eot_pgd_adapter",
                "lab.plugins.core.attacks.fgsm_adapter",
                "lab.plugins.core.attacks.pgd_adapter",
                "lab.plugins.core.attacks.square_adapter",
            ),
        )

    def test_extra_attack_bootstrap_modules_match_contract(self) -> None:
        self.assertEqual(
            extra_attack_bootstrap.ADAPTER_MODULES,
            (
                "lab.plugins.extra.attacks.cw_adapter",
                "lab.plugins.extra.attacks.fgsm_center_mask_adapter",
                "lab.plugins.extra.attacks.fgsm_edge_mask_adapter",
                "lab.plugins.extra.attacks.jpeg_attack_adapter",
                "lab.plugins.extra.attacks.pretrained_patch_adapter",
            ),
        )

    def test_core_defense_bootstrap_modules_match_contract(self) -> None:
        self.assertEqual(
            core_defense_bootstrap.ADAPTER_MODULES,
            (
                "lab.plugins.core.defenses.none_adapter",
                "lab.plugins.core.defenses.preprocess_bitdepth_adapter",
                "lab.plugins.core.defenses.preprocess_jpeg_adapter",
                "lab.plugins.core.defenses.preprocess_median_blur_adapter",
            ),
        )

    def test_extra_defense_bootstrap_modules_match_contract(self) -> None:
        self.assertEqual(
            extra_defense_bootstrap.ADAPTER_MODULES,
            (
                "lab.plugins.extra.defenses.confidence_filter_adapter",
                "lab.plugins.extra.defenses.oracle_patch_recover_adapter",
                "lab.plugins.extra.defenses.preprocess_dpc_unet_adapter",
                "lab.plugins.extra.defenses.preprocess_random_resize_adapter",
            ),
        )

    def test_core_model_bootstrap_modules_match_contract(self) -> None:
        self.assertEqual(
            core_model_bootstrap.ADAPTER_MODULES,
            ("lab.plugins.core.models.yolo_adapter",),
        )

    def test_extra_model_bootstrap_modules_match_contract(self) -> None:
        self.assertEqual(
            extra_model_bootstrap.ADAPTER_MODULES,
            ("lab.plugins.extra.models.torchvision_adapter",),
        )


if __name__ == "__main__":
    unittest.main()
