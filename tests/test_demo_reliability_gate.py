from __future__ import annotations

import unittest
from pathlib import Path


class DemoReliabilityGateTest(unittest.TestCase):
    def test_demo_gate_has_required_reliability_assertions(self) -> None:
        text = Path("scripts/ci/check_demo_gate.py").read_text(encoding="utf-8")
        self.assertIn("run_and_require_success(", text)
        self.assertIn("assert_required_artifacts(", text)
        self.assertIn("path.stat().st_size <= 0", text)
        self.assertIn('print("NO CRITICAL FAILURES")', text)


if __name__ == "__main__":
    unittest.main()
