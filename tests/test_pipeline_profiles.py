from __future__ import annotations

import unittest

from lab.config.profiles import (
    build_profile_config,
    learned_defense_compatibility,
    load_pipeline_profile,
    profile_canonical_attacks,
    profile_canonical_defenses,
    resolve_profile_compatibility,
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


if __name__ == "__main__":
    unittest.main()
