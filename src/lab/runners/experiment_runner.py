from __future__ import annotations

import hashlib
import inspect
import json
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TYPE_CHECKING

import yaml

from lab.attacks import build_attack
from lab.defenses import build_defense
from lab.eval import append_run_metrics
from lab.models.model_utils import model_label_from_path, normalize_model_path

if TYPE_CHECKING:
    from lab.models import YOLOModel


@dataclass
class ExperimentSpec:
    name: str
    attack: str = "none"
    defense: str = "none"
    attack_label: str | None = None
    defense_label: str | None = None
    run_name_template: str = "{name}_conf{conf_token}"
    attack_params: dict[str, Any] = field(default_factory=dict)
    defense_params: dict[str, Any] = field(default_factory=dict)
    source_override: str | None = None
    run_validation: bool | None = None


@dataclass
class ExperimentRunner:
    model_path: str
    model_label: str
    data_yaml: str
    image_dir: Path
    confs: list[float]
    iou: float
    imgsz: int
    seed: int
    output_root: Path
    metrics_csv: str
    default_run_validation: bool
    clean_existing_runs: bool
    experiments: list[ExperimentSpec]

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> "ExperimentRunner":
        config = yaml.safe_load(Path(config_path).read_text())
        return cls.from_dict(config)

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "ExperimentRunner":
        model_cfg = config.get("model", {})
        data_cfg = config.get("data", {})
        runner_cfg = config.get("runner", {})
        experiments_cfg = config.get("experiments", [])

        if not experiments_cfg:
            raise ValueError("Config must include at least one experiment in 'experiments'.")

        model_path: str
        model_label: str
        if isinstance(model_cfg, dict):
            model_path = normalize_model_path(
                str(model_cfg.get("path") or model_cfg.get("name") or "")
            )
            model_label = str(model_cfg.get("label") or model_label_from_path(model_path))
        else:
            model_path = normalize_model_path(str(model_cfg or ""))
            model_label = model_label_from_path(model_path)

        experiments = [ExperimentSpec(**exp_cfg) for exp_cfg in experiments_cfg]
        data_yaml_path = Path(data_cfg.get("data_yaml", "configs/coco_subset500.yaml")).expanduser().resolve()
        image_dir_path = Path(data_cfg.get("image_dir", "coco/val2017_subset500/images")).expanduser().resolve()
        output_root_path = Path(runner_cfg.get("output_root", "outputs")).expanduser().resolve()
        return cls(
            model_path=model_path,
            model_label=model_label,
            data_yaml=str(data_yaml_path),
            image_dir=image_dir_path,
            confs=[float(value) for value in runner_cfg.get("confs", [0.5])],
            iou=float(runner_cfg.get("iou", 0.7)),
            imgsz=int(runner_cfg.get("imgsz", 640)),
            seed=int(runner_cfg.get("seed", 0)),
            output_root=output_root_path,
            metrics_csv=runner_cfg.get("metrics_csv", "metrics_summary.csv"),
            default_run_validation=bool(runner_cfg.get("run_validation", True)),
            clean_existing_runs=bool(runner_cfg.get("clean_existing_runs", True)),
            experiments=experiments,
        )

    @staticmethod
    def _conf_token(conf: float) -> str:
        return f"{int(round(conf * 100)):03d}"

    @staticmethod
    def _assert_run_name_safe(run_name: str) -> None:
        normalized = run_name.strip()
        if not normalized:
            raise ValueError("run_name cannot be empty.")
        if normalized in {".", ".."}:
            raise ValueError(f"Unsafe run_name '{run_name}'.")
        if Path(normalized).is_absolute():
            raise ValueError(f"Unsafe run_name '{run_name}': absolute paths are not allowed.")
        if ".." in Path(normalized).parts:
            raise ValueError(f"Unsafe run_name '{run_name}': path traversal is not allowed.")
        if re.search(r"[\\/]", normalized):
            raise ValueError(
                f"Unsafe run_name '{run_name}': path separators are not allowed in run names."
            )

    def _assert_within_output_root(self, path: Path, *, context: str) -> Path:
        output_root_resolved = self.output_root.resolve()
        candidate = path.resolve()
        if candidate != output_root_resolved and output_root_resolved not in candidate.parents:
            raise ValueError(
                f"Refusing to access path outside output_root for {context}: "
                f"'{candidate}' not under '{output_root_resolved}'."
            )
        return candidate

    def _metrics_csv_path(self) -> Path:
        raw = Path(self.metrics_csv).expanduser()
        candidate = raw if raw.is_absolute() else (self.output_root / raw)
        return self._assert_within_output_root(candidate, context="metrics_csv")

    def _reset_dir(self, path: Path, *, context: str) -> None:
        if not path.exists():
            return
        if not self.clean_existing_runs:
            raise FileExistsError(
                f"{context} already exists at '{path}'. "
                "Set runner.clean_existing_runs=true to allow overwrite."
            )
        shutil.rmtree(path)

    def _run_name_for(self, spec: ExperimentSpec, conf: float) -> str:
        context = {
            "model": self.model_label,
            "name": spec.name,
            "attack": spec.attack,
            "defense": spec.defense,
            "conf": conf,
            "conf_token": self._conf_token(conf),
            **spec.attack_params,
            **spec.defense_params,
        }
        run_name = spec.run_name_template.format(**context)
        model_prefix = f"{self.model_label}_"
        if run_name.startswith(model_prefix):
            return run_name
        return f"{model_prefix}{run_name}"

    def _write_val_metrics(
        self,
        run_dir: Path,
        validation_results: Any,
        *,
        data_yaml_used: str,
    ) -> None:
        box = getattr(validation_results, "box", None)
        if box is None:
            print(
                f"WARNING: Validation results for run '{run_dir.name}' did not include "
                "a 'box' metrics object; precision/recall/mAP will be unavailable."
            )
            return

        metrics = {
            "mAP50": float(getattr(box, "map50", 0.0)),
            "mAP50-95": float(getattr(box, "map", 0.0)),
            "precision": float(getattr(box, "mp", 0.0)),
            "recall": float(getattr(box, "mr", 0.0)),
        }
        val_dir = run_dir / "val"
        val_dir.mkdir(parents=True, exist_ok=True)
        (val_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
        print(
            f"Validation metrics saved for run '{run_dir.name}' from data='{data_yaml_used}': "
            f"precision={metrics['precision']:.6f}, recall={metrics['recall']:.6f}, "
            f"mAP50={metrics['mAP50']:.6f}, mAP50-95={metrics['mAP50-95']:.6f}"
        )

    def _resolve_labels_dir(self, *, source_dir: Path) -> Path:
        source_labels = source_dir.parent / "labels"
        default_labels = self.image_dir.parent / "labels"
        for candidate in (source_labels, default_labels):
            if candidate.exists():
                return candidate
        raise FileNotFoundError(
            "Cannot locate labels directory for per-run validation. "
            f"Checked '{source_labels}' and '{default_labels}'."
        )

    @staticmethod
    def _count_source_images(source_dir: Path) -> int:
        image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
        return sum(
            1
            for path in source_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in image_exts
        )

    def _validation_data_yaml_for_run(self, *, run_name: str, source_dir: Path) -> str:
        """Build a per-run data YAML that validates against attacked/defended images."""
        self._assert_run_name_safe(run_name)
        labels_dir = self._resolve_labels_dir(source_dir=source_dir)

        intermediate_root = self.output_root / "_intermediates" / run_name
        self._assert_within_output_root(
            intermediate_root,
            context=f"validation intermediate root for run '{run_name}'",
        )
        val_dataset_root = intermediate_root / "_val_dataset"
        self._assert_within_output_root(
            val_dataset_root,
            context=f"validation dataset root for run '{run_name}'",
        )
        self._reset_dir(
            val_dataset_root,
            context=f"validation dataset root for run '{run_name}'",
        )
        val_dataset_root.mkdir(parents=True, exist_ok=True)

        images_link = val_dataset_root / "images"
        labels_link = val_dataset_root / "labels"
        images_link.mkdir(parents=True, exist_ok=True)
        image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}

        # Keep "images/" as a real directory under val_dataset_root so Ultralytics
        # can consistently resolve sibling "labels/" for validation.
        for image_path in source_dir.rglob("*"):
            if not image_path.is_file() or image_path.suffix.lower() not in image_exts:
                continue
            relative = image_path.relative_to(source_dir)
            target_path = images_link / relative
            target_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                target_path.symlink_to(image_path.resolve())
            except OSError:
                shutil.copy2(image_path, target_path)

        try:
            labels_link.symlink_to(labels_dir.resolve(), target_is_directory=True)
        except OSError:
            shutil.copytree(labels_dir, labels_link)

        base_data = yaml.safe_load(Path(self.data_yaml).read_text()) or {}
        if not isinstance(base_data, dict):
            base_data = {}
        names = base_data.get("names", {})

        run_data_yaml = val_dataset_root / "data.yaml"
        run_data_yaml.write_text(
            yaml.safe_dump(
                {
                    "path": str(val_dataset_root.resolve()),
                    "train": "images",
                    "val": "images",
                    "names": names,
                },
                sort_keys=False,
            )
        )
        return str(run_data_yaml)

    def _config_fingerprint(
        self,
        *,
        spec: ExperimentSpec,
        conf: float,
        transformed_source_dir: Path,
        validation_labels_dir: str,
        transformed_image_count: int,
        validation_data_yaml: str | None,
    ) -> str:
        payload = {
            "model_path": self.model_path,
            "model_label": self.model_label,
            "data_yaml": self.data_yaml,
            "image_dir": str(self.image_dir),
            "conf": conf,
            "iou": self.iou,
            "imgsz": self.imgsz,
            "seed": self.seed,
            "attack": spec.attack,
            "attack_label": spec.attack_label,
            "attack_params": spec.attack_params,
            "defense": spec.defense,
            "defense_label": spec.defense_label,
            "defense_params": spec.defense_params,
            "run_name_template": spec.run_name_template,
            "source_override": spec.source_override,
            "transformed_source_dir": str(transformed_source_dir.resolve()),
            "validation_labels_dir": validation_labels_dir,
            "transformed_image_count": transformed_image_count,
            "validation_data_yaml": validation_data_yaml or "",
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

    def _prepare_source(
        self,
        *,
        spec: ExperimentSpec,
        run_name: str,
        model: YOLOModel,
    ) -> Path:
        self._assert_run_name_safe(run_name)
        source_dir = (
            Path(spec.source_override).expanduser().resolve()
            if spec.source_override
            else self.image_dir
        )
        intermediate_root = self.output_root / "_intermediates" / run_name
        self._assert_within_output_root(
            intermediate_root,
            context=f"attack/defense intermediate root for run '{run_name}'",
        )
        self._reset_dir(
            intermediate_root,
            context=f"attack/defense intermediate root for run '{run_name}'",
        )
        intermediate_root.mkdir(parents=True, exist_ok=True)

        attack = build_attack(spec.attack, spec.attack_params)
        attack_apply_kwargs: dict[str, Any] = {"seed": self.seed}
        attack_signature = inspect.signature(attack.apply)
        accepts_var_kwargs = any(
            parameter.kind == inspect.Parameter.VAR_KEYWORD
            for parameter in attack_signature.parameters.values()
        )
        if "model" in attack_signature.parameters or accepts_var_kwargs:
            # Use a fresh model instance for gradient-based attack preprocessing
            # to avoid inference-mode tensor state leaking from prior predict/val calls.
            from lab.models import YOLOModel as AttackYOLOModel

            attack_apply_kwargs["model"] = AttackYOLOModel(self.model_path)
        attacked_source = attack.apply(
            source_dir,
            intermediate_root / "attacked",
            **attack_apply_kwargs,
        )

        defense = build_defense(spec.defense, spec.defense_params)
        defended_source = defense.apply(attacked_source, intermediate_root / "defended", seed=self.seed)
        return defended_source

    def run(self) -> list[dict[str, Any]]:
        self.output_root.mkdir(parents=True, exist_ok=True)
        from lab.models import YOLOModel

        model = YOLOModel(self.model_path)
        csv_path = self._metrics_csv_path()
        all_rows: list[dict[str, Any]] = []
        run_started_at_utc = datetime.now(timezone.utc).isoformat()
        run_session_id = hashlib.sha1(
            f"{run_started_at_utc}|{self.output_root.resolve()}|{self.model_path}|{self.seed}".encode(
                "utf-8"
            )
        ).hexdigest()[:12]

        for conf in self.confs:
            for spec in self.experiments:
                run_name = self._run_name_for(spec, conf)
                self._assert_run_name_safe(run_name)
                run_dir = self._assert_within_output_root(
                    self.output_root / run_name,
                    context=f"run directory for run '{run_name}'",
                )
                self._reset_dir(run_dir, context=f"run directory for run '{run_name}'")
                should_validate = (
                    spec.run_validation
                    if spec.run_validation is not None
                    else self.default_run_validation
                )
                validation_data_yaml: str | None = None
                validation_labels_dir = ""
                validation_reason = ""
                source_dir: Path | None = None
                source_image_count = 0
                stage = "prepare_source"
                try:
                    source_dir = self._prepare_source(spec=spec, run_name=run_name, model=model)
                    # Validate every run by default so precision/recall/mAP fields
                    # are always populated in metrics_summary.csv.
                    stage = "count_source_images"
                    source_image_count = self._count_source_images(source_dir)
                    if source_image_count == 0:
                        raise RuntimeError(
                            f"No source images found for run '{run_name}' at '{source_dir}'. "
                            "Cannot trust metrics for an empty transformed dataset."
                        )
                    if should_validate:
                        stage = "prepare_validation_dataset"
                        labels_dir = self._resolve_labels_dir(source_dir=source_dir)
                        validation_labels_dir = str(labels_dir.resolve())
                        validation_data_yaml = self._validation_data_yaml_for_run(
                            run_name=run_name,
                            source_dir=source_dir,
                        )
                        stage = "validate"
                        validation = model.validate(
                            data=validation_data_yaml,
                            imgsz=self.imgsz,
                            conf=conf,
                            iou=self.iou,
                            seed=self.seed,
                        )
                        self._write_val_metrics(
                            run_dir,
                            validation,
                            data_yaml_used=validation_data_yaml,
                        )
                    else:
                        validation_reason = "validation_disabled_by_config"
                        try:
                            validation_labels_dir = str(
                                self._resolve_labels_dir(source_dir=source_dir).resolve()
                            )
                        except FileNotFoundError:
                            validation_labels_dir = ""
                            validation_reason = "validation_disabled_labels_missing"
                        print(
                            f"WARNING: Validation disabled for run '{run_name}' "
                            "(run_validation=false); precision/recall/mAP fields may be empty."
                        )

                    stage = "predict"
                    model.predict(
                        source=str(source_dir),
                        imgsz=self.imgsz,
                        conf=conf,
                        iou=self.iou,
                        seed=self.seed,
                        save=True,
                        save_txt=True,
                        save_conf=True,
                        project=str(self.output_root.resolve()),
                        name=run_name,
                        exist_ok=True,
                    )
                    stage = "append_metrics"
                    row = append_run_metrics(
                        run_dir=run_dir,
                        csv_path=csv_path,
                        run_name=run_name,
                        model=self.model_label,
                        attack=spec.attack_label or spec.attack,
                        defense=spec.defense_label or spec.defense,
                        conf=conf,
                        iou=self.iou,
                        imgsz=self.imgsz,
                        seed=self.seed,
                        extra_metadata={
                            "validation_enabled": should_validate,
                            "validation_reason": validation_reason,
                            "run_session_id": run_session_id,
                            "run_started_at_utc": run_started_at_utc,
                            "validation_data_yaml": validation_data_yaml or "",
                            "validation_labels_dir": validation_labels_dir,
                            "transformed_source_dir": str(source_dir.resolve()),
                            "transformed_image_count": source_image_count,
                            "config_fingerprint": self._config_fingerprint(
                                spec=spec,
                                conf=conf,
                                transformed_source_dir=source_dir,
                                validation_labels_dir=validation_labels_dir,
                                transformed_image_count=source_image_count,
                                validation_data_yaml=validation_data_yaml,
                            ),
                            "attack_params_json": json.dumps(spec.attack_params, sort_keys=True),
                            "defense_params_json": json.dumps(spec.defense_params, sort_keys=True),
                        },
                    )
                    all_rows.append(row)
                    print(
                        f"Completed run={run_name} model={self.model_label} "
                        f"attack={spec.attack_label or spec.attack} "
                        f"defense={spec.defense_label or spec.defense} conf={conf}"
                    )
                except Exception as exc:  # broad: any failure in a batch run should be logged, not fatal
                    error_reason = f"{type(exc).__name__} at {stage}: {exc}"
                    row = append_run_metrics(
                        run_dir=run_dir,
                        csv_path=csv_path,
                        run_name=run_name,
                        model=self.model_label,
                        attack=spec.attack_label or spec.attack,
                        defense=spec.defense_label or spec.defense,
                        conf=conf,
                        iou=self.iou,
                        imgsz=self.imgsz,
                        seed=self.seed,
                        extra_metadata={
                            "row_status": "failed",
                            "error_reason": error_reason,
                            "validation_enabled": should_validate,
                            "validation_reason": validation_reason,
                            "run_session_id": run_session_id,
                            "run_started_at_utc": run_started_at_utc,
                            "validation_data_yaml": validation_data_yaml or "",
                            "validation_labels_dir": validation_labels_dir,
                            "transformed_source_dir": (
                                str(source_dir.resolve()) if source_dir is not None else ""
                            ),
                            "transformed_image_count": source_image_count,
                            "config_fingerprint": "",
                            "attack_params_json": json.dumps(spec.attack_params, sort_keys=True),
                            "defense_params_json": json.dumps(spec.defense_params, sort_keys=True),
                        },
                    )
                    all_rows.append(row)
                    raise RuntimeError(
                        f"Run '{run_name}' failed during stage '{stage}': {exc}"
                    ) from exc
        return all_rows

