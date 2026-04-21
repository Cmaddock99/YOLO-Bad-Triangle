from __future__ import annotations

import importlib
import unittest


class CoreAdapterCompatTest(unittest.TestCase):
    def test_old_and_new_fgsm_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("lab.attacks.fgsm_adapter")
        new_mod = importlib.import_module("lab.plugins.core.attacks.fgsm_adapter")
        self.assertIs(old_mod, new_mod)

    def test_old_and_new_deepfool_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("lab.attacks.deepfool_adapter")
        new_mod = importlib.import_module("lab.plugins.core.attacks.deepfool_adapter")
        self.assertIs(old_mod, new_mod)

    def test_old_and_new_none_defense_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("lab.defenses.none_adapter")
        new_mod = importlib.import_module("lab.plugins.core.defenses.none_adapter")
        self.assertIs(old_mod, new_mod)

    def test_old_and_new_yolo_modules_are_identical(self) -> None:
        old_mod = importlib.import_module("lab.models.yolo_adapter")
        new_mod = importlib.import_module("lab.plugins.core.models.yolo_adapter")
        self.assertIs(old_mod, new_mod)

    def test_old_paths_still_expose_expected_classes(self) -> None:
        from lab.attacks.deepfool_adapter import DeepFoolAttack
        from lab.attacks.fgsm_adapter import FGSMAttack, FGSMAttackAdapter
        from lab.models.yolo_adapter import YOLOModelAdapter

        self.assertEqual(FGSMAttack.__name__, "FGSMAttack")
        self.assertEqual(FGSMAttackAdapter.__name__, "FGSMAttackAdapter")
        self.assertEqual(DeepFoolAttack.__name__, "DeepFoolAttack")
        self.assertEqual(YOLOModelAdapter.__name__, "YOLOModelAdapter")


if __name__ == "__main__":
    unittest.main()
