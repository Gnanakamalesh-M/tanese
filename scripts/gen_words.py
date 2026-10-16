"""Generate legal Tanese words deterministically.

Usage (from any working directory):
    python scripts/gen_words.py [count]

These are phonotactically legal *forms*, not vocabulary: nothing here has a meaning, and
nothing here is official (locked decision 14 -- words become official only through the
Phase 2 pipeline with human approval). The purpose is to give the round-trip test a corpus
that actually covers the glyph table.

Sampling alone does not cover it: long vowels, geminates and the apostrophe cases are rare
by chance, and the rarer moras would never appear. So the generator builds to explicit
quotas, checks them, and raises if any is unmet -- a silently under-covering corpus would
make the round-trip test look stronger than it is. Quotas are expressed against the sets
loaded from spec/, never against literal letter lists.
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tanese_nlp.phonology import spec_load as S  # noqa: E402
from tanese_nlp.phonology.phonotactics import validate  # noqa: E402
from tanese_nlp.phonology.romanization import (  # noqa: E402
    GEM,
    LENGTH,
    NASAL,
    SYLLABIC,
    Mora,
    moras_to_roman,
)

SEED = 1704
DEFAULT_COUNT = 200

# Shapes to build from, as mora-kind templates. Each is a syllable skeleton; the generator
# picks the segments. Weights keep ordinary words common while still forcing the rare
# structures to appear often enough to matter.
SHAPES: list[tuple[str, ...]] = [
    (SYLLABIC, SYLLABIC),
    (SYLLABIC, SYLLABIC, SYLLABIC),
    (SYLLABIC, LENGTH, SYLLABIC),
    (SYLLABIC, SYLLABIC, LENGTH),
    (SYLLABIC, NASAL, SYLLABIC),
    (SYLLABIC, GEM, SYLLABIC),
    (SYLLABIC, LENGTH, GEM, SYLLABIC),
    (SYLLABIC, NASAL, SYLLABIC, SYLLABIC),
    (SYLLABIC, SYLLABIC, NASAL),
    (SYLLABIC, GEM, SYLLABIC, LENGTH),
]


def _onsets() -> list[str]:
    return list(S.consonants())


def _build(rng: random.Random, shape: tuple[str, ...]) -> list[Mora] | None:
    """Fill one shape with segments. Returns None if the draw happens to be illegal."""
    legal = set(S.legal_syllabic_moras())
    geminable = sorted(S.geminable())
    onsets = _onsets()
    moras: list[Mora] = []

    for index, kind in enumerate(shape):
        if kind == SYLLABIC:
            previous = moras[-1] if moras else None
            after_gem = previous is not None and previous.kind == GEM
            if after_gem:
                onset = previous.onset
            elif index == 0 and rng.random() < 0.12:
                onset = None  # a word-initial vowel, the only hiatus-free zero onset
            elif previous is not None and previous.kind == NASAL and rng.random() < 0.35:
                onset = None  # the kan'a shape: legal because it follows a moraic n
            else:
                onset = rng.choice(onsets)
            choices = [vowel for vowel in S.vowels() if (onset, vowel) in legal]
            if not choices:
                return None
            moras.append(Mora(SYLLABIC, onset, rng.choice(choices)))
        elif kind == GEM:
            moras.append(Mora(GEM, onset=rng.choice(geminable)))
        else:
            moras.append(Mora(kind))

    # A length mora needs a vowel before it, and a gem mora a syllabic after it; the shapes
    # above all satisfy that, so anything illegal here is an unlucky segment draw.
    return moras


def _features(word: str) -> set[str]:
    """Which coverage buckets this word falls into."""
    moras = validate(word).moras
    found: set[str] = set()
    for index, mora in enumerate(moras):
        if mora.kind == LENGTH:
            found.add("long_vowel")
            following = moras[index + 1] if index + 1 < len(moras) else None
            if following is not None and following.kind == SYLLABIC and following.onset:
                found.add("long_then_onset")
        elif mora.kind == NASAL:
            found.add("moraic_n")
            if mora.explicit_break:
                found.add("apostrophe")
        elif mora.kind == GEM:
            found.add("geminate")
            found.add(f"gem:{mora.onset}")
        elif mora.kind == SYLLABIC:
            if mora.onset is None and index > 0:
                found.add("inner_zero_onset")
            if mora.onset:
                found.add(f"onset:{mora.onset}")
    return found


def quotas() -> dict[str, int]:
    """Coverage requirements, derived from spec/ rather than written out by hand."""
    required = {
        "long_vowel": 20,
        "geminate": 20,
        "moraic_n": 20,
        "apostrophe": 10,
        "inner_zero_onset": 5,
        "long_then_onset": 5,
    }
    # Every retroflex consonant, whatever the inventory happens to contain.
    for key, entry in S.consonants().items():
        if entry["place"] == "retroflex":
            required[f"onset:{key}"] = 10
    # Every consonant the spec says may geminate must actually be geminated.
    for key in S.geminable():
        required[f"gem:{key}"] = 1
    return required


def generate(count: int = DEFAULT_COUNT, seed: int = SEED) -> list[str]:
    """`count` distinct legal words meeting every quota. Deterministic for a given seed."""
    rng = random.Random(seed)
    required = quotas()
    needed_ids = set(S.legal_mora_ids())

    words: list[str] = []
    seen: set[str] = set()
    tally: Counter[str] = Counter()
    attempts = 0
    limit = count * 4000

    while len(words) < count:
        attempts += 1
        if attempts > limit:
            raise RuntimeError(
                f"gave up after {attempts} attempts with {len(words)}/{count} words; "
                f"unmet quotas: {_unmet(tally, required)}; "
                f"unused mora ids: {sorted(needed_ids)}"
            )
        moras = _build(rng, rng.choice(SHAPES))
        if moras is None:
            continue
        try:
            word = moras_to_roman(moras)
        except ValueError:
            continue
        if word in seen or not validate(word).ok:
            continue

        features = _features(word)
        glyphs = {mora.glyph for mora in moras}
        remaining = count - len(words)
        useful = bool(glyphs & needed_ids) or any(
            tally[key] < need for key, need in required.items() if key in features
        )
        # Once only as many slots are left as there are outstanding requirements, take
        # nothing that does not close a gap.
        if not useful and remaining <= len(_unmet(tally, required)) + len(needed_ids):
            continue

        words.append(word)
        seen.add(word)
        tally.update(features)
        needed_ids -= glyphs

    unmet = _unmet(tally, required)
    if unmet:
        raise RuntimeError(f"coverage quotas unmet: {unmet}")
    if needed_ids:
        raise RuntimeError(f"mora ids never used: {sorted(needed_ids)}")
    return words


def _unmet(tally: Counter[str], required: dict[str, int]) -> dict[str, str]:
    return {
        key: f"{tally[key]}/{need}" for key, need in sorted(required.items()) if tally[key] < need
    }


def main() -> int:
    count = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_COUNT
    words = generate(count)

    tally: Counter[str] = Counter()
    for word in words:
        tally.update(_features(word))

    print(f"{len(words)} legal words, seed {SEED}")
    print(f"mora ids covered: {len({m.glyph for w in words for m in validate(w).moras})}"
          f"/{len(S.legal_mora_ids())}")
    print("coverage:")
    for key, need in sorted(quotas().items()):
        print(f"  {key:<24} {tally[key]:>4}  (need {need})")
    print("\nfirst 20:")
    print("  " + " ".join(words[:20]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
