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
from lab.reporting.warnings import (
    WARN_ATTACK_BELOW_NOISE,
    WARN_DEFENSE_DEGRADES_PERFORMANCE,
    WARN_DEFENSE_RECOVERY_UNDEFINED,
    WARN_LOW_ATTACK_COUNT,
    WARN_MISSING_PER_CLASS,
    WARN_MULTIPLE_BASELINES,
    WARN_NO_VALIDATION,
    evaluate_warnings,
)
from scripts import print_summary as print_summary_cli


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

    def test_build_comparison_rows_treats_identity_as_none_like(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_run(root, "baseline_identity", attack="identity", map50=0.6)
            self._write_run(root, "fgsm_run", attack="fgsm", map50=0.2)
            records = discover_framework_runs(root)
            rows = build_comparison_rows(records)
            self.assertEqual(len(rows), 1)
            self.assertAlmostEqual(float(rows[0]["mAP50_drop"]), 0.4)


if __name__ == "__main__":
    unittest.main()
