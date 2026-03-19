from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from lab.migration.cycle_tracker import update_migration_cycle_tracker


class MigrationCycleTrackerTest(unittest.TestCase):
    def test_tracker_counts_consecutive_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "tracker.json"
            state1 = update_migration_cycle_tracker(
                cycle_name="cycle1",
                gate_results={
                    "contract_ownership": True,
                    "parity": True,
                    "demo": True,
                    "artifact": True,
                    "schema": True,
                    "system_health": True,
                },
                state_path=state_path,
            )
            self.assertEqual(state1.consecutive_full_passes, 1)
            state2 = update_migration_cycle_tracker(
                cycle_name="cycle2",
                gate_results={
                    "contract_ownership": True,
                    "parity": True,
                    "demo": True,
                    "artifact": True,
                    "schema": True,
                    "system_health": True,
                },
                state_path=state_path,
            )
            self.assertEqual(state2.consecutive_full_passes, 2)
            self.assertEqual(state2.legacy_status, "deprecated")

    def test_tracker_resets_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "tracker.json"
            update_migration_cycle_tracker(
                cycle_name="pass",
                gate_results={
                    "contract_ownership": True,
                    "parity": True,
                    "demo": True,
                    "artifact": True,
                    "schema": True,
                    "system_health": True,
                },
                state_path=state_path,
            )
            state = update_migration_cycle_tracker(
                cycle_name="fail",
                gate_results={
                    "contract_ownership": True,
                    "parity": False,
                    "demo": True,
                    "artifact": True,
                    "schema": True,
                    "system_health": True,
                },
                state_path=state_path,
            )
            self.assertEqual(state.consecutive_full_passes, 0)
            self.assertFalse(state.last_cycle_passed)


if __name__ == "__main__":
    unittest.main()
