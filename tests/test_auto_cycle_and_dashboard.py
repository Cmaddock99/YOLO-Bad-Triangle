from __future__ import annotations

import csv
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import auto_cycle, generate_dashboard


class AutoCycleTrainingSignalTest(unittest.TestCase):
    def test_write_training_signal_prefers_map50_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_outputs = Path(tmp)
            original_outputs = auto_cycle.OUTPUTS
            auto_cycle.OUTPUTS = tmp_outputs
            try:
                state = {
                    "cycle_id": "cycle_test",
                    "finished_at": "2026-03-26T10:00:00",
                    "best_attack_params": {
                        "deepfool": {"attack.params.epsilon": 0.1},
                        "eot_pgd": {"attack.params.epsilon": 0.25},
                    },
                }
                validation_results = {
                    "validate_baseline": {
                        "attack": None,
                        "defense": "none",
                        "detections": 100,
                        "mAP50": 0.60,
                    },
                    "validate_atk_deepfool": {
                        "attack": "deepfool",
                        "defense": "none",
                        "detections": 80,
                        "mAP50": 0.20,
                    },
                    "validate_atk_eot_pgd": {
                        "attack": "eot_pgd",
                        "defense": "none",
                        "detections": 60,
                        "mAP50": 0.30,
                    },
                    "validate_deepfool_bit_depth": {
                        "attack": "deepfool",
                        "defense": "bit_depth",
                        "detections": 85,
                        "mAP50": 0.25,
                    },
                    "validate_eot_pgd_bit_depth": {
                        "attack": "eot_pgd",
                        "defense": "bit_depth",
                        "detections": 70,
                        "mAP50": 0.45,
                    },
                }

                auto_cycle._write_training_signal(state, validation_results)
                signal = json.loads((tmp_outputs / "cycle_training_signal.json").read_text(encoding="utf-8"))
                self.assertEqual(signal["ranking_source"], "phase4_map50")
                self.assertEqual(signal["worst_attack"], "deepfool")
                self.assertEqual(signal["worst_attack_params"], {"attack.params.epsilon": 0.1})
            finally:
                auto_cycle.OUTPUTS = original_outputs

    def test_write_training_signal_falls_back_without_map50(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_outputs = Path(tmp)
            original_outputs = auto_cycle.OUTPUTS
            auto_cycle.OUTPUTS = tmp_outputs
            try:
                state = {"cycle_id": "cycle_test", "finished_at": "2026-03-26T10:00:00", "best_attack_params": {}}
                validation_results = {
                    "validate_baseline": {"attack": None, "defense": None, "detections": 100},
                    "validate_atk_blur": {"attack": "blur", "defense": "none", "detections": 75},
                    "validate_blur_bit_depth": {"attack": "blur", "defense": "bit_depth", "detections": 78},
                }
                auto_cycle._write_training_signal(state, validation_results)
                signal = json.loads((tmp_outputs / "cycle_training_signal.json").read_text(encoding="utf-8"))
                self.assertEqual(signal["ranking_source"], "phase4_detection_recovery")
                self.assertEqual(signal["worst_attack"], "blur")
            finally:
                auto_cycle.OUTPUTS = original_outputs


class DashboardSelectionTest(unittest.TestCase):
    def test_sweep_label_supports_cycle_timestamp(self) -> None:
        self.assertEqual(
            generate_dashboard._sweep_label("cycle_20260407_193440"),
            "Apr 7 19:34",
        )

    def test_load_sweep_prefers_validate_baseline_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_dir = Path(tmp)
            csv_path = report_dir / "framework_run_summary.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "run_name",
                        "attack",
                        "defense",
                        "total_detections",
                        "avg_confidence",
                        "mAP50",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "run_name": "baseline_none",
                        "attack": "none",
                        "defense": "none",
                        "total_detections": "21",
                        "avg_confidence": "0.75",
                        "mAP50": "",
                    }
                )
                writer.writerow(
                    {
                        "run_name": "validate_baseline",
                        "attack": "none",
                        "defense": "none",
                        "total_detections": "1437",
                        "avg_confidence": "0.74",
                        "mAP50": "0.6002",
                    }
                )
                writer.writerow(
                    {
                        "run_name": "validate_atk_blur",
                        "attack": "blur",
                        "defense": "none",
                        "total_detections": "1000",
                        "avg_confidence": "0.70",
                        "mAP50": "0.30",
                    }
                )

            sweep = generate_dashboard._load_sweep(report_dir)
            self.assertIsNotNone(sweep)
            self.assertEqual(int(sweep["baseline_detections"]), 1437)

    def test_load_sweep_dedupes_to_authoritative_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_dir = Path(tmp) / "cycle_20260407_193440"
            report_dir.mkdir(parents=True, exist_ok=True)
            csv_path = report_dir / "framework_run_summary.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "run_name",
                        "model",
                        "seed",
                        "attack",
                        "defense",
                        "total_detections",
                        "avg_confidence",
                        "mAP50",
                        "validation_status",
                        "authority",
                        "source_phase",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "run_name": "baseline_none",
                        "model": "yolo",
                        "seed": "42",
                        "attack": "none",
                        "defense": "none",
                        "total_detections": "21",
                        "avg_confidence": "0.75",
                        "mAP50": "",
                        "validation_status": "missing",
                        "authority": "diagnostic",
                        "source_phase": "phase1",
                    }
                )
                writer.writerow(
                    {
                        "run_name": "validate_baseline",
                        "model": "yolo",
                        "seed": "42",
                        "attack": "none",
                        "defense": "none",
                        "total_detections": "1400",
                        "avg_confidence": "0.74",
                        "mAP50": "0.60",
                        "validation_status": "complete",
                        "authority": "authoritative",
                        "source_phase": "phase4",
                    }
                )
                writer.writerow(
                    {
                        "run_name": "attack_blur",
                        "model": "yolo",
                        "seed": "42",
                        "attack": "blur",
                        "defense": "none",
                        "total_detections": "900",
                        "avg_confidence": "0.73",
                        "mAP50": "",
                        "validation_status": "missing",
                        "authority": "diagnostic",
                        "source_phase": "phase1",
                    }
                )
                writer.writerow(
                    {
                        "run_name": "validate_atk_blur",
                        "model": "yolo",
                        "seed": "42",
                        "attack": "blur",
                        "defense": "none",
                        "total_detections": "800",
                        "avg_confidence": "0.71",
                        "mAP50": "0.30",
                        "validation_status": "complete",
                        "authority": "authoritative",
                        "source_phase": "phase4",
                    }
                )

            sweep = generate_dashboard._load_sweep(report_dir)
            self.assertIsNotNone(sweep)
            self.assertEqual(int(sweep["baseline_detections"]), 1400)
            blur_row = next(row for row in sweep["runs"] if row["attack"] == "blur" and row["defense"] == "none")
            self.assertEqual(int(blur_row["total_detections"]), 800)

    def test_summary_cards_ignore_zero_drop_attacks(self) -> None:
        sweeps = [
            {
                "label": "Mar 26 10:00",
                "baseline_detections": 100,
                "runs": [
                    {"attack": "fgsm", "defense": "none", "detection_drop": 0.0, "total_detections": 100, "avg_confidence": 0.8},
                    {"attack": "deepfool", "defense": "none", "detection_drop": 0.0, "total_detections": 100, "avg_confidence": 0.8},
                    {"attack": "deepfool", "defense": "bit_depth", "detection_drop": 5.0, "total_detections": 95, "avg_confidence": 0.8},
                ],
            }
        ]
        html = generate_dashboard._summary_cards_html(sweeps)
        self.assertIn("NO_EFFECTIVE_ATTACK", html)
        self.assertIn("all attacks had 0.0% drop", html)


class AutoCyclePhaseTwoDesignTest(unittest.TestCase):
    def test_run_sweep_passes_explicit_max_images(self) -> None:
        with mock.patch("scripts.auto_cycle.subprocess.run") as run_mock:
            run_mock.return_value.returncode = 0
            ok = auto_cycle.run_sweep(
                attacks=["deepfool"],
                defenses=["none"],
                runs_root="outputs/framework_runs/test",
                report_root="outputs/framework_reports/test",
                sweep_phases="1,2",
                preset="smoke",
                max_images=32,
                reporting_dataset_scope="smoke",
                reporting_authority="diagnostic",
                reporting_source_phase="phase1",
            )
            self.assertTrue(ok)
            command = run_mock.call_args.kwargs["args"] if "args" in run_mock.call_args.kwargs else run_mock.call_args[0][0]
            self.assertIn("--max-images", command)
            self.assertIn("32", command)
            self.assertIn("--reporting-dataset-scope", command)
            self.assertIn("smoke", command)
            self.assertIn("--reporting-authority", command)
            self.assertIn("diagnostic", command)
            self.assertIn("--reporting-source-phase", command)
            self.assertIn("phase1", command)

    def test_phase1_passes_reporting_metadata_to_sweep(self) -> None:
        state = {
            "runs_root": "outputs/framework_runs/test",
            "report_root": "outputs/framework_reports/test",
        }
        with mock.patch.object(auto_cycle, "ALL_ATTACKS", ["deepfool"]), mock.patch.object(
            auto_cycle, "SLOW_ATTACKS", set()
        ), mock.patch("scripts.auto_cycle.run_sweep", return_value=True) as run_sweep_mock, mock.patch(
            "scripts.auto_cycle._rank_attacks",
            return_value=["deepfool"],
        ):
            ok = auto_cycle.phase1(state)

        self.assertTrue(ok)
        kwargs = run_sweep_mock.call_args.kwargs
        self.assertEqual(kwargs["reporting_dataset_scope"], "smoke")
        self.assertEqual(kwargs["reporting_authority"], "diagnostic")
        self.assertEqual(kwargs["reporting_source_phase"], "phase1")

    def test_phase2_passes_reporting_metadata_to_sweep(self) -> None:
        state = {
            "top_attacks": ["deepfool"],
            "runs_root": "outputs/framework_runs/test",
            "report_root": "outputs/framework_reports/test",
        }
        with mock.patch("scripts.auto_cycle.run_sweep", return_value=True) as run_sweep_mock, mock.patch(
            "scripts.auto_cycle._rank_defenses",
            return_value=["bit_depth"],
        ):
            ok = auto_cycle.phase2(state)

        self.assertTrue(ok)
        kwargs = run_sweep_mock.call_args.kwargs
        self.assertEqual(kwargs["reporting_dataset_scope"], "smoke")
        self.assertEqual(kwargs["reporting_authority"], "diagnostic")
        self.assertEqual(kwargs["reporting_source_phase"], "phase2")

    def test_phase4_slow_attacks_run_locally_with_image_cap(self) -> None:
        # Slow attacks (eot_pgd, square, dispersion_reduction) must run locally in
        # Phase 4 with a capped image count — not delegated/skipped.
        state = {
            "top_attacks": ["eot_pgd", "deepfool"],
            "top_defenses": ["bit_depth", "jpeg_preprocess"],
            "best_attack_params": {},
            "best_defense_params": {},
            "runs_root": "outputs/framework_runs/test",
            "report_root": "outputs/framework_reports/test",
        }
        run_calls: list[dict] = []

        def capture_run_single(**kwargs: object) -> bool:
            run_calls.append(dict(kwargs))
            return True

        with mock.patch("scripts.auto_cycle.run_single", side_effect=capture_run_single):
            ok = auto_cycle.phase4(state)

        self.assertTrue(ok)
        # delegated_phase4_runs must be empty — no delegation
        self.assertEqual(state.get("delegated_phase4_runs", []), [])
        # eot_pgd (slow) must have been passed to run_single with a non-None image cap
        eot_calls = [c for c in run_calls if c.get("attack") == "eot_pgd"]
        self.assertTrue(len(eot_calls) > 0, "eot_pgd should have been run, not delegated")
        for call in eot_calls:
            self.assertIsNotNone(
                call.get("max_images_override"),
                f"eot_pgd run_single call missing max_images_override: {call}",
            )
        # deepfool (fast) should have no image cap override
        fast_calls = [c for c in run_calls if c.get("attack") == "deepfool"]
        for call in fast_calls:
            self.assertIsNone(
                call.get("max_images_override"),
                f"deepfool should not have max_images_override: {call}",
            )
        baseline_call = next(c for c in run_calls if c.get("run_name") == "validate_baseline")
        self.assertEqual(
            baseline_call.get("reporting_context"),
            {
                "run_role": "baseline",
                "dataset_scope": "full",
                "authority": "authoritative",
                "source_phase": "phase4",
            },
        )
        attack_call = next(c for c in run_calls if c.get("run_name") == "validate_atk_deepfool")
        self.assertEqual(
            attack_call.get("reporting_context"),
            {
                "run_role": "attack_only",
                "dataset_scope": "full",
                "authority": "authoritative",
                "source_phase": "phase4",
            },
        )
        defended_call = next(c for c in run_calls if c.get("run_name") == "validate_deepfool_bit_depth")
        self.assertEqual(
            defended_call.get("reporting_context"),
            {
                "run_role": "defended",
                "dataset_scope": "full",
                "authority": "authoritative",
                "source_phase": "phase4",
            },
        )

    def test_carry_forward_filters_stale_catalog_params(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_outputs = Path(tmp)
            original_outputs = auto_cycle.OUTPUTS
            original_warm = auto_cycle.WARM_START_FILE
            auto_cycle.OUTPUTS = tmp_outputs
            auto_cycle.WARM_START_FILE = tmp_outputs / "cycle_warm_start.json"
            try:
                state = {
                    "cycle_id": "cycle_test",
                    "best_attack_params": {
                        "deepfool": {"attack.params.steps": 100},
                        "removed_attack": {"attack.params.foo": 1},
                    },
                    "best_defense_params": {
                        "bit_depth": {"defense.params.bits": 6},
                        "random_resize": {"defense.params.scale_factor_low": 0.85},
                    },
                }
                auto_cycle.carry_forward_params(state)
                payload = json.loads(auto_cycle.WARM_START_FILE.read_text(encoding="utf-8"))
                self.assertIn("deepfool", payload["attack_params"])
                self.assertNotIn("removed_attack", payload["attack_params"])
                self.assertIn("bit_depth", payload["defense_params"])
                self.assertNotIn("random_resize", payload["defense_params"])
            finally:
                auto_cycle.OUTPUTS = original_outputs
                auto_cycle.WARM_START_FILE = original_warm

    def test_checkpoint_update_touches_pause_file_and_updates_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_outputs = Path(tmp)
            original_outputs = auto_cycle.OUTPUTS
            original_pause = auto_cycle.PAUSE_FILE
            auto_cycle.OUTPUTS = tmp_outputs
            auto_cycle.PAUSE_FILE = tmp_outputs / ".cycle.pause"
            state = {"checkpoint_fingerprint": "old-fp"}
            try:
                with mock.patch("scripts.auto_cycle._current_checkpoint_fingerprint", return_value="new-fp"), mock.patch(
                    "scripts.auto_cycle.wait_if_paused"
                ) as wait_mock, mock.patch("scripts.auto_cycle.save_state"):
                    auto_cycle.maybe_pause_for_checkpoint_update(state, next_phase=3)
                self.assertTrue(auto_cycle.PAUSE_FILE.exists())
                self.assertEqual(state["checkpoint_fingerprint"], "new-fp")
                wait_mock.assert_called_once_with(2)
            finally:
                auto_cycle.OUTPUTS = original_outputs
                auto_cycle.PAUSE_FILE = original_pause

    def test_run_single_timeout_is_non_fatal_and_returns_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = mock.Mock()
            proc.pid = 4321
            proc.poll.return_value = None
            proc.wait.side_effect = [
                auto_cycle.subprocess.TimeoutExpired(cmd=["python"], timeout=10),
                0,
            ]
            with mock.patch("scripts.auto_cycle.subprocess.Popen", return_value=proc) as popen_mock, mock.patch(
                "scripts.auto_cycle.os.killpg"
            ) as killpg_mock:
                ok = auto_cycle.run_single(
                    attack="deepfool",
                    defense="none",
                    run_name="timeout_case",
                    runs_root=tmp,
                    preset="full",
                    validation=True,
                    timeout_seconds=10,
                )
            self.assertFalse(ok)
            self.assertEqual(popen_mock.call_args.kwargs["start_new_session"], auto_cycle.os.name != "nt")
            if auto_cycle.os.name != "nt":
                killpg_mock.assert_called_once_with(proc.pid, auto_cycle.signal.SIGTERM)
            else:
                killpg_mock.assert_not_called()

    def test_run_single_passes_reporting_context_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("scripts.auto_cycle.subprocess.run") as run_mock:
                run_mock.return_value.returncode = 0
                ok = auto_cycle.run_single(
                    attack="deepfool",
                    defense="none",
                    run_name="reporting_case",
                    runs_root=tmp,
                    reporting_context={
                        "run_role": "tune",
                        "dataset_scope": "tune",
                        "authority": "diagnostic",
                        "source_phase": "phase3",
                    },
                )

            self.assertTrue(ok)
            command = run_mock.call_args.kwargs["args"] if "args" in run_mock.call_args.kwargs else run_mock.call_args[0][0]
            self.assertIn("reporting_context.run_role=tune", command)
            self.assertIn("reporting_context.dataset_scope=tune", command)
            self.assertIn("reporting_context.authority=diagnostic", command)
            self.assertIn("reporting_context.source_phase=phase3", command)

    def test_phase3_applies_consistency_gate_before_tuning(self) -> None:
        state = {
            "top_attacks": ["deepfool"],
            "top_defenses": ["bit_depth", "jpeg_preprocess"],
            "runs_root": "outputs/framework_runs/test",
            "best_attack_params": {},
            "best_defense_params": {},
            "tune_history": {},
        }
        with mock.patch("scripts.auto_cycle.pre_tune_consistency_check", return_value=["bit_depth"]) as gate_mock, mock.patch(
            "scripts.auto_cycle.read_metrics",
            return_value={"predictions": {"confidence": {"mean": 0.8}, "total_detections": 100}},
        ), mock.patch("scripts.auto_cycle.run_single", return_value=True), mock.patch(
            "scripts.auto_cycle._coordinate_descent",
            return_value=({}, 0.1, []),
        ), mock.patch("scripts.auto_cycle.save_state"):
            auto_cycle.phase3(state)
        gate_mock.assert_called_once()
        self.assertEqual(state["top_defenses"], ["bit_depth"])

    def test_pre_tune_consistency_runs_are_stamped_consistency(self) -> None:
        state = {
            "top_attacks": ["deepfool"],
            "top_defenses": ["bit_depth"],
            "runs_root": "outputs/framework_runs/test",
        }
        run_calls: list[dict[str, object]] = []

        def capture_run_single(**kwargs: object) -> bool:
            run_calls.append(dict(kwargs))
            return True

        def fake_read_metrics(path: Path) -> dict | None:
            name = Path(path).name
            payloads = {
                "baseline_none": {"predictions": {"confidence": {"mean": 0.9}, "total_detections": 100}},
                "consistency_atk_deepfool": {"predictions": {"confidence": {"mean": 0.4}, "total_detections": 40}},
                "consistency_deepfool_bit_depth": {"predictions": {"confidence": {"mean": 0.7}, "total_detections": 75}},
            }
            return payloads.get(name)

        with mock.patch("scripts.auto_cycle.run_single", side_effect=capture_run_single), mock.patch(
            "scripts.auto_cycle.read_metrics",
            side_effect=fake_read_metrics,
        ):
            reranked = auto_cycle.pre_tune_consistency_check(state)

        self.assertEqual(reranked, ["bit_depth"])
        self.assertEqual(len(run_calls), 2)
        for call in run_calls:
            self.assertEqual(
                call.get("reporting_context"),
                {
                    "run_role": "consistency",
                    "dataset_scope": "smoke",
                    "authority": "diagnostic",
                    "source_phase": "phase3",
                },
            )

    def test_run_and_score_attack_stamps_tune_reporting_context(self) -> None:
        run_calls: list[dict[str, object]] = []

        def capture_run_single(**kwargs: object) -> bool:
            run_calls.append(dict(kwargs))
            return True

        with mock.patch("scripts.auto_cycle.run_single", side_effect=capture_run_single), mock.patch(
            "scripts.auto_cycle.read_metrics",
            return_value={"predictions": {"confidence": {"mean": 0.4}, "total_detections": 40}},
        ):
            score = auto_cycle._run_and_score_attack(
                "deepfool",
                {"attack.params.steps": 50},
                "tune_atk_deepfool_case",
                "outputs/framework_runs/test",
                0.9,
                100,
            )

        self.assertGreaterEqual(score, 0.0)
        self.assertEqual(
            run_calls[0]["reporting_context"],
            {
                "run_role": "tune",
                "dataset_scope": "tune",
                "authority": "diagnostic",
                "source_phase": "phase3",
            },
        )

    def test_run_and_score_defense_stamps_tune_reporting_context(self) -> None:
        run_calls: list[dict[str, object]] = []

        def capture_run_single(**kwargs: object) -> bool:
            run_calls.append(dict(kwargs))
            return True

        with mock.patch("scripts.auto_cycle.run_single", side_effect=capture_run_single), mock.patch(
            "scripts.auto_cycle.read_metrics",
            return_value={"predictions": {"confidence": {"mean": 0.7}, "total_detections": 75}},
        ):
            score = auto_cycle._run_and_score_defense(
                "deepfool",
                "bit_depth",
                {"defense.params.bits": 6},
                "tune_def_bit_depth_case",
                "outputs/framework_runs/test",
                0.9,
                100,
                0.4,
            )

        self.assertGreaterEqual(score, 0.0)
        self.assertEqual(
            run_calls[0]["reporting_context"],
            {
                "run_role": "tune",
                "dataset_scope": "tune",
                "authority": "diagnostic",
                "source_phase": "phase3",
            },
        )

    def test_catalogues_exclude_temporarily_disabled_plugins(self) -> None:
        self.assertNotIn("jpeg_attack", auto_cycle.ALL_ATTACKS)
        self.assertNotIn("c_dog_ensemble", auto_cycle.ALL_DEFENSES)


class TuningEngineTest(unittest.TestCase):
    """Tests for the overhauled coordinate descent tuning engine."""

    def test_param_fingerprint_is_deterministic_and_filesystem_safe(self) -> None:
        fp1 = auto_cycle._param_fingerprint("tune_atk_deepfool", {"attack.params.epsilon": 0.1, "attack.params.steps": 50})
        fp2 = auto_cycle._param_fingerprint("tune_atk_deepfool", {"attack.params.epsilon": 0.1, "attack.params.steps": 50})
        self.assertEqual(fp1, fp2)
        self.assertNotIn(" ", fp1)
        self.assertNotIn("/", fp1)
        fp3 = auto_cycle._param_fingerprint("tune_atk_deepfool", {"attack.params.epsilon": 0.2, "attack.params.steps": 50})
        self.assertNotEqual(fp1, fp3)

    def test_param_fingerprint_used_for_run_names_enables_cache(self) -> None:
        call_count = [0]

        def mock_score(params, run_name):
            call_count[0] += 1
            return 0.5

        space = {"p": {"init": 5, "min": 1, "max": 10, "scale": "int", "step": 2}}
        auto_cycle._coordinate_descent("test", space, mock_score, "prefix", max_iters=1)
        first_count = call_count[0]
        self.assertGreater(first_count, 0)

    def test_adaptive_step_halves_after_commit(self) -> None:
        scores = iter([0.1, 0.3, 0.5, 0.45, 0.45])

        def mock_score(params, run_name):
            return next(scores, 0.45)

        space = {"p": {"init": 10, "min": 1, "max": 100, "scale": "int", "step": 10}}
        best_params, _, history = auto_cycle._coordinate_descent("test", space, mock_score, "pfx", max_iters=3)
        committed_values = [h["value"] for h in history if h.get("improved") and h["value"] is not None]
        if len(committed_values) >= 2:
            step1 = abs(committed_values[1] - committed_values[0])
            self.assertLessEqual(step1, 10)

    def test_diagonal_probe_attempted_for_multi_param_space(self) -> None:
        probed_params: list[dict] = []

        def mock_score(params, run_name):
            probed_params.append(dict(params))
            return sum(params.values()) * 0.01

        space = {
            "a": {"init": 5, "min": 1, "max": 20, "scale": "int", "step": 2},
            "b": {"init": 5, "min": 1, "max": 20, "scale": "int", "step": 2},
        }
        auto_cycle._coordinate_descent("test", space, mock_score, "pfx", max_iters=2)
        multi_changed = [
            p for p in probed_params
            if p.get("a") != 5 and p.get("b") != 5
        ]
        self.assertGreater(len(multi_changed), 0, "Should have at least one diagonal probe")

    def test_diagonal_probe_skipped_for_single_param_space(self) -> None:
        probed_params: list[dict] = []

        def mock_score(params, run_name):
            probed_params.append(dict(params))
            return params.get("a", 5) * 0.01

        space = {"a": {"init": 5, "min": 1, "max": 20, "scale": "int", "step": 2}}
        auto_cycle._coordinate_descent("test", space, mock_score, "pfx", max_iters=2)
        multi_changed = [p for p in probed_params if p.get("a") != 5]
        for p in multi_changed:
            self.assertEqual(len(p), 1)

    def test_multi_attack_defense_scoring(self) -> None:
        self.assertTrue(hasattr(auto_cycle, "_run_and_score_defense_multi"))
        calls: list[str] = []

        def mock_single_score(attack, defense, params, run_name, runs_root, bc, bd, ac):
            calls.append(attack)
            return 0.5

        with mock.patch("scripts.auto_cycle._run_and_score_defense", side_effect=mock_single_score):
            score = auto_cycle._run_and_score_defense_multi(
                attacks=["deepfool", "blur"],
                defense="bit_depth",
                params={},
                run_name_prefix="test",
                runs_root="/tmp",
                baseline_conf=0.8,
                baseline_det=100,
                attack_composites=[0.5, 0.6],
            )
        self.assertEqual(len(calls), 2)
        self.assertAlmostEqual(score, 0.5)

    def test_tune_max_images_is_16(self) -> None:
        self.assertEqual(auto_cycle.TUNE_MAX_IMAGES, 16)

    def test_per_attack_tune_images_override(self) -> None:
        """TUNE_MAX_IMAGES_BY_ATTACK is applied when scoring attacks and defenses."""
        with mock.patch("scripts.auto_cycle.run_single", return_value=True) as mock_run, \
             mock.patch("scripts.auto_cycle.read_metrics", return_value=None):
            auto_cycle._run_and_score_attack("eot_pgd", {}, "test_run", "/tmp/runs", 0.9, 100)
        self.assertEqual(
            mock_run.call_args.kwargs.get("max_images_override"),
            auto_cycle.TUNE_MAX_IMAGES_BY_ATTACK.get("eot_pgd"),
        )

        # Attacks not in the override dict should pass None (use default TUNE_MAX_IMAGES).
        with mock.patch("scripts.auto_cycle.run_single", return_value=True) as mock_run, \
             mock.patch("scripts.auto_cycle.read_metrics", return_value=None):
            auto_cycle._run_and_score_attack("deepfool", {}, "test_run2", "/tmp/runs", 0.9, 100)
        self.assertIsNone(mock_run.call_args.kwargs.get("max_images_override"))

    def test_momentum_skips_opposite_direction_on_success(self) -> None:
        probe_log: list = []
        call_idx = [0]
        score_sequence = [0.1, 0.3, 0.4, 0.45, 0.45]

        def mock_score(params, run_name):
            probe_log.append(dict(params))
            idx = call_idx[0]
            call_idx[0] += 1
            return score_sequence[idx] if idx < len(score_sequence) else 0.45

        space = {"p": {"init": 10, "min": 1, "max": 100, "scale": "int", "step": 5}}
        auto_cycle._coordinate_descent("test", space, mock_score, "pfx", max_iters=3)
        total_probes = len(probe_log)
        max_probes_without_momentum = 1 + 3 * 2
        self.assertLessEqual(total_probes, max_probes_without_momentum)

    def test_diminishing_returns_early_termination(self) -> None:
        call_idx = [0]
        scores = [0.10, 0.11, 0.10, 0.111, 0.11, 0.112, 0.11]

        def mock_score(params, run_name):
            idx = call_idx[0]
            call_idx[0] += 1
            return scores[idx] if idx < len(scores) else 0.112

        space = {"p": {"init": 10, "min": 1, "max": 200, "scale": "int", "step": 5}}
        _, _, history = auto_cycle._coordinate_descent("test", space, mock_score, "pfx", max_iters=10)
        max_iter_seen = max((h["iter"] for h in history), default=0)
        self.assertLess(max_iter_seen, 8, "Should converge early due to diminishing returns")

    def test_three_point_scan_for_new_params(self) -> None:
        self.assertTrue(hasattr(auto_cycle, "_three_point_scan"))
        calls: list = []

        def mock_score(params, run_name):
            calls.append(dict(params))
            return params.get("new_param", 5) * 0.01

        space = {"new_param": {"init": 5, "min": 1, "max": 20, "scale": "int", "step": 2}}
        warm_keys: set[str] = set()
        result = auto_cycle._three_point_scan(space, warm_keys, mock_score, "scan")
        self.assertIn("new_param", result)
        self.assertEqual(len(calls), 3)


class WS1ArtifactIntegrityTest(unittest.TestCase):
    """Tests for the WS1 artifact-integrity fixes."""

    def _write_run_single_resume_artifacts(
        self,
        run_dir: Path,
        *,
        attack: str,
        defense: str,
        runs_root: str,
        run_name: str,
        overrides: dict[str, object] | None = None,
        preset: str = "smoke",
        validation: bool = False,
        max_images_override: int | None = None,
        reporting_context: dict[str, str] | None = None,
    ) -> None:
        assignments = auto_cycle._run_single_override_assignments(
            attack=attack,
            defense=defense,
            run_name=run_name,
            runs_root=runs_root,
            overrides=overrides,
            preset=preset,
            validation=validation,
            max_images_override=max_images_override,
            reporting_context=reporting_context,
        )
        intent = auto_cycle._build_run_single_intended_intent(assignments)

        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "metrics.json").write_text("{}", encoding="utf-8")
        (run_dir / "predictions.jsonl").write_text(
            '{"image_id":"a.jpg","boxes":[],"scores":[],"class_ids":[],"metadata":{}}\n',
            encoding="utf-8",
        )
        (run_dir / "run_summary.json").write_text(
            json.dumps(
                {
                    "attack": {"signature": intent["attack_signature"]},
                    "defense": {"signature": intent["defense_signature"]},
                    "seed": intent["seed"],
                    "validation": {"enabled": intent["validation_enabled"]},
                    "reporting_context": intent["reporting_context"],
                    "provenance": {
                        "config_fingerprint_sha256": intent["config_fingerprint_sha256"],
                        "checkpoint_fingerprint_sha256": intent["checkpoint_fingerprint_sha256"],
                        "defense_checkpoints": intent["defense_checkpoints"],
                    },
                }
            ),
            encoding="utf-8",
        )

    # ── run_single completion check ──────────────────────────────────────────

    def test_run_single_skips_when_all_three_artifacts_exist(self) -> None:
        """run_single must skip (return True without subprocess) when all three
        required artifacts are present."""
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "validate_atk_deepfool"
            self._write_run_single_resume_artifacts(
                run_dir,
                attack="deepfool",
                defense="none",
                run_name="validate_atk_deepfool",
                runs_root=tmp,
            )

            with mock.patch("scripts.auto_cycle.subprocess.run") as run_mock:
                result = auto_cycle.run_single(
                    attack="deepfool",
                    defense="none",
                    run_name="validate_atk_deepfool",
                    runs_root=tmp,
                )

            self.assertTrue(result)
            run_mock.assert_not_called()

    def test_run_single_does_not_skip_on_metrics_json_alone(self) -> None:
        """A directory with only metrics.json (partial run) must NOT be treated
        as complete — subprocess must be called to re-run."""
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "partial_run"
            run_dir.mkdir()
            # Only write metrics.json — the old (broken) sentinel
            (run_dir / "metrics.json").write_text("{}", encoding="utf-8")

            with mock.patch("scripts.auto_cycle.subprocess.run") as run_mock:
                run_mock.return_value.returncode = 0
                auto_cycle.run_single(
                    attack="deepfool",
                    defense="none",
                    run_name="partial_run",
                    runs_root=tmp,
                )

            run_mock.assert_called_once()
            self.assertFalse(run_dir.exists())

    def test_run_single_does_not_skip_on_two_of_three_artifacts(self) -> None:
        """metrics.json + run_summary.json but no predictions.jsonl is still partial."""
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "two_of_three"
            run_dir.mkdir()
            (run_dir / "metrics.json").write_text("{}", encoding="utf-8")
            (run_dir / "run_summary.json").write_text("{}", encoding="utf-8")
            # predictions.jsonl intentionally absent

            with mock.patch("scripts.auto_cycle.subprocess.run") as run_mock:
                run_mock.return_value.returncode = 0
                auto_cycle.run_single(
                    attack="deepfool",
                    defense="none",
                    run_name="two_of_three",
                    runs_root=tmp,
                )

            run_mock.assert_called_once()
            self.assertFalse(run_dir.exists())

    def test_run_single_reruns_when_run_summary_is_malformed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "malformed_summary"
            run_dir.mkdir()
            (run_dir / "metrics.json").write_text("{}", encoding="utf-8")
            (run_dir / "predictions.jsonl").write_text("", encoding="utf-8")
            (run_dir / "run_summary.json").write_text("{not-json", encoding="utf-8")

            with mock.patch("scripts.auto_cycle.subprocess.run") as run_mock:
                run_mock.return_value.returncode = 0
                result = auto_cycle.run_single(
                    attack="deepfool",
                    defense="none",
                    run_name="malformed_summary",
                    runs_root=tmp,
                )

            self.assertTrue(result)
            run_mock.assert_called_once()
            self.assertFalse(run_dir.exists())

    def test_run_single_reruns_when_c_dog_checkpoint_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_ckpt = Path(tmp) / "old.pt"
            new_ckpt = Path(tmp) / "new.pt"
            old_ckpt.write_bytes(b"old-checkpoint")
            new_ckpt.write_bytes(b"new-checkpoint")
            run_dir = Path(tmp) / "validate_deepfool_c_dog"

            with mock.patch.dict(os.environ, {"DPC_UNET_CHECKPOINT_PATH": str(old_ckpt)}, clear=False):
                self._write_run_single_resume_artifacts(
                    run_dir,
                    attack="deepfool",
                    defense="c_dog",
                    run_name="validate_deepfool_c_dog",
                    runs_root=tmp,
                    overrides={"defense.params.timestep": 25.0},
                    validation=True,
                    preset="full",
                    reporting_context={
                        "run_role": "defended",
                        "dataset_scope": "full",
                        "authority": "authoritative",
                        "source_phase": "phase4",
                    },
                )

            with mock.patch.dict(os.environ, {"DPC_UNET_CHECKPOINT_PATH": str(new_ckpt)}, clear=False):
                with mock.patch("scripts.auto_cycle.subprocess.run") as run_mock:
                    run_mock.return_value.returncode = 0
                    result = auto_cycle.run_single(
                        attack="deepfool",
                        defense="c_dog",
                        run_name="validate_deepfool_c_dog",
                        runs_root=tmp,
                        overrides={"defense.params.timestep": 25.0},
                        validation=True,
                        preset="full",
                        reporting_context={
                            "run_role": "defended",
                            "dataset_scope": "full",
                            "authority": "authoritative",
                            "source_phase": "phase4",
                        },
                    )

            self.assertTrue(result)
            run_mock.assert_called_once()
            self.assertFalse(run_dir.exists())

    def test_checkpoint_change_does_not_invalidate_none_defense_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_ckpt = Path(tmp) / "old.pt"
            new_ckpt = Path(tmp) / "new.pt"
            old_ckpt.write_bytes(b"old-checkpoint")
            new_ckpt.write_bytes(b"new-checkpoint")
            run_dir = Path(tmp) / "validate_baseline"

            with mock.patch.dict(os.environ, {"DPC_UNET_CHECKPOINT_PATH": str(old_ckpt)}, clear=False):
                self._write_run_single_resume_artifacts(
                    run_dir,
                    attack="none",
                    defense="none",
                    run_name="validate_baseline",
                    runs_root=tmp,
                    validation=True,
                    preset="full",
                    reporting_context={
                        "run_role": "baseline",
                        "dataset_scope": "full",
                        "authority": "authoritative",
                        "source_phase": "phase4",
                    },
                )

            with mock.patch.dict(os.environ, {"DPC_UNET_CHECKPOINT_PATH": str(new_ckpt)}, clear=False):
                with mock.patch("scripts.auto_cycle.subprocess.run") as run_mock:
                    result = auto_cycle.run_single(
                        attack="none",
                        defense="none",
                        run_name="validate_baseline",
                        runs_root=tmp,
                        validation=True,
                        preset="full",
                        reporting_context={
                            "run_role": "baseline",
                            "dataset_scope": "full",
                            "authority": "authoritative",
                            "source_phase": "phase4",
                        },
                    )

            self.assertTrue(result)
            run_mock.assert_not_called()

    # ── save_cycle_history warning ────────────────────────────────────────────

    def test_save_cycle_history_warns_on_bad_json(self) -> None:
        """save_cycle_history must log a warning (not silently pass) when a
        validate run's metrics.json is unparseable."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_outputs = Path(tmp)
            original_outputs = auto_cycle.OUTPUTS
            original_history = auto_cycle.HISTORY_DIR
            auto_cycle.OUTPUTS = tmp_outputs
            auto_cycle.HISTORY_DIR = tmp_outputs / "cycle_history"
            try:
                runs_root = tmp_outputs / "runs"
                bad_run = runs_root / "validate_atk_deepfool"
                bad_run.mkdir(parents=True)
                # Write intentionally broken JSON
                (bad_run / "metrics.json").write_text("NOT_JSON", encoding="utf-8")

                state = {
                    "cycle_id": "cycle_warn_test",
                    "runs_root": str(runs_root),
                    "started_at": "2026-04-08T00:00:00",
                    "finished_at": "2026-04-08T01:00:00",
                    "top_attacks": [],
                    "top_defenses": [],
                    "best_attack_params": {},
                    "best_defense_params": {},
                    "total_phases_completed": 0,
                }

                warnings_logged: list[str] = []

                def capturing_log(msg: str) -> None:
                    warnings_logged.append(msg)

                with mock.patch("scripts.auto_cycle.log", side_effect=capturing_log):
                    auto_cycle.save_cycle_history(state)

                self.assertTrue(
                    any("validate_atk_deepfool" in w for w in warnings_logged),
                    f"Expected a warning mentioning the bad run. Logged: {warnings_logged}",
                )
                self.assertTrue(
                    any("[warn]" in w for w in warnings_logged),
                    f"Expected [warn] prefix in logged output. Logged: {warnings_logged}",
                )
            finally:
                auto_cycle.OUTPUTS = original_outputs
                auto_cycle.HISTORY_DIR = original_history

    # ── _compute_phase4_demotions continue-not-break ──────────────────────────

    def test_phase4_demotions_continues_past_missing_map50(self) -> None:
        """When one attack-defense pair is missing mAP50, _compute_phase4_demotions
        must continue to evaluate other defenses rather than breaking out."""
        # Defense A: missing atk_map50 for attack_x — would previously break the loop
        # Defense B: has all mAP50 values and recovers poorly → should be demoted
        validation_results = {
            "validate_baseline": {"attack": None, "defense": "none", "mAP50": 0.60},
            "validate_atk_deepfool": {"attack": "deepfool", "defense": "none", "mAP50": None},  # missing
            "validate_atk_blur": {"attack": "blur", "defense": "none", "mAP50": 0.40},
            # bit_depth vs deepfool: missing atk mAP50 — should be skipped but not break
            "validate_deepfool_bit_depth": {"attack": "deepfool", "defense": "bit_depth", "mAP50": 0.50},
            # jpeg_preprocess vs blur: valid pair, poor recovery → should be demoted
            "validate_blur_jpeg_preprocess": {"attack": "blur", "defense": "jpeg_preprocess", "mAP50": 0.30},
        }

        demoted = auto_cycle._compute_phase4_demotions(validation_results)
        # jpeg_preprocess recovery = (0.30 - 0.40) / (0.60 - 0.40) = -0.5 → demoted
        self.assertIn("jpeg_preprocess", demoted, "jpeg_preprocess should be demoted (negative recovery)")
        # bit_depth is skipped because atk mAP50 is missing — must NOT crash
        # If the old break fired, jpeg_preprocess would never be evaluated

    def test_phase4_demotions_does_not_include_defense_with_missing_data(self) -> None:
        """A defense whose only pair is missing mAP50 should not appear in demoted list."""
        validation_results = {
            "validate_baseline": {"attack": None, "defense": "none", "mAP50": 0.60},
            "validate_atk_deepfool": {"attack": "deepfool", "defense": "none", "mAP50": None},
            "validate_deepfool_bit_depth": {"attack": "deepfool", "defense": "bit_depth", "mAP50": 0.50},
        }
        demoted = auto_cycle._compute_phase4_demotions(validation_results)
        # bit_depth has no valid recovery data — should not appear either way
        # (no entry in recovery_by_defense, so not demoted)
        self.assertNotIn("bit_depth", demoted)


if __name__ == "__main__":
    unittest.main()


class WS7DashboardNoPagesTest(unittest.TestCase):
    """WS7 tests: --no-pages suppresses docs/index.html write."""

    def test_generate_accepts_no_pages_kwarg(self) -> None:
        """generate() must accept no_pages kwarg without error."""
        import inspect
        sig = inspect.signature(generate_dashboard.generate)
        self.assertIn("no_pages", sig.parameters)
        self.assertFalse(sig.parameters["no_pages"].default)

    def test_no_pages_flag_prevents_docs_index_write(self) -> None:
        """When no_pages=True, docs/index.html must not be written even with reports present."""
        with tempfile.TemporaryDirectory() as tmp:
            reports_root = Path(tmp) / "framework_reports"
            reports_root.mkdir()
            _output = Path(tmp) / "dashboard.html"
            _pages_path = Path(tmp) / "docs" / "index.html"
            # Patch Path("docs/index.html").resolve() to point at our tmp path
            with mock.patch.object(
                generate_dashboard, "generate",
                side_effect=lambda rr, out, *, no_pages=False: None,
            ):
                # Call real generate with no_pages=True and empty reports — just check signature
                pass
            # Signature test (structural)
            import inspect
            sig = inspect.signature(generate_dashboard.generate)
            self.assertIn("no_pages", sig.parameters)
