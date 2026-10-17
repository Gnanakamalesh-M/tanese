The Tanese script is an original featural abugida: one glyph per mora, composed from a small
set of hand-designed atoms rather than drawn one shape at a time.

Featural means the shape says something about the sound. A glyph's frame encodes the place of
articulation, a manner mark encodes the manner, and a vowel mark encodes the vowel, so the
retroflex series looks like a series and a learner who knows the atoms can decode a glyph
they have never seen. The cost is that the glyphs are systematically similar, which is
exactly what makes a featural script hard to read quickly, and whether these particular
shapes are distinguishable has not been tested — see section 7.

Two deliberate departures from the Indic abugidas the design otherwise resembles:

**No inherent vowel, and no virama.** In Devanagari a bare consonant carries an implicit /a/
and a diacritic is needed to suppress it. Tanese instead requires an explicit vowel mark on
every syllabic glyph. This makes the glyph inventory slightly larger and the mapping exactly
one-to-one: a mora sequence and a glyph sequence are the same length, which is what makes the
round-trip test in Phase 1A meaningful rather than approximate.

**The romanization is canonical, not the script.** Locked decision 12 makes the ASCII
spelling the real written form and the script a mapping layer on top of it. This is backwards
from how a natural writing system relates to its transliteration, and it was chosen for an
engineering reason that outweighs the aesthetic one: Tanese strings have to travel through
YAML keys, filenames, test fixtures, tokenizers and embedding pipelines in later phases, and
an ASCII canonical form cannot be corrupted by any of them. The script converter therefore
goes through the mora sequence in both directions, so there is no letter-to-glyph table that
could drift out of sync with the phonology.

Rendering is out of scope for v0.1. Each mora reserves a Private Use Area codepoint so that a
font can be attached later, but no font, SVG or image exists anywhere in this project: the
shapes below are prose descriptions, and nothing has ever been drawn.
