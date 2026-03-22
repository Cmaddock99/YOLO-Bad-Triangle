from __future__ import annotations

import unittest

from lab.attacks.objective import AttackObjective


class AttackObjectiveContractTest(unittest.TestCase):
    def test_default_objective_is_untargeted(self) -> None:
        obj = AttackObjective.from_params({})
        self.assertEqual(obj.mode, "untargeted_conf_suppression")
        self.assertIsNone(obj.target_class)

    def test_target_class_requires_target_class_id(self) -> None:
        with self.assertRaises(ValueError):
            AttackObjective.from_params({"objective_mode": "target_class_misclassification"})

    def test_roi_is_normalized_and_serialized(self) -> None:
        obj = AttackObjective.from_params(
            {
                "objective_mode": "class_conditional_hiding",
                "target_class": 0,
                "attack_roi": "0.1,0.2,0.4,0.5",
            }
        )
        self.assertEqual(obj.to_dict()["attack_roi"], [0.1, 0.2, 0.4, 0.5])


if __name__ == "__main__":
    unittest.main()
