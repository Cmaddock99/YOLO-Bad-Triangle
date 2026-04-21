from __future__ import annotations

import unittest

from lab.attacks.framework_registry import build_attack_plugin, list_available_attack_plugins
from lab.defenses.framework_registry import build_defense_plugin, list_available_defense_plugins
from lab.models.framework_registry import build_model, list_available_models
from lab.plugins.core import (
    build_core_attack_plugin,
    build_core_defense_plugin,
    build_core_model,
    list_core_attack_aliases,
    list_core_defense_aliases,
    list_core_model_aliases,
)


class CorePluginHelpersTest(unittest.TestCase):
    def test_core_alias_helpers_match_registry_core_only_lists(self) -> None:
        self.assertEqual(
            list_core_attack_aliases(),
            list_available_attack_plugins(include_extra=False),
        )
        self.assertEqual(
            list_core_defense_aliases(),
            list_available_defense_plugins(include_extra=False),
        )
        self.assertEqual(
            list_core_model_aliases(),
            list_available_models(include_extra=False),
        )

    def test_build_core_attack_plugin_succeeds(self) -> None:
        attack = build_core_attack_plugin("fgsm", epsilon=0.005)
        regular = build_attack_plugin("fgsm", include_extra=False, epsilon=0.005)
        self.assertEqual(type(attack), type(regular))

    def test_build_core_defense_plugin_succeeds(self) -> None:
        defense = build_core_defense_plugin("preprocess_median_blur", kernel_size=3)
        regular = build_defense_plugin(
            "preprocess_median_blur",
            include_extra=False,
            kernel_size=3,
        )
        self.assertEqual(type(defense), type(regular))

    def test_build_core_model_matches_regular_core_only_builder(self) -> None:
        model = build_core_model("yolo")
        regular = build_model("yolo", include_extra=False)
        self.assertEqual(type(model), type(regular))

    def test_build_core_helpers_reject_extra_only_plugins(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported attack plugin 'cw'"):
            build_core_attack_plugin(
                "cw",
                c=10.0,
                max_iter=4,
                lr=0.01,
                binary_search_steps=1,
                device="cpu",
            )
        with self.assertRaisesRegex(
            ValueError, "Unsupported defense plugin 'confidence_filter'"
        ):
            build_core_defense_plugin("confidence_filter", threshold=0.5)
        with self.assertRaisesRegex(ValueError, "Unsupported model plugin 'faster_rcnn'"):
            build_core_model("faster_rcnn")


if __name__ == "__main__":
    unittest.main()
