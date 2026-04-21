from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

import cv2
import numpy as np

from lab.config.profiles import build_profile_config
from lab.runners.run_experiment import UnifiedExperimentRunner
from lab.runners.run_intent import build_run_intent


class _DummyRuntimeModel:
    def load(self) -> None:
        return

    def predict(self, images: list[Path], **kwargs: Any) -> list[dict[str, Any]]:
        del kwargs
        return [
            {
                "image_id": image.name,
                "boxes": [[0.0, 0.0, 1.0, 1.0]],
                "scores": [0.9],
                "class_ids": [0],
                "metadata": {},
            }
            for image in images
        ]

    def validate(self, dataset: str, **kwargs: Any) -> dict[str, Any]:
        del dataset, kwargs
        return {"precision": None, "recall": None, "mAP50": None, "mAP50-95": None}


class _PassthroughDefense:
    def preprocess(
        self,
        image: np.ndarray,
        *,
        attack_hint: str | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        del attack_hint
        return image, {}

    def postprocess(
        self,
        records: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        return list(records), {}


class RuntimePluginScopeTest(unittest.TestCase):
    def test_build_run_intent_uses_core_only_builders_for_canonical_profile(self) -> None:
        config = build_profile_config("yolo11n_lab_v1")
        config["attack"]["name"] = "fgsm"
        config["defense"]["name"] = "none"

        attack_calls: list[tuple[str, dict[str, Any]]] = []
        defense_calls: list[tuple[str, dict[str, Any]]] = []

        def _build_attack(name: str, **kwargs: Any) -> object:
            attack_calls.append((name, dict(kwargs)))
            return object()

        def _build_defense(name: str, **kwargs: Any) -> object:
            defense_calls.append((name, dict(kwargs)))
            return object()

        with (
            patch("lab.runners.run_intent.build_attack_plugin", side_effect=_build_attack),
            patch("lab.runners.run_intent.build_defense_plugin", side_effect=_build_defense),
        ):
            build_run_intent(config)

        self.assertFalse(attack_calls[0][1]["include_extra"])
        self.assertFalse(defense_calls[0][1]["include_extra"])

    def test_build_run_intent_uses_full_surface_for_manual_only_attack(self) -> None:
        config = build_profile_config("yolo11n_lab_v1")
        config["attack"]["name"] = "pretrained_patch"

        attack_calls: list[dict[str, Any]] = []
        defense_calls: list[dict[str, Any]] = []

        def _build_attack(name: str, **kwargs: Any) -> object:
            del name
            attack_calls.append(dict(kwargs))
            return object()

        def _build_defense(name: str, **kwargs: Any) -> object:
            del name
            defense_calls.append(dict(kwargs))
            return object()

        with (
            patch("lab.runners.run_intent.build_attack_plugin", side_effect=_build_attack),
            patch("lab.runners.run_intent.build_defense_plugin", side_effect=_build_defense),
        ):
            build_run_intent(config)

        self.assertTrue(attack_calls[0]["include_extra"])
        self.assertTrue(defense_calls[0]["include_extra"])

    def test_build_run_intent_uses_full_surface_for_manual_only_defense(self) -> None:
        config = build_profile_config("yolo11n_lab_v1")
        config["attack"]["name"] = "fgsm"
        config["defense"]["name"] = "c_dog"

        attack_calls: list[dict[str, Any]] = []
        defense_calls: list[dict[str, Any]] = []

        def _build_attack(name: str, **kwargs: Any) -> object:
            del name
            attack_calls.append(dict(kwargs))
            return object()

        def _build_defense(name: str, **kwargs: Any) -> object:
            del name
            defense_calls.append(dict(kwargs))
            return object()

        with (
            patch("lab.runners.run_intent.build_attack_plugin", side_effect=_build_attack),
            patch("lab.runners.run_intent.build_defense_plugin", side_effect=_build_defense),
        ):
            build_run_intent(config)

        self.assertTrue(attack_calls[0]["include_extra"])
        self.assertTrue(defense_calls[0]["include_extra"])

    def test_runner_uses_core_only_scope_for_canonical_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_dir = root / "images"
            source_dir.mkdir(parents=True, exist_ok=True)
            image = np.full((16, 16, 3), 127, dtype=np.uint8)
            self.assertTrue(cv2.imwrite(str(source_dir / "a.jpg"), image))

            config = build_profile_config("yolo11n_lab_v1")
            config["data"]["source_dir"] = str(source_dir)
            config["attack"]["name"] = "fgsm"
            config["runner"]["output_root"] = str(root / "outputs")
            config["runner"]["run_name"] = "scope_test"
            config["runner"]["max_images"] = 1
            config["validation"]["enabled"] = False
            config["summary"]["enabled"] = False

            model_calls: list[dict[str, Any]] = []
            attack_calls: list[dict[str, Any]] = []
            defense_calls: list[dict[str, Any]] = []

            def _build_model(name: str, **kwargs: Any) -> _DummyRuntimeModel:
                del name
                model_calls.append(dict(kwargs))
                return _DummyRuntimeModel()

            def _resolve_attack(
                attack_name: str,
                attack_params: dict[str, Any],
                *,
                include_extra: bool = True,
            ) -> tuple[Any | None, dict[str, Any], dict[str, Any]]:
                del attack_name, attack_params
                attack_calls.append({"include_extra": include_extra})
                return None, {}, {
                    "objective_mode": None,
                    "target_class": None,
                    "attack_roi": None,
                    "preserve_weight": None,
                }

            def _resolve_defense(
                defense_name: str,
                defense_params: dict[str, Any],
                *,
                include_extra: bool = True,
            ) -> tuple[Any, dict[str, Any], list[dict[str, str]]]:
                del defense_name, defense_params
                defense_calls.append({"include_extra": include_extra})
                return _PassthroughDefense(), {}, []

            with (
                patch("lab.runners.run_experiment.build_model", side_effect=_build_model),
                patch("lab.runners.run_experiment.resolve_attack_instance", side_effect=_resolve_attack),
                patch("lab.runners.run_experiment.resolve_defense_instance", side_effect=_resolve_defense),
                patch(
                    "lab.runners.run_experiment.build_run_intent",
                    return_value={
                        "config_fingerprint_sha256": "cfg",
                        "attack_signature": "{}",
                        "defense_signature": "{}",
                        "checkpoint_fingerprint_sha256": None,
                        "checkpoint_fingerprint_source": None,
                        "defense_checkpoints": [],
                        "pipeline_profile": "yolo11n_lab_v1",
                        "authoritative_metric": "mAP50",
                        "profile_compatibility": {
                            "status": "canonical",
                            "model_status": "canonical",
                            "attack_status": "canonical",
                            "defense_status": "canonical",
                            "reasons": [],
                        },
                    },
                ),
            ):
                UnifiedExperimentRunner(config=config).run()

        self.assertFalse(model_calls[0]["include_extra"])
        self.assertFalse(attack_calls[0]["include_extra"])
        self.assertFalse(defense_calls[0]["include_extra"])


if __name__ == "__main__":
    unittest.main()
