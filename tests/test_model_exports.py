from __future__ import annotations

import unittest

from lab.models import YOLOModel, YOLOModelAdapter


class ModelExportsTest(unittest.TestCase):
    def test_yolo_legacy_export_points_to_adapter(self) -> None:
        self.assertIs(YOLOModel, YOLOModelAdapter)


if __name__ == "__main__":
    unittest.main()
