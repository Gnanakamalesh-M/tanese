"""Check spec/grammar_rules/ for contradictions and print the Phase 1B counts.

Usage (from any working directory):
    python scripts/check_grammar.py

Every number the README reports for Phase 1B comes from this script's output. The run fails
if any of the twelve checks reports a problem, if a rule category that must declare
morphemes does not, or if the rule set falls below the done-criteria in docs/SPEC.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Run as a plain script, sys.path[0] is scripts/, not the repo root -- so `import
# tanese_nlp` would fail. Put the repo root first explicitly.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tanese_nlp.grammar import contradictions as C  # noqa: E402

# docs/SPEC.md, Phase 1B done-criteria.
MIN_RULES = 40
MIN_EXAMPLES_PER_RULE = 2


def main() -> int:
    stats = C.stats()

    print("== counts")
    print(f"  rules                {stats['rules']} in {stats['files']} files")
    print(f"  valid examples       {stats['valid_examples']}")
    print(f"  invalid examples     {stats['invalid_examples']}")
    print(f"  declared morphemes   {stats['morphemes']}"
          f" ({stats['particles']} particles, {stats['suffixes']} suffixes)")
    print(f"  demo words           {stats['demo_words']} (experimental, not vocabulary)")
    print(f"  banned source forms  {stats['banned_forms']}")
    print("  rules by category")
    for category, count in stats["by_category"].items():
        print(f"    {category:<12} {count}")
    print("  rules by file")
    for name, count in stats["by_file"].items():
        print(f"    {name:<22} {count}")

    print("\n== checks")
    failures: list[str] = []
    for name, check in C.CHECKS:
        errors = check()
        print(f"  {'FAIL' if errors else 'ok  '}  check {name}")
        failures.extend(errors)

    undeclared = C.missing_morpheme_declarations()
    print(f"  {'FAIL' if undeclared else 'ok  '}  morpheme declarations by category")
    failures.extend(undeclared)

    misfiled = C.misfiled_morpheme_declarations()
    print(f"  {'FAIL' if misfiled else 'ok  '}  morpheme-declaring rules are categorised as such")
    failures.extend(misfiled)

    print("\n== done-criteria (docs/SPEC.md, Phase 1B)")
    criteria = [
        (f">= {MIN_RULES} rules", stats["rules"] >= MIN_RULES, stats["rules"]),
        (
            f">= {MIN_EXAMPLES_PER_RULE} valid examples per rule",
            stats["min_valid_per_rule"] >= MIN_EXAMPLES_PER_RULE,
            stats["min_valid_per_rule"],
        ),
        (
            f">= {MIN_EXAMPLES_PER_RULE} invalid examples per rule",
            stats["min_invalid_per_rule"] >= MIN_EXAMPLES_PER_RULE,
            stats["min_invalid_per_rule"],
        ),
    ]
    for label, ok, observed in criteria:
        print(f"  {'PASS' if ok else 'FAIL'}  {label} (lowest observed: {observed})")
        if not ok:
            failures.append(f"done-criteria: {label} is not met (lowest observed: {observed})")

    if failures:
        print(f"\n{len(failures)} problem(s):")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("\nGrammar checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
