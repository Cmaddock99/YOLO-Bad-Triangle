from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from scripts import cleanup_stale_runs


def _make_run_dir(root: Path, name: str, sha: str | None = "abc123", age_hours: float = 48.0) -> Path:
    """Create a complete run directory with all three required artifacts."""
    run_dir = root / name
    run_dir.mkdir(parents=True)
    for artifact in ("metrics.json", "predictions.jsonl"):
        (run_dir / artifact).write_text("{}", encoding="utf-8")
    summary = {"provenance": {"checkpoint_fingerprint_sha256": sha}} if sha else {}
    (run_dir / "run_summary.json").write_text(json.dumps(summary), encoding="utf-8")
    # Back-date the directory and run_summary.json
    ts = (datetime.now(tz=timezone.utc) - timedelta(hours=age_hours)).timestamp()
    os.utime(run_dir / "run_summary.json", (ts, ts))
    os.utime(run_dir, (ts, ts))
    return run_dir


def _make_manifest(manifest_root: Path, cycle_id: str, promoted_sha: str, age_hours: float = 1.0) -> Path:
    """Create a training_manifest.json at the canonical location."""
    manifest_dir = manifest_root / cycle_id
    manifest_dir.mkdir(parents=True)
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=age_hours)
    payload = {
        "cycle_id": cycle_id,
        "generated_at": cutoff.isoformat(),
        "candidate_checkpoint": {"sha256": promoted_sha},
        "final_verdict": "passed_both_manual_promotion_required",
    }
    path = manifest_dir / "training_manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class StaleRunCleanupTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.runs_root = self.tmp / "framework_runs"
        self.runs_root.mkdir()
        self.training_runs = self.tmp / "training_runs"
        self.training_runs.mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _patch_roots(self) -> tuple[mock._patch, mock._patch]:
        p1 = mock.patch.object(cleanup_stale_runs, "FRAMEWORK_RUNS", self.runs_root)
        p2 = mock.patch.object(cleanup_stale_runs, "TRAINING_RUNS", self.training_runs)
        return p1, p2

    def test_dry_run_does_not_delete(self) -> None:
        """--dry-run prints but does not remove directories."""
        _make_run_dir(self.runs_root, "run_old", sha="old_sha", age_hours=72)
        _make_manifest(self.training_runs, "cycle_001", promoted_sha="new_sha", age_hours=24)

        p1, p2 = self._patch_roots()
        with p1, p2:
            rc = cleanup_stale_runs.main(["--dry-run"])

        self.assertEqual(rc, 0)
        # Directory still exists
        self.assertTrue((self.runs_root / "run_old").is_dir())

    def test_identifies_stale_dirs_by_checkpoint_sha(self) -> None:
        """Dirs with old checkpoint SHA and predating cutoff are identified as stale."""
        _make_run_dir(self.runs_root, "run_old_sha", sha="old_sha", age_hours=48)
        _make_manifest(self.training_runs, "cycle_001", promoted_sha="new_sha", age_hours=24)

        p1, p2 = self._patch_roots()
        with p1, p2:
            # Use find_stale_dirs directly to inspect results
            manifest = cleanup_stale_runs._load_latest_manifest()
            cutoff = cleanup_stale_runs._parse_iso(manifest["generated_at"])
            promoted_sha = manifest["candidate_checkpoint"]["sha256"]
            stale = cleanup_stale_runs.find_stale_dirs(cutoff, promoted_sha)

        self.assertEqual(len(stale), 1)
        self.assertEqual(stale[0].name, "run_old_sha")

    def test_keeps_dirs_matching_promoted_checkpoint(self) -> None:
        """Dirs whose checkpoint SHA matches the promoted checkpoint are kept."""
        _make_run_dir(self.runs_root, "run_same_sha", sha="promoted_sha", age_hours=48)
        _make_manifest(self.training_runs, "cycle_001", promoted_sha="promoted_sha", age_hours=24)

        p1, p2 = self._patch_roots()
        with p1, p2:
            manifest = cleanup_stale_runs._load_latest_manifest()
            cutoff = cleanup_stale_runs._parse_iso(manifest["generated_at"])
            promoted_sha = manifest["candidate_checkpoint"]["sha256"]
            stale = cleanup_stale_runs.find_stale_dirs(cutoff, promoted_sha)

        self.assertEqual(stale, [])

    def test_skips_incomplete_dirs_missing_all_three_artifacts(self) -> None:
        """Directories with none of the three artifacts are treated as in-progress and skipped."""
        incomplete = self.runs_root / "run_incomplete"
        incomplete.mkdir()
        # Back-date the dir so it would otherwise be stale
        old_ts = (datetime.now(tz=timezone.utc) - timedelta(hours=72)).timestamp()
        os.utime(incomplete, (old_ts, old_ts))

        _make_manifest(self.training_runs, "cycle_001", promoted_sha="new_sha", age_hours=24)

        p1, p2 = self._patch_roots()
        with p1, p2:
            manifest = cleanup_stale_runs._load_latest_manifest()
            cutoff = cleanup_stale_runs._parse_iso(manifest["generated_at"])
            stale = cleanup_stale_runs.find_stale_dirs(cutoff, "new_sha")

        self.assertNotIn(incomplete, stale)

    def test_requires_before_mtime_when_no_manifest(self) -> None:
        """main() returns exit code 2 when no manifest exists and --before-mtime is absent."""
        p1, p2 = self._patch_roots()
        with p1, p2:
            rc = cleanup_stale_runs.main([])  # no manifest, no --before-mtime

        self.assertEqual(rc, 2)

    def test_before_mtime_arg_used_as_cutoff(self) -> None:
        """--before-mtime overrides manifest-derived cutoff."""
        _make_run_dir(self.runs_root, "run_old", sha="old_sha", age_hours=100)
        # future cutoff — everything older than now is stale
        cutoff_str = datetime.now(tz=timezone.utc).isoformat()

        p1, p2 = self._patch_roots()
        with p1, p2:
            rc = cleanup_stale_runs.main(["--dry-run", "--before-mtime", cutoff_str])

        self.assertEqual(rc, 0)
        # dry-run: dir still exists
        self.assertTrue((self.runs_root / "run_old").is_dir())

    def test_deletes_stale_dirs_in_live_mode(self) -> None:
        """Without --dry-run, stale directories are actually removed."""
        _make_run_dir(self.runs_root, "run_stale", sha="old_sha", age_hours=48)
        _make_manifest(self.training_runs, "cycle_001", promoted_sha="new_sha", age_hours=24)

        p1, p2 = self._patch_roots()
        with p1, p2:
            rc = cleanup_stale_runs.main([])

        self.assertEqual(rc, 0)
        self.assertFalse((self.runs_root / "run_stale").exists())


if __name__ == "__main__":
    unittest.main()
