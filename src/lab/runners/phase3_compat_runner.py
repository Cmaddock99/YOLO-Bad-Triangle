from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2

from lab.attacks.framework_registry import build_attack_plugin
from lab.attacks.utils import iter_images
from lab.eval.prediction_io import write_predictions_jsonl
from lab.models.registry import build_model


@dataclass
class Phase3CompatRunner:
    """Phase 3 compatibility runner for baseline/blur parity scaffolding."""

    model_name: str
    model_params: dict[str, Any]
    source_dir: Path
    output_dir: Path
    attack_name: str = "none"
    attack_params: dict[str, Any] | None = None
    max_images: int = 0
    predict_kwargs: dict[str, Any] | None = None

    def run(self) -> Path:
        model = build_model(self.model_name, **self.model_params)
        model.load()

        attack = None
        attack_params = dict(self.attack_params or {})
        if self.attack_name != "none":
            attack = build_attack_plugin(self.attack_name, **attack_params)

        prepared_dir = self.output_dir / "prepared_images"
        prepared_dir.mkdir(parents=True, exist_ok=True)

        prepared_paths: list[Path] = []
        for idx, image_path in enumerate(iter_images(self.source_dir)):
            if self.max_images > 0 and idx >= self.max_images:
                break
            image = cv2.imread(str(image_path))
            if image is None:
                continue
            transformed = image
            if attack is not None:
                transformed, _metadata = attack.apply(image)
            target = prepared_dir / image_path.name
            cv2.imwrite(str(target), transformed)
            prepared_paths.append(target)

        predictions = model.predict(prepared_paths, **dict(self.predict_kwargs or {}))
        prediction_file = self.output_dir / "predictions.jsonl"
        write_predictions_jsonl(predictions, prediction_file)
        return prediction_file
