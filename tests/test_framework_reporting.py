from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from lab.reporting import (
    build_auto_summary_payload,
    build_comparison_rows,
    build_team_summary_payload,
    discover_framework_runs,
    generate_summary,
    render_markdown_report,
    write_team_summary,
)
from lab.reporting.framework_comparison import discover_framework_runs as _discover, write_summary_csv
from lab.reporting.warnings import (
    WARN_ATTACK_BELOW_NOISE,
    WARN_DEFENSE_DEGRADES_PERFORMANCE,
    WARN_DEFENSE_RECOVERY_UNDEFINED,
    WARN_LOW_ATTACK_COUNT,
    WARN_LOW_CONFIDENCE_FLOOR,
    WARN_MISSING_PER_CLASS,
    WARN_MULTIPLE_BASELINES,
    WARN_NO_VALIDATION,
    evaluate_warnings,
)
from scripts import generate_failure_gallery, print_summary as print_summary_cli


class FrameworkReportingTest(unittest.TestCase):
    def _write_run(
        self,
        root: Path,
        run_name: str,
        *,
        attack: str,
        map50: float | None,
        defense: str = "none",
        seed: int = 42,
        model: str = "yolo",
        attack_params: dict[str, object] | None = None,
        defense_params: dict[str, object] | None = None,
        resolved_objective: dict[str, object] | None = None,
        semantic_order: str | None = "attack_then_defense",
        transform_order: tuple[str, ...] | None = None,
        validation_status: str = "complete",
        total_detections: int = 10,
        avg_confidence: float = 0.5,
        per_class: dict[int, dict[str, object]] | None = None,
        reporting_context: dict[str, str] | None = None,
        source_dir: str | None = None,
        summary_provenance: dict[str, object] | None = None,
        prediction_rows: list[dict[str, object]] | None = None,
    ) -> None:
        run_dir = root / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        if transform_order is None:
            transform_order = (
                "attack.apply",
                "defense.preprocess",
                "model.predict",
                "defense.postprocess",
            )
        pipeline_payload: dict[str, object] = {
            "transform_order": list(transform_order),
            "attack_applied": attack not in {"", "none", "identity"},
        }
        provenance_payload: dict[str, object] = {
            "transform_order": list(transform_order),
            "attack_applied": attack not in {"", "none", "identity"},
        }
        if semantic_order is not None:
            pipeline_payload["semantic_order"] = semantic_order
            provenance_payload["semantic_order"] = semantic_order
        run_summary = {
            "model": {"name": model},
            "attack": {
                "name": attack,
                "params": attack_params or {},
                "resolved_objective": resolved_objective or {},
            },
            "defense": {"name": defense, "params": defense_params or {}},
            "seed": seed,
            "prediction_record_count": 5,
            "pipeline": pipeline_payload,
        }
        if reporting_context is not None:
            run_summary["reporting_context"] = reporting_context
        if source_dir is not None:
            run_summary["source_dir"] = source_dir
        if summary_provenance is not None:
            run_summary["provenance"] = summary_provenance
        (run_dir / "run_summary.json").write_text(
            json.dumps(run_summary),
            encoding="utf-8",
        )

        predictions_payload: dict[str, object] = {
            "images_with_detections": 5 if total_detections > 0 else 0,
            "total_detections": total_detections,
            "confidence": {"mean": avg_confidence},
        }
        if per_class is not None:
            predictions_payload["per_class"] = {
                str(class_id): values
                for class_id, values in per_class.items()
            }

        (run_dir / "metrics.json").write_text(
            json.dumps(
                {
                    "predictions": predictions_payload,
                    "validation": {
                        "status": validation_status,
                        "precision": 0.7,
                        "recall": 0.6,
                        "mAP50": map50,
                        "mAP50-95": 0.4,
                    },
                    "provenance": provenance_payload,
                }
            ),
            encoding="utf-8",
        )
        if prediction_rows is not None:
            lines = [json.dumps(row, sort_keys=True) for row in prediction_rows]
            (run_dir / "predictions.jsonl").write_text(
                "\n".join(lines) + ("\n" if lines else ""),
                encoding="utf-8",
            )

    def test_discover_and_compare(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(root, "baseline_run", attack="none", map50=0.6)
            self._write_run(root, "fgsm_run", attack="fgsm", map50=0.2)
            records = discover_framework_runs(root)
            self.assertEqual(len(records), 2)
            rows = build_comparison_rows(records)
            self.assertEqual(len(rows), 1)
            self.assertAlmostEqual(float(rows[0]["mAP50_drop"]), 0.4)

    def test_discover_framework_runs_exposes_reporting_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(
                root,
                "validate_baseline",
                attack="none",
                map50=0.7,
                reporting_context={
                    "run_role": "baseline",
                    "dataset_scope": "full",
                    "authority": "authoritative",
                    "source_phase": "phase4",
                },
            )

            records = discover_framework_runs(root)
            self.assertEqual(len(records), 1)
            record = records[0]
            self.assertEqual(record.run_role, "baseline")
            self.assertEqual(record.dataset_scope, "full")
            self.assertEqual(record.authority, "authoritative")
            self.assertEqual(record.source_phase, "phase4")

    def test_authoritative_metadata_drives_warning_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            diagnostic_baseline = {
                "run_role": "baseline",
                "dataset_scope": "smoke",
                "authority": "diagnostic",
                "source_phase": "phase1",
            }
            authoritative_baseline = {
                "run_role": "baseline",
                "dataset_scope": "full",
                "authority": "authoritative",
                "source_phase": "phase4",
            }
            authoritative_attack = {
                "run_role": "attack_only",
                "dataset_scope": "full",
                "authority": "authoritative",
                "source_phase": "phase4",
            }
            diagnostic_attack = {
                "run_role": "attack_only",
                "dataset_scope": "smoke",
                "authority": "diagnostic",
                "source_phase": "phase1",
            }
            authoritative_defense = {
                "run_role": "defended",
                "dataset_scope": "full",
                "authority": "authoritative",
                "source_phase": "phase4",
            }
            diagnostic_defense = {
                "run_role": "defended",
                "dataset_scope": "smoke",
                "authority": "diagnostic",
                "source_phase": "phase2",
            }

            self._write_run(
                root,
                "baseline_none",
                attack="none",
                map50=0.68,
                validation_status="missing",
                total_detections=90,
                reporting_context=diagnostic_baseline,
            )
            self._write_run(
                root,
                "validate_baseline",
                attack="none",
                map50=0.70,
                total_detections=140,
                reporting_context=authoritative_baseline,
            )
            self._write_run(
                root,
                "attack_blur",
                attack="blur",
                map50=0.69,
                validation_status="missing",
                total_detections=138,
                reporting_context=diagnostic_attack,
            )
            self._write_run(
                root,
                "validate_atk_fgsm",
                attack="fgsm",
                map50=0.20,
                total_detections=50,
                reporting_context=authoritative_attack,
            )
            self._write_run(
                root,
                "validate_atk_pgd",
                attack="pgd",
                map50=0.25,
                total_detections=55,
                reporting_context=authoritative_attack,
            )
            self._write_run(
                root,
                "defended_fgsm_bit_depth",
                attack="fgsm",
                defense="bit_depth",
                map50=0.10,
                total_detections=40,
                reporting_context=diagnostic_defense,
            )
            self._write_run(
                root,
                "validate_fgsm_bit_depth",
                attack="fgsm",
                defense="bit_depth",
                map50=0.45,
                total_detections=95,
                reporting_context=authoritative_defense,
            )

            payload = build_auto_summary_payload(root, bootstrap=False)
            warnings = evaluate_warnings(payload)
            codes = {warning["code"] for warning in warnings}

            self.assertEqual(payload["baseline"]["run_name"], "validate_baseline")
            self.assertNotIn(WARN_MULTIPLE_BASELINES, codes)
            self.assertNotIn(WARN_LOW_ATTACK_COUNT, codes)
            self.assertNotIn(WARN_ATTACK_BELOW_NOISE, codes)
            self.assertNotIn(WARN_DEFENSE_DEGRADES_PERFORMANCE, codes)
            self.assertIn(WARN_MISSING_PER_CLASS, codes)

    def test_diagnostic_only_rows_suppress_phase4_dependent_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            diagnostic_baseline = {
                "run_role": "baseline",
                "dataset_scope": "smoke",
                "authority": "diagnostic",
                "source_phase": "phase1",
            }
            diagnostic_attack = {
                "run_role": "attack_only",
                "dataset_scope": "smoke",
                "authority": "diagnostic",
                "source_phase": "phase1",
            }
            diagnostic_defense = {
                "run_role": "defended",
                "dataset_scope": "smoke",
                "authority": "diagnostic",
                "source_phase": "phase2",
            }

            self._write_run(
                root,
                "baseline_none",
                attack="none",
                map50=None,
                validation_status="missing",
                total_detections=100,
                reporting_context=diagnostic_baseline,
            )
            self._write_run(
                root,
                "attack_fgsm",
                attack="fgsm",
                map50=None,
                validation_status="missing",
                total_detections=95,
                reporting_context=diagnostic_attack,
            )
            self._write_run(
                root,
                "defended_fgsm_bit_depth",
                attack="fgsm",
                defense="bit_depth",
                map50=None,
                validation_status="missing",
                total_detections=90,
                reporting_context=diagnostic_defense,
            )

            payload = build_auto_summary_payload(root, bootstrap=False)
            warnings = evaluate_warnings(payload)
            codes = {warning["code"] for warning in warnings}

            self.assertNotIn(WARN_NO_VALIDATION, codes)
            self.assertNotIn(WARN_DEFENSE_RECOVERY_UNDEFINED, codes)
            self.assertNotIn(WARN_DEFENSE_DEGRADES_PERFORMANCE, codes)
            self.assertIn(WARN_LOW_ATTACK_COUNT, codes)
            self.assertIn(WARN_ATTACK_BELOW_NOISE, codes)
            self.assertIn(WARN_MISSING_PER_CLASS, codes)

    def test_authoritative_rows_still_emit_phase4_dependent_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authoritative_baseline = {
                "run_role": "baseline",
                "dataset_scope": "full",
                "authority": "authoritative",
                "source_phase": "phase4",
            }
            authoritative_attack = {
                "run_role": "attack_only",
                "dataset_scope": "full",
                "authority": "authoritative",
                "source_phase": "phase4",
            }
            authoritative_defense = {
                "run_role": "defended",
                "dataset_scope": "full",
                "authority": "authoritative",
                "source_phase": "phase4",
            }

            self._write_run(
                root,
                "validate_baseline",
                attack="none",
                map50=None,
                validation_status="missing",
                total_detections=100,
                reporting_context=authoritative_baseline,
            )
            self._write_run(
                root,
                "validate_atk_fgsm",
                attack="fgsm",
                map50=None,
                validation_status="missing",
                total_detections=95,
                reporting_context=authoritative_attack,
            )
            self._write_run(
                root,
                "validate_fgsm_bit_depth",
                attack="fgsm",
                defense="bit_depth",
                map50=None,
                validation_status="missing",
                total_detections=90,
                reporting_context=authoritative_defense,
            )

            payload = build_auto_summary_payload(root, bootstrap=False)
            warnings = evaluate_warnings(payload)
            codes = {warning["code"] for warning in warnings}

            self.assertIn(WARN_NO_VALIDATION, codes)
            self.assertIn(WARN_DEFENSE_RECOVERY_UNDEFINED, codes)
            self.assertIn(WARN_DEFENSE_DEGRADES_PERFORMANCE, codes)

    def test_defense_recovery_pairs_by_attack_signature_not_name_only(self) -> None:
        from lab.reporting.framework_comparison import build_defense_recovery_rows

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(root, "baseline_run", attack="none", map50=0.7)
            self._write_run(
                root,
                "attack_fgsm_targeted",
                attack="fgsm",
                map50=0.2,
                attack_params={"objective_mode": "target_class_misclassification", "target_class": 1},
                resolved_objective={"objective_mode": "target_class_misclassification", "target_class": 1},
            )
            self._write_run(
                root,
                "attack_fgsm_untargeted",
                attack="fgsm",
                map50=0.4,
                attack_params={"objective_mode": "untargeted"},
                resolved_objective={"objective_mode": "untargeted"},
            )
            self._write_run(
                root,
                "defended_targeted",
                attack="fgsm",
                defense="jpeg",
                map50=0.3,
                attack_params={"objective_mode": "target_class_misclassification", "target_class": 1},
                resolved_objective={"objective_mode": "target_class_misclassification", "target_class": 1},
                defense_params={"quality": 75},
            )
            records = discover_framework_runs(root)
            rows = build_defense_recovery_rows(records)
            self.assertEqual(len(rows), 1)
            # Must pair with targeted attack-only run (0.2), not untargeted (0.4).
            self.assertAlmostEqual(float(rows[0]["attack_mAP50"]), 0.2)

    def test_markdown_render(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(root, "baseline_run", attack="none", map50=0.6)
            records = discover_framework_runs(root)
            report = render_markdown_report(records)
            self.assertIn("# Framework Run Comparison Report", report)
            self.assertIn("baseline_run", report)
            self.assertIn("attack_then_defense", report)

    def test_legacy_defended_runs_are_marked_incomparable(self) -> None:
        from lab.reporting.framework_comparison import build_defense_recovery_rows

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(root, "baseline_run", attack="none", map50=0.7)
            self._write_run(root, "attack_run", attack="fgsm", map50=0.2)
            self._write_run(
                root,
                "defended_legacy",
                attack="fgsm",
                defense="jpeg",
                map50=0.35,
                semantic_order=None,
                transform_order=(
                    "defense.preprocess",
                    "attack.apply",
                    "model.predict",
                    "defense.postprocess",
                ),
            )
            self._write_run(
                root,
                "defended_current",
                attack="fgsm",
                defense="median_preprocess",
                map50=0.4,
            )

            records = discover_framework_runs(root)
            recovery_rows = build_defense_recovery_rows(records)
            self.assertEqual(len(recovery_rows), 1)
            self.assertEqual(recovery_rows[0]["defended_run"], "defended_current")
            legacy_record = next(record for record in records if record.run_name == "defended_legacy")
            self.assertEqual(legacy_record.semantic_order, "defense_then_attack")

            report = render_markdown_report(records)
            self.assertIn("Comparability Warning", report)
            self.assertIn("defended_legacy", report)
            self.assertIn("excluded from recovery comparisons", report)

    def test_generate_summary_interpretation_rules(self) -> None:
        baseline = {
            "predictions": {"total_detections": 100, "confidence": {"mean": 0.9}},
        }
        attack = {
            "predictions": {"total_detections": 70, "confidence": {"mean": 0.8}},
        }
        defense = {
            "predictions": {"total_detections": 72, "confidence": {"mean": 0.82}},
        }
        summary = generate_summary(baseline, attack, defense)
        self.assertEqual(summary["interpretation"], "Strong attack effect, weak defense")
        self.assertAlmostEqual(float(summary["attack_effectiveness"]), 0.3)
        self.assertAlmostEqual(float(summary["defense_recovery"]), 0.02)
        self.assertAlmostEqual(float(summary["confidence_drop"]), (0.9 - 0.8) / 0.9)
        self.assertEqual(summary["attack_effectiveness_detection"], summary["attack_effectiveness"])
        self.assertEqual(summary["defense_recovery_detection"], summary["defense_recovery"])
        self.assertIn("metric_basis", summary)

    def test_generate_summary_interpretation_insufficient_when_detection_missing(self) -> None:
        baseline = {"predictions": {"confidence": {"mean": 0.9}}}
        attack = {"predictions": {"confidence": {"mean": 0.8}}}
        summary = generate_summary(baseline, attack, None)
        self.assertIsNone(summary["attack_effectiveness"])
        self.assertEqual(summary["interpretation"], "Insufficient data for robustness interpretation")

    def test_print_summary_read_metrics_accepts_run_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(root, "baseline_run", attack="none", map50=0.6)
            payload = print_summary_cli._read_metrics(str(root / "baseline_run"))
            self.assertIn("predictions", payload)
            self.assertIn("validation", payload)

    def test_print_summary_auto_discovers_latest_matching_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(root, "baseline_old", attack="none", defense="none", seed=42, map50=0.6)
            self._write_run(root, "attack_old", attack="fgsm", defense="none", seed=42, map50=0.3)
            self._write_run(root, "baseline_new", attack="none", defense="none", seed=42, map50=0.62)
            self._write_run(root, "attack_new", attack="fgsm", defense="none", seed=42, map50=0.28)
            self._write_run(root, "defense_new", attack="fgsm", defense="blur", seed=42, map50=0.4)

            # Ensure deterministic "latest" ordering in auto mode.
            os.utime(root / "baseline_old", (1000, 1000))
            os.utime(root / "attack_old", (1001, 1001))
            os.utime(root / "baseline_new", (2000, 2000))
            os.utime(root / "attack_new", (2001, 2001))
            os.utime(root / "defense_new", (2002, 2002))

            baseline_dir, attack_dir, defense_dir = print_summary_cli._discover_auto_run_paths(root)
            self.assertEqual(baseline_dir.name, "baseline_new")
            self.assertEqual(attack_dir.name, "attack_new")
            self.assertEqual(defense_dir.name, "defense_new")

    def test_print_summary_auto_fail_fast_without_attack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(root, "baseline_only", attack="none", defense="none", seed=42, map50=0.6)
            with self.assertRaises(ValueError) as context:
                print_summary_cli._discover_auto_run_paths(root)
            self.assertIn("Unable to auto-resolve attack run", str(context.exception))
            self.assertIn("scripts/print_summary.py --baseline", str(context.exception))

    def test_team_summary_payload_and_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_root = Path(tmp)
            csv_path = report_root / "framework_run_summary.csv"
            csv_path.write_text(
                "\n".join(
                    [
                        "run_name,run_dir,model,attack,defense,seed,prediction_count,images_with_detections,total_detections,avg_confidence,validation_status,precision,recall,mAP50,mAP50-95",
                        "baseline_none,/tmp/baseline,yolo,none,none,42,8,8,21,0.76,missing,,,,",
                        "attack_blur,/tmp/blur,yolo,blur,none,42,8,8,16,0.72,missing,,,,",
                        "attack_fgsm,/tmp/fgsm,yolo,fgsm,none,42,8,8,17,0.75,missing,,,,",
                    ]
                ),
                encoding="utf-8",
            )
            (report_root / "summary_blur.txt").write_text(
                "----------------------------------\n"
                "Attack effectiveness: +23.8%\n"
                "Defense recovery: n/a\n"
                "Confidence drop: +5.0%\n"
                "\n"
                "Conclusion:\n"
                "Strong attack effect\n"
                "----------------------------------\n",
                encoding="utf-8",
            )
            payload = build_team_summary_payload(report_root)
            self.assertEqual(payload["total_attack_runs"], 2)
            strongest = payload["strongest_attack_by_detection_drop"]
            self.assertIsNotNone(strongest)
            self.assertEqual(strongest["attack"], "blur")
            json_path, md_path = write_team_summary(report_root)
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())

    def test_team_summary_prefers_authoritative_attack_only_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs_root = root / "runs"
            report_root = root / "report"
            runs_root.mkdir(parents=True, exist_ok=True)
            report_root.mkdir(parents=True, exist_ok=True)

            self._write_run(
                runs_root,
                "baseline_none",
                attack="none",
                defense="none",
                map50=0.59,
                validation_status="missing",
                total_detections=900,
                reporting_context={
                    "run_role": "baseline",
                    "dataset_scope": "smoke",
                    "authority": "diagnostic",
                    "source_phase": "phase1",
                },
            )
            self._write_run(
                runs_root,
                "validate_baseline",
                attack="none",
                defense="none",
                map50=0.61,
                total_detections=1000,
                reporting_context={
                    "run_role": "baseline",
                    "dataset_scope": "full",
                    "authority": "authoritative",
                    "source_phase": "phase4",
                },
            )
            self._write_run(
                runs_root,
                "attack_square",
                attack="square",
                defense="none",
                map50=0.30,
                validation_status="missing",
                total_detections=150,
                reporting_context={
                    "run_role": "attack_only",
                    "dataset_scope": "smoke",
                    "authority": "diagnostic",
                    "source_phase": "phase1",
                },
            )
            self._write_run(
                runs_root,
                "validate_atk_square",
                attack="square",
                defense="none",
                map50=0.28,
                total_detections=120,
                reporting_context={
                    "run_role": "attack_only",
                    "dataset_scope": "full",
                    "authority": "authoritative",
                    "source_phase": "phase4",
                },
            )
            self._write_run(
                runs_root,
                "attack_deepfool",
                attack="deepfool",
                defense="none",
                map50=0.22,
                validation_status="missing",
                total_detections=200,
                reporting_context={
                    "run_role": "attack_only",
                    "dataset_scope": "smoke",
                    "authority": "diagnostic",
                    "source_phase": "phase1",
                },
            )
            self._write_run(
                runs_root,
                "tune_atk_square_best",
                attack="square",
                defense="none",
                map50=0.27,
                validation_status="missing",
                total_detections=90,
                reporting_context={
                    "run_role": "tune",
                    "dataset_scope": "tune",
                    "authority": "diagnostic",
                    "source_phase": "phase3",
                },
            )
            self._write_run(
                runs_root,
                "consistency_atk_square",
                attack="square",
                defense="none",
                map50=0.26,
                validation_status="missing",
                total_detections=80,
                reporting_context={
                    "run_role": "consistency",
                    "dataset_scope": "smoke",
                    "authority": "diagnostic",
                    "source_phase": "phase3",
                },
            )
            self._write_run(
                runs_root,
                "validate_square_c_dog",
                attack="square",
                defense="c_dog",
                map50=0.35,
                total_detections=180,
                reporting_context={
                    "run_role": "defended",
                    "dataset_scope": "full",
                    "authority": "authoritative",
                    "source_phase": "phase4",
                },
            )

            csv_path = report_root / "framework_run_summary.csv"
            csv_path.write_text(
                "\n".join(
                    [
                        "run_name,run_dir,model,attack,defense,seed,prediction_count,images_with_detections,total_detections,avg_confidence,validation_status,precision,recall,mAP50,mAP50-95",
                        f"baseline_none,{runs_root / 'baseline_none'},yolo,none,none,42,8,8,900,0.76,missing,,,,",
                        f"validate_baseline,{runs_root / 'validate_baseline'},yolo,none,none,42,8,8,1000,0.77,complete,0.7,0.6,0.61,0.4",
                        f"attack_square,{runs_root / 'attack_square'},yolo,square,none,42,8,8,150,0.72,missing,,,,",
                        f"validate_atk_square,{runs_root / 'validate_atk_square'},yolo,square,none,42,8,8,120,0.71,complete,0.7,0.6,0.28,0.4",
                        f"attack_deepfool,{runs_root / 'attack_deepfool'},yolo,deepfool,none,42,8,8,200,0.70,missing,,,,",
                        f"tune_atk_square_best,{runs_root / 'tune_atk_square_best'},yolo,square,none,42,8,8,90,0.69,missing,,,,",
                        f"consistency_atk_square,{runs_root / 'consistency_atk_square'},yolo,square,none,42,8,8,80,0.68,missing,,,,",
                        f"validate_square_c_dog,{runs_root / 'validate_square_c_dog'},yolo,square,c_dog,42,8,8,180,0.74,complete,0.7,0.6,0.35,0.4",
                    ]
                ),
                encoding="utf-8",
            )
            (report_root / "summary_square.txt").write_text(
                "Conclusion:\nStrong attack effect\n",
                encoding="utf-8",
            )
            (report_root / "summary_deepfool.txt").write_text(
                "Conclusion:\nStrong attack effect\n",
                encoding="utf-8",
            )

            payload = build_team_summary_payload(report_root)

            self.assertEqual(payload["baseline"]["run_name"], "validate_baseline")
            self.assertEqual(payload["total_attack_runs"], 2)
            self.assertEqual(
                [row["run_name"] for row in payload["attacks_ranked"]],
                ["validate_atk_square", "attack_deepfool"],
            )
            self.assertEqual(
                payload["strongest_attack_by_detection_drop"]["run_name"],
                "validate_atk_square",
            )

    def test_team_summary_baseline_requires_none_like_attack_and_defense(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_root = Path(tmp)
            csv_path = report_root / "framework_run_summary.csv"
            csv_path.write_text(
                "\n".join(
                    [
                        "run_name,run_dir,model,attack,defense,seed,prediction_count,images_with_detections,total_detections,avg_confidence,validation_status,precision,recall,mAP50,mAP50-95",
                        "baseline_wrong,/tmp/baseline_wrong,identity,none,median_blur,42,8,8,40,0.76,missing,,,,",
                        "baseline_true,/tmp/baseline_true,yolo,identity,identity,42,8,8,50,0.76,missing,,,,",
                        "attack_blur,/tmp/blur,yolo,blur,none,42,8,8,25,0.72,missing,,,,",
                    ]
                ),
                encoding="utf-8",
            )
            payload = build_team_summary_payload(report_root)
            baseline = payload["baseline"]
            self.assertEqual(baseline["run_name"], "baseline_true")
            strongest = payload["strongest_attack_by_detection_drop"]
            self.assertIsNotNone(strongest)
            self.assertEqual(strongest["attack"], "blur")

    def test_team_summary_markdown_includes_provenance_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs_root = root / "outputs" / "framework_runs" / "sweep_test"
            report_root = root / "outputs" / "framework_reports" / "sweep_test"
            runs_root.mkdir(parents=True, exist_ok=True)
            report_root.mkdir(parents=True, exist_ok=True)
            clean_gate_path = root / "outputs" / "eval_ab_clean.json"
            clean_gate_path.parent.mkdir(parents=True, exist_ok=True)
            clean_gate_path.write_text(json.dumps({"verdict": "B is better — deploy"}), encoding="utf-8")

            self._write_run(
                runs_root,
                "validate_baseline",
                attack="none",
                defense="none",
                map50=0.61,
                total_detections=1000,
                reporting_context={
                    "run_role": "baseline",
                    "dataset_scope": "full",
                    "authority": "authoritative",
                    "source_phase": "phase4",
                },
                summary_provenance={
                    "checkpoint_fingerprint_sha256": "abc123def4567890",
                    "checkpoint_fingerprint_source": "/models/yolo.pt",
                    "defense_checkpoints": [
                        {"sha256": "fedcba9876543210", "path": "/models/c_dog.pt"}
                    ],
                },
            )
            self._write_run(
                runs_root,
                "validate_atk_blur",
                attack="blur",
                defense="none",
                map50=0.25,
                total_detections=200,
                reporting_context={
                    "run_role": "attack_only",
                    "dataset_scope": "full",
                    "authority": "authoritative",
                    "source_phase": "phase4",
                },
            )
            (report_root / "summary_blur.txt").write_text("Conclusion:\nStrong attack effect\n", encoding="utf-8")
            (report_root / "framework_run_summary.csv").write_text(
                "\n".join(
                    [
                        "run_name,run_dir,model,attack,defense,seed,semantic_order,run_role,dataset_scope,authority,source_phase,objective_mode,target_class,attack_roi,prediction_count,images_with_detections,total_detections,avg_confidence,validation_status,precision,recall,mAP50,mAP50-95",
                        f"validate_baseline,{runs_root / 'validate_baseline'},yolo,none,none,42,attack_then_defense,baseline,full,authoritative,phase4,,,,8,8,1000,0.77,complete,0.7,0.6,0.61,0.4",
                        f"validate_atk_blur,{runs_root / 'validate_atk_blur'},yolo,blur,none,42,attack_then_defense,attack_only,full,authoritative,phase4,,,,8,8,200,0.70,complete,0.7,0.6,0.25,0.4",
                    ]
                ),
                encoding="utf-8",
            )

            json_path, md_path = write_team_summary(report_root)
            md_text = md_path.read_text(encoding="utf-8")
            json_payload = json.loads(json_path.read_text(encoding="utf-8"))

            self.assertIn("## Provenance", md_text)
            self.assertIn("`abc123def456`", md_text)
            self.assertIn("`fedcba987654`", md_text)
            self.assertIn("B is better — deploy", md_text)
            self.assertNotIn("provenance", json_payload)

    def test_failure_gallery_handles_missing_image_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs_root = root / "runs"
            clean_dir = root / "clean"
            clean_dir.mkdir(parents=True, exist_ok=True)
            (clean_dir / "a.jpg").write_bytes(b"clean-a")
            (clean_dir / "b.jpg").write_bytes(b"clean-b")

            def _pred(image_id: str, count: int) -> dict[str, object]:
                return {
                    "image_id": image_id,
                    "boxes": [[0, 0, 1, 1] for _ in range(count)],
                    "scores": [0.9 for _ in range(count)],
                    "class_ids": [0 for _ in range(count)],
                    "metadata": {},
                }

            self._write_run(
                runs_root,
                "baseline_none",
                attack="none",
                defense="none",
                map50=0.60,
                total_detections=9,
                source_dir=str(clean_dir),
                prediction_rows=[_pred("a.jpg", 5), _pred("b.jpg", 4)],
            )
            self._write_run(
                runs_root,
                "attack_fgsm",
                attack="fgsm",
                defense="none",
                map50=0.20,
                total_detections=3,
                prediction_rows=[_pred("a.jpg", 0), _pred("b.jpg", 3)],
            )
            attack_images = runs_root / "attack_fgsm" / "images"
            attack_images.mkdir(parents=True, exist_ok=True)
            (attack_images / "a.jpg").write_bytes(b"attack-a")

            output_path = root / "report" / "failure_gallery.html"
            generate_failure_gallery.generate_gallery(
                runs_root=runs_root,
                output_path=output_path,
                max_images=5,
            )

            html_text = output_path.read_text(encoding="utf-8")
            self.assertIn("Failure Gallery", html_text)
            self.assertIn("missing", html_text)
            self.assertIn("a.jpg", html_text)
            self.assertIn("b.jpg", html_text)

    def test_failure_gallery_falls_back_to_text_only_without_prepared_images(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs_root = root / "runs"
            clean_dir = root / "clean"
            clean_dir.mkdir(parents=True, exist_ok=True)
            (clean_dir / "drop_big.jpg").write_bytes(b"clean-big")
            (clean_dir / "drop_small.jpg").write_bytes(b"clean-small")

            def _pred(image_id: str, count: int) -> dict[str, object]:
                return {
                    "image_id": image_id,
                    "boxes": [[0, 0, 1, 1] for _ in range(count)],
                    "scores": [0.9 for _ in range(count)],
                    "class_ids": [0 for _ in range(count)],
                    "metadata": {},
                }

            self._write_run(
                runs_root,
                "baseline_none",
                attack="none",
                defense="none",
                map50=0.60,
                total_detections=10,
                source_dir=str(clean_dir),
                prediction_rows=[_pred("drop_big.jpg", 6), _pred("drop_small.jpg", 4)],
            )
            self._write_run(
                runs_root,
                "attack_blur",
                attack="blur",
                defense="none",
                map50=0.30,
                total_detections=5,
                prediction_rows=[_pred("drop_big.jpg", 1), _pred("drop_small.jpg", 4)],
            )

            output_path = root / "report" / "failure_gallery.html"
            generate_failure_gallery.generate_gallery(
                runs_root=runs_root,
                output_path=output_path,
                max_images=5,
            )

            html_text = output_path.read_text(encoding="utf-8")
            self.assertIn("Prepared images were not available", html_text)
            self.assertNotIn("<img src=", html_text)
            self.assertLess(html_text.index("drop_big.jpg"), html_text.index("drop_small.jpg"))

    def test_build_comparison_rows_treats_identity_as_none_like(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(root, "baseline_identity", attack="identity", map50=0.6)
            self._write_run(root, "fgsm_run", attack="fgsm", map50=0.2)
            records = discover_framework_runs(root)
            rows = build_comparison_rows(records)
            self.assertEqual(len(rows), 1)
            self.assertAlmostEqual(float(rows[0]["mAP50_drop"]), 0.4)


class WS1AtomicWriteTest(unittest.TestCase):
    """Tests for atomic (tmp+replace) writes in reporting writers (WS1)."""

    def _make_minimal_run_dir(self, root: Path, run_name: str, *, attack: str = "none") -> None:
        """Write minimal valid run artifacts for discover_framework_runs."""
        run_dir = root / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "run_summary.json").write_text(
            json.dumps({
                "model": {"name": "yolo", "params": {}},
                "attack": {"name": attack, "params": {}},
                "defense": {"name": "none", "params": {}},
                "seed": 42,
                "prediction_record_count": 1,
                "pipeline": {
                    "transform_order": ["attack.apply", "defense.preprocess", "model.predict", "defense.postprocess"],
                    "semantic_order": "attack_then_defense",
                },
                "provenance": {"checkpoint_fingerprint_sha256": None, "defense_checkpoints": []},
                "attack": {"name": attack, "params": {}, "signature": "sig"},
                "defense": {"name": "none", "params": {}, "signature": "sig"},
            }),
            encoding="utf-8",
        )
        (run_dir / "metrics.json").write_text(
            json.dumps({
                "predictions": {
                    "image_count": 1,
                    "images_with_detections": 1,
                    "total_detections": 5,
                    "confidence": {"mean": 0.8},
                },
                "validation": {"status": "missing", "enabled": False, "error": None},
                "provenance": {
                    "transform_order": ["attack.apply", "defense.preprocess", "model.predict", "defense.postprocess"],
                    "semantic_order": "attack_then_defense",
                },
            }),
            encoding="utf-8",
        )
        (run_dir / "predictions.jsonl").write_text(
            json.dumps({"image_id": "a.jpg", "boxes": [], "scores": [], "class_ids": [], "metadata": {}}) + "\n",
            encoding="utf-8",
        )

    def test_write_summary_csv_leaves_no_tmp_file(self) -> None:
        """write_summary_csv must leave no .tmp file after a successful write."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_minimal_run_dir(root, "baseline_none")
            records = _discover(root)
            out_csv = root / "framework_run_summary.csv"
            write_summary_csv(records, out_csv)
            self.assertTrue(out_csv.exists())
            tmp_files = list(root.glob("*.tmp"))
            self.assertEqual(tmp_files, [], f"Leftover .tmp after write_summary_csv: {tmp_files}")

    def test_write_summary_csv_output_is_readable_csv(self) -> None:
        """write_summary_csv output must be a valid CSV with at least a header row."""
        import csv as _csv
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_minimal_run_dir(root, "baseline_none")
            records = _discover(root)
            out_csv = root / "framework_run_summary.csv"
            write_summary_csv(records, out_csv)
            rows = list(_csv.DictReader(out_csv.open(encoding="utf-8")))
            self.assertGreater(len(rows), 0)
            self.assertIn("run_name", rows[0])

    def test_write_team_summary_leaves_no_tmp_files(self) -> None:
        """write_team_summary must leave no .tmp file after a successful write."""
        with tempfile.TemporaryDirectory() as tmp:
            report_root = Path(tmp)
            import csv as _csv
            csv_path = report_root / "framework_run_summary.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as fh:
                writer = _csv.writer(fh)
                writer.writerow([
                    "run_name", "run_dir", "model", "attack", "defense", "seed",
                    "prediction_count", "images_with_detections", "total_detections",
                    "avg_confidence", "validation_status", "precision", "recall",
                    "mAP50", "mAP50-95",
                ])
                writer.writerow([
                    "baseline_none", str(tmp), "yolo", "none", "none", "42",
                    "8", "8", "20", "0.8", "missing", "", "", "", "",
                ])
            write_team_summary(report_root)
            tmp_files = list(report_root.glob("*.tmp"))
            self.assertEqual(tmp_files, [], f"Leftover .tmp after write_team_summary: {tmp_files}")
            self.assertTrue((report_root / "team_summary.json").exists())
            self.assertTrue((report_root / "team_summary.md").exists())


class WS3WarningCorrectnessTest(unittest.TestCase):
    """WS3 tests: warning code rename, NO_VALIDATION pre-filter, attack_signature dedup."""

    def _make_payload(
        self,
        *,
        attack_rows: list[dict] | None = None,
        baseline_avg_confidence: float | None = None,
    ) -> dict:
        baseline: dict = {"run_name": "baseline", "candidate_count": 1}
        if baseline_avg_confidence is not None:
            baseline["avg_confidence"] = baseline_avg_confidence
        return {
            "baseline": baseline,
            "attack_effectiveness_rows": attack_rows or [],
            "defense_recovery_rows": [],
            "per_class_vulnerability_rows": [],
        }

    def test_warn_low_confidence_floor_code_is_correct_string(self) -> None:
        """The renamed constant must carry the correct string value."""
        self.assertEqual(WARN_LOW_CONFIDENCE_FLOOR, "LOW_CONFIDENCE_FLOOR")

    def test_warn_low_confidence_floor_fires_when_confidence_below_half(self) -> None:
        """evaluate_warnings must emit LOW_CONFIDENCE_FLOOR (not HIGH_*) when avg_confidence < 0.5."""
        payload = self._make_payload(baseline_avg_confidence=0.3)
        warnings = evaluate_warnings(payload)
        codes = [w["code"] for w in warnings]
        self.assertIn(WARN_LOW_CONFIDENCE_FLOOR, codes)
        self.assertNotIn("HIGH_CONFIDENCE_FLOOR", codes)

    def test_no_validation_not_fired_when_phase4_rows_exist_but_not_authoritative(self) -> None:
        """NO_VALIDATION must be suppressed when full (unfiltered) rows have a success status,
        even if those rows are not authoritative and get filtered out by _prefer_authoritative_rows.

        The bug: has_validation was computed AFTER _prefer_authoritative_rows stripped Phase 4
        rows, causing a false NO_VALIDATION warning. The fix computes has_validation first.
        """
        from lab.config.contracts import REPORTING_AUTHORITY_DIAGNOSTIC, REPORTING_AUTHORITY_AUTHORITATIVE
        # One authoritative diagnostic-only smoke row (no validation success)
        authoritative_smoke = {
            "authority": REPORTING_AUTHORITY_AUTHORITATIVE,
            "validation_status": "missing",
            "attack": "fgsm",
        }
        # One non-authoritative Phase 4 row with a real validation success
        phase4_row = {
            "authority": REPORTING_AUTHORITY_DIAGNOSTIC,
            "validation_status": "complete",
            "attack": "fgsm",
        }
        payload = self._make_payload(attack_rows=[authoritative_smoke, phase4_row])
        warnings = evaluate_warnings(payload)
        codes = [w["code"] for w in warnings]
        self.assertNotIn(WARN_NO_VALIDATION, codes)

    def test_no_validation_still_fires_when_all_rows_lack_success(self) -> None:
        """NO_VALIDATION must still fire when no row anywhere has a success status."""
        from lab.config.contracts import REPORTING_AUTHORITY_AUTHORITATIVE
        row = {
            "authority": REPORTING_AUTHORITY_AUTHORITATIVE,
            "validation_status": "missing",
            "attack": "fgsm",
        }
        payload = self._make_payload(attack_rows=[row, row])
        warnings = evaluate_warnings(payload)
        codes = [w["code"] for w in warnings]
        self.assertIn(WARN_NO_VALIDATION, codes)


if __name__ == "__main__":
    unittest.main()
