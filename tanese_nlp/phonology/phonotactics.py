"""Is this string a legal Tanese word?

Every rejection carries the id of the constraint it broke, taken from the `constraints` block
of spec/phonology.yaml. A boolean would be enough for Phase 1A's done-criteria, but Phase 2's
vocabulary pipeline has to tell a human *why* a candidate was dropped and Phase 4's grammar
checker has to report it, so the reason is part of the result from the start.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tanese_nlp.phonology import spec_load as S
from tanese_nlp.phonology.romanization import (
    GEM,
    LENGTH,
    NASAL,
    SYLLABIC,
    Mora,
    Violation,
    parse_roman,
)


@dataclass(frozen=True)
class Result:
    """The outcome of validating one word."""

    word: str
    ok: bool
    moras: list[Mora] = field(default_factory=list)
    violations: list[Violation] = field(default_factory=list)

    @property
    def codes(self) -> list[str]:
        return [violation.code for violation in self.violations]

    @property
    def mora_count(self) -> int:
        return len(self.moras)

    def __str__(self) -> str:
        if self.ok:
            return f"{self.word}: legal ({self.mora_count} moras)"
        return f"{self.word}: illegal -- " + "; ".join(str(v) for v in self.violations)


def validate(word: str) -> Result:
    """Validate a romanized Tanese word against spec/phonology.yaml."""
    moras, spelling_violations = parse_roman(word)
    violations = [*spelling_violations, *check_moras(moras)]
    return Result(word=word, ok=not violations, moras=moras, violations=violations)


def validate_moras(moras: list[Mora]) -> Result:
    """Validate a mora sequence that did not come from a romanized string.

    The lexer cannot produce every ill-formed sequence the constraints describe -- a
    word-final gemination mora, for one, is unspellable -- but the script side can
    (Phase 6 feeds glyph sequences straight in), so the mora-level check is the real one and
    validate() is a thin wrapper over it.
    """
    violations = check_moras(moras)
    return Result(
        word=_spell_safely(moras),
        ok=not violations,
        moras=moras,
        violations=violations,
    )


def _spell_safely(moras: list[Mora]) -> str:
    from tanese_nlp.phonology.romanization import moras_to_roman

    try:
        return moras_to_roman(moras)
    except ValueError:
        return "<unspellable>"


def check_moras(moras: list[Mora]) -> list[Violation]:
    """Every phonotactic constraint that is a property of the mora sequence itself."""
    violations: list[Violation] = []
    geminable = S.geminable()
    gaps = S.gaps()

    for index, mora in enumerate(moras):
        previous = moras[index - 1] if index else None
        following = moras[index + 1] if index + 1 < len(moras) else None

        if index == 0 and mora.kind in (NASAL, GEM):
            violations.append(
                Violation(
                    "PT-005",
                    f"a word may not begin with a {mora.kind} mora",
                    mora.position,
                )
            )

        if mora.kind == SYLLABIC:
            if (mora.onset, mora.vowel) in gaps:
                violations.append(
                    Violation(
                        "PT-012",
                        f"{(mora.onset or '') + (mora.vowel or '')!r} is not a legal mora",
                        mora.position,
                    )
                )
            if mora.onset is None and index > 0 and (previous is None or previous.kind != NASAL):
                violations.append(
                    Violation(
                        "PT-008",
                        f"vowel {mora.vowel!r} has no onset and is not word-initial",
                        mora.position,
                    )
                )

        elif mora.kind == LENGTH:
            if previous is not None and previous.kind == LENGTH:
                violations.append(
                    Violation(
                        "PT-009",
                        "a vowel may be lengthened only once",
                        mora.position,
                    )
                )

        elif mora.kind == NASAL:
            if previous is not None and previous.kind == NASAL:
                violations.append(
                    Violation(
                        "PT-003",
                        "two moraic n in a row form a cluster",
                        mora.position,
                    )
                )
            needs_break = (
                following is not None
                and following.kind == SYLLABIC
                and (following.onset is None or following.onset in {"y", "w"})
            )
            if needs_break and not mora.explicit_break:
                violations.append(
                    Violation(
                        "PT-010",
                        "a moraic n before a vowel, y or w must be written with an apostrophe",
                        mora.position,
                    )
                )

        elif mora.kind == GEM:
            if following is None:
                violations.append(
                    Violation("PT-006", "a word may not end in a gemination mora", mora.position)
                )
            elif following.kind != SYLLABIC or following.onset != mora.onset:
                violations.append(
                    Violation(
                        "PT-006",
                        f"the gemination mora doubles {mora.onset!r} but the next mora does not "
                        f"start with it",
                        mora.position,
                    )
                )
            if mora.onset is not None and mora.onset not in geminable:
                violations.append(
                    Violation(
                        "PT-007",
                        f"{mora.onset!r} may not be geminated",
                        mora.position,
                    )
                )

    return violations


def is_legal(word: str) -> bool:
    """Boolean shorthand. Use validate() when the reason matters."""
    return validate(word).ok
