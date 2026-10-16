"""Validate spec/*.yaml against the JSON Schemas in spec/schemas/.

Usage (from any working directory):
    python scripts/check_yaml_schema.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Run as a plain script, sys.path[0] is scripts/, not the repo root -- so `import
# tanese_nlp` would fail. Put the repo root first explicitly.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tanese_nlp.speccheck import check_spec_tree  # noqa: E402


def main() -> int:
    errors = check_spec_tree()
    if errors:
        print(f"YAML schema check: {len(errors)} problem(s)")
        for error in errors:
            print(f"  {error}")
        return 1
    print("YAML schema check: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
