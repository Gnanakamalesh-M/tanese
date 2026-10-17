"""Check spec/vocabulary_rules.yaml for consistency and print the Phase 1C counts.

Usage (from any working directory):
    python scripts/check_vocabulary.py

Every number the README reports for Phase 1C comes from this script's output. The run fails
if any of the thirteen checks reports a problem, or if the rule set falls below the
done-criteria in docs/SPEC.md.

Three reports are printed that never cause a failure, because they are measurements rather
than requirements: the distance from each form this file introduces to the nearest listed
source form, the existing forms the non-retroactive originality gate spares, and the adapted
loans that are legal words but exceed the root mora cap.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Run as a plain script, sys.path[0] is scripts/, not the repo root -- so `import
# tanese_nlp` would fail. Put the repo root first explicitly.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tanese_nlp.vocabulary import consistency as C  # noqa: E402
from tanese_nlp.vocabulary import rules as V  # noqa: E402

# docs/SPEC.md, Phase 1C: the rule format requires 2 valid and 2 invalid examples per rule.
MIN_EXAMPLES_PER_RULE = 2
# Not a SPEC.md number: the five word sources Phase 1C is required to cover.
REQUIRED_STRATA = 5


def main() -> int:
    stats = C.stats()

    print("== counts")
    print(f"  rules                {stats['rules']}")
    print(f"  valid examples       {stats['valid_examples']}")
    print(f"  invalid examples     {stats['invalid_examples']}"
          f" ({stats['illegal_examples']} deliberately not legal Tanese)")
    print(f"  strata               {stats['strata']}")
    print(f"  root shapes          {stats['root_shapes']}")
    print(f"  semantic fields      {stats['semantic_fields']}")
    print(f"  compound patterns    {stats['compound_patterns']}")
    print(f"  loan substitutions   {stats['substitutions']}"
          f" ({stats['unmapped']} sounds deliberately unmapped)")
    print(f"  loan repair steps    {stats['repairs']}")
    print(f"  adaptation examples  {stats['adaptation_examples']} expected outputs,"
          f" {stats['adaptation_rejections']} expected rejections")
    print(f"  pipeline stages      {stats['pipeline_stages']}")
    print(f"  forms introduced     {stats['declared_forms']}"
          f" ({stats['illustrative_forms']} illustrative roots + adapted loans,"
          f" all experimental)")
    print("  rules by category")
    for category, count in stats["by_category"].items():
        print(f"    {category:<12} {count}")

    print("\n== checks")
    failures: list[str] = []
    for name, check in C.CHECKS:
        errors = check()
        print(f"  {'FAIL' if errors else 'ok  '}  check {name}")
        failures.extend(errors)

    print("\n== originality distances (reported, not a gate)")
    print("  every form spec/vocabulary_rules.yaml introduces, nearest listed source form:")
    for form, nearest, distance in C.originality_report():
        print(f"    {form:<12} {distance}  ({nearest})")

    spared = C.retroactive_exceptions()
    floor = V.originality()["new_root_gate"]["min_edit_distance"]
    print(f"\n== forms the non-retroactive gate spares ({len(spared)} below distance {floor})")
    print("  existing Phase 1B morphemes and demo roots; reported so the exemption is visible:")
    for form, nearest, distance in spared:
        print(f"    {form:<12} {distance}  ({nearest})")

    oversized = C.oversized_loans()
    cap = V.mora_counts()["max"]
    print(f"\n== adapted loans over the {cap}-mora root cap ({len(oversized)})")
    print("  legal Tanese words that cannot be roots; predicted by LR-5's `problems` field:")
    for source, form, count in oversized:
        print(f"    {form:<12} {count} moras  (from {source})")

    print("\n== done-criteria (docs/SPEC.md, Phase 1C)")
    spec_doc = REPO_ROOT / "docs" / "language-specification.md"
    criteria = [
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
        (
            f"{REQUIRED_STRATA} strata (native, 2 inspired, compound, loan)",
            stats["strata"] == REQUIRED_STRATA,
            stats["strata"],
        ),
        (
            "docs/language-specification.md exists",
            spec_doc.is_file(),
            "present" if spec_doc.is_file() else "missing",
        ),
    ]
    for label, ok, observed in criteria:
        print(f"  {'PASS' if ok else 'FAIL'}  {label} (observed: {observed})")
        if not ok:
            failures.append(f"done-criteria: {label} is not met (observed: {observed})")

    if failures:
        print(f"\n{len(failures)} problem(s):")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("\nVocabulary checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
