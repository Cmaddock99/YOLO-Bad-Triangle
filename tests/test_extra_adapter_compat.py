from __future__ import annotations

import importlib
import unittest


class ExtraAdapterCompatTest(unittest.TestCase):
    def test_old_and_new_cw_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("lab.attacks.cw_adapter")
        new_mod = importlib.import_module("lab.plugins.extra.attacks.cw_adapter")
        self.assertIs(old_mod, new_mod)

    def test_old_and_new_dpc_unet_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("lab.defenses.preprocess_dpc_unet_adapter")
        new_mod = importlib.import_module(
            "lab.plugins.extra.defenses.preprocess_dpc_unet_adapter"
        )
        self.assertIs(old_mod, new_mod)

    def test_old_and_new_torchvision_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("lab.models.torchvision_adapter")
        new_mod = importlib.import_module("lab.plugins.extra.models.torchvision_adapter")
        self.assertIs(old_mod, new_mod)

    def test_old_paths_still_expose_expected_classes(self) -> None:
        from lab.attacks.cw_adapter import CWAttack
        from lab.attacks.pretrained_patch_adapter import PretrainedPatchAttackAdapter
        from lab.defenses.confidence_filter_adapter import ConfidenceFilterDefenseAdapter
        from lab.models.torchvision_adapter import FasterRCNNAdapter

        self.assertEqual(CWAttack.__name__, "CWAttack")
        self.assertEqual(
            PretrainedPatchAttackAdapter.__name__,
            "PretrainedPatchAttackAdapter",
        )
        self.assertEqual(
            ConfidenceFilterDefenseAdapter.__name__,
            "ConfidenceFilterDefenseAdapter",
        )
        self.assertEqual(FasterRCNNAdapter.__name__, "FasterRCNNAdapter")


if __name__ == "__main__":
    unittest.main()
