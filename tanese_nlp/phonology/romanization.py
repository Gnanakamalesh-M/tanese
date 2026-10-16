"""Romanized Tanese <-> mora sequence.

The romanization is the canonical form of Tanese (locked decision 12), so this module is the
entry point for every other component: the phonotactic validator, the script converter and
(from Phase 2) the vocabulary pipeline all work on the mora list this lexer produces.

Parsing is deterministic longest-match, in the order spec/romanization.yaml documents under
`parse_order`. Spelling errors are reported as violations rather than raised, so one pass can
report everything wrong with a word; see phonotactics.validate for the full check.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from tanese_nlp.phonology import spec_load as S

SYLLABIC = "syllabic"
LENGTH = "length"
NASAL = "nasal"
GEM = "gem"


@dataclass(frozen=True)
class Violation:
    """One broken constraint, identified by its id in spec/phonology.yaml."""

    code: str
    message: str
    position: int

    def __str__(self) -> str:
        return f"{self.code} at {self.position}: {self.message}"


@dataclass(frozen=True)
class Mora:
    """One mora. `kind` is one of the four kinds in spec/phonology.yaml's mora_kinds."""

    kind: str
    onset: str | None = None
    vowel: str | None = None
    # True when a nasal mora was written with the apostrophe separator (kan'a).
    explicit_break: bool = False
    # Index in the romanized string where this mora starts; for error messages.
    position: int = 0

    @property
    def glyph(self) -> str:
        if self.kind == SYLLABIC:
            assert self.vowel is not None
            return S.glyph_id(self.onset, self.vowel)
        if self.kind == LENGTH:
            return S.LENGTH_GLYPH
        if self.kind == NASAL:
            return S.NASAL_GLYPH
        if self.kind == GEM:
            return S.GEM_GLYPH
        raise ValueError(f"unknown mora kind {self.kind!r}")


def _syllable_vowel(moras: list[Mora]) -> str | None:
    """The vowel of the syllable currently being built, if any."""
    for mora in reversed(moras):
        if mora.kind == SYLLABIC:
            return mora.vowel
        if mora.kind != LENGTH:
            return None
    return None


def parse_roman(word: str) -> tuple[list[Mora], list[Violation]]:
    """Split a romanized word into moras.

    Returns whatever moras could be read plus any spelling violations. A word with
    violations may still produce moras, so callers must check the violations, not the moras.
    """
    violations: list[Violation] = []
    if not word:
        return [], [Violation("PT-002", "empty word", 0)]

    allowed = S.letters() | {S.separator()}
    unknown = [(i, ch) for i, ch in enumerate(word) if ch not in allowed]
    if unknown:
        return [], [
            Violation("PT-001", f"{ch!r} is not a Tanese romanization character", i)
            for i, ch in unknown
        ]

    vowels = S.vowels()
    graphemes = S.consonant_graphemes_longest_first()
    glides = {"y", "w"}
    moras: list[Mora] = []
    i = 0
    length = len(word)

    while i < length:
        char = word[i]

        if char == S.separator():
            follows_nasal = bool(moras) and moras[-1].kind == NASAL and not moras[-1].explicit_break
            before_break = i + 1 < length and (word[i + 1] in vowels or word[i + 1] in glides)
            if follows_nasal and before_break:
                moras[-1] = replace(moras[-1], explicit_break=True)
            else:
                violations.append(
                    Violation(
                        "PT-011",
                        "an apostrophe is legal only after a moraic n and before a vowel, y or w",
                        i,
                    )
                )
            i += 1
            continue

        if char in vowels:
            # A repeat of the syllable's own vowel is always length, never a second mora.
            if _syllable_vowel(moras) == char and moras[-1].kind in (SYLLABIC, LENGTH):
                moras.append(Mora(LENGTH, position=i))
            else:
                moras.append(Mora(SYLLABIC, None, char, position=i))
            i += 1
            continue

        grapheme = next((g for g in graphemes if word.startswith(g, i)), None)
        if grapheme is None:
            # Reachable only for `h`, which is a diacritic letter and never begins a mora.
            violations.append(
                Violation("PT-003", f"{char!r} does not begin a mora", i)
            )
            i += 1
            continue

        after = i + len(grapheme)
        if after < length and word[after] in vowels:
            moras.append(Mora(SYLLABIC, grapheme, word[after], position=i))
            i = after + 1
            continue

        # A consonant with no vowel after it: moraic n, a geminate's first half, or an error.
        if grapheme == "n":
            moras.append(Mora(NASAL, position=i))
            i = after
            continue

        doubled = word.startswith(grapheme, after)
        vowel_after_double = after + len(grapheme)
        if doubled and vowel_after_double < length and word[vowel_after_double] in vowels:
            moras.append(Mora(GEM, onset=grapheme, position=i))
            i = after
            continue

        if after >= length:
            violations.append(
                Violation(
                    "PT-004",
                    f"word ends in {grapheme!r}; only a vowel or the moraic n may be final",
                    i,
                )
            )
        else:
            violations.append(
                Violation(
                    "PT-003",
                    f"{grapheme!r} is not followed by a vowel, so it forms a cluster",
                    i,
                )
            )
        i = after

    return moras, violations


def moras_to_roman(moras: list[Mora]) -> str:
    """Spell a mora sequence. Inverse of parse_roman for every legal word."""
    out: list[str] = []
    for index, mora in enumerate(moras):
        following = moras[index + 1] if index + 1 < len(moras) else None
        if mora.kind == SYLLABIC:
            out.append(f"{mora.onset or ''}{mora.vowel}")
        elif mora.kind == LENGTH:
            vowel = _syllable_vowel(moras[:index])
            if vowel is None:
                raise ValueError(f"length mora at {index} has no vowel to lengthen")
            out.append(vowel)
        elif mora.kind == NASAL:
            needs_break = (
                following is not None
                and following.kind == SYLLABIC
                and (following.onset is None or following.onset in {"y", "w"})
            )
            out.append("n" + (S.separator() if needs_break else ""))
        elif mora.kind == GEM:
            if following is None or following.kind != SYLLABIC or following.onset is None:
                raise ValueError(f"gemination mora at {index} has no onset to double")
            out.append(following.onset)
        else:
            raise ValueError(f"unknown mora kind {mora.kind!r}")
    return "".join(out)
