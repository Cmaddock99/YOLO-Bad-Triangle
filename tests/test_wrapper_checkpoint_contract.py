from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import torch

from lab.defenses.dpc_unet_wrapper import DPCUNet, load_checkpoint_state_dict, strict_load_with_report


class WrapperCheckpointContractTests(unittest.TestCase):
    def test_load_checkpoint_state_dict_and_strict_load_pass(self) -> None:
        model = DPCUNet()
        state_dict = model.state_dict()
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint = Path(tmp) / "wrapper.pt"
            torch.save(state_dict, checkpoint)
            loaded = load_checkpoint_state_dict(checkpoint)
            report = strict_load_with_report(DPCUNet(), loaded)
            self.assertTrue(report.strict_passed)
            self.assertEqual(report.missing_keys, [])
            self.assertEqual(report.unexpected_keys, [])
            self.assertIsNone(report.error_message)

    def test_strict_load_report_flags_missing_keys(self) -> None:
        model = DPCUNet()
        state_dict = dict(model.state_dict())
        state_dict.pop("final.bias")
        report = strict_load_with_report(DPCUNet(), state_dict)
        self.assertFalse(report.strict_passed)
        self.assertIn("final.bias", report.missing_keys)
        self.assertIsNotNone(report.error_message)


if __name__ == "__main__":
    unittest.main()
