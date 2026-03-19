from __future__ import annotations

import unittest
from pathlib import Path

from lab.config.contracts import MAX_FIX_LOOP


class FixLoopGovernanceTest(unittest.TestCase):
    def test_global_fix_loop_constant(self) -> None:
        self.assertEqual(MAX_FIX_LOOP, 5)

    def test_reason_code_mapping(self) -> None:
        script_path = Path("scripts/ci/orchestrate_multi_agent_validation.py").resolve()
        text = script_path.read_text(encoding="utf-8")
        self.assertIn("SCHEMA_RECURRING", text)
        self.assertIn("DEMO_ARTIFACT_FLAP", text)
        self.assertIn("PARITY_STUCK", text)


if __name__ == "__main__":
    unittest.main()
