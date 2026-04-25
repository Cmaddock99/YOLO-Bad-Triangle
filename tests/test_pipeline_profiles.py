from __future__ import annotations

import unittest

from lab.config.profiles import (
    build_profile_config,
    learned_defense_compatibility,
    load_pipeline_profile,
    profile_canonical_attacks,
    profile_canonical_defenses,
    profile_manual_only_attacks,
    profile_manual_only_defenses,
    profile_model_name,
    resolve_profile_compatibility,
    should_include_extra_plugins,
)


class PipelineProfilesTest(unittest.TestCase):
    def test_build_profile_config_sets_profile_metadata(self) -> None:
        config = build_profile_config("yolo11n_lab_v1")

        self.assertEqual(config["model"]["params"]["model"], "yolo11n.pt")
        self.assertEqual(config["pipeline_profile"]["name"], "yolo11n_lab_v1")
        self.assertEqual(config["pipeline_profile"]["authoritative_metric"], "mAP50")

    def test_profile_catalogs_match_v1_contract(self) -> None:
        self.assertEqual(
            profile_canonical_attacks("yolo11n_lab_v1"),
            ["fgsm", "pgd", "deepfool", "eot_pgd", "dispersion_reduction", "blur", "square"],
        )
        self.assertEqual(
            profile_canonical_defenses("yolo11n_lab_v1"),
            ["bit_depth", "jpeg_preprocess", "median_preprocess"],
        )

    def test_profile_manual_only_catalogs_match_v1_contract(self) -> None:
        self.assertEqual(
            profile_manual_only_attacks("yolo11n_lab_v1"),
            ["cw", "fgsm_center_mask", "fgsm_edge_mask", "jpeg_attack", "pretrained_patch"],
        )
        self.assertEqual(
            profile_manual_only_defenses("yolo11n_lab_v1"),
            ["c_dog", "c_dog_ensemble", "confidence_filter", "random_resize"],
        )

    def test_profile_model_name_for_v1_is_yolo(self) -> None:
        self.assertEqual(profile_model_name("yolo11n_lab_v1"), "yolo")

    def test_should_include_extra_plugins_is_false_for_canonical_profile(self) -> None:
        self.assertFalse(should_include_extra_plugins(build_profile_config("yolo11n_lab_v1")))

    def test_should_include_extra_plugins_is_true_for_manual_only_attack(self) -> None:
        config = build_profile_config("yolo11n_lab_v1")
        config["attack"]["name"] = "pretrained_patch"
        self.assertTrue(should_include_extra_plugins(config))

    def test_should_include_extra_plugins_is_true_for_manual_only_defense(self) -> None:
        config = build_profile_config("yolo11n_lab_v1")
        config["defense"]["name"] = "c_dog"
        self.assertTrue(should_include_extra_plugins(config))

    def test_should_include_extra_plugins_is_true_without_profile_metadata(self) -> None:
        config = build_profile_config("yolo11n_lab_v1")
        config.pop("pipeline_profile")
        self.assertTrue(should_include_extra_plugins(config))

    def test_profile_compatibility_marks_manual_only_defense(self) -> None:
        config = build_profile_config("yolo11n_lab_v1")
        config["attack"]["name"] = "fgsm"
        config["defense"]["name"] = "c_dog"
        compatibility = resolve_profile_compatibility(config)

        self.assertIsNotNone(compatibility)
        self.assertEqual(compatibility["status"], "manual_only")
        self.assertEqual(compatibility["defense_status"], "manual_only")

    def test_profile_compatibility_marks_pretrained_patch_manual_only(self) -> None:
        config = build_profile_config("yolo11n_lab_v1")
        config["attack"]["name"] = "pretrained_patch"
        config["defense"]["name"] = "none"

        compatibility = resolve_profile_compatibility(config)

        self.assertIsNotNone(compatibility)
        self.assertEqual(compatibility["status"], "manual_only")
        self.assertEqual(compatibility["attack_status"], "manual_only")

    def test_learned_defense_compatibility_is_incompatible_for_v1(self) -> None:
        compatibility = learned_defense_compatibility("yolo11n_lab_v1")

        self.assertFalse(compatibility["trainable"])
        self.assertEqual(compatibility["status"], "incompatible")

    def test_unknown_profile_raises(self) -> None:
        with self.assertRaises(ValueError):
            load_pipeline_profile("missing_profile")

    def test_patch_eval_profile_catalogs_match_contract(self) -> None:
        self.assertEqual(profile_canonical_attacks("yolo11n_patch_eval_v1"), ["pretrained_patch"])
        self.assertEqual(
            profile_canonical_defenses("yolo11n_patch_eval_v1"),
            ["bit_depth", "jpeg_preprocess", "median_preprocess", "c_dog", "blind_patch_recover", "oracle_patch_recover"],
        )

    def test_patch_eval_profile_keeps_extra_plugins_enabled_for_canonical_surface(self) -> None:
        config = build_profile_config("yolo11n_patch_eval_v1")

        self.assertTrue(should_include_extra_plugins(config))
        compatibility = resolve_profile_compatibility(config)
        self.assertIsNotNone(compatibility)
        self.assertEqual(compatibility["status"], "canonical")


if __name__ == "__main__":
    unittest.main()
