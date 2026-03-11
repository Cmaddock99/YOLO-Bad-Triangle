from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from lab.attacks import build_attack
from lab.defenses import build_defense
from lab.eval import append_run_metrics
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
    data_yaml: str
    image_dir: Path
    confs: list[float]
    iou: float
    imgsz: int
    seed: int
    output_root: Path
    metrics_csv: str
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

        experiments = [ExperimentSpec(**exp_cfg) for exp_cfg in experiments_cfg]
        return cls(
            model_path=model_cfg.get("path", "yolo11n.pt"),
            data_yaml=data_cfg.get("data_yaml", "configs/coco_subset500.yaml"),
            image_dir=Path(data_cfg.get("image_dir", "coco/val2017_subset500/images")),
            confs=[float(value) for value in runner_cfg.get("confs", [0.5])],
            iou=float(runner_cfg.get("iou", 0.7)),
            imgsz=int(runner_cfg.get("imgsz", 640)),
            seed=int(runner_cfg.get("seed", 0)),
            output_root=Path(runner_cfg.get("output_root", "outputs")),
            metrics_csv=runner_cfg.get("metrics_csv", "metrics_summary.csv"),
            experiments=experiments,
        )

    @staticmethod
    def _conf_token(conf: float) -> str:
        return f"{int(round(conf * 100)):03d}"

    def _run_name_for(self, spec: ExperimentSpec, conf: float) -> str:
        context = {
            "name": spec.name,
            "attack": spec.attack,
            "defense": spec.defense,
            "conf": conf,
            "conf_token": self._conf_token(conf),
            **spec.attack_params,
            **spec.defense_params,
        }
        return spec.run_name_template.format(**context)

    def _write_val_metrics(self, run_dir: Path, validation_results: Any) -> None:
        box = getattr(validation_results, "box", None)
        if box is None:
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

    def _prepare_source(
        self,
        *,
        spec: ExperimentSpec,
        run_name: str,
    ) -> Path:
        source_dir = Path(spec.source_override) if spec.source_override else self.image_dir
        intermediate_root = self.output_root / "_intermediates" / run_name
        if intermediate_root.exists():
            shutil.rmtree(intermediate_root)
        intermediate_root.mkdir(parents=True, exist_ok=True)

        attack = build_attack(spec.attack, spec.attack_params)
        attacked_source = attack.apply(source_dir, intermediate_root / "attacked", seed=self.seed)

        defense = build_defense(spec.defense, spec.defense_params)
        defended_source = defense.apply(attacked_source, intermediate_root / "defended", seed=self.seed)
        return defended_source

    def run(self) -> list[dict[str, Any]]:
        self.output_root.mkdir(parents=True, exist_ok=True)
        model = YOLOModel(self.model_path)
        csv_path = self.output_root / self.metrics_csv
        all_rows: list[dict[str, Any]] = []

        for conf in self.confs:
            for spec in self.experiments:
                run_name = self._run_name_for(spec, conf)
                run_dir = self.output_root / run_name
                if run_dir.exists():
                    shutil.rmtree(run_dir)

                source_dir = self._prepare_source(spec=spec, run_name=run_name)
                should_validate = (
                    spec.run_validation
                    if spec.run_validation is not None
                    else spec.attack == "none" and spec.defense == "none"
                )
                if should_validate:
                    validation = model.validate(
                        data=self.data_yaml,
                        imgsz=self.imgsz,
                        conf=conf,
                        iou=self.iou,
                        seed=self.seed,
                    )
                    self._write_val_metrics(run_dir, validation)

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

                row = append_run_metrics(
                    run_dir=run_dir,
                    csv_path=csv_path,
                    run_name=run_name,
                    attack=spec.attack_label or spec.attack,
                    defense=spec.defense_label or spec.defense,
                    conf=conf,
                    iou=self.iou,
                    imgsz=self.imgsz,
                    seed=self.seed,
                )
                all_rows.append(row)
                print(
                    f"Completed run={run_name} attack={spec.attack_label or spec.attack} "
                    f"defense={spec.defense_label or spec.defense} conf={conf}"
                )
        return all_rows

