from __future__ import annotations

import importlib
import unittest


class RepoStructureCompatTest(unittest.TestCase):
    def test_root_wrappers_alias_to_moved_modules(self) -> None:
        cases = (
            ("scripts.auto_cycle", "scripts.automation.auto_cycle"),
            ("scripts.run_training_ritual", "scripts.training.run_training_ritual"),
            ("scripts.run_demo", "scripts.demo.run_demo"),
            ("scripts.generate_auto_summary", "scripts.reporting.generate_auto_summary"),
        )

        for old_name, new_name in cases:
            with self.subTest(old_name=old_name):
                old_mod = importlib.import_module(old_name)
                new_mod = importlib.import_module(new_name)
                self.assertIs(old_mod, new_mod)

    def test_old_adapter_shims_alias_to_moved_modules(self) -> None:
        cases = (
            ("lab.attacks.fgsm_adapter", "lab.plugins.core.attacks.fgsm_adapter"),
            ("lab.attacks.cw_adapter", "lab.plugins.extra.attacks.cw_adapter"),
            ("lab.models.yolo_adapter", "lab.plugins.core.models.yolo_adapter"),
            ("lab.models.torchvision_adapter", "lab.plugins.extra.models.torchvision_adapter"),
        )

        for old_name, new_name in cases:
            with self.subTest(old_name=old_name):
                old_mod = importlib.import_module(old_name)
                new_mod = importlib.import_module(new_name)
                self.assertIs(old_mod, new_mod)

    def test_reporting_umbrella_still_exports_render_markdown_report(self) -> None:
        from lab.reporting import render_markdown_report
        from lab.reporting.framework import render_markdown_report as framework_render_markdown_report

        self.assertIs(render_markdown_report, framework_render_markdown_report)


if __name__ == "__main__":
    unittest.main()
