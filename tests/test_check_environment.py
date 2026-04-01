from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import check_environment


class CheckEnvironmentTest(unittest.TestCase):
    def test_dataset_pairing_requires_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            images_dir = Path(tmp) / "images"
            images_dir.mkdir(parents=True, exist_ok=True)
            (images_dir / "a.jpg").write_bytes(b"stub")
            result = check_environment.check_dataset_path(str(images_dir))
            self.assertFalse(result.ok)
            self.assertIn("labels", (result.label or "").lower())

    def test_dataset_pairing_passes_when_labels_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images_dir = root / "images"
            labels_dir = root / "labels"
            images_dir.mkdir(parents=True, exist_ok=True)
            labels_dir.mkdir(parents=True, exist_ok=True)
            (images_dir / "a.jpg").write_bytes(b"stub")
            (labels_dir / "a.txt").write_text("0 0.5 0.5 0.1 0.1\n", encoding="utf-8")
            result = check_environment.check_dataset_path(str(images_dir))
            self.assertTrue(result.ok)


if __name__ == "__main__":
    unittest.main()
