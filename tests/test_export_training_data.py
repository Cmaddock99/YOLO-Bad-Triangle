from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from scripts import export_training_data


class ExportTrainingDataTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmpdir.name)
        self.framework_runs = self.repo / "outputs" / "framework_runs"
        self.framework_runs.mkdir(parents=True)

        clean_dir = self.repo / export_training_data.CLEAN_DIR_DEFAULT
        clean_dir.mkdir(parents=True)
        (clean_dir / "clean_a.jpg").write_bytes(b"clean-a")
        (clean_dir / "clean_b.png").write_bytes(b"clean-b")
        (self.repo / export_training_data.CHECKPOINT_DEFAULT).write_bytes(b"checkpoint")

        self._repo_patcher = mock.patch.object(export_training_data, "REPO", self.repo)
        self._repo_patcher.start()

    def tearDown(self) -> None:
        self._repo_patcher.stop()
        self._tmpdir.cleanup()

    def _set_mtime(self, path: Path, timestamp: int) -> None:
        os.utime(path, (timestamp, timestamp))

    def _write_signal(self, *, worst_attack: str = "fgsm", cycle_id: str | None = None) -> None:
        signal_path = self.repo / export_training_data.SIGNAL_PATH_DEFAULT
        signal_path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, object] = {"worst_attack": worst_attack}
        if cycle_id is not None:
            payload["cycle_id"] = cycle_id
        signal_path.write_text(json.dumps(payload))

    def _make_attack_images(
        self,
        run_root: Path,
        *,
        attack: str = "fgsm",
        validate_names: tuple[str, ...] = (),
        attack_names: tuple[str, ...] = (),
    ) -> None:
        for name in validate_names:
            path = run_root / f"validate_atk_{attack}" / "images" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(f"validate:{name}".encode())
        for name in attack_names:
            path = run_root / f"attack_{attack}" / "images" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(f"attack:{name}".encode())

    def _run_main(self, *args: str) -> str:
        stdout = io.StringIO()
        with redirect_stdout(stdout), mock.patch.object(
            sys, "argv", ["export_training_data.py", *args]
        ):
            export_training_data.main()
        return stdout.getvalue()

    def _zip_names(self, path: Path) -> list[str]:
        with zipfile.ZipFile(path) as archive:
            return sorted(archive.namelist())

    def test_resolve_runs_root_picks_newest_dir_across_generations(self) -> None:
        older_sweep = self.framework_runs / "sweep_20260326T094116Z"
        newer_cycle = self.framework_runs / "cycle_20260330_115004"
        older_sweep.mkdir()
        newer_cycle.mkdir()
        self._set_mtime(older_sweep, 1_700_000_000)
        self._set_mtime(newer_cycle, 1_800_000_000)

        resolved = export_training_data._resolve_runs_root("")

        self.assertEqual(resolved, newer_cycle.resolve())

    def test_from_signal_prefers_signal_cycle_root_when_present(self) -> None:
        signal_cycle = self.framework_runs / "cycle_20260330_115004"
        newer_other = self.framework_runs / "cycle_20260401_090000"
        signal_cycle.mkdir()
        newer_other.mkdir()
        self._make_attack_images(signal_cycle, validate_names=("signal_choice.jpg",))
        self._make_attack_images(newer_other, validate_names=("newest_generic.jpg",))
        self._set_mtime(signal_cycle, 1_700_000_000)
        self._set_mtime(newer_other, 1_800_000_000)
        self._write_signal(cycle_id=signal_cycle.name)

        output = self._run_main("--from-signal")
        output_zip = self.repo / "outputs" / "training_exports" / f"{signal_cycle.name}_training_data.zip"

        self.assertIn(f"Runs root:        {signal_cycle.resolve()}", output)
        self.assertTrue(output_zip.is_file())
        names = self._zip_names(output_zip)
        self.assertIn("adversarial/fgsm/signal_choice.jpg", names)
        self.assertNotIn("adversarial/fgsm/newest_generic.jpg", names)

    def test_from_signal_warns_and_falls_back_when_cycle_root_missing(self) -> None:
        older_sweep = self.framework_runs / "sweep_training_round2"
        newer_cycle = self.framework_runs / "cycle_20260330_115004"
        older_sweep.mkdir()
        newer_cycle.mkdir()
        self._make_attack_images(older_sweep, validate_names=("old_sweep.jpg",))
        self._make_attack_images(newer_cycle, validate_names=("fallback_cycle.jpg",))
        self._set_mtime(older_sweep, 1_700_000_000)
        self._set_mtime(newer_cycle, 1_800_000_000)
        self._write_signal(cycle_id="cycle_missing")

        output = self._run_main("--from-signal")
        output_zip = self.repo / "outputs" / "training_exports" / "cycle_missing_training_data.zip"

        self.assertIn("[warn] Signal-linked runs root not found:", output)
        self.assertIn(f"Runs root:        {newer_cycle.resolve()}", output)
        self.assertTrue(output_zip.is_file())
        self.assertIn("adversarial/fgsm/fallback_cycle.jpg", self._zip_names(output_zip))

    def test_validate_images_are_preferred_over_attack_images(self) -> None:
        run_root = self.framework_runs / "cycle_20260330_115004"
        run_root.mkdir()
        self._make_attack_images(
            run_root,
            validate_names=("preferred_validate.jpg",),
            attack_names=("legacy_attack.jpg",),
        )

        output_zip = self.repo / "outputs" / "training_exports" / "manual.zip"
        output = self._run_main(
            "--attacks",
            "fgsm",
            "--sweep-root",
            "outputs/framework_runs/cycle_20260330_115004",
            "--output-zip",
            "outputs/training_exports/manual.zip",
        )

        self.assertIn("fgsm: using validate_atk_fgsm/images/ (1 images)", output)
        names = self._zip_names(output_zip)
        self.assertIn("adversarial/fgsm/preferred_validate.jpg", names)
        self.assertNotIn("adversarial/fgsm/legacy_attack.jpg", names)

    def test_preset_square_retention_uses_isolated_default_zip_name(self) -> None:
        run_root = self.framework_runs / "cycle_20260330_115004"
        run_root.mkdir()
        self._make_attack_images(run_root, attack="deepfool", validate_names=("deepfool.jpg",))
        self._make_attack_images(run_root, attack="blur", validate_names=("blur.jpg",))
        self._make_attack_images(run_root, attack="square", validate_names=("square.jpg",))

        output = self._run_main(
            "--preset",
            "square_retention",
            "--sweep-root",
            "outputs/framework_runs/cycle_20260330_115004",
        )
        output_zip = self.repo / "outputs" / "training_exports" / "square_retention_training_data.zip"

        self.assertIn("Training preset: square_retention -> ['deepfool', 'blur', 'square']", output)
        self.assertTrue(output_zip.is_file())
        names = self._zip_names(output_zip)
        self.assertIn("adversarial/deepfool/deepfool.jpg", names)
        self.assertIn("adversarial/blur/blur.jpg", names)
        self.assertIn("adversarial/square/square.jpg", names)

    def test_rejects_multiple_attack_selection_modes(self) -> None:
        with self.assertRaises(ValueError):
            self._run_main("--preset", "square_retention", "--attacks", "square")

    def test_no_usable_attacks_exits_zero_without_writing_zip(self) -> None:
        run_root = self.framework_runs / "cycle_20260330_115004"
        run_root.mkdir()
        output_zip = self.repo / "outputs" / "training_exports" / "empty.zip"
        stdout = io.StringIO()

        with redirect_stdout(stdout), mock.patch.object(
            sys,
            "argv",
            [
                "export_training_data.py",
                "--attacks",
                "fgsm",
                "--sweep-root",
                "outputs/framework_runs/cycle_20260330_115004",
                "--output-zip",
                "outputs/training_exports/empty.zip",
            ],
        ):
            with self.assertRaises(SystemExit) as exit_ctx:
                export_training_data.main()

        self.assertEqual(exit_ctx.exception.code, 0)
        self.assertIn("No usable attacked image pairs found", stdout.getvalue())
        self.assertFalse(output_zip.exists())

    def test_preset_rejects_generic_training_zip_path(self) -> None:
        run_root = self.framework_runs / "cycle_20260330_115004"
        run_root.mkdir()
        self._make_attack_images(run_root, attack="square", validate_names=("square.jpg",))

        with self.assertRaises(ValueError):
            self._run_main(
                "--preset",
                "square_retention",
                "--sweep-root",
                "outputs/framework_runs/cycle_20260330_115004",
                "--output-zip",
                export_training_data.OUTPUT_ZIP_DEFAULT,
            )

    def test_manual_attack_list_deduplicates_entries(self) -> None:
        run_root = self.framework_runs / "cycle_20260330_115004"
        run_root.mkdir()
        self._make_attack_images(run_root, attack="square", validate_names=("square.jpg",))

        output_zip = self.repo / "outputs" / "training_exports" / "manual.zip"
        output = self._run_main(
            "--attacks",
            "square,square",
            "--sweep-root",
            "outputs/framework_runs/cycle_20260330_115004",
            "--output-zip",
            "outputs/training_exports/manual.zip",
        )

        self.assertIn("square: using validate_atk_square/images/ (1 images)", output)
        names = self._zip_names(output_zip)
        self.assertEqual(names.count("adversarial/square/square.jpg"), 1)
        self.assertIn("adversarial/square/square.jpg", names)

    def test_preset_can_export_subset_when_some_attacks_missing(self) -> None:
        run_root = self.framework_runs / "cycle_20260330_115004"
        run_root.mkdir()
        self._make_attack_images(run_root, attack="deepfool", validate_names=("deepfool.jpg",))
        self._make_attack_images(run_root, attack="square", validate_names=("square.jpg",))

        output = self._run_main(
            "--preset",
            "square_retention",
            "--sweep-root",
            "outputs/framework_runs/cycle_20260330_115004",
        )

        self.assertIn("[warn] No attacked images found for 'blur'", output)
        self.assertIn("adversarial: 1", output)
        output_zip = self.repo / "outputs" / "training_exports" / "square_retention_training_data.zip"
        names = self._zip_names(output_zip)
        self.assertIn("adversarial/deepfool/deepfool.jpg", names)
        self.assertIn("adversarial/square/square.jpg", names)
        self.assertNotIn("adversarial/blur/blur.jpg", names)

    def test_from_signal_and_preset_can_share_named_output_scheme(self) -> None:
        signal_cycle = self.framework_runs / "cycle_20260330_115004"
        signal_cycle.mkdir()
        self._make_attack_images(signal_cycle, validate_names=("signal_choice.jpg",))
        self._write_signal(cycle_id=signal_cycle.name)

        self._run_main("--from-signal")
        self.assertTrue(
            (self.repo / "outputs" / "training_exports" / f"{signal_cycle.name}_training_data.zip").is_file()
        )
        self._make_attack_images(signal_cycle, attack="deepfool", validate_names=("deepfool.jpg",))
        self._make_attack_images(signal_cycle, attack="blur", validate_names=("blur.jpg",))
        self._make_attack_images(signal_cycle, attack="square", validate_names=("square.jpg",))
        self._run_main("--preset", "square_retention", "--sweep-root", f"outputs/framework_runs/{signal_cycle.name}")
        self.assertTrue(
            (self.repo / "outputs" / "training_exports" / "square_retention_training_data.zip").is_file()
        )


if __name__ == "__main__":
    unittest.main()
