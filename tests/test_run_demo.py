"""Tests for scripts/run_demo.py.

Unit tests cover pure logic and do not require a live YOLO environment.
Integration tests (marked with @pytest.mark.integration) run the full
pipeline and require the full environment including dataset + model weights.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Make sure the repo src is on path for imports
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from scripts import run_demo


class TestBuildExpectedRuns(unittest.TestCase):
    def test_baseline_always_present(self) -> None:
        runs = run_demo.build_expected_runs(["fgsm"], ["median_preprocess"])
        names = [r["run_name"] for r in runs]
        self.assertIn("baseline_none", names)
        self.assertEqual(runs[0]["run_name"], "baseline_none")

    def test_attack_run_naming(self) -> None:
        runs = run_demo.build_expected_runs(["fgsm", "pgd"], ["median_preprocess"])
        names = [r["run_name"] for r in runs]
        self.assertIn("attack_fgsm", names)
        self.assertIn("attack_pgd", names)

    def test_defense_run_naming(self) -> None:
        runs = run_demo.build_expected_runs(["fgsm"], ["median_preprocess"])
        names = [r["run_name"] for r in runs]
        self.assertIn("defended_fgsm_median_preprocess", names)

    def test_multiple_attacks_and_defenses(self) -> None:
        runs = run_demo.build_expected_runs(["fgsm", "pgd"], ["m1", "m2"])
        names = [r["run_name"] for r in runs]
        # baseline + 2 attack + 4 defense = 7
        self.assertEqual(len(runs), 7)
        self.assertIn("defended_fgsm_m1", names)
        self.assertIn("defended_fgsm_m2", names)
        self.assertIn("defended_pgd_m1", names)
        self.assertIn("defended_pgd_m2", names)

    def test_attack_metadata_fields(self) -> None:
        runs = run_demo.build_expected_runs(["fgsm"], ["median_preprocess"])
        attack_run = next(r for r in runs if r["run_name"] == "attack_fgsm")
        self.assertEqual(attack_run["attack"], "fgsm")
        self.assertEqual(attack_run["defense"], "none")

    def test_empty_defenses_skips_defense_runs(self) -> None:
        runs = run_demo.build_expected_runs(["fgsm"], [])
        names = [r["run_name"] for r in runs]
        # baseline + 1 attack = 2; no defense runs
        self.assertEqual(len(runs), 2)
        self.assertNotIn("defended_fgsm_", str(names))


class TestConfigFingerprint(unittest.TestCase):
    def test_fingerprint_deterministic(self) -> None:
        cfg = {"model": {"name": "yolo"}, "runner": {"seed": 42}}
        fp1 = run_demo._config_fingerprint(cfg)
        fp2 = run_demo._config_fingerprint(cfg)
        self.assertEqual(fp1, fp2)

    def test_fingerprint_changes_with_content(self) -> None:
        cfg1 = {"seed": 42}
        cfg2 = {"seed": 99}
        self.assertNotEqual(run_demo._config_fingerprint(cfg1), run_demo._config_fingerprint(cfg2))

    def test_fingerprint_is_64_hex_chars(self) -> None:
        fp = run_demo._config_fingerprint({"a": 1})
        self.assertEqual(len(fp), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in fp))


class TestDryRun(unittest.TestCase):
    """Test --dry-run exits 0 and prints plan without touching filesystem beyond init dirs."""

    def _run_dry(self, extra_args: list[str] | None = None) -> int:
        from scripts.run_demo import main
        argv = ["run_demo.py", "--dry-run", "--skip-preflight"]
        if extra_args:
            argv.extend(extra_args)
        with tempfile.TemporaryDirectory() as tmp:
            argv.extend(["--output-root", tmp])
            with patch.object(sys, "argv", argv):
                return main()

    def test_dry_run_exits_0(self) -> None:
        code = self._run_dry()
        self.assertEqual(code, run_demo.EXIT_SUCCESS)

    def test_dry_run_with_custom_attacks(self) -> None:
        code = self._run_dry(["--attacks", "fgsm,pgd", "--defenses", "median_preprocess"])
        self.assertEqual(code, run_demo.EXIT_SUCCESS)


class TestOutputDirsCreated(unittest.TestCase):
    def test_output_dirs_created_on_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            argv = [
                "run_demo.py", "--dry-run", "--skip-preflight",
                "--output-root", tmp,
            ]
            with patch.object(sys, "argv", argv):
                run_demo.main()
            # Timestamped subdir should exist
            subdirs = list(Path(tmp).iterdir())
            self.assertEqual(len(subdirs), 1)
            demo_root = subdirs[0]
            self.assertTrue((demo_root / "runs").is_dir())
            self.assertTrue((demo_root / "reports").is_dir())
            self.assertTrue((demo_root / "summary").is_dir())


class TestHelp(unittest.TestCase):
    def test_help_exits_0(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with patch.object(sys, "argv", ["run_demo.py", "--help"]):
                run_demo._parse_args()
        self.assertEqual(ctx.exception.code, 0)


class TestStageValidateRuns(unittest.TestCase):
    def _make_run_dir(self, tmp_root: Path, run_name: str, include_files: bool = True) -> Path:
        run_dir = tmp_root / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        if include_files:
            # Write minimal valid JSON
            metrics = {
                "schema_version": "framework_metrics/v1",
                "predictions": {
                    "image_count": 4,
                    "images_with_detections": 3,
                    "total_detections": 10,
                    "detections_per_image_mean": 2.5,
                    "confidence": {"count": 10, "mean": 0.7, "median": 0.7, "min": 0.5, "max": 0.9},
                    "per_class": {},
                },
                "validation": {"status": "complete", "enabled": True},
            }
            (run_dir / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
            run_summary = {
                "schema_version": "framework_run_summary/v1",
                "run_dir": str(run_dir),
                "metrics_path": str(run_dir / "metrics.json"),
                "model": {"name": "yolo", "params": {}},
                "attack": {"name": "none", "params": {}},
                "defense": {"name": "none", "params": {}},
                "seed": 42,
            }
            (run_dir / "run_summary.json").write_text(json.dumps(run_summary), encoding="utf-8")
            (run_dir / "predictions.jsonl").write_text("", encoding="utf-8")
        return run_dir

    def test_missing_run_dir_records_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp) / "runs"
            runs_root.mkdir()
            expected = [{"run_name": "baseline_none", "attack": "none", "defense": "none"}]
            code, errors = run_demo.stage_validate_runs(expected, runs_root)
            self.assertEqual(code, run_demo.EXIT_ARTIFACT)
            self.assertTrue(errors["baseline_none"])

    def test_missing_run_dir_exits_3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp) / "runs"
            runs_root.mkdir()
            expected = [{"run_name": "ghost_run", "attack": "none", "defense": "none"}]
            code, _ = run_demo.stage_validate_runs(expected, runs_root)
            self.assertEqual(code, run_demo.EXIT_ARTIFACT)

    def test_missing_artifacts_records_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp) / "runs"
            runs_root.mkdir()
            # Create dir but no files
            (runs_root / "baseline_none").mkdir()
            expected = [{"run_name": "baseline_none", "attack": "none", "defense": "none"}]
            code, errors = run_demo.stage_validate_runs(expected, runs_root)
            self.assertEqual(code, run_demo.EXIT_ARTIFACT)
            self.assertTrue(errors["baseline_none"])


class TestStageCheckReports(unittest.TestCase):
    def test_all_present_returns_0(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reports = Path(tmp)
            for fname in ("framework_run_summary.csv", "framework_run_report.md", "dashboard.html"):
                (reports / fname).write_text("data", encoding="utf-8")
            code = run_demo.stage_check_reports(reports)
            self.assertEqual(code, run_demo.EXIT_SUCCESS)

    def test_missing_report_exits_3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reports = Path(tmp)
            (reports / "framework_run_summary.csv").write_text("data", encoding="utf-8")
            # framework_run_report.md and dashboard.html missing
            code = run_demo.stage_check_reports(reports)
            self.assertEqual(code, run_demo.EXIT_ARTIFACT)

    def test_empty_report_exits_3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reports = Path(tmp)
            for fname in ("framework_run_summary.csv", "framework_run_report.md", "dashboard.html"):
                (reports / fname).write_text("", encoding="utf-8")
            code = run_demo.stage_check_reports(reports)
            self.assertEqual(code, run_demo.EXIT_ARTIFACT)

    def test_missing_dashboard_exits_3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reports = Path(tmp)
            (reports / "framework_run_summary.csv").write_text("data", encoding="utf-8")
            (reports / "framework_run_report.md").write_text("data", encoding="utf-8")
            code = run_demo.stage_check_reports(reports)
            self.assertEqual(code, run_demo.EXIT_ARTIFACT)


class TestDemoCommandBuilders(unittest.TestCase):
    def _args(self, *, max_images: int | None = None) -> argparse.Namespace:
        return argparse.Namespace(
            python_bin="./.venv/bin/python",
            config="configs/demo.yaml",
            attacks="fgsm,pgd",
            defenses="median_preprocess",
            seed=42,
            max_images=max_images,
        )

    def test_stage3_command_uses_run_unified_sweep(self) -> None:
        args = self._args(max_images=8)
        command = run_demo._build_stage3_sweep_command(
            args=args,
            config_path=Path("/repo/configs/demo.yaml"),
            runs_root=Path("/tmp/demo/runs"),
            reports_root=Path("/tmp/demo/reports"),
        )

        self.assertEqual(command[:3], ["./.venv/bin/python", str(run_demo.REPO_ROOT / "scripts" / "run_unified.py"), "sweep"])
        self.assertIn("--phases", command)
        self.assertIn("1,2,3", command)
        self.assertIn("--validation-enabled", command)
        self.assertIn("--max-images", command)
        self.assertNotIn("--no-team-summary", command)
        self.assertNotIn("--no-failure-gallery", command)
        self.assertNotIn("--no-compat-dashboard", command)

    def test_stage3b_command_uses_run_unified_phase4_with_core_report_flags(self) -> None:
        args = self._args(max_images=8)
        command = run_demo._build_stage3b_report_regen_command(
            args=args,
            config_path=Path("/repo/configs/demo.yaml"),
            runs_root=Path("/tmp/demo/runs"),
            reports_root=Path("/tmp/demo/reports"),
        )

        self.assertEqual(command[:3], ["./.venv/bin/python", str(run_demo.REPO_ROOT / "scripts" / "run_unified.py"), "sweep"])
        self.assertIn("--phases", command)
        self.assertIn("4", command)
        self.assertIn("--validation-enabled", command)
        self.assertIn("--no-team-summary", command)
        self.assertIn("--no-failure-gallery", command)
        self.assertIn("--no-compat-dashboard", command)
        self.assertNotIn("--max-images", command)


class TestStageNoopCheck(unittest.TestCase):
    def _make_run(
        self, runs_root: Path, run_name: str, total_detections: int, images: dict[str, bytes] | None = None
    ) -> None:
        run_dir = runs_root / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "schema_version": "framework_metrics/v1",
            "predictions": {
                "total_detections": total_detections,
                "image_count": 4,
                "images_with_detections": 3,
                "detections_per_image_mean": 1.0,
                "confidence": {},
                "per_class": {},
            },
            "validation": {"status": "disabled", "enabled": False},
        }
        (run_dir / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
        if images is not None:
            img_dir = run_dir / "images"
            img_dir.mkdir()
            for fname, data in images.items():
                (img_dir / fname).write_bytes(data)

    def test_noop_attack_exits_4(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp)
            # Baseline and attack have identical detections and no images → metrics-only noop
            self._make_run(runs_root, "baseline_none", total_detections=100)
            self._make_run(runs_root, "attack_fgsm", total_detections=100)
            expected = [
                {"run_name": "baseline_none", "attack": "none", "defense": "none"},
                {"run_name": "attack_fgsm", "attack": "fgsm", "defense": "none"},
            ]
            code, warnings = run_demo.stage_noop_check(expected, runs_root)
            self.assertEqual(code, run_demo.EXIT_NOOP)
            self.assertTrue(any(w["run_name"] == "attack_fgsm" for w in warnings))

    def test_noop_skipped_when_images_differ(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp)
            self._make_run(runs_root, "baseline_none", total_detections=100,
                           images={"img1.png": b"\x00\x01\x02"})
            self._make_run(runs_root, "attack_fgsm", total_detections=90,
                           images={"img1.png": b"\x00\x01\x03"})  # different bytes
            expected = [
                {"run_name": "baseline_none", "attack": "none", "defense": "none"},
                {"run_name": "attack_fgsm", "attack": "fgsm", "defense": "none"},
            ]
            code, warnings = run_demo.stage_noop_check(expected, runs_root)
            attack_warnings = [w for w in warnings if w["run_name"] == "attack_fgsm"]
            self.assertEqual(code, run_demo.EXIT_SUCCESS)
            self.assertEqual(len(attack_warnings), 0)

    def test_noop_skipped_when_no_images_dir(self) -> None:
        """Runs without an images/ dir fall back to metrics check only."""
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp)
            self._make_run(runs_root, "baseline_none", total_detections=100)
            self._make_run(runs_root, "attack_fgsm", total_detections=50)  # 50% change — not noop
            expected = [
                {"run_name": "baseline_none", "attack": "none", "defense": "none"},
                {"run_name": "attack_fgsm", "attack": "fgsm", "defense": "none"},
            ]
            code, warnings = run_demo.stage_noop_check(expected, runs_root)
            attack_warnings = [w for w in warnings if w["run_name"] == "attack_fgsm"]
            self.assertEqual(code, run_demo.EXIT_SUCCESS)
            self.assertEqual(len(attack_warnings), 0)

    def test_byte_identical_images_triggers_noop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp)
            img_bytes = b"\x00\x01\x02\x03"
            self._make_run(runs_root, "baseline_none", total_detections=100,
                           images={"img1.png": img_bytes})
            self._make_run(runs_root, "attack_fgsm", total_detections=98,  # small metric change
                           images={"img1.png": img_bytes})  # identical bytes
            expected = [
                {"run_name": "baseline_none", "attack": "none", "defense": "none"},
                {"run_name": "attack_fgsm", "attack": "fgsm", "defense": "none"},
            ]
            code, warnings = run_demo.stage_noop_check(expected, runs_root)
            self.assertEqual(code, run_demo.EXIT_NOOP)


class TestSweepFailureExits1(unittest.TestCase):
    def test_sweep_failure_exits_1(self) -> None:
        """A failing sweep subprocess should result in EXIT_PARTIAL_FAILURE."""
        with tempfile.TemporaryDirectory() as tmp:
            argv = [
                "run_demo.py",
                "--skip-preflight",
                "--output-root", tmp,
                "--attacks", "fgsm",
                "--defenses", "median_preprocess",
            ]
            # Mock _run_subprocess to simulate sweep failure
            call_count = {"n": 0}

            def fake_subprocess(cmd, log_path, env=None):
                call_count["n"] += 1
                log_path.write_text("simulated failure", encoding="utf-8")
                # First call = sweep → fail; subsequent = summary → fail (no artifacts anyway)
                return 1

            with patch.object(sys, "argv", argv):
                with patch("scripts.run_demo._run_subprocess", side_effect=fake_subprocess):
                    code = run_demo.main()

        # Exit priority: sweep failure=1, but artifact failure=3 should dominate
        self.assertIn(code, (run_demo.EXIT_PARTIAL_FAILURE, run_demo.EXIT_ARTIFACT))


class TestManifestWritten(unittest.TestCase):
    def test_manifest_written_on_success_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            demo_root = Path(tmp) / "demo"
            (demo_root / "runs").mkdir(parents=True)
            (demo_root / "reports").mkdir()
            (demo_root / "summary").mkdir()
            import time as _time
            run_demo.write_manifest(
                demo_root=demo_root,
                git_commit="abc123",
                git_dirty=False,
                args=MagicMock(seed=42),
                config_path=Path("configs/demo.yaml"),
                fingerprint="deadbeef",
                model_name="yolo26n",
                dataset_name="val2017_subset500",
                dataset_path="/data/val",
                images_count=4,
                conf=0.25,
                iou=0.45,
                imgsz=640,
                expected_runs=[],
                validation_errors={},
                noop_warnings=[],
                failed_runs=[],
                start_time_str="2026-03-29T14:00:00Z",
                t0_wall=_time.monotonic() - 1.0,
                exit_code=0,
                exit_reason="success",
            )
            manifest_path = demo_root / "demo_manifest.json"
            self.assertTrue(manifest_path.is_file())

    def test_manifest_schema_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            demo_root = Path(tmp) / "demo"
            (demo_root / "runs").mkdir(parents=True)
            (demo_root / "reports").mkdir()
            (demo_root / "summary").mkdir()
            import time as _time
            run_demo.write_manifest(
                demo_root=demo_root,
                git_commit="abc123",
                git_dirty=False,
                args=MagicMock(seed=42),
                config_path=Path("configs/demo.yaml"),
                fingerprint="deadbeef",
                model_name="yolo26n",
                dataset_name="val2017_subset500",
                dataset_path="/data/val",
                images_count=4,
                conf=0.25,
                iou=0.45,
                imgsz=640,
                expected_runs=[],
                validation_errors={},
                noop_warnings=[],
                failed_runs=[],
                start_time_str="2026-03-29T14:00:00Z",
                t0_wall=_time.monotonic() - 1.0,
                exit_code=0,
                exit_reason="success",
            )
            manifest_path = demo_root / "demo_manifest.json"
            data = json.loads(manifest_path.read_text())
            # Check required top-level keys
            for key in ("schema_version", "reproducibility", "config", "source_files",
                        "runs", "artifacts", "timing", "outcome", "bootstrap"):
                self.assertIn(key, data)
            self.assertEqual(data["schema_version"], "demo_manifest/v1")

    def test_manifest_checksums_match_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            demo_root = Path(tmp) / "demo"
            runs_root = demo_root / "runs"
            runs_root.mkdir(parents=True)
            (demo_root / "reports").mkdir()
            (demo_root / "summary").mkdir()
            # Create a real file in reports
            report_file = demo_root / "reports" / "framework_run_summary.csv"
            report_file.write_bytes(b"schema_version,run_name\n")
            expected_sha = run_demo._sha256_file(report_file)
            dashboard_file = demo_root / "reports" / "dashboard.html"
            dashboard_file.write_text("<html></html>", encoding="utf-8")
            dashboard_sha = run_demo._sha256_file(dashboard_file)
            import time as _time
            run_demo.write_manifest(
                demo_root=demo_root,
                git_commit="abc",
                git_dirty=False,
                args=MagicMock(seed=42),
                config_path=Path("configs/demo.yaml"),
                fingerprint="ff",
                model_name="yolo26n",
                dataset_name="val",
                dataset_path="/d",
                images_count=1,
                conf=0.25,
                iou=0.45,
                imgsz=640,
                expected_runs=[],
                validation_errors={},
                noop_warnings=[],
                failed_runs=[],
                start_time_str="2026-03-29T14:00:00Z",
                t0_wall=_time.monotonic() - 1.0,
                exit_code=0,
                exit_reason="success",
            )
            data = json.loads((demo_root / "demo_manifest.json").read_text())
            checksums = data["artifacts"]["checksums"]
            self.assertIn("reports/framework_run_summary.csv", checksums)
            self.assertEqual(checksums["reports/framework_run_summary.csv"], expected_sha)
            self.assertIn("reports/dashboard.html", checksums)
            self.assertEqual(checksums["reports/dashboard.html"], dashboard_sha)

    def test_manifest_source_files_track_canonical_sweep_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            demo_root = Path(tmp) / "demo"
            (demo_root / "runs").mkdir(parents=True)
            (demo_root / "reports").mkdir()
            (demo_root / "summary").mkdir()
            import time as _time
            run_demo.write_manifest(
                demo_root=demo_root,
                git_commit="abc123",
                git_dirty=False,
                args=MagicMock(seed=42),
                config_path=Path("configs/demo.yaml"),
                fingerprint="deadbeef",
                model_name="yolo26n",
                dataset_name="val2017_subset500",
                dataset_path="/data/val",
                images_count=4,
                conf=0.25,
                iou=0.45,
                imgsz=640,
                expected_runs=[],
                validation_errors={},
                noop_warnings=[],
                failed_runs=[],
                start_time_str="2026-03-29T14:00:00Z",
                t0_wall=_time.monotonic() - 1.0,
                exit_code=0,
                exit_reason="success",
            )
            data = json.loads((demo_root / "demo_manifest.json").read_text())
            source_files = data["source_files"]
            self.assertIn("scripts/run_unified.py", source_files)
            self.assertIn("scripts/sweep_and_report.py", source_files)
            self.assertNotIn("scripts/generate_team_summary.py", source_files)
            self.assertNotIn("scripts/generate_framework_report.py", source_files)


class TestExitPriority(unittest.TestCase):
    def test_preflight_failure_highest_priority(self) -> None:
        staged = [run_demo.EXIT_PARTIAL_FAILURE, run_demo.EXIT_ARTIFACT, run_demo.EXIT_PREFLIGHT]
        final = run_demo.EXIT_SUCCESS
        for p in run_demo._EXIT_PRIORITY:
            if p in staged:
                final = p
                break
        self.assertEqual(final, run_demo.EXIT_PREFLIGHT)

    def test_artifact_beats_noop_and_partial(self) -> None:
        staged = [run_demo.EXIT_PARTIAL_FAILURE, run_demo.EXIT_ARTIFACT, run_demo.EXIT_NOOP]
        final = run_demo.EXIT_SUCCESS
        for p in run_demo._EXIT_PRIORITY:
            if p in staged:
                final = p
                break
        self.assertEqual(final, run_demo.EXIT_ARTIFACT)

    def test_noop_beats_partial_failure(self) -> None:
        staged = [run_demo.EXIT_PARTIAL_FAILURE, run_demo.EXIT_NOOP]
        final = run_demo.EXIT_SUCCESS
        for p in run_demo._EXIT_PRIORITY:
            if p in staged:
                final = p
                break
        self.assertEqual(final, run_demo.EXIT_NOOP)


@pytest.mark.integration
class TestIntegrationFullPipeline(unittest.TestCase):
    """Full pipeline integration test.  Skipped unless -m integration is passed."""

    def test_full_run_exits_0(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            argv = [
                "run_demo.py",
                "--output-root", tmp,
                "--attacks", "fgsm",
                "--defenses", "median_preprocess",
                "--max-images", "1",
            ]
            with patch.object(sys, "argv", argv):
                code = run_demo.main()
            self.assertEqual(code, run_demo.EXIT_SUCCESS)
            subdirs = list(Path(tmp).iterdir())
            self.assertEqual(len(subdirs), 1)
            demo_root = subdirs[0]
            manifest_path = demo_root / "demo_manifest.json"
            self.assertTrue(manifest_path.is_file())
            data = json.loads(manifest_path.read_text())
            self.assertEqual(data["outcome"]["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
