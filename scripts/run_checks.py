"""Run every Phase 0 check with plain python (no make).

Usage (from any working directory):
    python scripts/run_checks.py

Steps: lint (ruff), unit tests (pytest), YAML schema check. The first failure stops
the run. CI runs this exact command, so local green and CI green mean the same thing.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Run as a plain script, sys.path[0] is scripts/, not the repo root. Both the import
# below and the child processes need the repo root, so make it explicit.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Use sys.executable -m so we get this interpreter's tools, not whatever is on PATH.
STEPS: list[tuple[str, list[str]]] = [
    ("lint", [sys.executable, "-m", "ruff", "check", "."]),
    ("tests", [sys.executable, "-m", "pytest"]),
    ("yaml-schema", [sys.executable, str(REPO_ROOT / "scripts" / "check_yaml_schema.py")]),
    ("grammar", [sys.executable, str(REPO_ROOT / "scripts" / "check_grammar.py")]),
]


def main() -> int:
    results: list[tuple[str, bool]] = []
    failed = False

    for name, cmd in STEPS:
        print(f"\n== {name}: {' '.join(cmd)}")
        ok = subprocess.call(cmd, cwd=REPO_ROOT) == 0
        results.append((name, ok))
        if not ok:
            failed = True
            break

    print("\n== summary")
    for name, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    for name, _ in STEPS[len(results) :]:
        print(f"  SKIP  {name}")

    if failed:
        print("\nChecks failed.")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
