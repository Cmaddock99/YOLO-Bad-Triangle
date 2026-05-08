#!/usr/bin/env python3
"""Verify shim files in src/lab/{attacks,defenses,models}/ contain only the forward-import
pattern and have not accumulated logic.

These shim files are scheduled for retirement (they redirect to src/lab/plugins/ via
sys.modules replacement). This check prevents logic from drifting back into them while
the migration is in progress.

Phase 2 of this check also verifies that no canonical code (outside tests/) forms a
new import dependency on the shim adapter paths — callers should use the framework
registry API or the canonical plugin paths instead.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Directories containing shim files (backward-compat redirects to src/lab/plugins/)
SHIM_DIRS = [
    REPO_ROOT / "src" / "lab" / "attacks",
    REPO_ROOT / "src" / "lab" / "defenses",
    REPO_ROOT / "src" / "lab" / "models",
]

# Files in shim dirs that are real implementation files, not shims
REAL_FILES = {
    "__init__.py",
    "base_attack.py",
    "base_defense.py",
    "base_model.py",
    "framework_registry.py",
    "objective.py",
    "utils.py",
    "model_utils.py",
    "dpc_unet_wrapper.py",
    "dpc_unet.py",
}

# Patterns that indicate a genuine shim (pure forward-import, no logic)
SHIM_MARKERS = {
    "sys.modules[__name__]",
    "import_module(",
}

# Pattern that indicates logic has drifted into a shim
FORBIDDEN_IN_SHIM = [
    "def ",
    "class ",
    "@dataclass",
    "@register_",
]

# Directories to scan for illegal direct shim imports (canonical code only)
SCAN_DIRS_FOR_IMPORTS = [
    REPO_ROOT / "scripts",
    REPO_ROOT / "src" / "lab" / "plugins",
    REPO_ROOT / "src" / "lab" / "runners",
    REPO_ROOT / "src" / "lab" / "eval",
    REPO_ROOT / "src" / "lab" / "reporting",
    REPO_ROOT / "src" / "lab" / "config",
]

# Shim module names that canonical code should not import from directly
# (they should use framework_registry or lab.plugins.* instead)
SHIM_ADAPTER_PATTERNS = [
    "lab.attacks.fgsm_adapter",
    "lab.attacks.pgd_adapter",
    "lab.attacks.deepfool_adapter",
    "lab.attacks.square_adapter",
    "lab.defenses.preprocess_median_blur_adapter",
    "lab.defenses.preprocess_bitdepth_adapter",
    "lab.defenses.preprocess_jpeg_adapter",
    "lab.models.yolo_adapter",
]


def check_shim_integrity() -> list[str]:
    failures: list[str] = []

    for shim_dir in SHIM_DIRS:
        if not shim_dir.exists():
            continue

        for path in shim_dir.glob("*_adapter.py"):
            if path.name in REAL_FILES:
                continue

            text = path.read_text(encoding="utf-8")

            # Must contain the shim markers to be recognised as a shim
            is_shim = any(marker in text for marker in SHIM_MARKERS)
            if not is_shim:
                # Not a shim — may be a real implementation, skip
                continue

            # Check for logic drift
            lines = text.splitlines()
            for lineno, line in enumerate(lines, start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                for forbidden in FORBIDDEN_IN_SHIM:
                    if forbidden in stripped:
                        rel = path.relative_to(REPO_ROOT)
                        failures.append(
                            f"{rel}:{lineno}: shim contains forbidden pattern {forbidden!r} "
                            f"— logic has drifted back into the shim file"
                        )

    return failures


def check_import_discipline() -> list[str]:
    failures: list[str] = []

    for scan_dir in SCAN_DIRS_FOR_IMPORTS:
        if not scan_dir.exists():
            continue

        for path in scan_dir.rglob("*.py"):
            # Skip this script itself
            if path.resolve() == Path(__file__).resolve():
                continue

            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            for lineno, line in enumerate(lines, start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                # Only flag actual import statements, not string literals or comments
                is_import = stripped.startswith("import ") or stripped.startswith("from ")
                if not is_import:
                    continue
                for pattern in SHIM_ADAPTER_PATTERNS:
                    if pattern in stripped:
                        rel = path.relative_to(REPO_ROOT)
                        failures.append(
                            f"{rel}:{lineno}: imports from shim path {pattern!r} — "
                            f"use lab.*.framework_registry or lab.plugins.* instead"
                        )

    return failures


def main() -> int:
    shim_failures = check_shim_integrity()
    import_failures = check_import_discipline()

    all_failures = shim_failures + import_failures
    if all_failures:
        print("Shim integrity / import discipline failures:\n")
        for failure in all_failures:
            print(f"  {failure}")
        print(
            f"\n{len(all_failures)} failure(s). "
            "Use lab.*.framework_registry or lab.plugins.* imports instead of shim paths."
        )
        return 1

    n_shim_dirs = sum(1 for d in SHIM_DIRS if d.exists())
    print(f"Shim integrity OK ({n_shim_dirs} shim dirs checked).")
    print("Import discipline OK (no canonical code depends on shim adapter paths).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
