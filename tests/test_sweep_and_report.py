from __future__ import annotations

import io
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


class SweepAndReportScriptTest(unittest.TestCase):
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

    def test_default_max_images_for_presets(self) -> None:
        self.assertEqual(sweep_and_report._default_max_images("smoke"), 8)
        self.assertEqual(sweep_and_report._default_max_images("full"), 0)

    def test_default_attacks_are_canonical(self) -> None:
        self.assertEqual(sweep_and_report.DEFAULT_ATTACKS, ("blur", "deepfool", "fgsm", "pgd"))

    def test_experiment_command_contains_required_overrides(self) -> None:
        command = sweep_and_report._experiment_command(
            python_bin="./.venv/bin/python",
            config=Path("configs/default.yaml"),
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
                str(REPO_ROOT / ".venv/bin/python"),
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

        output = buffer.getvalue()
        self.assertIn("Attacks:      ['pgd', 'blur']", output)
        self.assertIn("Total runs:   2", output)


if __name__ == "__main__":
    unittest.main()
