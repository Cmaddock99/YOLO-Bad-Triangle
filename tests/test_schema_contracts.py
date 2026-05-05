from __future__ import annotations

import json
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


class WS6SchemaContractsTest(unittest.TestCase):
    """WS6 tests: schema-ID consistency, zero-row CSV, status enum, duplicate alias."""

    def test_schema_ids_consistent_with_files(self) -> None:
        """Every key in SCHEMA_IDS must have a corresponding schema file in schemas/v1/."""
        from lab.config.contracts import SCHEMA_IDS
        schema_root = Path("schemas/v1").resolve()
        for key, schema_id in SCHEMA_IDS.items():
            # Derive expected file name from the schema id (e.g. "cycle_summary/v1" → cycle_summary.schema.json)
            base = schema_id.split("/")[0]
            expected_file = schema_root / f"{base}.schema.json"
            self.assertTrue(
                expected_file.is_file(),
                msg=f"SCHEMA_IDS['{key}'] = '{schema_id}' has no matching file {expected_file}",
            )

    def test_schema_files_have_id_fields(self) -> None:
        """Every schema file in schemas/v1/ must have an 'id' field."""
        schema_root = Path("schemas/v1").resolve()
        for path in sorted(schema_root.glob("*.schema.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("id", payload, msg=f"Schema missing 'id': {path.name}")

    def test_zero_row_csv_fails_validation(self) -> None:
        """validate_legacy_csv_file must raise ValueError on an empty CSV."""
        import tempfile
        from lab.health_checks.schema import validate_legacy_csv_file
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "empty.csv"
            csv_path.write_text("col_a,col_b\n", encoding="utf-8")
            schema_path = Path(tmp) / "schema.json"
            schema_path.write_text(
                json.dumps({"id": "test/v1", "required_columns": ["col_a"]}),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                validate_legacy_csv_file(path=csv_path, schema_file=schema_path)

    def test_duplicate_attack_plugin_alias_raises(self) -> None:
        """Registering the same alias to a different class must raise ValueError."""
        from lab.core.plugin_registry import PluginRegistry

        class _Base:
            pass

        registry: PluginRegistry[_Base] = PluginRegistry("test")

        @registry.register("tool_a")
        class ClassA(_Base):
            pass

        class ClassB(_Base):
            pass

        with self.assertRaises(ValueError):
            registry.register("tool_a")(ClassB)

    def test_same_class_re_registered_under_same_alias_is_idempotent(self) -> None:
        """Re-registering the SAME class under the same alias must not raise."""
        from lab.core.plugin_registry import PluginRegistry

        class _Base:
            pass

        registry: PluginRegistry[_Base] = PluginRegistry("test")

        @registry.register("myalias")
        class ClassA(_Base):
            pass

        # Same class, same alias — must not raise
        registry.register("myalias")(ClassA)
        self.assertIs(registry.get("myalias"), ClassA)


if __name__ == "__main__":
    unittest.main()
