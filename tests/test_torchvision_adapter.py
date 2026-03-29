from __future__ import annotations

import unittest
from unittest.mock import MagicMock


def _torchvision_available() -> bool:
    try:
        import torchvision  # noqa: F401
        return True
    except ImportError:
        return False


@unittest.skipUnless(_torchvision_available(), "torchvision not installed")
class TorchvisionAdapterTest(unittest.TestCase):
    def _make_adapter(self, **kwargs):
        from lab.models.torchvision_adapter import FasterRCNNAdapter
        return FasterRCNNAdapter(**kwargs)

    def test_adapter_registered_in_model_registry(self) -> None:
        from lab.models.framework_registry import list_available_models
        available = list_available_models()
        self.assertIn("faster_rcnn", available)

    def test_load_succeeds(self) -> None:
        # Use pretrained=False to avoid downloading weights in tests
        adapter = self._make_adapter(pretrained=False)
        adapter.load()
        self.assertIsNotNone(adapter._model)

    def test_predict_returns_prediction_records(self) -> None:
        import torch
        import tempfile
        import numpy as np
        import cv2
        from pathlib import Path

        adapter = self._make_adapter(pretrained=False, score_threshold=0.0)
        adapter.load()

        # Stub model output so inference doesn't depend on actual weights
        fake_output = {
            "boxes": torch.tensor([[5.0, 5.0, 20.0, 20.0]]),
            "scores": torch.tensor([0.95]),
            "labels": torch.tensor([2]),
        }
        adapter._model = MagicMock(return_value=[fake_output])

        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = Path(tmpdir) / "test.jpg"
            img = np.zeros((64, 64, 3), dtype=np.uint8)
            cv2.imwrite(str(img_path), img)
            records = adapter.predict([img_path])

        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertIn("image_id", record)
        self.assertIn("boxes", record)
        self.assertIn("scores", record)
        self.assertIn("class_ids", record)
        self.assertIn("metadata", record)
        self.assertIsInstance(record["boxes"], list)
        self.assertIsInstance(record["scores"], list)
        self.assertIsInstance(record["class_ids"], list)

    def test_class_ids_are_zero_indexed(self) -> None:
        """torchvision uses 1-indexed COCO IDs; adapter must remap to 0-indexed."""
        import torch
        import tempfile
        import numpy as np
        import cv2
        from pathlib import Path

        adapter = self._make_adapter(pretrained=False, score_threshold=0.0)

        # Stub model that returns label=1 (torchvision 'person') with high conf
        fake_output = {
            "boxes": torch.tensor([[10.0, 10.0, 50.0, 50.0]]),
            "scores": torch.tensor([0.99]),
            "labels": torch.tensor([1]),  # torchvision class 1 = person
        }
        adapter._model = MagicMock(return_value=[fake_output])

        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = Path(tmpdir) / "test.jpg"
            img = np.zeros((64, 64, 3), dtype=np.uint8)
            cv2.imwrite(str(img_path), img)
            records = adapter.predict([img_path])

        self.assertEqual(len(records[0]["class_ids"]), 1)
        self.assertEqual(records[0]["class_ids"][0], 0,  # remapped: 1 - 1 = 0
                         "torchvision label 1 (person) must be remapped to class_id 0")

    def test_validate_returns_not_supported_stub(self) -> None:
        adapter = self._make_adapter()
        result = adapter.validate("dummy_dataset")
        self.assertIsNone(result["mAP50"])
        self.assertIsNone(result["mAP50-95"])
        self.assertEqual(result.get("_status"), "not_supported")


if __name__ == "__main__":
    unittest.main()
