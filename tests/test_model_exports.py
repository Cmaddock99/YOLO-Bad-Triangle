from __future__ import annotations

import unittest

from lab.models import YOLOModel, YOLOModelAdapter
from lab.models.model_utils import normalize_model_path


class ModelExportsTest(unittest.TestCase):
    def test_yolo_legacy_export_points_to_adapter(self) -> None:
        self.assertIs(YOLOModel, YOLOModelAdapter)

    def test_normalize_model_path_defaults_to_canonical_yolo26n(self) -> None:
        self.assertEqual(normalize_model_path(None), "yolo26n.pt")
        self.assertEqual(normalize_model_path(""), "yolo26n.pt")


if __name__ == "__main__":
    unittest.main()
