"""Adapt a source word into a legal Tanese form, or reject it by name.

Deterministic and table-driven: every substitution, every repair and every rejection comes
from the `loan_substitutions`, `unmapped` and `loan_repairs` blocks of
spec/vocabulary_rules.yaml. There is no sound-specific knowledge in this module -- the
repair *order* (LR-1 to LR-7) is encoded here because order is logic rather than data, and
check 6 asserts the order it implements is the order the spec declares.

Input is a list of source segments, using the `source` keys of the substitution table. It is
deliberately not a spelling: a source orthography does not say how many segments a word has
or whether a doubled letter is one sound, and those are exactly the questions steps 3 and 4
need answered. The caller supplies sounds; this module supplies Tanese.

Internally the word is a list of Tanese *graphemes*, not characters, because `th`, `dh` and
`nh` are single consonants -- splitting them would silently turn one retroflex into a `t`
plus a non-existent `h`. The moraic nasal is carried as its own token (`MORAIC_N`) rather
than as the letter `n`, so that an onset `n` and a coda `n` can never be confused by the
later steps; it becomes `n` only when the word is spelled.

Three ways to fail, all explicit (no input is ever approximated):

    VL-UNMAPPED   a sound the spec deliberately leaves undecided
    VL-UNKNOWN    a sound in neither table
    VL-RESIDUE    the repairs ran and the result is still illegal -- a gap in the table,
                  surfaced loudly instead of being returned

This module reads spec/ only. It never touches data/evaluation/.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tanese_nlp.phonology import spec_load as S
from tanese_nlp.phonology import validate
from tanese_nlp.vocabulary import rules as V

# LR-5 and LR-4's choices. The vowel inventory and the gaps they consult come from
# spec/phonology.yaml; these three constants are the choices spec/vocabulary_rules.yaml
# declares in the `loan_repairs` block.
DEFAULT_EPENTHETIC = "u"
RETROFLEX_EPENTHETIC = "a"
GAP_FALLBACK_VOWEL = "i"
BACK_VOWELS = ("u", "o")

# The moraic nasal, while the word is still a grapheme list. Not a letter: it is the only
# legal coda and must not be mistaken for an onset `n` by LR-3, LR-4 or LR-5.
MORAIC_N = "N"


@dataclass(frozen=True)
class Adapted:
    """A successful adaptation."""

    source_word: str
    form: str
    steps_fired: tuple[str, ...] = ()

    ok = True

    def __str__(self) -> str:
        return f"{self.source_word} -> {self.form} ({', '.join(self.steps_fired)})"


@dataclass(frozen=True)
class Rejected:
    """A refusal, naming the sound or constraint responsible."""

    source_word: str
    code: str
    offending: str
    detail: str = ""
    steps_fired: tuple[str, ...] = field(default_factory=tuple)

    ok = False
    form = None

    def __str__(self) -> str:
        suffix = f": {self.detail}" if self.detail else ""
        return f"{self.source_word} -> rejected {self.code} on {self.offending!r}{suffix}"


Result = Adapted | Rejected


def _is_vowel(grapheme: str) -> bool:
    return grapheme in S.vowels()


def _place(grapheme: str) -> str | None:
    entry = S.consonants().get(grapheme)
    return entry["place"] if entry else None


def _is_nasal(grapheme: str) -> bool:
    entry = S.consonants().get(grapheme)
    return bool(entry) and entry["manner"] == "nasal"


def _is_gap(onset: str, vowel: str) -> bool:
    return (onset, vowel) in S.gaps()


def split_graphemes(text: str) -> list[str]:
    """Split a romanized string into Tanese graphemes, longest consonant first.

    The same longest-match discipline as the romanization lexer, and for the same reason:
    `th` is one consonant, so a substitution table entry of `th` is one grapheme and not
    two. Raises on a character that is no grapheme at all, which can only be a typo in
    spec/vocabulary_rules.yaml.
    """
    out: list[str] = []
    index = 0
    while index < len(text):
        for grapheme in S.consonant_graphemes_longest_first():
            if text.startswith(grapheme, index):
                out.append(grapheme)
                index += len(grapheme)
                break
        else:
            char = text[index]
            if not _is_vowel(char):
                raise ValueError(f"{char!r} in {text!r} is not a Tanese grapheme")
            out.append(char)
            index += 1
    return out


def _substitute(segments: list[str], source_word: str) -> list[str] | Rejected:
    """LR-1. Source sounds to Tanese graphemes, or a rejection naming the sound."""
    table = V.substitutions()
    undecided = V.unmapped()
    out: list[str] = []
    for segment in segments:
        if segment in undecided:
            return Rejected(
                source_word,
                undecided[segment],
                segment,
                "the spec leaves this sound deliberately unmapped",
            )
        if segment not in table:
            return Rejected(
                source_word,
                V.UNKNOWN,
                segment,
                "not in loan_substitutions and not in unmapped",
            )
        # An empty mapping is deletion, which in v0.1 is source /h/ and nothing else.
        out.extend(split_graphemes(table[segment]))
    return out


def _nasal_to_moraic(graphemes: list[str]) -> tuple[list[str], bool]:
    """LR-2. A word-final nasal, or one before a consonant, becomes the moraic nasal.

    Never word-initially: constraint PT-005 forbids an initial moraic nasal, which has
    nothing to attach to, so an initial nasal keeps its consonant status and is left to
    epenthesis instead.

    Returns the new sequence and whether the step did anything. `n` before a consonant is
    already spelled `n`, so the caller cannot tell from the string alone -- which is why
    the moraic nasal is a separate token and why this returns a flag.
    """
    out = list(graphemes)
    fired = False
    for index, grapheme in enumerate(out):
        if index == 0 or not _is_nasal(grapheme):
            continue
        following = out[index + 1] if index + 1 < len(out) else None
        if following is None or not _is_vowel(following):
            out[index] = MORAIC_N
            fired = True
    return out, fired


def _licensed_geminates(graphemes: list[str]) -> set[int]:
    """LR-3. Indices of consonants that are the first half of a legal geminate.

    The step rewrites nothing: a geminate is already spelled by repeating the onset, so its
    whole effect is to license the pair against epenthesis in LR-5. A pair of a
    non-geminable consonant is not licensed and falls through -- a nasal pair to LR-2, any
    other to LR-5 (constraint PT-007).
    """
    licensed: set[int] = set()
    geminable = S.geminable()
    for index, grapheme in enumerate(graphemes[:-1]):
        following = graphemes[index + 1]
        after = graphemes[index + 2] if index + 2 < len(graphemes) else None
        if (
            grapheme == following
            and grapheme in geminable
            and after is not None
            and _is_vowel(after)
        ):
            licensed.add(index)
    return licensed


def _glide_for(preceding: str, following: str) -> str:
    """LR-4's glide: chosen by the preceding vowel, with the gap fallback."""
    glide = "w" if preceding in BACK_VOWELS else "y"
    if _is_gap(glide, following):
        glide = "y" if glide == "w" else "w"
    return glide


def _break_hiatus(graphemes: list[str]) -> tuple[list[str], bool]:
    """LR-4. Identical vowels collapse to a long vowel; different ones take a glide."""
    out: list[str] = []
    fired = False
    for grapheme in graphemes:
        if not out or not _is_vowel(grapheme) or not _is_vowel(out[-1]):
            out.append(grapheme)
            continue
        previous = out[-1]
        if previous == grapheme:
            # A long vowel is two identical vowels and no more: constraint PT-009 permits
            # exactly one length mora, so a third copy is dropped.
            if len(out) >= 2 and out[-2] == grapheme:
                fired = True
                continue
            out.append(grapheme)
            continue
        out.append(_glide_for(previous, grapheme))
        out.append(grapheme)
        fired = True
    return out, fired


def _epenthesise(graphemes: list[str]) -> tuple[list[str], bool]:
    """LR-5. Insert a vowel after any consonant that is not followed by one."""
    licensed = _licensed_geminates(graphemes)
    out: list[str] = []
    fired = False
    for index, grapheme in enumerate(graphemes):
        out.append(grapheme)
        if _is_vowel(grapheme) or grapheme == MORAIC_N or index in licensed:
            # The moraic nasal from LR-2 and the first half of a geminate from LR-3 are
            # already licensed codas and need no vowel.
            continue
        following = graphemes[index + 1] if index + 1 < len(graphemes) else None
        if following is not None and _is_vowel(following):
            continue
        vowel = RETROFLEX_EPENTHETIC if _place(grapheme) == "retroflex" else DEFAULT_EPENTHETIC
        if _is_gap(grapheme, vowel):
            vowel = GAP_FALLBACK_VOWEL
        out.append(vowel)
        fired = True
    return out, fired


def _spell(graphemes: list[str]) -> str:
    """LR-6. Write the result, inserting the apostrophe constraint PT-010 requires."""
    out: list[str] = []
    for index, grapheme in enumerate(graphemes):
        if grapheme != MORAIC_N:
            out.append(grapheme)
            continue
        out.append("n")
        following = graphemes[index + 1] if index + 1 < len(graphemes) else None
        if following is not None and (_is_vowel(following) or following in ("y", "w")):
            out.append("'")
    return "".join(out)


def adapt(segments: list[str], source_word: str = "") -> Result:
    """Adapt a list of source segments into a Tanese form, or reject it by name.

    Applies LR-1 to LR-7 in the order spec/vocabulary_rules.yaml declares. The result is
    either an `Adapted` carrying a validated legal Tanese word, or a `Rejected` naming the
    sound or constraint responsible -- never an unvalidated form.
    """
    label = source_word or "".join(segments)
    fired: set[str] = set()

    substituted = _substitute(list(segments), label)
    if isinstance(substituted, Rejected):
        return substituted
    fired.add("LR-1-SUBSTITUTE")

    nasalised, nasal_fired = _nasal_to_moraic(substituted)
    if nasal_fired:
        fired.add("LR-2-NASAL")

    if _licensed_geminates(nasalised):
        fired.add("LR-3-GEMINATE")

    broken, hiatus_fired = _break_hiatus(nasalised)
    if hiatus_fired:
        fired.add("LR-4-HIATUS")

    epenthesised, epenthesis_fired = _epenthesise(broken)
    if epenthesis_fired:
        fired.add("LR-5-EPENTHESIS")

    form = _spell(epenthesised)
    steps = tuple(entry["id"] for entry in V.repairs() if entry["id"] in fired)

    result = validate(form)
    if not result.ok:
        # LR-7. The repairs above are believed total, but "believed" is not a guarantee, and
        # a silently illegal loanword would poison the Phase 2 lexicon at its source.
        return Rejected(label, V.RESIDUE, form, "; ".join(result.codes), steps_fired=steps)

    return Adapted(label, form, steps)
