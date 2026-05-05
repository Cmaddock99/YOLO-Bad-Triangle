from __future__ import annotations

import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from scripts import sweep_and_report


class _FakeTqdm:
    instances: list["_FakeTqdm"] = []

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.args = args
        self.kwargs = kwargs
        self.total = kwargs.get("total")
        self.desc = kwargs.get("desc")
        self.updates: list[int] = []
        self.descriptions: list[str] = []
        self.writes: list[str] = []
        _FakeTqdm.instances.append(self)

    def __enter__(self) -> "_FakeTqdm":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False

    def update(self, n: int = 1) -> None:
        self.updates.append(n)

    def set_description(self, text: str) -> None:
        self.descriptions.append(text)

    def write(self, text: str) -> None:
        self.writes.append(text)


class SweepAndReportScriptTest(unittest.TestCase):
    def _write_resume_artifacts(
        self,
        run_dir: Path,
        *,
        config_sha: str = "cfg",
        attack_signature: str = '{"attack":"fgsm"}',
        defense_signature: str = '{"defense":"none"}',
        checkpoint_sha: str = "checkpoint",
        defense_shas: list[str] | None = None,
        seed: int = 42,
        validation_enabled: bool = False,
        reporting_context: dict[str, object] | None = None,
    ) -> None:
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "metrics.json").write_text("{}", encoding="utf-8")
        (run_dir / "predictions.jsonl").write_text('{"image_id":"a.jpg","boxes":[],"scores":[],"class_ids":[],"metadata":{}}\n', encoding="utf-8")
        (run_dir / "run_summary.json").write_text(
            json.dumps(
                {
                    "attack": {"signature": attack_signature},
                    "defense": {"signature": defense_signature},
                    "seed": seed,
                    "validation": {"enabled": validation_enabled},
                    "reporting_context": reporting_context or {},
                    "provenance": {
                        "config_fingerprint_sha256": config_sha,
                        "checkpoint_fingerprint_sha256": checkpoint_sha,
                        "defense_checkpoints": [
                            {"sha256": value, "path": f"/tmp/{value}.pt"}
                            for value in (defense_shas or [])
                        ],
                    },
                }
            ),
            encoding="utf-8",
        )

    def test_parse_attacks_from_csv(self) -> None:
        attacks = sweep_and_report._parse_attacks("fgsm, blur ,pgd")
        self.assertEqual(attacks, ["fgsm", "blur", "pgd"])

    def test_parse_attacks_normalizes_aliases_and_dedupes(self) -> None:
        attacks = sweep_and_report._parse_attacks("bim, pgd, gaussian_blur, blur")
        self.assertEqual(attacks, ["pgd", "blur"])

    def test_parse_attacks_rejects_empty(self) -> None:
        with self.assertRaises(ValueError):
            sweep_and_report._parse_attacks(" , , ")

    def test_resolve_all_attacks_returns_canonical_names_only(self) -> None:
        attacks = sweep_and_report._resolve_all_plugins("all", "attack")
        self.assertEqual(attacks, list(sweep_and_report.CANONICAL_ATTACKS_ALL))

    def test_resolve_all_attacks_uses_profile_canonical_core_scope(self) -> None:
        attacks = sweep_and_report._resolve_all_plugins(
            "all",
            "attack",
            profile_name="yolo11n_lab_v1",
            include_extra=False,
        )
        self.assertEqual(
            attacks,
            ["fgsm", "pgd", "deepfool", "eot_pgd", "dispersion_reduction", "blur", "square"],
        )

    def test_resolve_all_defenses_uses_profile_canonical_core_scope(self) -> None:
        defenses = sweep_and_report._resolve_all_plugins(
            "all",
            "defense",
            profile_name="yolo11n_lab_v1",
            include_extra=False,
        )
        self.assertEqual(
            defenses,
            ["bit_depth", "jpeg_preprocess", "median_preprocess"],
        )

    def test_default_max_images_for_presets(self) -> None:
        self.assertEqual(sweep_and_report._default_max_images("smoke"), 8)
        self.assertEqual(sweep_and_report._default_max_images("full"), 0)

    def test_default_attacks_are_canonical(self) -> None:
        self.assertEqual(sweep_and_report.DEFAULT_ATTACKS, ("blur", "deepfool", "fgsm", "pgd"))

    def test_experiment_command_contains_required_overrides(self) -> None:
        command = sweep_and_report._experiment_command(
            python_bin="./.venv/bin/python",
            config=Path("configs/default.yaml"),
            profile=None,
            output_root=Path("outputs/framework_runs/sweep_x"),
            run_name="attack_fgsm",
            attack_name="fgsm",
            defense_name="none",
            seed=42,
            max_images=8,
            validation_enabled=False,
        )
        rendered = " ".join(command)
        self.assertIn("src/lab/runners/run_experiment.py", rendered)
        self.assertIn("runner.run_name=attack_fgsm", rendered)
        self.assertIn("attack.name=fgsm", rendered)
        self.assertIn("summary.enabled=false", rendered)

    def test_experiment_overrides_place_extra_overrides_before_generated_values(self) -> None:
        overrides = sweep_and_report._experiment_overrides(
            output_root=Path("outputs/framework_runs/sweep_x"),
            run_name="attack_pretrained_patch",
            attack_name="pretrained_patch",
            defense_name="none",
            seed=42,
            max_images=8,
            validation_enabled=False,
            extra_overrides=[
                "attack.params.artifact_path=/tmp/patch.png",
                "runner.run_name=user_requested_name",
            ],
        )

        self.assertEqual(overrides[0], "attack.params.artifact_path=/tmp/patch.png")
        self.assertEqual(overrides[1], "runner.run_name=user_requested_name")
        self.assertIn("runner.run_name=attack_pretrained_patch", overrides)
        self.assertGreater(
            overrides.index("runner.run_name=attack_pretrained_patch"),
            overrides.index("runner.run_name=user_requested_name"),
        )

    def test_repo_script_commands_use_shared_builder_paths(self) -> None:
        report_command = sweep_and_report._generate_framework_report_command(
            python_bin="python",
            runs_root=Path("outputs/framework_runs/sweep_x"),
            output_dir=Path("outputs/framework_reports/sweep_x"),
        )
        team_command = sweep_and_report._generate_team_summary_command(
            python_bin="python",
            report_root=Path("outputs/framework_reports/sweep_x"),
        )
        summary_command = sweep_and_report._print_summary_command(
            python_bin="python",
            baseline_dir=Path("outputs/framework_runs/sweep_x/baseline_none"),
            attack_dir=Path("outputs/framework_runs/sweep_x/attack_fgsm"),
        )

        self.assertEqual(report_command[:2], ["python", str(sweep_and_report.REPO_ROOT / "scripts/generate_framework_report.py")])
        self.assertEqual(team_command[:2], ["python", str(sweep_and_report.REPO_ROOT / "scripts/generate_team_summary.py")])
        self.assertEqual(summary_command[:2], ["python", str(sweep_and_report.REPO_ROOT / "scripts/print_summary.py")])
        self.assertIn("--runs-root", report_command)
        self.assertIn("--report-root", team_command)
        self.assertIn("--baseline", summary_command)

    def test_list_plugins_output_contains_core_extra_and_alias_sections(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            sweep_and_report._list_plugins("yolo11n_lab_v1")

        output = buffer.getvalue()
        self.assertIn("Profile plugin inventory: yolo11n_lab_v1", output)
        self.assertIn("Baseline sentinels:", output)
        self.assertIn("attack: none", output)
        self.assertIn("defense: none, identity", output)
        self.assertIn("Core attacks:", output)
        self.assertIn("Extra/manual-only attacks:", output)
        self.assertIn("All registered attack aliases:", output)
        self.assertIn("Core defenses:", output)
        self.assertIn("Extra/manual-only defenses:", output)
        self.assertIn("All registered defense aliases:", output)

    def test_main_list_plugins_uses_explicit_profile_when_passed(self) -> None:
        argv = [
            "sweep_and_report.py",
            "--profile",
            "manual_profile",
            "--list-plugins",
        ]
        with patch.object(sys, "argv", argv):
            with patch.object(sweep_and_report, "_list_plugins") as mock_list_plugins:
                sweep_and_report.main()

        mock_list_plugins.assert_called_once_with("manual_profile")

    def test_main_list_plugins_defaults_to_v1_profile(self) -> None:
        argv = [
            "sweep_and_report.py",
            "--config",
            str(REPO_ROOT / "configs/default.yaml"),
            "--list-plugins",
        ]
        with patch.object(sys, "argv", argv):
            with patch.object(sweep_and_report, "_list_plugins") as mock_list_plugins:
                sweep_and_report.main()

        mock_list_plugins.assert_called_once_with("yolo11n_lab_v1")

    def test_dashboard_command_targets_local_output_and_compat_mirror(self) -> None:
        command = sweep_and_report._generate_dashboard_command(
            python_bin="python",
            report_root=Path("outputs/framework_reports/custom_report"),
            output_path=Path("outputs/framework_reports/custom_report/dashboard.html"),
            compat_output_path=Path("outputs/dashboard.html"),
            update_pages=False,
        )

        self.assertEqual(command[:2], ["python", str(sweep_and_report.REPO_ROOT / "scripts/generate_dashboard.py")])
        self.assertIn("--report-dir", command)
        self.assertIn("--output", command)
        self.assertIn("--compat-output", command)
        self.assertIn("--no-pages", command)

    def test_dashboard_command_omits_compat_output_when_not_requested(self) -> None:
        command = sweep_and_report._generate_dashboard_command(
            python_bin="python",
            report_root=Path("outputs/framework_reports/custom_report"),
            output_path=Path("outputs/framework_reports/custom_report/dashboard.html"),
            compat_output_path=None,
            update_pages=False,
        )

        self.assertEqual(command[:2], ["python", str(sweep_and_report.REPO_ROOT / "scripts/generate_dashboard.py")])
        self.assertIn("--report-dir", command)
        self.assertIn("--output", command)
        self.assertNotIn("--compat-output", command)
        self.assertIn("--no-pages", command)

    def test_run_command_adds_src_pythonpath(self) -> None:
        with patch("scripts.sweep_and_report.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = ""

            ok = sweep_and_report._run_command(["python", "script.py"], dry_run=False)

        self.assertTrue(ok)
        env = mock_run.call_args.kwargs["env"]
        self.assertIn(str(sweep_and_report.REPO_ROOT / "src"), env["PYTHONPATH"])

    def test_run_command_can_skip_src_pythonpath(self) -> None:
        with patch.dict(os.environ, {"PYTHONPATH": "existing"}, clear=True):
            with patch("scripts.sweep_and_report.subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = ""
                mock_run.return_value.stderr = ""

                ok = sweep_and_report._run_command(
                    ["python", "script.py"],
                    dry_run=False,
                    include_src_pythonpath=False,
                )

        self.assertTrue(ok)
        env = mock_run.call_args.kwargs["env"]
        self.assertEqual(env["PYTHONPATH"], "existing")

    def test_metrics_exists_helper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir(parents=True, exist_ok=True)
            self.assertFalse(sweep_and_report._metrics_exists(run_dir))
            (run_dir / "metrics.json").write_text("{}", encoding="utf-8")
            self.assertTrue(sweep_and_report._metrics_exists(run_dir))

    def test_check_resume_skips_exact_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            reporting_context = {"run_role": "attack_only", "authority": "authoritative"}
            self._write_resume_artifacts(
                run_dir,
                config_sha="cfg123",
                checkpoint_sha="ckpt123",
                defense_shas=["def1", "def2"],
                reporting_context=reporting_context,
                validation_enabled=True,
            )

            action, reason = sweep_and_report._check_resume(
                run_dir,
                {
                    "config_fingerprint_sha256": "cfg123",
                    "attack_signature": '{"attack":"fgsm"}',
                    "defense_signature": '{"defense":"none"}',
                    "checkpoint_fingerprint_sha256": "ckpt123",
                    "defense_checkpoints": [
                        {"sha256": "def2"},
                        {"sha256": "def1"},
                    ],
                    "seed": 42,
                    "validation_enabled": True,
                    "reporting_context": reporting_context,
                },
            )

            self.assertEqual(action, "skipped_exact")
            self.assertIn("exact run-intent match", reason)

    def test_check_resume_reruns_partial_when_predictions_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "metrics.json").write_text("{}", encoding="utf-8")
            (run_dir / "run_summary.json").write_text("{}", encoding="utf-8")

            action, reason = sweep_and_report._check_resume(run_dir, {})

            self.assertEqual(action, "reran_partial")
            self.assertIn("predictions.jsonl", reason)

    def test_check_resume_reruns_partial_when_run_summary_is_malformed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "metrics.json").write_text("{}", encoding="utf-8")
            (run_dir / "predictions.jsonl").write_text("{}", encoding="utf-8")
            (run_dir / "run_summary.json").write_text("{bad-json", encoding="utf-8")

            action, reason = sweep_and_report._check_resume(run_dir, {})

            self.assertEqual(action, "reran_partial")
            self.assertIn("run_summary.json missing or malformed", reason)

    def test_check_resume_reruns_on_run_intent_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            self._write_resume_artifacts(run_dir, config_sha="cfg123", seed=42)

            action, reason = sweep_and_report._check_resume(
                run_dir,
                {
                    "config_fingerprint_sha256": "cfg999",
                    "attack_signature": '{"attack":"fgsm"}',
                    "defense_signature": '{"defense":"none"}',
                    "checkpoint_fingerprint_sha256": "checkpoint",
                    "defense_checkpoints": [],
                    "seed": 42,
                    "validation_enabled": False,
                    "reporting_context": {},
                },
            )

            self.assertEqual(action, "reran_mismatch")
            self.assertIn("config_fingerprint_sha256", reason)

    def test_main_dry_run_reports_deduped_attack_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp) / "runs"
            report_root = Path(tmp) / "report"
            buffer = io.StringIO()
            argv = [
                "sweep_and_report.py",
                "--config",
                str(REPO_ROOT / "configs/default.yaml"),
                "--python-bin",
                sys.executable,
                "--runs-root",
                str(runs_root),
                "--report-root",
                str(report_root),
                "--attacks",
                "bim,pgd,gaussian_blur",
                "--defenses",
                "none",
                "--phases",
                "2",
                "--dry-run",
            ]
            with patch.object(sys, "argv", argv):
                with redirect_stdout(buffer):
                    sweep_and_report.main()
            manifest = json.loads((report_root / "sweep_manifest.json").read_text(encoding="utf-8"))

        output = buffer.getvalue()
        self.assertIn("Attacks:      ['pgd', 'blur']", output)
        self.assertIn("Total runs:   2", output)
        self.assertEqual(manifest["aggregate"]["total"], 2)

    def test_profile_defaults_to_canonical_catalogs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp) / "runs"
            report_root = Path(tmp) / "report"
            argv = [
                "sweep_and_report.py",
                "--profile",
                "yolo11n_lab_v1",
                "--python-bin",
                sys.executable,
                "--runs-root",
                str(runs_root),
                "--report-root",
                str(report_root),
                "--phases",
                "2",
                "--dry-run",
            ]
            with patch.object(sys, "argv", argv):
                sweep_and_report.main()

            manifest = json.loads((report_root / "sweep_manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["pipeline_profile"], "yolo11n_lab_v1")
        self.assertEqual(manifest["authoritative_metric"], "mAP50")
        self.assertEqual(
            manifest["requested_attacks"],
            ["fgsm", "pgd", "deepfool", "eot_pgd", "dispersion_reduction", "blur", "square"],
        )
        self.assertEqual(
            manifest["requested_defenses"],
            ["bit_depth", "jpeg_preprocess", "median_preprocess"],
        )

    def test_profile_all_expansion_uses_canonical_core_catalogs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp) / "runs"
            report_root = Path(tmp) / "report"
            argv = [
                "sweep_and_report.py",
                "--profile",
                "yolo11n_lab_v1",
                "--python-bin",
                sys.executable,
                "--runs-root",
                str(runs_root),
                "--report-root",
                str(report_root),
                "--attacks",
                "all",
                "--defenses",
                "all",
                "--phases",
                "2",
                "--dry-run",
            ]
            with patch.object(sys, "argv", argv):
                sweep_and_report.main()

            manifest = json.loads((report_root / "sweep_manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(
            manifest["requested_attacks"],
            ["fgsm", "pgd", "deepfool", "eot_pgd", "dispersion_reduction", "blur", "square"],
        )
        self.assertEqual(
            manifest["requested_defenses"],
            ["bit_depth", "jpeg_preprocess", "median_preprocess"],
        )

    def test_main_dry_run_forwards_repeatable_set_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp) / "runs"
            report_root = Path(tmp) / "report"
            buffer = io.StringIO()
            argv = [
                "sweep_and_report.py",
                "--config",
                str(REPO_ROOT / "configs/default.yaml"),
                "--python-bin",
                sys.executable,
                "--runs-root",
                str(runs_root),
                "--report-root",
                str(report_root),
                "--attacks",
                "pretrained_patch",
                "--defenses",
                "none",
                "--phases",
                "2",
                "--set",
                "attack.params.artifact_path=/tmp/patch.png",
                "--set",
                "attack.params.clean_detect_conf=0.6",
                "--dry-run",
            ]
            with patch.object(sys, "argv", argv):
                with redirect_stdout(buffer):
                    sweep_and_report.main()

        output = buffer.getvalue()
        self.assertIn("--set attack.params.artifact_path=/tmp/patch.png", output)
        self.assertIn("--set attack.params.clean_detect_conf=0.6", output)


class WS7SweepNoPagesTest(unittest.TestCase):
    """Item 6: --no-pages passed to dashboard by default; --update-pages suppresses it."""

    _BASE_ARGV = [
        "sweep_and_report.py",
        "--config",
        str(REPO_ROOT / "configs/default.yaml"),
        "--python-bin",
        sys.executable,
        "--attacks",
        "pgd",
        "--defenses",
        "none",
        "--phases",
        "4",
        "--dry-run",
    ]

    def _captured_dashboard_args(self, extra_argv: list[str]) -> list[str]:
        """Run sweep in dry-run mode and capture args passed to generate_dashboard.py."""
        captured: list[list[str]] = []

        original_run_command = sweep_and_report._run_command

        def capturing_run_command(cmd: list[str], **kwargs: object) -> bool:
            if "generate_dashboard.py" in " ".join(str(c) for c in cmd):
                captured.append([str(c) for c in cmd])
            return original_run_command(cmd, **kwargs)

        with tempfile.TemporaryDirectory() as tmp:
            argv = self._BASE_ARGV + [
                "--runs-root", str(Path(tmp) / "runs"),
                "--report-root", str(Path(tmp) / "report"),
            ] + extra_argv
            with patch.object(sys, "argv", argv):
                with patch.object(sweep_and_report, "_run_command", side_effect=capturing_run_command):
                    try:
                        sweep_and_report.main()
                    except SystemExit:
                        pass

        self.assertTrue(captured, "generate_dashboard.py was never invoked")
        return captured[0]

    def test_no_pages_passed_by_default(self) -> None:
        """Without --update-pages, dashboard command includes --no-pages."""
        args = self._captured_dashboard_args([])
        flat = " ".join(args)
        self.assertIn("--no-pages", flat)
        self.assertIn("--report-dir", flat)
        self.assertIn("--compat-output", flat)
        self.assertNotIn("--reports-root", flat)
        report_dir = Path(args[args.index("--report-dir") + 1])
        output = Path(args[args.index("--output") + 1])
        compat_output = Path(args[args.index("--compat-output") + 1])
        self.assertEqual(output, report_dir / "dashboard.html")
        self.assertEqual(compat_output, sweep_and_report.REPO_ROOT / "outputs/dashboard.html")

    def test_update_pages_omits_no_pages_flag(self) -> None:
        """With --update-pages, --no-pages is NOT added to the dashboard command."""
        args = self._captured_dashboard_args(["--update-pages"])
        flat = " ".join(args)
        self.assertNotIn("--no-pages", flat)
        self.assertIn("--report-dir", flat)

    def test_no_compat_dashboard_omits_compat_output_flag(self) -> None:
        args = self._captured_dashboard_args(["--no-compat-dashboard"])
        flat = " ".join(args)
        self.assertIn("--report-dir", flat)
        self.assertIn("--output", flat)
        self.assertNotIn("--compat-output", flat)


class SweepAndReportOptionalExtrasTest(unittest.TestCase):
    _BASE_ARGV = [
        "sweep_and_report.py",
        "--config",
        str(REPO_ROOT / "configs/default.yaml"),
        "--python-bin",
        sys.executable,
        "--attacks",
        "pgd",
        "--defenses",
        "none",
        "--phases",
        "4",
        "--dry-run",
    ]

    def _captured_phase4_commands(self, extra_argv: list[str]) -> list[list[str]]:
        captured: list[list[str]] = []
        original_run_command = sweep_and_report._run_command

        def capturing_run_command(cmd: list[str], **kwargs: object) -> bool:
            captured.append([str(c) for c in cmd])
            return original_run_command(cmd, **kwargs)

        with tempfile.TemporaryDirectory() as tmp:
            argv = self._BASE_ARGV + [
                "--runs-root",
                str(Path(tmp) / "runs"),
                "--report-root",
                str(Path(tmp) / "report"),
            ] + extra_argv
            with patch.object(sys, "argv", argv):
                with patch.object(sweep_and_report, "_run_command", side_effect=capturing_run_command):
                    sweep_and_report.main()
        return captured

    def _phase4_stdout(self, extra_argv: list[str]) -> str:
        buffer = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            argv = self._BASE_ARGV + [
                "--runs-root",
                str(Path(tmp) / "runs"),
                "--report-root",
                str(Path(tmp) / "report"),
            ] + extra_argv
            with patch.object(sys, "argv", argv):
                with redirect_stdout(buffer):
                    sweep_and_report.main()
        return buffer.getvalue()

    def test_no_failure_gallery_skips_failure_gallery_command(self) -> None:
        commands = self._captured_phase4_commands(["--no-failure-gallery"])
        rendered = [" ".join(command) for command in commands]
        self.assertTrue(any("generate_framework_report.py" in command for command in rendered))
        self.assertTrue(any("generate_dashboard.py" in command for command in rendered))
        self.assertFalse(any("generate_failure_gallery.py" in command for command in rendered))

    def test_final_stdout_omits_disabled_optional_artifact_lines(self) -> None:
        output = self._phase4_stdout([
            "--no-team-summary",
            "--no-failure-gallery",
            "--no-compat-dashboard",
        ])

        self.assertIn("Aggregate CSV:", output)
        self.assertIn("Aggregate Markdown:", output)
        self.assertIn("Dashboard (local):", output)
        self.assertNotIn("Team JSON summary:", output)
        self.assertNotIn("Team MD summary:", output)
        self.assertNotIn("Failure Gallery:", output)
        self.assertNotIn("Dashboard (compat):", output)


class SweepAndReportPhase4InProcessTest(unittest.TestCase):
    _BASE_ARGV = [
        "sweep_and_report.py",
        "--config",
        str(REPO_ROOT / "configs/default.yaml"),
        "--python-bin",
        sys.executable,
        "--attacks",
        "pgd",
        "--defenses",
        "none",
        "--phases",
        "4",
    ]

    def _run_phase4(
        self,
        extra_argv: list[str],
    ) -> tuple[Path, Path]:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp) / "runs"
            report_root = Path(tmp) / "report"
            argv = self._BASE_ARGV + [
                "--runs-root",
                str(runs_root),
                "--report-root",
                str(report_root),
            ] + extra_argv
            with patch.object(sys, "argv", argv):
                sweep_and_report.main()
            return runs_root.resolve(), report_root.resolve()

    def test_non_dry_run_phase4_calls_framework_report_helper_once(self) -> None:
        with patch.object(sweep_and_report, "_write_framework_report") as mock_framework_report:
            with patch.object(sweep_and_report, "_write_team_summary") as mock_team_summary:
                with patch.object(sweep_and_report, "_write_failure_gallery") as mock_failure_gallery:
                    with patch.object(sweep_and_report, "_write_dashboard") as mock_dashboard:
                        with patch.object(sweep_and_report, "_run_command") as mock_run_command:
                            runs_root, report_root = self._run_phase4([])

        mock_framework_report.assert_called_once_with(
            runs_root=runs_root.resolve(),
            report_root=report_root.resolve(),
        )
        mock_team_summary.assert_called_once_with(report_root=report_root.resolve())
        mock_failure_gallery.assert_called_once_with(
            runs_root=runs_root.resolve(),
            output_path=report_root.resolve() / "failure_gallery.html",
        )
        mock_dashboard.assert_called_once_with(
            report_root=report_root.resolve(),
            output_path=report_root.resolve() / "dashboard.html",
            compat_output_path=(sweep_and_report.REPO_ROOT / "outputs/dashboard.html").resolve(),
            update_pages=False,
        )
        mock_run_command.assert_not_called()

    def test_non_dry_run_phase4_passes_dashboard_paths_and_update_pages(self) -> None:
        scenarios = [
            {
                "extra_argv": [],
                "compat_output_path": (sweep_and_report.REPO_ROOT / "outputs/dashboard.html").resolve(),
                "update_pages": False,
            },
            {
                "extra_argv": ["--update-pages", "--no-compat-dashboard"],
                "compat_output_path": None,
                "update_pages": True,
            },
        ]

        for scenario in scenarios:
            with self.subTest(extra_argv=scenario["extra_argv"]):
                with patch.object(sweep_and_report, "_write_framework_report"):
                    with patch.object(sweep_and_report, "_write_team_summary"):
                        with patch.object(sweep_and_report, "_write_failure_gallery"):
                            with patch.object(sweep_and_report, "_write_dashboard") as mock_dashboard:
                                with patch.object(sweep_and_report, "_run_command") as mock_run_command:
                                    with tempfile.TemporaryDirectory() as tmp:
                                        runs_root = Path(tmp) / "runs"
                                        report_root = Path(tmp) / "report"
                                        argv = self._BASE_ARGV + [
                                            "--runs-root",
                                            str(runs_root),
                                            "--report-root",
                                            str(report_root),
                                        ] + scenario["extra_argv"]
                                        with patch.object(sys, "argv", argv):
                                            sweep_and_report.main()

                mock_dashboard.assert_called_once_with(
                    report_root=report_root.resolve(),
                    output_path=report_root.resolve() / "dashboard.html",
                    compat_output_path=scenario["compat_output_path"],
                    update_pages=scenario["update_pages"],
                )
                mock_run_command.assert_not_called()

    def test_non_dry_run_phase4_skips_team_summary_when_disabled(self) -> None:
        with patch.object(sweep_and_report, "_write_framework_report"):
            with patch.object(sweep_and_report, "_write_team_summary") as mock_team_summary:
                with patch.object(sweep_and_report, "_write_failure_gallery"):
                    with patch.object(sweep_and_report, "_write_dashboard"):
                        self._run_phase4(["--no-team-summary"])

        mock_team_summary.assert_not_called()

    def test_non_dry_run_phase4_skips_failure_gallery_when_disabled(self) -> None:
        with patch.object(sweep_and_report, "_write_framework_report"):
            with patch.object(sweep_and_report, "_write_team_summary"):
                with patch.object(sweep_and_report, "_write_failure_gallery") as mock_failure_gallery:
                    with patch.object(sweep_and_report, "_write_dashboard"):
                        self._run_phase4(["--no-failure-gallery"])

        mock_failure_gallery.assert_not_called()

    def test_non_dry_run_phase4_swallows_failure_gallery_exception(self) -> None:
        with patch.object(sweep_and_report, "_write_framework_report"):
            with patch.object(sweep_and_report, "_write_team_summary"):
                with patch.object(
                    sweep_and_report,
                    "_write_failure_gallery",
                    side_effect=RuntimeError("gallery failed"),
                ) as mock_failure_gallery:
                    with patch.object(sweep_and_report, "_write_dashboard") as mock_dashboard:
                        self._run_phase4([])

        mock_failure_gallery.assert_called_once()
        mock_dashboard.assert_called_once()

    def test_non_dry_run_phase4_raises_on_dashboard_failure(self) -> None:
        with patch.object(sweep_and_report, "_write_framework_report"):
            with patch.object(sweep_and_report, "_write_team_summary"):
                with patch.object(sweep_and_report, "_write_failure_gallery"):
                    with patch.object(
                        sweep_and_report,
                        "_write_dashboard",
                        side_effect=RuntimeError("dashboard failed"),
                    ):
                        with self.assertRaises(SystemExit) as excinfo:
                            self._run_phase4([])

        self.assertEqual(excinfo.exception.code, 2)


class SweepAndReportPhase4ProgressTest(unittest.TestCase):
    _BASE_ARGV = [
        "sweep_and_report.py",
        "--config",
        str(REPO_ROOT / "configs/default.yaml"),
        "--python-bin",
        sys.executable,
        "--attacks",
        "pgd",
        "--defenses",
        "none",
        "--phases",
        "4",
        "--dry-run",
    ]

    def _phase4_bar_for(self, extra_argv: list[str]) -> _FakeTqdm:
        _FakeTqdm.instances = []
        with tempfile.TemporaryDirectory() as tmp:
            argv = self._BASE_ARGV + [
                "--runs-root",
                str(Path(tmp) / "runs"),
                "--report-root",
                str(Path(tmp) / "report"),
            ] + extra_argv
            with patch.object(sys, "argv", argv):
                with patch.object(sweep_and_report, "tqdm", _FakeTqdm):
                    sweep_and_report.main()
        self.assertEqual(len(_FakeTqdm.instances), 1)
        return _FakeTqdm.instances[0]

    def test_phase4_counts_four_steps_by_default(self) -> None:
        bar = self._phase4_bar_for([])
        self.assertEqual(bar.total, 4)
        self.assertEqual(sum(bar.updates), 4)
        self.assertIn("  reports | team summary done", bar.descriptions)
        self.assertIn("  reports | failure gallery done", bar.descriptions)
        self.assertIn("  reports | dashboard done", bar.descriptions)

    def test_phase4_counts_three_steps_without_team_summary(self) -> None:
        bar = self._phase4_bar_for(["--no-team-summary"])
        self.assertEqual(bar.total, 3)
        self.assertEqual(sum(bar.updates), 3)
        self.assertNotIn("  reports | team summary done", bar.descriptions)
        self.assertIn("  reports | failure gallery done", bar.descriptions)
        self.assertIn("  reports | dashboard done", bar.descriptions)

    def test_phase4_counts_three_steps_without_failure_gallery(self) -> None:
        bar = self._phase4_bar_for(["--no-failure-gallery"])
        self.assertEqual(bar.total, 3)
        self.assertEqual(sum(bar.updates), 3)
        self.assertIn("  reports | team summary done", bar.descriptions)
        self.assertNotIn("  reports | failure gallery done", bar.descriptions)
        self.assertIn("  reports | dashboard done", bar.descriptions)

    def test_phase4_counts_two_steps_without_team_summary_or_failure_gallery(self) -> None:
        bar = self._phase4_bar_for(["--no-team-summary", "--no-failure-gallery"])
        self.assertEqual(bar.total, 2)
        self.assertEqual(sum(bar.updates), 2)
        self.assertNotIn("  reports | team summary done", bar.descriptions)
        self.assertNotIn("  reports | failure gallery done", bar.descriptions)
        self.assertIn("  reports | dashboard done", bar.descriptions)


if __name__ == "__main__":
    unittest.main()
