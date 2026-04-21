from __future__ import annotations

import unittest

from lab.plugins import build_plugin_inventory
from lab.plugins.core import (
    list_core_attack_plugins,
    list_core_defense_plugins,
    list_core_model_plugins,
)
from lab.plugins.extra import (
    list_extra_attack_plugins,
    list_extra_defense_plugins,
    list_extra_model_plugins,
)


class PluginInventoryTest(unittest.TestCase):
    def test_build_plugin_inventory_matches_v1_contract(self) -> None:
        inventory = build_plugin_inventory("yolo11n_lab_v1")

        self.assertEqual(inventory["profile"], "yolo11n_lab_v1")
        self.assertEqual(inventory["baseline_sentinels"]["attack"], ["none"])
        self.assertEqual(inventory["baseline_sentinels"]["defense"], ["none", "identity"])

        self.assertEqual(inventory["models"]["core"], ["yolo"])
        self.assertIn("faster_rcnn", inventory["models"]["extra"])

        self.assertEqual(
            inventory["attacks"]["core"],
            ["fgsm", "pgd", "deepfool", "eot_pgd", "dispersion_reduction", "blur", "square"],
        )
        self.assertIn("pretrained_patch", inventory["attacks"]["extra"])
        self.assertIn("cw", inventory["attacks"]["extra"])

        self.assertEqual(
            inventory["defenses"]["core"],
            ["bit_depth", "jpeg_preprocess", "median_preprocess"],
        )
        self.assertIn("c_dog", inventory["defenses"]["extra"])
        self.assertIn("confidence_filter", inventory["defenses"]["extra"])
        self.assertIn("random_resize", inventory["defenses"]["extra"])

    def test_all_aliases_retain_raw_registry_alias_surfaces(self) -> None:
        inventory = build_plugin_inventory("yolo11n_lab_v1")

        self.assertIn("adv_patch", inventory["attacks"]["all_aliases"])
        self.assertIn("cw_l2", inventory["attacks"]["all_aliases"])
        self.assertIn("gaussian_blur", inventory["attacks"]["all_aliases"])
        self.assertIn("ifgsm", inventory["attacks"]["all_aliases"])
        self.assertIn("bim", inventory["attacks"]["all_aliases"])

        self.assertIn("identity", inventory["defenses"]["all_aliases"])

        self.assertIn("ultralytics_yolo", inventory["models"]["all_aliases"])
        self.assertIn("torchvision_frcnn", inventory["models"]["all_aliases"])

    def test_preferred_name_surfaces_exclude_alias_only_names(self) -> None:
        inventory = build_plugin_inventory("yolo11n_lab_v1")

        for attack_name in inventory["attacks"]["core"] + inventory["attacks"]["extra"]:
            self.assertNotEqual(attack_name, "adv_patch")
        for defense_name in inventory["defenses"]["core"] + inventory["defenses"]["extra"]:
            self.assertNotEqual(defense_name, "identity")
        for model_name in inventory["models"]["core"] + inventory["models"]["extra"]:
            self.assertNotEqual(model_name, "ultralytics_yolo")
            self.assertNotEqual(model_name, "torchvision_frcnn")

    def test_core_and_extra_helpers_delegate_to_inventory(self) -> None:
        inventory = build_plugin_inventory("yolo11n_lab_v1")

        self.assertEqual(list_core_attack_plugins(), inventory["attacks"]["core"])
        self.assertEqual(list_core_defense_plugins(), inventory["defenses"]["core"])
        self.assertEqual(list_core_model_plugins(), inventory["models"]["core"])
        self.assertEqual(list_extra_attack_plugins(), inventory["attacks"]["extra"])
        self.assertEqual(list_extra_defense_plugins(), inventory["defenses"]["extra"])
        self.assertEqual(list_extra_model_plugins(), inventory["models"]["extra"])

    def test_inventory_surfaces_remain_stable_after_loader_reroute(self) -> None:
        inventory = build_plugin_inventory("yolo11n_lab_v1")

        self.assertEqual(
            inventory["attacks"]["core"],
            ["fgsm", "pgd", "deepfool", "eot_pgd", "dispersion_reduction", "blur", "square"],
        )
        self.assertEqual(
            inventory["attacks"]["extra"],
            ["cw", "fgsm_center_mask", "fgsm_edge_mask", "jpeg_attack", "pretrained_patch"],
        )
        self.assertIn("adv_patch", inventory["attacks"]["all_aliases"])
        self.assertIn("cw_l2", inventory["attacks"]["all_aliases"])
        self.assertIn("identity", inventory["defenses"]["all_aliases"])
        self.assertIn("ultralytics_yolo", inventory["models"]["all_aliases"])
        self.assertIn("torchvision_frcnn", inventory["models"]["all_aliases"])
