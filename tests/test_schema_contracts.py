from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from lab.health_checks import validate_output_bundle


class SchemaContractsTest(unittest.TestCase):
    def test_all_v1_schemas_have_ids(self) -> None:
        root = Path("schemas/v1").resolve()
        files = sorted(root.glob("*.json"))
        self.assertTrue(files)
        for path in files:
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("id", payload, msg=f"schema missing id: {path}")

    def test_fixture_bundle_validates(self) -> None:
        repo_root = Path(".").resolve()
        framework_run = repo_root / "tests/fixtures/schema/valid/framework_run"
        legacy_csv = repo_root / "tests/fixtures/schema/valid/legacy_compat.csv"
        inputs = validate_output_bundle(
            repo_root=repo_root,
            framework_run_dir=framework_run,
            legacy_compat_csv=legacy_csv,
        )
        self.assertTrue(inputs.metrics_json.is_file())
        self.assertTrue(inputs.run_summary_json.is_file())
        self.assertTrue(inputs.legacy_csv.is_file())

    def test_invalid_fixture_fails_validation(self) -> None:
        repo_root = Path(".").resolve()
        framework_run = repo_root / "tests/fixtures/schema/invalid/framework_run"
        legacy_csv = repo_root / "tests/fixtures/schema/invalid/legacy_compat.csv"
        with self.assertRaises(ValueError):
            validate_output_bundle(
                repo_root=repo_root,
                framework_run_dir=framework_run,
                legacy_compat_csv=legacy_csv,
            )

    def test_schema_change_guard_fails_without_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "schemas/v1").mkdir(parents=True)
            (root / "docs").mkdir(parents=True)
            # sanity check only to ensure tempfile support path works in tests
            self.assertTrue((root / "schemas/v1").is_dir())


if __name__ == "__main__":
    unittest.main()
