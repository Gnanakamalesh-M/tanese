# The Tanese Language Specification

**Version v0.1**

> This file is generated. Do not edit it.
>
> Run `python scripts/gen_spec_doc.py` to rebuild it from `spec/*.yaml` (the
> machine-readable source of truth for the language) and `docs/_rationale/*.md`
> (the hand-written narrative). `python scripts/gen_spec_doc.py --check` fails if
> this file and `spec/` disagree, and `python scripts/run_checks.py` runs that check.

Tanese is a constructed language inspired by Tamil and Japanese. This document is its
complete specification as of v0.1: the sounds, the spelling, the writing system, the
grammar, and the rules that say what a Tanese word may be.

It is worth being exact about what "inspired by" means here, because it is the claim most
easily overstated. Tanese takes from Tamil a retroflex consonant series, agglutinative
suffixing morphology, and a habit of carving meaning finely where the distinction matters.
It takes from Japanese a mora-based phonology, a strict ban on consonant clusters, verb-final
clause structure, and a productive compounding habit. It takes **no forms at all**: not a
particle, not a case ending, not a root. Every form in this document was coined for Tanese,
and the one place where resemblance is permitted — adapted loanwords, section 5.6 — is
labelled as such and capped by quota.

### How to read this document

Each section states a decision, then why it was made, then what it costs. The last part is
not decoration. A constructed language is a pile of trade-offs, and a specification that
lists only the benefits is not a specification but an advertisement, so every rule here
carries its known problems alongside its justification, in the same `problems` field of the
same YAML file.

Three things this document is not:

- **A teaching grammar.** It is organised by the structure of the language, not by what a
  learner would need first.
- **A record of usage.** Nothing in Tanese has ever been spoken, and no text has been
  written in it beyond the examples here. Section 7 is specific about what that means.
- **Hand-written.** Everything factual below is generated from `spec/*.yaml`, which is the
  actual source of truth. If this document and `spec/` ever disagree, `spec/` is right and
  `python scripts/gen_spec_doc.py --check` fails until the document is rebuilt.

### What exists and what does not

| Layer | Status |
| --- | --- |
| Phonology, romanization, script | specified and implemented (Phase 1A) |
| Grammar: word order, morphology, particles, politeness | specified and implemented (Phase 1B) |
| Vocabulary rules: how a word may be formed | specified and implemented (Phase 1C) |
| **The vocabulary itself** | **does not exist yet** (Phase 2) |
| Corpus, NLP toolkit, evaluation | do not exist yet (Phases 3–7) |

The absence in the middle of that table is the thing to keep in mind while reading. Tanese
has a complete grammar and no words. Every form in the examples below is either a
placeholder invented so that a rule could be demonstrated, or an illustration of a word
*shape*; none is official vocabulary, and a checker enforces that none of them leaks into
the lexicon when Phase 2 builds it. A rule that looks well-supported here has been tested
against other rules, not against use.

## 1. Sounds

The sound system is the layer every other layer is built on, so it was designed to be small,
unambiguous, and mechanically checkable before anything else existed.

Five vowels with a length contrast, and sixteen consonants including a retroflex series. The
retroflexes are the one feature taken straight from Tamil in character — they are the sound
most Tamil speakers would recognise as familiar and most Japanese speakers as foreign — and
they are what keeps Tanese from sounding simply Japanese, given how much of the syllable
structure is mora-based.

Two consequences of the inventory are worth noticing because they shape everything later:

**There is no /h/.** This is not an omission. The absence of /h/ is what lets the letter `h`
work as a pure retroflex marker, so `th`, `dh` and `nh` are single consonants and no reader
has to wonder whether `tha` is one sound or two. A language with both /h/ and a retroflex
digraph convention would need a third device to tell them apart.

**Six of the sixteen consonants cannot be geminated** — the nasals, the tap and the two
glides. The criterion is phonetic rather than arbitrary: a geminate is a consonant held
across a mora boundary, and these are the consonants a speaker cannot audibly hold without
turning them into something else. It costs the lexicon some word shapes, and it leaves an
asymmetry that has to be taught rather than derived ("why can /t/ double when /n/ cannot?").

Accent is fixed on the first mora and is never contrastive, so it is not written at all. It
is recorded in the spec only so that a future pronunciation guide has one place to read it
from.

The constraint list in 1.4 is the real definition of a legal word, and it is executable:
`tanese_nlp.phonology.validate` returns the id of the constraint a rejected word broke, not
a boolean. That matters for two later phases — Phase 2 has to tell a human *why* a candidate
word was dropped, and Phase 4 has to report it to a learner — so the reason was built in
from the start rather than retrofitted.

### 1.1 Vowels

| Letter | IPA | Height | Backness |
| --- | --- | --- | --- |
| a | a | low | central |
| i | i | high | front |
| u | u | high | back |
| e | e | mid | front |
| o | o | mid | back |

Length is contrastive: Locked decision 9. Length is carried by a separate mora (see mora_kinds.length), not by a distinct vowel phoneme, so the vowel inventory stays at five and the mora count of a word is read directly off its mora sequence.

### 1.2 Consonants

| Letter | IPA | Place | Manner | Voiced | Geminable |
| --- | --- | --- | --- | --- | --- |
| p | p | labial | plosive | no | yes |
| b | b | labial | plosive | yes | yes |
| t | t | alveolar | plosive | no | yes |
| d | d | alveolar | plosive | yes | yes |
| th | ʈ | retroflex | plosive | no | yes |
| dh | ɖ | retroflex | plosive | yes | yes |
| k | k | velar | plosive | no | yes |
| g | g | velar | plosive | yes | yes |
| s | s | alveolar | fricative | no | yes |
| m | m | labial | nasal | yes | no |
| n | n | alveolar | nasal | yes | no |
| nh | ɳ | retroflex | nasal | yes | no |
| r | ɾ | alveolar | tap | yes | no |
| l | l | alveolar | lateral | yes | yes |
| w | w | labial | glide | yes | no |
| y | j | palatal | glide | yes | no |

### 1.3 Moras and syllables

| Mora kind | Description | Glyph role |
| --- | --- | --- |
| syllabic | An optional onset consonant plus exactly one short vowel -- (C)V. | base |
| length | The second mora of a long vowel. Carries no segment of its own. | mark |
| nasal | The moraic nasal, written `n`. The only legal coda. | mark |
| gem | The held closure before a geminate onset. Precedes the mora it doubles. | mark |

Syllable template: `(C)V(N)`. Locked decision 10. Stated in moras: a syllable is one syllabic mora, optionally followed by a length mora, optionally followed by a nasal mora. A long vowel therefore makes a two-mora syllable, which is why `CVV` is not a mora kind of its own.

Accent is fixed, on the first mora, and not contrastive. Locked decision 11. Being fully predictable, accent is not written in the romanization or the script and needs no code: it is recorded here so documentation and any future pronunciation guide have a single source.

### 1.4 What is not a legal word

Every rejection names the constraint it broke, so it can be explained rather than
merely counted.

| Id | Name | Constraint |
| --- | --- | --- |
| PT-001 | unknown character | Every character must be a romanization grapheme letter or the apostrophe. |
| PT-002 | empty word | A word must contain at least one mora. |
| PT-003 | consonant not followed by a vowel | A word-internal consonant must begin a syllabic mora, be the moraic nasal, or be the first half of a geminate. Anything else is a consonant cluster. |
| PT-004 | illegal word-final consonant | A word may end only in a vowel or the moraic nasal. |
| PT-005 | illegal word-initial mora | A word may not begin with a nasal mora or a gemination mora. |
| PT-006 | ill-formed geminate | A gemination mora may not be word-final, and the mora after it must be a syllabic mora whose onset is the consonant being doubled. |
| PT-007 | non-geminable consonant doubled | The doubled consonant must be marked `geminable` in the consonant inventory above. |
| PT-008 | vowel hiatus | A syllabic mora with no onset may appear only as the first mora of a word, or immediately after a nasal mora. |
| PT-009 | over-long vowel | A length mora may not follow another length mora. |
| PT-010 | missing apostrophe after moraic n | A moraic nasal followed by a vowel, `y`, or `w` must be written with an apostrophe: `kan'a`, `kan'ya`, `kan'wa`. |
| PT-011 | misplaced apostrophe | An apostrophe is legal only immediately after a moraic nasal and immediately before a vowel, `y`, or `w`. |
| PT-012 | illegal mora | The mora is not in the legal mora set (see `gaps`). |

### 1.5 Gaps in the mora inventory

| Mora | Why it does not exist |
| --- | --- |
| yi | /ji/ is near-indistinguishable from /i/: the glide and the following vowel share the same articulation. Japanese has the same gap, for the same reason. |
| wu | /wu/ is near-indistinguishable from /u/, both being high back rounded. Japanese has the same gap. |

## 2. Spelling

The romanization is the canonical written form of Tanese (locked decision 12); the
script in section 3 is a mapping layer on top of it, never the other way round. Every
rule in this document is stated in the romanization.

- Letters (lower): `a` `b` `d` `e` `g` `h` `i` `k` `l` `m` `n` `o` `p` `r` `s` `t` `u` `w` `y`
- Syllable-boundary marker: `'`
- Word separator: a single space, as declared by GR-ORD-001

Lowercase a-z plus one apostrophe. No capitals, no digits, no diacritics, nothing outside 7-bit ASCII. Keeping the form case-insensitive matters because Tanese strings travel through YAML keys, filenames, URLs and embedding pipelines in later phases, where a stray lowercasing of a case-significant spelling would silently corrupt a word.

`c`, `f`, `j`, `q`, `v`, `x` and `z` are deliberately unused and are reserved, so that a future phoneme can be added without respelling existing vocabulary.

### 2.1 Length, gemination and the moraic nasal

| Feature | How it is written | Why |
| --- | --- | --- |
| long vowels | Double the vowel grapheme -- aa, ii, uu, ee, oo. | Forced by locked decision 12: a macron or colon is either non-ASCII or punctuation. Doubling is also mora-transparent, since a long vowel is two moras and gets two letters. |
| gemination | Repeat the full onset spelling of the doubled consonant -- kk, pp, tt, ss, ll, thth, dhdh. | One rule with no exceptions, including for the retroflex digraphs. The obvious shortcut -- double only the digraph's first letter, giving `kattha` for /ka(TT)a/ -- was rejected because it collides with moraic-n spellings and would make `nnha` ambiguous. |
| moraic nasal | `n` is the moraic nasal whenever it is not followed by a vowel grapheme and does not form the digraph `nh` with a following vowel. It is written with an apostrophe before a vowel, `y`, or `w`. | `nn` is therefore always moraic-n + /n/, never a geminate, because nasal gemination is illegal (see the `gemination` block in spec/phonology.yaml). Likewise `nnh` is always moraic-n + /nh/, while a geminate /nh/ would have to be spelled `nhnh` and is rejected. |

### 2.2 Worked cases that pin the parse down

The parse is deterministic longest-match, so every legal word has exactly one
spelling and every spelling exactly one reading. These are the cases that fix it.

| Spelling | Moras | Why that reading and no other |
| --- | --- | --- |
| `katha` | TS-KA . TS-THA | `th` is one onset; no `ha` mora exists, so no other reading is available. |
| `kantha` | TS-KA . TS-NASAL . TS-THA | `n` is not followed by `h`, so it is the moraic nasal; then `th` is the onset. |
| `kanha` | TS-KA . TS-NHA | Longest-match takes the digraph `nh` as one onset. |
| `kannha` | TS-KA . TS-NASAL . TS-NHA | The first `n` is not followed by `h`, so it is moraic; then `nh` is the onset. |
| `kanna` | TS-KA . TS-NASAL . TS-NA | Always moraic-n + /n/, because nasal gemination is illegal. |
| `kan'a` | TS-KA . TS-NASAL . TS-A | The apostrophe forces the syllable break; without it `kana` is /ka.na/. |
| `kana` | TS-KA . TS-NA | `n` is followed by a vowel, so it is an onset, not the moraic nasal. |
| `kaa` | TS-KA . TS-LONG | Identical adjacent vowels are always one long vowel. |
| `kaaka` | TS-KA . TS-LONG . TS-KA | A long vowel followed by an ordinary onset. Legal; only hiatus is forbidden. |
| `kaththa` | TS-KA . TS-GEM . TS-THA | The onset spelling `th` is repeated in full, so the gemination mora is recognised. |

The parse order, as the lexer applies it:

1. Reject any character outside `alphabet`.
2. At each position, match the longest consonant grapheme first (two-letter digraphs before single letters).
3. A consonant grapheme followed by a vowel grapheme opens a syllabic mora. A bare `n` not followed by a vowel is the moraic nasal. A consonant grapheme immediately repeated before a vowel is a gemination mora. Anything else is constraint PT-003.
4. A vowel grapheme with no preceding onset opens a syllabic mora with no onset.
5. After a syllabic mora, a repeat of the same vowel grapheme is a length mora, never a second syllabic mora.

## 3. The script

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

| Property | Value |
| --- | --- |
| type | featural abugida |
| reason | A pure syllabary would need one independently drawn glyph per mora, which is neither honestly finishable nor justifiable -- there would be nothing principled to say about any individual shape. Making the script featural instead (place encoded by the frame, manner by an inner mark, in the spirit of Hangul but with no shared shapes) means the whole table follows from 25 decisions, each of which has a reason, and it gives Phase 6 a composition recipe it can render as SVG without a font. |
| alternatives | (a) A hand-drawn syllabary, rejected above. (b) An abugida with arbitrary but maximally distinctive base shapes, which would keep the consonants easier to tell apart but leave every shape unjustified and lose the featural logic. |
| problems | Featurally derived glyphs risk looking alike: the three retroflexes differ from their alveolar counterparts only by the curled foot, and the two glides only by a doubled stroke. Nothing has been rendered yet, so the shape descriptions are unverified prose -- see README "Not verified". |

- Inherent vowel: none
- Virama: none

A deliberate departure from Indic abugidas, which give the bare consonant an inherent /a/ and need a virama to cancel it. Here every syllabic glyph carries an explicit vowel mark. That costs one extra mark on the /a/ moras and removes a whole class of converter bugs, since no glyph is ever ambiguous between "consonant + a" and "bare consonant".

### 3.1 Atoms

The hand-designed pieces every glyph is composed from.

**frames**

| Id | Shape |
| --- | --- |
| FRAME-CARRIER | A plain vertical stem, unadorned. |
| FRAME-LABIAL | A vertical stem closed by a bowl on its left side. |
| FRAME-ALVEOLAR | A vertical stem with a flat crossbar at mid height. |
| FRAME-RETROFLEX | A vertical stem whose foot curls rightward into a hook. |
| FRAME-VELAR | A vertical stem opening into a two-pronged fork at the top. |
| FRAME-PALATAL | A stem leaning to the right, drawn as a single diagonal. |

**manner_marks**

| Id | Shape |
| --- | --- |
| MANNER-PLAIN | No inner mark. The bare frame is the voiceless plosive of its place. |
| MANNER-DOT | A single dot inside the frame. |
| MANNER-BAR | A horizontal bar drawn through the stem. |
| MANNER-SLASHES | Two short parallel slashes across the stem. |
| MANNER-WAVE | One short wave on the stem. |
| MANNER-TAIL | A straight tail extending from the foot of the stem. |
| MANNER-DOUBLE | The frame drawn twice as two parallel strokes. |

**standalone_marks**

| Id | Shape |
| --- | --- |
| MARK-LONG | A long horizontal stroke on the baseline. |
| MARK-NASAL | A small closed hook on the baseline. |
| MARK-GEM | A single dot on the baseline. |

**vowel_marks**

| Id | Shape |
| --- | --- |
| VOW-A | A short stroke to the right of the foot. |
| VOW-I | A tick at the top right. |
| VOW-U | A hook beneath the foot. |
| VOW-E | A bar across the top. |
| VOW-O | A bar on the right side at mid height. |

### 3.2 Bases

17 bases, each a frame plus a manner mark.

| Id | Composition |
| --- | --- |
| BASE-CARRIER | FRAME-CARRIER + MANNER-PLAIN |
| BASE-P | FRAME-LABIAL + MANNER-PLAIN |
| BASE-B | FRAME-LABIAL + MANNER-DOT |
| BASE-M | FRAME-LABIAL + MANNER-BAR |
| BASE-W | FRAME-LABIAL + MANNER-DOUBLE |
| BASE-T | FRAME-ALVEOLAR + MANNER-PLAIN |
| BASE-D | FRAME-ALVEOLAR + MANNER-DOT |
| BASE-N | FRAME-ALVEOLAR + MANNER-BAR |
| BASE-S | FRAME-ALVEOLAR + MANNER-SLASHES |
| BASE-R | FRAME-ALVEOLAR + MANNER-WAVE |
| BASE-L | FRAME-ALVEOLAR + MANNER-TAIL |
| BASE-TH | FRAME-RETROFLEX + MANNER-PLAIN |
| BASE-DH | FRAME-RETROFLEX + MANNER-DOT |
| BASE-NH | FRAME-RETROFLEX + MANNER-BAR |
| BASE-K | FRAME-VELAR + MANNER-PLAIN |
| BASE-G | FRAME-VELAR + MANNER-DOT |
| BASE-Y | FRAME-PALATAL + MANNER-DOUBLE |

### 3.3 The mora table

One glyph per legal mora: 86 in total, each with a reserved
Private Use Area codepoint for later rendering. The canonical script form of a word is
the dot-joined sequence of its mora ids.

| Id | Mora | Kind | Composition | PUA |
| --- | --- | --- | --- | --- |
| TS-A | `a` | syllabic | BASE-CARRIER + VOW-A | U+E000 |
| TS-I | `i` | syllabic | BASE-CARRIER + VOW-I | U+E001 |
| TS-U | `u` | syllabic | BASE-CARRIER + VOW-U | U+E002 |
| TS-E | `e` | syllabic | BASE-CARRIER + VOW-E | U+E003 |
| TS-O | `o` | syllabic | BASE-CARRIER + VOW-O | U+E004 |
| TS-PA | `pa` | syllabic | BASE-P + VOW-A | U+E005 |
| TS-PI | `pi` | syllabic | BASE-P + VOW-I | U+E006 |
| TS-PU | `pu` | syllabic | BASE-P + VOW-U | U+E007 |
| TS-PE | `pe` | syllabic | BASE-P + VOW-E | U+E008 |
| TS-PO | `po` | syllabic | BASE-P + VOW-O | U+E009 |
| TS-BA | `ba` | syllabic | BASE-B + VOW-A | U+E00A |
| TS-BI | `bi` | syllabic | BASE-B + VOW-I | U+E00B |
| TS-BU | `bu` | syllabic | BASE-B + VOW-U | U+E00C |
| TS-BE | `be` | syllabic | BASE-B + VOW-E | U+E00D |
| TS-BO | `bo` | syllabic | BASE-B + VOW-O | U+E00E |
| TS-TA | `ta` | syllabic | BASE-T + VOW-A | U+E00F |
| TS-TI | `ti` | syllabic | BASE-T + VOW-I | U+E010 |
| TS-TU | `tu` | syllabic | BASE-T + VOW-U | U+E011 |
| TS-TE | `te` | syllabic | BASE-T + VOW-E | U+E012 |
| TS-TO | `to` | syllabic | BASE-T + VOW-O | U+E013 |
| TS-DA | `da` | syllabic | BASE-D + VOW-A | U+E014 |
| TS-DI | `di` | syllabic | BASE-D + VOW-I | U+E015 |
| TS-DU | `du` | syllabic | BASE-D + VOW-U | U+E016 |
| TS-DE | `de` | syllabic | BASE-D + VOW-E | U+E017 |
| TS-DO | `do` | syllabic | BASE-D + VOW-O | U+E018 |
| TS-THA | `tha` | syllabic | BASE-TH + VOW-A | U+E019 |
| TS-THI | `thi` | syllabic | BASE-TH + VOW-I | U+E01A |
| TS-THU | `thu` | syllabic | BASE-TH + VOW-U | U+E01B |
| TS-THE | `the` | syllabic | BASE-TH + VOW-E | U+E01C |
| TS-THO | `tho` | syllabic | BASE-TH + VOW-O | U+E01D |
| TS-DHA | `dha` | syllabic | BASE-DH + VOW-A | U+E01E |
| TS-DHI | `dhi` | syllabic | BASE-DH + VOW-I | U+E01F |
| TS-DHU | `dhu` | syllabic | BASE-DH + VOW-U | U+E020 |
| TS-DHE | `dhe` | syllabic | BASE-DH + VOW-E | U+E021 |
| TS-DHO | `dho` | syllabic | BASE-DH + VOW-O | U+E022 |
| TS-KA | `ka` | syllabic | BASE-K + VOW-A | U+E023 |
| TS-KI | `ki` | syllabic | BASE-K + VOW-I | U+E024 |
| TS-KU | `ku` | syllabic | BASE-K + VOW-U | U+E025 |
| TS-KE | `ke` | syllabic | BASE-K + VOW-E | U+E026 |
| TS-KO | `ko` | syllabic | BASE-K + VOW-O | U+E027 |
| TS-GA | `ga` | syllabic | BASE-G + VOW-A | U+E028 |
| TS-GI | `gi` | syllabic | BASE-G + VOW-I | U+E029 |
| TS-GU | `gu` | syllabic | BASE-G + VOW-U | U+E02A |
| TS-GE | `ge` | syllabic | BASE-G + VOW-E | U+E02B |
| TS-GO | `go` | syllabic | BASE-G + VOW-O | U+E02C |
| TS-SA | `sa` | syllabic | BASE-S + VOW-A | U+E02D |
| TS-SI | `si` | syllabic | BASE-S + VOW-I | U+E02E |
| TS-SU | `su` | syllabic | BASE-S + VOW-U | U+E02F |
| TS-SE | `se` | syllabic | BASE-S + VOW-E | U+E030 |
| TS-SO | `so` | syllabic | BASE-S + VOW-O | U+E031 |
| TS-MA | `ma` | syllabic | BASE-M + VOW-A | U+E032 |
| TS-MI | `mi` | syllabic | BASE-M + VOW-I | U+E033 |
| TS-MU | `mu` | syllabic | BASE-M + VOW-U | U+E034 |
| TS-ME | `me` | syllabic | BASE-M + VOW-E | U+E035 |
| TS-MO | `mo` | syllabic | BASE-M + VOW-O | U+E036 |
| TS-NA | `na` | syllabic | BASE-N + VOW-A | U+E037 |
| TS-NI | `ni` | syllabic | BASE-N + VOW-I | U+E038 |
| TS-NU | `nu` | syllabic | BASE-N + VOW-U | U+E039 |
| TS-NE | `ne` | syllabic | BASE-N + VOW-E | U+E03A |
| TS-NO | `no` | syllabic | BASE-N + VOW-O | U+E03B |
| TS-NHA | `nha` | syllabic | BASE-NH + VOW-A | U+E03C |
| TS-NHI | `nhi` | syllabic | BASE-NH + VOW-I | U+E03D |
| TS-NHU | `nhu` | syllabic | BASE-NH + VOW-U | U+E03E |
| TS-NHE | `nhe` | syllabic | BASE-NH + VOW-E | U+E03F |
| TS-NHO | `nho` | syllabic | BASE-NH + VOW-O | U+E040 |
| TS-RA | `ra` | syllabic | BASE-R + VOW-A | U+E041 |
| TS-RI | `ri` | syllabic | BASE-R + VOW-I | U+E042 |
| TS-RU | `ru` | syllabic | BASE-R + VOW-U | U+E043 |
| TS-RE | `re` | syllabic | BASE-R + VOW-E | U+E044 |
| TS-RO | `ro` | syllabic | BASE-R + VOW-O | U+E045 |
| TS-LA | `la` | syllabic | BASE-L + VOW-A | U+E046 |
| TS-LI | `li` | syllabic | BASE-L + VOW-I | U+E047 |
| TS-LU | `lu` | syllabic | BASE-L + VOW-U | U+E048 |
| TS-LE | `le` | syllabic | BASE-L + VOW-E | U+E049 |
| TS-LO | `lo` | syllabic | BASE-L + VOW-O | U+E04A |
| TS-WA | `wa` | syllabic | BASE-W + VOW-A | U+E04B |
| TS-WI | `wi` | syllabic | BASE-W + VOW-I | U+E04C |
| TS-WE | `we` | syllabic | BASE-W + VOW-E | U+E04D |
| TS-WO | `wo` | syllabic | BASE-W + VOW-O | U+E04E |
| TS-YA | `ya` | syllabic | BASE-Y + VOW-A | U+E04F |
| TS-YU | `yu` | syllabic | BASE-Y + VOW-U | U+E050 |
| TS-YE | `ye` | syllabic | BASE-Y + VOW-E | U+E051 |
| TS-YO | `yo` | syllabic | BASE-Y + VOW-O | U+E052 |
| TS-LONG | -- | length | MARK-LONG | U+E053 |
| TS-NASAL | -- | nasal | MARK-NASAL | U+E054 |
| TS-GEM | -- | gem | MARK-GEM | U+E055 |

## 4. Grammar

Tanese is SOV and consistently head-final: modifiers precede what they modify, relative and
subordinate clauses precede their heads, and the verb closes the clause. Relations between
arguments are carried by postposition particles rather than by position, so the arguments
themselves may be reordered freely before the verb without changing who did what.

The morphology is agglutinative and suffixing only — no prefixes, no infixes, no stem
changes. A root is invariant, and a fully specified verb is its root plus up to four suffixes
in a fixed order: aspect, tense, mood, politeness. There is no agreement of any kind. The
verb does not vary for person, number or gender; pronouns carry person, plural is an optional
noun suffix, and grammatical gender does not exist. A single verb form therefore serves every
subject, which is the largest single simplification in the language and the one that most
reduces what a learner or a parser has to know.

Politeness is a three-way contrast — casual, neutral, formal — and it is marked **once per
clause**, on the final verb, rather than spread across the sentence as it is in Japanese. The
casual level is the empty slot, which keeps the shortest form the most informal.

Particles are separate words and suffixes are glued on. This is the whole of the word-boundary
definition, it is declared by exactly one rule (`GR-ORD-001`), and every component that needs
to know where a word ends — the tokenizer, the validator, the script converter, the
contradiction checker — reads it from that rule rather than assuming a space. One definition,
one place.

### The known wart

Negation is the mood suffix `-nhi`, which keeps the locked four-slot verb order intact but
means negation cannot co-occur with another mood. The prohibitive and the negative conditional
are therefore two words where their positive counterparts are one, and a negative
desiderative ("does not want to") has no form at all. This is the clearest unresolved problem
in the grammar; section 6 states the condition under which it would be reopened.

### What has been checked

The grammar is held together by twelve mechanical checks (`python scripts/check_grammar.py`),
which prove among other things that no form is claimed for two functions, no function is
claimed by two forms, no rule asserts a slot order that disagrees with the locked one, and
every example is a legal, tokenizable, script-consistent Tanese word sequence. Every one of
those checks is itself tested against a rule set built to break it, so a green run is not
green by accident.

What they do not prove is that the rules are *usable together*. Nothing has been written in
Tanese, so whether these rules compose into a language someone could say anything in is
genuinely unknown. That is what Phase 3 is for.

### 4.1 The morpheme inventory

Particles (separate words):

| Form | Slot | Function | Rule |
| --- | --- | --- | --- |
| ban | case | locative | GR-PART-005 |
| dhen | case | subject | GR-PART-001 |
| do | case | object | GR-PART-002 |
| kodhu | case | ablative | GR-PART-008 |
| lu | case | genitive | GR-PART-004 |
| nhu | case | comitative | GR-PART-007 |
| sen | case | instrumental | GR-PART-006 |
| thin | case | dative goal | GR-PART-003 |
| belu | clause | topic | GR-PART-009 |
| lun | clause | negative conditional | GR-NEG-004 |
| thenu | clause | quotative | GR-PART-011 |
| thon | clause | prohibitive | GR-NEG-003 |
| wen | clause | question yes no | GR-PART-010 |

Suffixes (attached to the root):

| Form | Slot | Function | Tense | Rule |
| --- | --- | --- | --- | --- |
| mu | aspect | perfective | -- | GR-TAM-001 |
| nhe | aspect | perfect | -- | GR-TAM-001 |
| ri | aspect | progressive | -- | GR-TAM-001 |
| bo | mood | conditional | required | GR-TAM-005 |
| le | mood | desiderative | required | GR-TAM-005 |
| lo | mood | hortative | forbidden | GR-IMP-003 |
| nhi | mood | negative | required | GR-NEG-001 |
| so | mood | imperative | forbidden | GR-IMP-001 |
| the | mood | polite request | forbidden | GR-IMP-002 |
| nen | number | plural | -- | GR-NOUN-001 |
| mi | politeness | neutral | -- | GR-POL-001 |
| sun | politeness | formal | -- | GR-POL-001 |
| dho | tense | past | -- | GR-TAM-003 |
| ke | tense | non past | -- | GR-TAM-003 |

Pronouns (whole words):

| Form | Function | Rule |
| --- | --- | --- |
| ano | first person | GR-PRON-001 |
| anonen | first person plural | GR-PRON-004 |
| iri | second person | GR-PRON-001 |
| irinen | second person plural | GR-PRON-004 |
| uthe | third person | GR-PRON-001 |
| uthenen | third person plural | GR-PRON-004 |

Verb suffix order (locked decision 6), as declared by GR-VERB-003:

    ROOT - ASPECT - TENSE - MOOD - POLITENESS

### 4.2 The rules

**morphology**

| Id | Name | Pattern | Rule |
| --- | --- | --- | --- |
| GR-NOUN-001 | optional plural suffix | `NOUN + -nen` | Plurality is marked by the suffix `-nen` on the noun. It is optional: a bare noun is unspecified for number, not singular. |
| GR-VERB-003 | verb suffix slot order | `ROOT - ASPECT - TENSE - MOOD - POLITENESS` | Verb suffixes occur in exactly this order after the root: aspect, tense, mood, politeness. Every slot is independently skippable except as GR-VERB-006 and the mood entries' `tense` field require. |
| GR-TAM-001 | aspect suffixes | `ROOT + (-ri \| -nhe \| -mu) + ...` | The aspect slot takes `-ri` (progressive: in progress), `-nhe` (perfect: completed with a result that holds) or `-mu` (perfective: viewed as a single whole event). It sits immediately after the root. |
| GR-TAM-003 | two-way tense | `ROOT [ASPECT] + (-dho \| -ke) + ...` | The tense slot takes `-dho` (past) or `-ke` (non-past). There is no third tense and no future suffix. |
| GR-TAM-005 | conditional and desiderative moods | `ROOT [ASPECT] TENSE + (-bo \| -le) [POLITENESS]` | The mood slot takes `-bo` (conditional: "if") or `-le` (desiderative: "wants to"). Both require a tense suffix before them. |
| GR-NEG-001 | verb negation | `ROOT [ASPECT] TENSE + -nhi [POLITENESS]` | The mood suffix `-nhi` negates the verb. It follows tense and precedes politeness, and the tense suffix is required before it. |
| GR-IMP-001 | imperative | `ROOT [ASPECT] + -so [POLITENESS]` | The mood suffix `-so` makes a direct command. It takes no tense suffix, and the subject is normally dropped. |
| GR-IMP-002 | polite request | `ROOT [ASPECT] + -the [POLITENESS]` | The mood suffix `-the` makes a request rather than a command. It is tenseless, and it takes a politeness suffix independently of its own politeness as a mood. |
| GR-IMP-003 | hortative | `ROOT [ASPECT] + -lo [POLITENESS]` | The mood suffix `-lo` proposes a joint action ("let us ..."). It is tenseless and includes the speaker, so no subject is stated. |

**particle**

| Id | Name | Pattern | Rule |
| --- | --- | --- | --- |
| GR-PART-001 | subject particle | `NP + dhen` | The particle `dhen` follows a noun phrase to mark it as the subject. |
| GR-PART-002 | object particle | `NP + do` | The particle `do` follows a noun phrase to mark it as the direct object. |
| GR-PART-003 | dative and goal particle | `NP + thin` | The particle `thin` marks the recipient of a transfer and the goal of motion -- the indirect object and the destination are the same case. |
| GR-PART-004 | genitive particle | `NP + lu + NOUN` | The particle `lu` follows a possessor, and the whole phrase precedes the possessed noun. |
| GR-PART-005 | locative particle | `NP + ban` | The particle `ban` marks the place where something is or happens. |
| GR-PART-006 | instrumental particle | `NP + sen` | The particle `sen` marks the instrument or means by which an action is carried out. |
| GR-PART-007 | comitative particle | `NP + nhu` | The particle `nhu` marks the person or thing accompanying the subject. |
| GR-PART-008 | ablative particle | `NP + kodhu` | The particle `kodhu` marks the source or origin of motion. |
| GR-PART-009 | topic particle | `NP + belu (in place of the case particle)` | The particle `belu` marks what the sentence is about. It replaces the case particle of the phrase it attaches to, rather than stacking with it. |
| GR-PART-010 | yes/no question particle | `CLAUSE + wen` | The clause-final particle `wen` turns a statement into a yes/no question. Nothing else changes: no word order shift, no verb form change. |
| GR-PART-011 | quotative particle | `[CLAUSE] + thenu + ... SPEECH_VERB` | The clause-final particle `thenu` closes a quoted or reported clause, which then serves as the complement of a speech or cognition verb. |
| GR-NEG-003 | prohibitive (analytic) | `... V+TENSE+-nhi [POLITENESS] + thon` | A negative command is the negated non-past verb followed by the clause-final particle `thon`. The verb takes no imperative suffix, and politeness stays on the verb. |
| GR-NEG-004 | negative conditional (analytic) | `[... V+TENSE+-nhi + lun] MAIN_CLAUSE` | A negative "if" clause is the negated verb followed by the clause-final particle `lun`. The conditional suffix `-bo` is not used, and the clause precedes the main clause. |

**politeness**

| Id | Name | Pattern | Rule |
| --- | --- | --- | --- |
| GR-POL-001 | three politeness levels | `ROOT [ASPECT] [TENSE] [MOOD] + (-mi \| -sun \| nothing)` | The politeness slot, last in the verb, takes `-mi` (neutral) or `-sun` (formal), or stands empty for the casual level. Exactly three levels exist. |

**pronoun**

| Id | Name | Pattern | Rule |
| --- | --- | --- | --- |
| GR-PRON-001 | pronoun inventory | `PRONOUN + particle` | Three pronouns: `ano` (1st person), `iri` (2nd person), `uthe` (3rd person). None of them marks gender, and none of them has a separate plural form. |
| GR-PRON-004 | pronoun plural | `PRONOUN + -nen` | Plural pronouns use the ordinary noun plural suffix: `anonen` ("we"), `irinen` ("you" plural), `uthenen` ("they"). There are no dedicated plural pronoun stems. |

**syntax**

| Id | Name | Pattern | Rule |
| --- | --- | --- | --- |
| GR-NOUN-002 | no grammatical gender | `NOUN (no gender class)` | Nouns have no gender class. Nothing in the language -- no particle, suffix, pronoun or agreement -- varies by the gender of a noun. |
| GR-NOUN-003 | no articles | `NOUN (bare)` | There is no definite or indefinite article. Definiteness is not marked grammatically. |
| GR-NOUN-004 | noun-noun compounding | `NOUN NOUN (modifier head)` | Two nouns may be written as separate words in modifier-head order to form a compound meaning. No linking particle and no fusion of the two forms occurs. |
| GR-NOUN-005 | numeral before noun, no classifier | `NUMERAL NOUN` | A numeral precedes the noun it counts, with no classifier or measure word, and the noun does not have to take the plural suffix. |
| GR-PART-012 | core arguments must be particle-marked | `ARG = NP + particle (never bare)` | Every noun phrase acting as subject, object or any other argument of the verb carries a particle. A bare noun phrase may only be a modifier (compound, genitive head, numeral head) or a relative-clause head. |
| GR-PART-013 | one particle per noun phrase | `NP + exactly one particle` | A noun phrase bears exactly one particle. Case particles do not stack, and the topic particle replaces a case particle rather than following it. |
| GR-VERB-001 | verbs are suffixing only | `ROOT + SUFFIX*` | A verb is a root followed by zero or more suffixes, in the order fixed by GR-VERB-003. There are no prefixes, no infixes, no auxiliary verbs and no stem changes: the root is identical in every form. |
| GR-VERB-002 | the citation form is non-finite | `ROOT (no suffix)` | The bare root -- no suffix of any kind -- is the citation form: the dictionary headword and the form quoted when talking about the verb. It is not a finite verb and cannot be the predicate of a sentence. |
| GR-VERB-004 | no verb agreement | `V (invariant across subjects)` | The verb never varies with the person, number or gender of any argument. The same verb form serves every subject. |
| GR-VERB-005 | the copula is an ordinary verb | `NP dhen NP esu+SUFFIX*` | Equation and location use the copula root `esu`, which takes the same four suffix slots as any other verb and stands in the same clause-final position. |
| GR-VERB-006 | tense is obligatory on an indicative verb | `ROOT [ASPECT] TENSE [MOOD] [POLITENESS]  \|  ROOT [ASPECT] TENSELESS_MOOD [POLITENESS]` | A verb with no mood suffix, or with a mood whose `tense` is `required`, must carry a tense suffix. Only the three tenseless moods -- imperative, hortative, polite request -- license a verb with no tense. |
| GR-TAM-002 | unmarked aspect is habitual or neutral | `ROOT + TENSE (aspect slot empty)` | A verb with an empty aspect slot is aspectually neutral: it reads as a habit, a general truth, or simply an unspecified event. |
| GR-TAM-004 | future is non-past plus an adverb | `TIME_ADVERB ... V+-ke` | Future time is expressed by the non-past verb together with a time adverb, or by the desiderative/conditional moods where intention is meant. No suffix marks the future. |
| GR-NEG-002 | copula negation | `NP dhen NP esu+TENSE+-nhi [POLITENESS]` | The copula is negated exactly like any other verb, by `-nhi` in its mood slot. There is no separate negative existential word. |
| GR-Q-001 | yes/no questions add a particle only | `DECLARATIVE + wen` | A yes/no question is a statement plus the clause-final particle `wen`. Word order, verb form and politeness are unchanged. |
| GR-Q-002 | wh-words stay in place and take no question particle | `... WH + particle ... V` | An interrogative word (`kena` "what", `kewa` "who") occupies the ordinary position of the phrase it questions, with the ordinary particle for that role. A wh-question does not take `wen`. |
| GR-Q-003 | wh-words are ordinary noun phrases | `WH + particle` | An interrogative word takes whichever particle its role requires -- `dhen` as subject, `do` as object, `ban` as location -- and may head a genitive phrase like any noun. |
| GR-Q-004 | embedded questions use the quotative particle | `[... WH ... V] + thenu ... V` | A question inside a larger clause is closed by `thenu`, like any reported clause, and loses its own clause particle. An embedded yes/no question is not expressible in v0.1. |
| GR-PRON-002 | pronouns carry person, verbs do not | `PRONOUN + particle ... V (invariant)` | Person information lives entirely in the pronoun. The verb form is identical for first, second and third person. |
| GR-PRON-003 | pronoun dropping | `[no subject] ... V` | A pronoun argument may be omitted entirely when it is clear from context. What is left is a verb with no subject phrase, which is a complete sentence. |
| GR-POL-002 | casual is the empty politeness slot | `ROOT [ASPECT] TENSE [MOOD] (politeness slot empty)` | An empty politeness slot is the casual level. It is a positive value of the feature, not an absence of politeness marking, and a verb with no politeness suffix is a fully well-formed casual verb. |
| GR-POL-003 | politeness is marked once per clause | `... V+POLITENESS (once per clause)` | Politeness is marked on the final verb or copula of the clause and nowhere else. Nouns, pronouns and particles never vary by politeness level. |
| GR-POL-004 | politeness on the copula and after a clause particle | `... esu+TENSE[+MOOD]+POLITENESS [CLAUSE_PARTICLE]` | An equational clause carries its politeness on the copula, like any other verb. Where a clause ends in a particle, the politeness suffix stays on the verb before it and never moves onto the particle. |

**word order**

| Id | Name | Pattern | Rule |
| --- | --- | --- | --- |
| GR-ORD-001 | word boundary | `ROOT+SUFFIX* (space PARTICLE)*` | A root and its suffixes are written solid as one word. Every particle is its own word. Words are separated by exactly one space, and nothing else separates them. |
| GR-ORD-002 | subject-object-verb | `S O V` | The basic order of a transitive clause is subject, object, verb. The verb is last. |
| GR-ORD-003 | modifier before head | `MODIFIER HEAD` | Every modifier precedes its head: numeral before noun, adjectival noun before noun, adverb before verb, genitive phrase before the noun it possesses. |
| GR-ORD-004 | argument order is free under particle marking | `ARG* V, where each ARG is NP + particle` | Because every argument carries its own relation particle, arguments may be reordered before the verb without changing who did what. Reordering changes emphasis only. |
| GR-ORD-005 | clause particles close the clause | `... V CLAUSE_PARTICLE` | The question, prohibitive, negative-conditional and quotative particles stand after the verb, at the very end of their clause. They are the only words that may follow a verb. |
| GR-ORD-006 | relative clause before its head | `[CLAUSE] HEAD_NOUN` | A relative clause precedes the noun it modifies. Its verb takes the ordinary finite suffixes, and there is no relative pronoun and no complementiser. |

## 5. Vocabulary

This section is the newest part of the specification and the one with the least behind it: it
says how Tanese words may be formed, and no Tanese words exist yet. Everything here is a
constraint on a lexicon that Phase 2 will build, not a description of one that exists.

### Where words come from

Five strata, and the distinction between them is **how a word was coined**, not how it
sounds. That is the central decision of this section and it needs stating plainly, because
"Tamil-inspired vocabulary" could easily mean adapted Tamil words, and here it does not.

A `tamil_inspired` word borrows a Tamil *habit* — fine semantic granularity, a separate root
where English would use one word plus a modifier — and its form is coined natively. A
`japanese_inspired` word borrows the Japanese habit of covering a large meaning space by
compounding a small stock of concrete roots, and its form, too, is coined natively. Locked
decision 3 forbids a Tanese particle from equalling a common Japanese or Tamil one; this
section applies the same gate to content words, because a lexicon of recognisably adapted
source words would make the originality claim untrue in the place it matters most.

The honest cost of that choice: the two inspired strata are **invisible in the words
themselves**. You cannot hear what is Tamil-inspired about a Tamil-inspired word. The
inspiration is real but it lives in the shape of the lexicon — which fields have many roots,
which are covered by compounds — and not in the shape of any individual form. It also means
the stratum label is unverifiable: no checker can catch a native root mislabelled
`tamil_inspired`, so it is provenance metadata that has to be recorded honestly rather than a
property that can be proved.

The exception is the `loan` stratum, which borrows a form by definition. It is confined to
one semantic field and capped at six percent of the lexicon, and that restriction — not the
adaptation rules — is what keeps Tanese sounding like itself.

### Why the root shapes are what they are

The mora bounds are a collision argument: a two-mora floor keeps roots out of the space the
particles and suffixes already occupy, and a four-mora ceiling stops the Phase 2 pipeline
from escaping a collision by simply making words longer.

The permitted word-finals are not a taste decision at all. Every suffix in the grammar is
consonant-initial, so a root ending in a vowel or the moraic nasal concatenates legally with
every one of them, and no morphophonemic rule is needed at the join — which matters because
the phonology deliberately declares no allophony and no morphophonemics, so there is no
machinery available to repair a bad join. This makes `RS-FINAL` a *consequence* of the
grammar rather than an independent rule, and it is checked as such: check 2 concatenates
every permitted final with every declared suffix on every run, so a vowel-initial suffix
added in a later phase would make the check fail rather than making the rule quietly wrong.

### Compounds are two words

Compounds are multi-word lexical entries, written with a space. This follows `GR-NOUN-004`,
which is already official and which lists the fused spelling as invalid. Phase 1C had an
obvious reason to want to reopen that — fused compounds are shorter and more natural-looking
— and did not, because the original reason is still good: fusion creates a seam, and a seam
raises questions about hiatus, sandhi and voicing at the join that the phonology has no
answers to. With nothing glued, there is no seam and no question.

The cost is that a lexicalized compound is spelled exactly like the ordinary noun sequence it
came from, so `sedha nami` is both the entry "restaurant" and the phrase "food house". Only
the dictionary separates them.

### Loanwords

The adaptation pipeline is deterministic and table-driven: one input gives exactly one
output, or an explicit rejection naming the sound responsible. There is no sound-specific
knowledge in the code at all — every substitution and every repair is read from the spec.

The unusual decision here is what happens to a sound Tanese has no good equivalent for.
Fourteen source sounds are listed as **unmapped**, and a word containing one is *refused*
rather than approximated. The reason is that each of them has at least two equally defensible
substitutes — the postalveolar fricative could be /s/ or a /sy/ sequence, the affricate could
be /t/ or /s/ or /ti/ — and silently picking one would make the adapter non-deterministic in
the sense that actually matters: a second person adapting the same word by hand would get a
different answer. Japanese convention has settled these questions; Tanese declines to inherit
another language's arbitration and says so out loud instead.

This has a real and intended consequence: Tanese cannot currently borrow `thing`, `chair` or
`shop`. Those words are not available until this specification is deliberately extended with
a decision about those sounds.

One repair deserves singling out because the phonology predicted it. Constraint `PT-008`
forbids vowel hiatus, and its own `problems` field recorded that Phase 1C would have to
supply a glide-based repair for source words with vowel sequences. It now does, and the
interesting part is the fallback: the default glide is chosen by the preceding vowel, but
`yi` and `wu` are gaps in the mora inventory, so `a` + `i` cannot become `ayi` and becomes
`awi` instead. That is not an extra rule but an unavoidable consequence of two moras not
existing.

### The pipeline

Nothing becomes an official Tanese word without a human approving it, and the LLM may act at
exactly one stage — proposing candidates — and nowhere else. The stages are declared with
ids so that the Phase 2 implementation cannot quietly reorder or drop one. This is the
project's standing rule in machine-readable form: rules define Tanese, and the LLM assists
without ever changing them.

### 5.1 Strata

| Stratum | Borrows | Borrows a form? | Share target | What it is |
| --- | --- | --- | --- | --- |
| native | -- | no | 0.60 | A root coined from nothing but the phonology: a legal mora sequence picked for the concept, with no source-language model of any kind. |
| tamil_inspired | semantic_granularity, field_specific_root_density | no | 0.12 | A root coined under a Tamil-like structural habit: fine semantic granularity, where Tamil distinguishes with separate roots what English covers with one word. |
| japanese_inspired | productive_compounding, small_concrete_root_set | no | 0.12 | A root coined under a Japanese-like structural habit: a small set of concrete roots that combine productively, so compounds rather than new roots cover the space. |
| compound | -- | no | 0.10 | A lexical entry made of two or more existing words in modifier-head order, written with a space, as GR-NOUN-004 requires. |
| loan | form, meaning | yes | 0.06 | A word taken from a source language and put through the adaptation pipeline below. The only stratum that borrows a form. |

### 5.2 Root shapes

A root is 2 to 4 moras long and ends in `a` or `i` or `u` or `e` or `o` or `n`.

| Id | Shape rule | Why |
| --- | --- | --- |
| RS-MIN | A root is at least two moras. | One-mora roots are the scarcest resource in the language and the most collision-prone: there are only 86 legal moras, and the particle and suffix inventory already occupies that space (`do`, `lu`, `ke`, `mi`). Starting roots at two moras keeps the root space and the morpheme space from competing. |
| RS-MAX | A root is at most four moras. | Four moras over 86 legal moras is a root space in the tens of millions, vastly more than 300 words needs. The cap exists to stop the Phase 2 pipeline from escaping a collision by simply making words longer, which would be the easy and wrong answer. |
| RS-FINAL | A root ends in a vowel or in the moraic nasal `n`. | Not a taste decision: it is forced by the suffixes. Every suffix declared in spec/grammar_rules/ is consonant-initial, so a root ending in a vowel or a moraic `n` concatenates legally with every one of them and needs no morphophonemic rule at the join -- which matters because spec/phonology.yaml declares no allophony and no morphophonemics at all. Check 2 proves this by concatenating every permitted final with every declared suffix, and fails loudly if a later phase adds a vowel-initial suffix. |
| RS-RESERVED | A root may not be identical to any particle, suffix or pronoun form declared in spec/grammar_rules/. | A root that equals a particle makes the tokenizer output genuinely ambiguous: in `X do`, `do` would be either the object marker or a noun. Suffix collisions are worse still, since a suffix is glued to its host and a root is not. |

### 5.3 Originality

- **Hard gate**: `not_equal`. LOCKED decision 3 says a form must NOT equal a common Japanese or Tamil particle or case ending. Exact equality against the spellable entries of spec/grammar_rules/_originality.yaml is the gate Phase 1B already applies to every particle and suffix; Phase 1C applies the same gate to roots.
- **New-root gate**: levenshtein absolute of at least 2, measured against the spellable entries of spec/grammar_rules/_originality.yaml, applying to roots coined from v0.1 onward. Retroactive: no.

Exact equality alone lets through a form one segment from its source, which is the real failure mode: a root `wesu` is not `desu`, but nobody would believe it was coined independently. An absolute distance of 2 rules out exactly that -- one substitution, one insertion or one deletion -- while staying achievable.

Known costs: Being non-retroactive, the gate leaves standing 21 existing forms it would have rejected, all at distance 1 and all listed by scripts/check_vocabulary.py so the exemption is visible rather than implied. Eighteen are Phase 1B particles and suffixes, and ten of those are two letters long, where distance 1 from a two-letter source particle is close to unavoidable -- which is the honest reason the gate is scoped to roots and not to morphemes. The other three are demo roots, and two of those are a real problem rather than a technicality: `esu`, the copula, is one edit from Japanese *desu* AND has the same grammatical function, and `wesu` ("see") is one edit from it as well. They are demo words, not vocabulary, so nothing official is affected -- but Phase 2 must not re-derive either, and the Phase 1C report recommends retiring both. More fundamentally, passing this gate proves only that no *listed* form was reused. The list is 61 hand-enumerated items; absence from Japanese and Tamil as a whole, let alone from any third language, is not proven and cannot be by this method.

### 5.4 Semantic fields

| Field | Stratum | Habit | Distinctions it keeps |
| --- | --- | --- | --- |
| kinship | tamil_inspired | separate roots per distinction | elder vs younger sibling, maternal vs paternal uncle, maternal vs paternal aunt |
| natural world | japanese_inspired | compound from a small concrete root set | -- |
| body and basic actions | native | opaque roots | -- |
| numbers | native | opaque roots | -- |
| abstract and technical | loan | adapt from a source language | -- |

### 5.5 Compounds

| Id | Pattern | Head | Written | What it is |
| --- | --- | --- | --- | --- |
| CP-NN | `NOUN NOUN` | final | separate words | A modifier noun followed by a head noun, lexicalized as one dictionary entry when the meaning is not fully predictable from the parts. |
| CP-NNN | `NOUN NOUN NOUN` | final | separate words | A three-noun chain, strictly head-final: each noun modifies everything to its right. |
| CP-REDUP | `WORD WORD (identical)` | none | separate words | Full reduplication of an adverb for intensity: the word repeated, as two words. |

### 5.6 Loanword adaptation

Source sounds that have a Tanese equivalent:

| Source | Becomes | Why |
| --- | --- | --- |
| `f` | `p` | Both labial obstruents; /p/ is the only labial voiceless consonant in the inventory, so the place is preserved and only the manner changes. |
| `v` | `w` | Labial and voiced, like /v/. Mapping to /b/ was the alternative; /w/ keeps the continuant manner, and /b/ is kept free so that source /b/ and source /v/ do not collapse together. |
| `z` | `s` | Same place and manner; only voicing is lost, and /s/ has no voiced counterpart. |
| `h` | (deleted) | Deleted, not substituted. There is no /h/ phoneme (spec/phonology.yaml: its absence is what lets `h` act as a pure retroflex marker), and every candidate substitute -- /k/, a glide, a vowel -- is further from /h/ than silence is. |
| `ng` | `n` | The velar nasal becomes the moraic nasal, which is the only coda Tanese has. Its place assimilation is not represented because the romanization writes one nasal symbol. |
| `t_retro` | `th` | A retroflex voiceless plosive in the source maps to the Tanese retroflex voiceless plosive. The inventory has a retroflex series precisely so that source words with retroflexes do not have to lose the contrast. |
| `d_retro` | `dh` | As `t_retro`, voiced. |
| `n_retro` | `nh` | As `t_retro`, nasal. |
| `p` | `p` | Identical. |
| `b` | `b` | Identical. |
| `t` | `t` | Identical. |
| `d` | `d` | Identical. |
| `k` | `k` | Identical. |
| `g` | `g` | Identical. |
| `s` | `s` | Identical. |
| `m` | `m` | Identical. |
| `n` | `n` | Identical. |
| `l` | `l` | Identical. |
| `r` | `r` | Every source rhotic -- trill, tap, approximant -- collapses onto the Tanese tap, which is the only rhotic in the inventory. |
| `j` | `y` | The palatal glide, spelled `y` in the romanization. |
| `w` | `w` | Identical. |
| `a` | `a` | Identical. |
| `i` | `i` | Identical. |
| `u` | `u` | Identical. |
| `e` | `e` | Identical. |
| `o` | `o` | Identical. |
| `a:` | `aa` | Source length maps to Tanese length, which is contrastive (LOCKED decision 9) and written by doubling the vowel. |
| `i:` | `ii` | As `a:`. |
| `u:` | `uu` | As `a:`. |
| `e:` | `ee` | As `a:`. |
| `o:` | `oo` | As `a:`. |
| `ae` | `a` | Low front unrounded, closest to Tanese /a/, the only low vowel. The front quality is lost; no vowel in the inventory keeps it. |
| `uh` | `a` | Low-central in most source accents, so /a/ is nearest. |
| `schwa` | `u` | Mapped to the same vowel as the default epenthesis below, so that an unstressed source vowel and an inserted vowel are spelled alike instead of inventing a contrast Tanese does not hear. |
| `I` | `i` | Near-high front; /i/ is nearest. |
| `U` | `u` | Near-high back; /u/ is nearest. |
| `E` | `e` | Mid front; /e/ is nearest. |
| `O` | `o` | Mid back; /o/ is nearest. |

Source sounds with **no** mapping. These are rejected by name, never approximated:

| Source | Code | Why it is left undecided |
| --- | --- | --- |
| `th` | VL-UNMAPPED | The voiceless dental fricative is equally close to /t/, /s/ and /th/. Source orthography does not decide it either, since `th` already spells the Tanese retroflex. |
| `dh_fric` | VL-UNMAPPED | As the voiceless dental fricative, between /d/, /dh/ and /s/. |
| `sh` | VL-UNMAPPED | The postalveolar fricative sits between /s/ and a /sy/ sequence. Japanese chooses the palatalised sequence and Tamil chooses a separate letter; Tanese has neither option, and /s/ alone loses a contrast that is highly audible. |
| `zh` | VL-UNMAPPED | As the postalveolar fricative, with voicing lost on top. |
| `ch` | VL-UNMAPPED | The affricate could be /t/, /s/, or a /ti/ sequence. All three are used by real borrowing traditions, which is exactly why Tanese will not pick one silently. |
| `j_aff` | VL-UNMAPPED | As the voiceless affricate, voiced. |
| `x` | VL-UNMAPPED | The velar fricative is between /k/ and deletion, and deletion is already spoken for by /h/. Ambiguous, so rejected. |
| `ny` | VL-UNMAPPED | The palatal nasal is a /ny/ sequence or a plain /n/, and the romanization deliberately forbids writing `ny` for a single segment (constraint PT-010), so the sequence reading cannot be spelled as one consonant. |
| `y_vowel` | VL-UNMAPPED | Front rounded vowels have no nearest fit: /i/ keeps the frontness and /u/ the rounding, and there is no basis for preferring either. |
| `oe` | VL-UNMAPPED | As the high front rounded vowel, mid. |
| `ai` | VL-UNMAPPED | Diphthongs are rejected as single segments on purpose. A diphthong is two Tanese moras, so the caller must say which two: supply `a` and `i` as separate segments and the hiatus repair below will handle the join deterministically. |
| `au` | VL-UNMAPPED | As the other diphthongs -- supply the two vowels separately. |
| `ei` | VL-UNMAPPED | As the other diphthongs. |
| `ou` | VL-UNMAPPED | As the other diphthongs. |

The repair steps, applied in this order:

| Step | Id | What it does |
| --- | --- | --- |
| 1 | LR-1-SUBSTITUTE | Replace every source segment by its `loan_substitutions` entry. A segment listed under `unmapped` is rejected with its code and name; a segment in neither table is rejected as unknown. |
| 2 | LR-2-NASAL | A nasal consonant that is word-final, or that stands immediately before another consonant, becomes the moraic nasal `n`. A word-initial nasal is never converted. |
| 3 | LR-3-GEMINATE | Two identical adjacent consonants followed by a vowel become a geminate if the consonant is `geminable` in spec/phonology.yaml. If it is not geminable, the pair is left for the later steps: a nasal pair is resolved by step 2, and any other pair by epenthesis. |
| 4 | LR-4-HIATUS | In a run of adjacent vowels: identical vowels collapse into one long vowel, and a run longer than two is truncated to two. Two different vowels are separated by a glide -- `y` after a front vowel (i, e), `w` after a back vowel (u, o), and `y` after `a`. If the chosen glide would form a mora listed in the `gaps` block of spec/phonology.yaml (`yi`, `wu`), the other glide is used instead. |
| 5 | LR-5-EPENTHESIS | Any consonant not followed by a vowel -- in a cluster, or word-final -- takes an inserted vowel: `a` after a retroflex consonant (th, dh, nh), otherwise `u`. The moraic nasal from step 2 and the first half of a geminate from step 3 are already licensed and are skipped. If the inserted vowel would form a gap mora, `i` is used instead. |
| 6 | LR-6-SPELL | Write the result in the canonical romanization, inserting the apostrophe required by constraint PT-010 when a moraic nasal precedes a vowel, `y` or `w`. |
| 7 | LR-7-ASSERT | Validate the spelled result with the phonotactic validator. If any constraint is still broken, reject the word with code VL-RESIDUE and the constraint id, rather than returning it. |

Worked examples, with the output each is required to produce:

| Source | Segments | Tanese | Steps that fired |
| --- | --- | --- | --- |
| film | `f` `i` `l` `m` | **pilun** | substitute, nasal, epenthesis |
| strike | `s` `t` `r` `a` `i` `k` | **suturawiku** | substitute, hiatus, epenthesis |
| bank | `b` `a` `n` `k` | **banku** | substitute, nasal, epenthesis |
| koːʈ (coat) | `k` `o` `t_retro` | **kotha** | substitute, epenthesis |
| paʈʈu (silk) | `p` `a` `t_retro` `t_retro` `u` | **paththu** | substitute, geminate |
| kiosk | `k` `i` `o` `s` `k` | **kiyosuku** | substitute, hiatus, epenthesis |
| anna (a source name) | `a` `n` `n` `a` | **anna** | substitute, nasal |
| karra (a source name) | `k` `a` `r` `r` `a` | **karura** | substitute, epenthesis |
| kaːr (car) | `k` `a:` `r` | **kaaru** | substitute, epenthesis |

Inputs that must be refused:

| Source | Code | Offending sound | Why |
| --- | --- | --- | --- |
| θɪŋ (thing) | VL-UNMAPPED | `th` | The dental fricative has no mapping; see the `unmapped` block. |
| tʃɛr (chair) | VL-UNMAPPED | `ch` | The affricate has no mapping. |
| ʃɔp (shop) | VL-UNMAPPED | `sh` | The postalveolar fricative has no mapping. |
| taɪm (time), given as a diphthong | VL-UNMAPPED | `ai` | Diphthongs must be supplied as two vowel segments so the hiatus repair can decide the join. Given as one segment, the adapter refuses rather than guessing the split. |
| an invented sound | VL-UNKNOWN | `q` | Not in `loan_substitutions` and not in `unmapped`. An unlisted sound is rejected as unknown, so adding a source sound to the language is always a deliberate edit to this file. |

### 5.7 How a word becomes official

Locked decision 14, as ordered stages. The LLM may act at the first stage and
nowhere else; the last stage cannot be automated.

| Id | Stage | Automated | LLM may act | What happens |
| --- | --- | --- | --- | --- |
| PL-0 | candidate generation | yes | yes | Produce candidate forms for a concept. The only stage an LLM may touch, and even here it proposes forms and nothing else. |
| PL-1 | phonotactic check | yes | no | Reject any candidate the Phase 1A validator rejects, keeping the constraint id. |
| PL-2 | morphology check | yes | no | Reject a candidate that breaks a root shape above, equals a declared morpheme (RS-RESERVED), or fails to combine with every suffix of its word class. |
| PL-3 | collision check | yes | no | Exact, phonetic, orthographic and semantic collision against the existing lexicon, as the Phase 2 done-criteria require. Semantic collision is the one sub-check that needs meaning, so it is where embeddings are used. |
| PL-4 | rank | yes | no | Order the survivors so a human reviews the best first. Ranking inputs include distance from the nearest existing word, mora count, and distance from the originality list. |
| PL-5 | human approve | no | no | A human promotes a candidate to `official`. Nothing else can, and this stage cannot be automated away. |

### 5.8 The vocabulary rules

**compound**

*VR-COMP-001 — a compound entry is more than one word*

A compound lexical entry is written as two or more separate words in modifier-head order. The parts are never fused and take no linking particle.

- Pattern: `WORD WORD (modifier head), separate words`
- Why: GR-NOUN-004 already decided this for the syntax, and declared the fused spelling invalid; Phase 1C does not reopen it. The reason it was right is that fusion would create a seam, and a seam raises morphophonemic questions -- hiatus at the join, sandhi, voicing -- that spec/phonology.yaml deliberately has no answers to. With nothing glued, there is no seam and no question.
- Considered and rejected: Fuse compounds into single words, as both source languages do, and add a seam rule (a glide for hiatus, as the loanword repair uses). Rejected and NOT proposed: it would amend an official rule to buy a shorter spelling, and the glide repair exists for loans because a source word arrives in one piece, which a compound does not.
- Known costs: A lexicalized compound is spelled exactly like the ordinary noun sequence it came from, so `sedha nami` is both the entry "restaurant" and the phrase "food house". Only the dictionary separates them, and the Phase 4 tokenizer will not attempt to.
- Inspiration (none): Tamil and Japanese both compound productively and both fuse the parts, with sandhi or with rendaku. How Tanese differs: The productivity is kept, the fusion is dropped, because Tanese has no morphophonemics to govern a join.

|  | Form | Note |
| --- | --- | --- |
| yes | `sedha nami` | restaurant (food house) |
| yes | `kalu thunga` | a rocky mountain, as a lexical entry rather than a description |
| no | `sedhanami` | The two nouns are fused into one word. GR-ORD-001 glues only suffixes, and GR-NOUN-004 lists exactly this spelling as invalid. It is a legal Tanese word; it is not a legal compound entry. |
| no | `sedha lu nami` | A genitive particle between the parts makes it a possessive phrase ("the food's house"), not a compound. A compound takes no linking particle (GR-NOUN-004). |

*VR-COMP-002 — lexicalize only what the parts do not predict*

A noun sequence becomes a dictionary entry only when its meaning is not predictable from its parts. A fully transparent sequence stays syntax and gets no entry.

- Pattern: `entry iff meaning not derivable from parts`
- Why: Otherwise the lexicon is unbounded: every grammatical noun pair would be an entry, the 300-word target would be met by listing transparent phrases, and the dictionary would stop carrying information. The test is whether a reader who knows both parts still needs to be told the meaning.
- Known costs: "Not predictable" is a judgement, and the margins are wide: `kalu nami` ("stone house") might be an ordinary description or a specific building type. Phase 2 has to make these calls one at a time and will not always be consistent.
- Inspiration (none): The distinction between a compound and a phrase is a standard lexicographic problem in every language. How Tanese differs: Tanese takes the standard test (semantic non-compositionality) and nothing language-specific, since neither source language resolves it any better.

|  | Form | Note |
| --- | --- | --- |
| yes | `bunko nami` | library (book house) -- a kind of building, not merely a house with books in it |
| yes | `sedha nami` | restaurant (food house) -- a business, which "food" and "house" do not give you |
| no | `kalu kalu` | A reduplication of a noun entered as a compound. Reduplication is intensive and applies to adverbs (VR-COMP-003); a doubled noun predicts nothing and means nothing new. |
| no | `thora weli` | "tree water" entered as a compound while meaning exactly tree water. Fully transparent, so it is a noun sequence the syntax already produces and needs no entry. |

*VR-COMP-003 — reduplication for intensity*

An adverb repeated as two identical words is an intensive: `thuri thuri` is "very quickly".

- Pattern: `ADVERB ADVERB (identical)`
- Why: It adds a productive meaning at zero cost -- no root, no morpheme, no new spelling convention -- which is exactly what a 300-word lexicon needs. The Tamil-like habit is structural, so borrowing it brings no Tamil form with it.
- Considered and rejected: An intensifying suffix. Rejected: it would be a new morpheme, it would need a slot in the noun or adverb morphology that does not exist, and the Phase 1B contradiction checker would have to arbitrate it against the verb slots.
- Known costs: Formally indistinguishable from an accidental repetition, which is a typo class the Phase 3 invalid corpus will deliberately contain. Nothing but the dictionary says `thuri thuri` is intensive and not a stutter, and the Phase 4 grammar checker will therefore not flag a doubled word.
- Inspiration (tamil): Tamil full reduplication for intensity and distribution. How Tanese differs: The intensive reading is kept; the distributive reading is not, the words are Tanese, and the two-word spelling follows GR-ORD-001 rather than either source language.

|  | Form | Note |
| --- | --- | --- |
| yes | `thuri thuri` | very quickly |
| yes | `thuri thuri ano dhen sippadho` | I wrote very quickly. |
| no | `thurithuri` | Fused into one word. Like every other compound, a reduplication is two words (GR-ORD-001 glues only suffixes). The fused form is a legal Tanese word but not an intensive. |
| no | `thuri thuri thuri` | Tripled. The intensive is full reduplication, which is exactly two copies; there is no third degree for a third copy to express. |

**loan**

*VR-LOAN-001 — an unmapped sound is rejected, never approximated*

A source sound with no entry in `loan_substitutions` is rejected by name: with code VL-UNMAPPED if it is listed in `unmapped`, and VL-UNKNOWN if it is in neither table.

- Pattern: `source sound not in table -> rejection naming the sound`
- Why: The sounds in `unmapped` each have at least two equally defensible substitutes, and silently picking one would make the adapter non-deterministic in the sense that matters: a second person adapting the same word by hand would get a different answer. Rejecting by name also makes the gap in the table visible and fixable, instead of burying it in output nobody can audit.
- Considered and rejected: Approximate everything, so adaptation never fails. Rejected: it would give the postalveolar fricative an arbitrary rendering, and that arbitrary choice would then be frozen into every loan containing it.
- Known costs: It makes the adapter refuse common English words -- `thing`, `chair`, `shop` -- so Phase 2 cannot borrow them at all until this file is extended with a decision. That is intended, but it is a real limitation and not merely a formality.
- Inspiration (japanese): Japanese has a fixed, conventional substitution table for foreign sounds, applied mechanically. How Tanese differs: The mechanical table is kept and the completeness is not: where Japanese convention has settled on a substitute, Tanese declares the choice undecided and refuses, rather than inheriting another language's arbitration.

|  | Form | Note |
| --- | --- | --- |
| yes | `banku` | bank -- every sound in /bank/ is in the table, so adaptation succeeds |
| yes | `kiyosuku` | kiosk -- likewise, with a hiatus repair on the way |
| no | `sopu` | "shop" adapted by quietly turning the postalveolar fricative into `s`. The sound is listed as unmapped, so the correct result is a VL-UNMAPPED rejection naming it, not a plausible-looking word. |
| no | `tini` | "thing" adapted by guessing `t` for the dental fricative and dropping the final nasal. Two undeclared decisions in one form. |

*VR-LOAN-002 — epenthesis repairs clusters and stranded finals*

A consonant not followed by a vowel takes an inserted vowel: `a` after a retroflex (th, dh, nh), otherwise `u`; and `i` instead if the default would make one of the gap moras `yi` or `wu`.

- Pattern: `C not followed by V -> C + epenthetic V`
- Why: LOCKED decision 10 allows no clusters and no word-final consonant but the moraic nasal, so every consonant a source word strands needs a vowel. `u` is the default because it is the least perceptually prominent vowel in the inventory, so the syllable it adds intrudes least. The retroflex exception is phonetic, not stylistic: a retroflex closure into a high back vowel is an unstable transition, and `a` leaves the tongue where the retroflex puts it.
- Considered and rejected: One epenthetic vowel everywhere. Simpler to state and to test, and rejected because the retroflex series is the feature Tanese most needs to stay pronounceable. Vowel harmony (copy the nearest vowel) was also rejected: it interacts with the hiatus repair, so the output would depend on repair order.
- Known costs: Epenthesis adds moras, so a long source word can clear every phonotactic constraint and still exceed the four-mora root cap -- `suturawiku` for "strike" is five moras, a legal word that cannot be a root. Whether to truncate or refuse such loans is left unresolved.
- Inspiration (japanese): Japanese breaks foreign clusters with epenthetic /u/. How Tanese differs: The default vowel coincides because the phonetic argument is the same one; the retroflex exception has no Japanese counterpart, Japanese having no retroflex series, and the gap fallback follows from Tanese gaps that Japanese does not share.

|  | Form | Note |
| --- | --- | --- |
| yes | `pilun` | film -- the stranded l takes u, and the final nasal becomes the moraic n |
| yes | `kotha` | coat (Indic source) -- the final retroflex takes a, not u |
| no | `pilm` | "film" with the cluster left unrepaired. Not a legal Tanese word: `l` is followed by a consonant (constraint PT-003) and the word ends in `m` (PT-004). |
| no | `kothu` | "coat" with the default `u` after the final retroflex instead of the declared `a`. A legal word, and the wrong output -- which is why this rule is tested against the expected value in `adaptation_examples` rather than against legality alone. |

*VR-LOAN-003 — hiatus is broken by a glide*

Two different adjacent vowels are separated by a glide chosen by the preceding vowel -- `y` after a front vowel or after `a`, `w` after a back vowel -- and by the other glide if the first would form the gap mora `yi` or `wu`. Identical adjacent vowels become one long vowel instead.

- Pattern: `V1 V2 (different) -> V1 GLIDE V2`
- Why: Constraint PT-008 forbids hiatus, and its own `problems` field committed Phase 1C to supplying this repair. The glide follows the preceding vowel because that is what makes the transition continuous: a front vowel glides out through /j/. The gap fallback is not an extra rule but a consequence of `yi` and `wu` not existing, so `a` + `i` cannot become `ayi` and becomes `awi`.
- Considered and rejected: Choose the glide by the following vowel. Rejected: `i` and `u` are the commonest second members of a source diphthong, so that rule would hit the gaps far more often than this one does.
- Known costs: A word with hiatus comes out one consonant longer than its source, which pushes it toward the four-mora root cap. Truncating a run of three or more identical vowels to two also loses information outright.
- Inspiration (none): Japanese permits hiatus freely and so needs no repair; Tamil has glide insertion in some sandhi contexts. How Tanese differs: The repair exists because Tanese forbids hiatus and Japanese does not, so the problem is Tanese's own. The glide choice is derived from the Tanese gap inventory, which neither source language shares.

|  | Form | Note |
| --- | --- | --- |
| yes | `kiyosuku` | kiosk -- i + o is broken by y, the default glide after a front vowel |
| yes | `suturawiku` | strike -- a + i would give the gap mora `yi` with the default glide, so `w` is used and the result is `awi` |
| no | `kiosuku` | "kiosk" with the hiatus left in place. Not a legal Tanese word: `o` has no onset and is not word-initial (constraint PT-008). |
| no | `suturayiku` | "strike" with the default glide applied blindly, producing the mora `yi`, which the phonology declares a gap (constraint PT-012). This is the case the fallback exists for. |

*VR-LOAN-004 — nasals and identical pairs before epenthesis*

A nasal that is word-final or stands before a consonant becomes the moraic nasal, never word-initially; and an identical adjacent consonant pair followed by a vowel becomes a geminate if the consonant is geminable.

- Pattern: `N before C -> moraic n ; C C (identical, geminable) -> geminate`
- Why: Both repairs exist to avoid inserting a vowel where Tanese already has a legal structure for the shape. The moraic nasal is the one coda the language has, so a source coda nasal survives as a coda; a geminate is legal, so a source double consonant survives as a geminate. Doing both before epenthesis is what makes `bank` come out as `banku` rather than `banuku`, and `pattu` as `paththu` rather than `pathuthu`.
- Known costs: The geminate repair depends on the segment list being sounds rather than spelling, since source orthography doubles consonants that are not doubled in speech. The restriction to geminable consonants is constraint PT-007, which is why a nasal pair falls through to the moraic-nasal repair and a rhotic pair falls through to epenthesis.
- Inspiration (japanese): Japanese uses its moraic nasal and its geminate for exactly these two source shapes. How Tanese differs: The strategy is the same because the phonotactics are the same shape; the geminable set is Tanese's own (ten of sixteen consonants, by the phonetic criterion in spec/phonology.yaml), and Japanese does not exclude nasals from gemination as Tanese does.

|  | Form | Note |
| --- | --- | --- |
| yes | `paththu` | a source form with a doubled retroflex: the pair becomes a geminate, so no vowel is inserted |
| yes | `anna` | a source form with a doubled n: `n` is not geminable, so the first becomes the moraic nasal and still no vowel is inserted |
| no | `banuku` | "bank" with the coda nasal broken up by epenthesis instead of becoming the moraic nasal. A legal word, one mora too long, and not the declared output. |
| no | `panhnhu` | A doubled retroflex nasal treated as a geminate. `nh` may not be geminated (constraint PT-007), so this is not a legal Tanese word -- the pair must fall through to the moraic-nasal repair instead. |

**originality**

*VR-ORIG-001 — no form may equal a listed source form*

No root, and no part of a compound entry, may be identical to any spellable entry in spec/grammar_rules/_originality.yaml.

- Pattern: `form not in _originality.yaml`
- Why: LOCKED decision 3 in its own words: a form must NOT equal a common Japanese or Tamil particle or case ending. Phase 1B applies this gate to every particle and suffix; Phase 1C applies the identical gate to the root space, so the two halves of the lexicon are held to one standard.
- Known costs: The list holds the 61 forms that could be enumerated by hand. Passing this gate proves that no listed form was reused and nothing more: it is not evidence of absence from Japanese or Tamil, let alone from any third language.
- Inspiration (none): none How Tanese differs: The machine-readable half of LOCKED decision 3; no source feature involved.

|  | Form | Note |
| --- | --- | --- |
| yes | `dhoka` | tomorrow -- at edit distance 3 or more from every listed source form |
| yes | `thaaben` | an illustrative maximal root, at distance 2 from the nearest listed form (Tamil *thaan*), so it clears both this gate and VR-ORIG-002 |
| no | `made` | Equals the Japanese particle *made* ("until"), which is on the banned list. It is a legal Tanese word, which is exactly why the gate has to be a list lookup and not a phonotactic test. |
| no | `yori` | Equals the Japanese comparative particle *yori*, also on the list. |

*VR-ORIG-002 — new roots keep an edit distance of two*

A root coined from v0.1 onward must be at least edit distance 2 (absolute Levenshtein) from every spellable entry in spec/grammar_rules/_originality.yaml. The gate is not retroactive.

- Pattern: `min edit distance to banned list >= 2`
- Why: Exact equality alone admits a form one segment from its source, which is the real failure mode rather than a theoretical one: a root `wesu` is not `desu`, but no reader would accept that it was coined independently. Distance 2 excludes precisely the one-edit cases -- one substitution, one insertion, one deletion -- and is achievable for a coined root, which a stricter gate is not.
- Considered and rejected: A normalised edit distance floor of 0.5, which was the original proposal. Rejected after measuring it against the existing spec: it fails twelve already-official Phase 1B morphemes, because a two-letter morpheme cannot be relatively far from a two-letter particle. The measurement is in the originality block above.
- Known costs: Not retroactive, so it leaves standing 21 existing forms at distance 1, which scripts/check_vocabulary.py prints in full. Eighteen are Phase 1B morphemes, where the measure means little because a two-letter suffix cannot be far from a two-letter particle; that is why this gate is scoped to roots. The remaining three are demo roots, and two are a genuine problem: `esu`, the copula, is one edit from Japanese *desu* and shares its grammatical function, and `wesu` is one edit from it as well. Both are experimental demo words rather than vocabulary, but Phase 2 must not re-derive either, and the Phase 1C report recommends retiring them.
- Inspiration (none): none How Tanese differs: An internal originality gate; no source feature involved.

|  | Form | Note |
| --- | --- | --- |
| yes | `nhodi` | an illustrative minimal root, distance 3 from the nearest listed form |
| yes | `welugan` | an illustrative n-final root, distance 4 from the nearest listed form |
| no | `wesu` | Distance 1 from Japanese *desu*. It is an existing demo word, which is why the gate is declared non-retroactive -- and why this rule names it rather than hiding it. |
| no | `mado` | Distance 1 from the Japanese particle *made*: one deletion. It clears the exact equality gate in VR-ORIG-001 and is exactly the case this rule exists to stop. |

**pipeline**

*VR-PIPE-001 — six ordered stages, LLM only at the first*

Every official word passes stages PL-0 to PL-5 in order. The LLM may act only at PL-0, candidate generation.

- Pattern: `PL-0 -> PL-1 -> PL-2 -> PL-3 -> PL-4 -> PL-5`
- Why: LOCKED decision 14 names the pipeline and says the LLM may only propose candidates. Order matters for a practical reason as well: each stage is more expensive than the one before, so the cheap deterministic checks run first and the collision detector only ever sees candidates that are already legal words of a legal shape.
- Known costs: A strict order means a candidate rejected at PL-1 is never seen by the semantic checks, so the pipeline cannot report "this would have been a good word if it were legal". That information would be useful to a human reviewer and is simply lost.
- Inspiration (none): none How Tanese differs: The machine-readable form of LOCKED decision 14, with the stages named so an implementation cannot quietly reorder or drop one.

|  | Form | Note |
| --- | --- | --- |
| yes | `nhodi` | an illustrative candidate: legal (PL-1), a legal root shape (PL-2), distinct from every declared morpheme and demo root (PL-3), and still experimental because PL-5 has not happened |
| yes | `welugan` | another illustrative candidate at the same stage -- generated, checked, ranked, and deliberately not approved |
| no | `do` | A candidate that would reach PL-3 without passing PL-2: it equals a declared particle and is one mora. Running collision detection on it would waste the expensive stage on a candidate the cheap one rejects. |
| no | `desu` | A candidate an LLM proposed and that was taken as official without PL-1 to PL-5. It is a banned source form, which is exactly what the stages between proposal and approval exist to catch. |

*VR-PIPE-002 — nothing is official without human approval*

A word is `experimental` until a human approves it at PL-5, and official and experimental words live in separate files.

- Pattern: `candidate -> experimental -> (human) -> official`
- Why: LOCKED decisions 14 and 15. Rules define Tanese and the LLM never changes them, so the moment a form becomes a rule is the moment that must stay human. Separate files make the distinction structural rather than a field somebody can flip by accident.
- Known costs: Approval is a bottleneck by design, so the lexicon grows only as fast as one person can review it. That is the main reason the Phase 2 target is 300 words and not 1000.
- Inspiration (none): none How Tanese differs: The machine-readable form of LOCKED decisions 14 and 15.

|  | Form | Note |
| --- | --- | --- |
| yes | `nhodi` | an illustrative form in this file: experimental, and forbidden by check 13 from appearing in data/vocabulary/ at all |
| yes | `thaaben` | likewise experimental -- Phase 2 must re-derive any of these through the pipeline, which may reject them |
| no | `nhodi` | The same form entered in data/vocabulary/ as official, which is what check 13 forbids. An illustration in the spec is not a word of the language, and copying it across would skip every pipeline stage. |
| no | `pilun` | An adapted loan from `adaptation_examples` entered as official. The adapter output demonstrates the adapter; it has had no collision check and no human approval. |

**root shape**

*VR-ROOT-001 — a root is two to four moras*

Every root is at least two and at most four moras long.

- Pattern: `2 <= mora count <= 4`
- Why: See RS-MIN and RS-MAX. The floor keeps roots out of the one-mora space the particles and suffixes already occupy; the ceiling stops the Phase 2 pipeline from escaping a collision by lengthening a word instead of rethinking it.
- Known costs: Measured in moras, not letters, so a root with a long vowel or a geminate reaches the ceiling with fewer consonants and vowels than one without. `thaaben` and `welugan` are both maximal, and only one of them looks long.
- Inspiration (japanese): Japanese native roots are overwhelmingly two moras, and the mora is the unit length is counted in. How Tanese differs: Counting in moras is kept because Tanese is mora-based (LOCKED decision 10); the range is wider than Japanese native roots and is set by the collision argument above rather than by any source language.

|  | Form | Note |
| --- | --- | --- |
| yes | `nami` | house -- two syllables, two moras: the minimum |
| yes | `thaaben` | an illustrative maximal root: four moras (tha + length + be + n), showing that the cap is counted in moras and not in letters |
| no | `do` | One mora. Below RS-MIN, and it also equals the object particle `do`, which VR-ROOT-003 forbids outright. |
| no | `welugaanen` | Six moras, over the RS-MAX ceiling. It is a perfectly legal Tanese word -- the cap is a vocabulary rule, not a phonotactic one -- which is why only this check can reject it. |

*VR-ROOT-002 — a root ends in a vowel or the moraic nasal*

A root ends either in a vowel or in the moraic nasal `n`, and in nothing else.

- Pattern: `ROOT -> ... (V | n)`
- Why: Forced by the suffix inventory, not chosen: every suffix in spec/grammar_rules/ is consonant-initial, so these two finals concatenate legally with all fourteen of them and no morphophonemic rule is needed at the join. That matters because spec/phonology.yaml declares no allophony and no morphophonemics at all -- there is no machinery to repair a bad join, so no join may be bad.
- Considered and rejected: Allow any phonotactically legal final and add a linking rule for the awkward cases. Rejected: the linking rule would be the first morphophonemics in the language, and LOCKED decision 2 (suffixing only, agglutinative) is at its most defensible when suffixation is literal concatenation.
- Known costs: This rule is coupled to spec/grammar_rules/: a future vowel-initial suffix would break it silently. Check 2 exists for exactly that reason -- it concatenates every permitted final with every declared suffix on every run.
- Inspiration (none): Japanese words end in a vowel or the moraic nasal too, for the same phonotactic reason. How Tanese differs: Arrived at independently from LOCKED decision 10, which permits exactly those two word-finals. The convergence is a consequence of both languages being mora-based, not a borrowing.

|  | Form | Note |
| --- | --- | --- |
| yes | `welugan` | an illustrative root ending in the moraic nasal |
| yes | `mothu` | cat -- a root ending in a vowel, the commoner case |
| no | `welugat` | Ends in `t`. A word may end only in a vowel or the moraic nasal (constraint PT-004), so this is not a legal Tanese word at all. |
| no | `welugam` | Ends in `m`. The moraic nasal is written `n` and is the only nasal that may close a word, so `m` here is an illegal final rather than an alternative spelling. |

*VR-ROOT-003 — a root may not equal a declared morpheme*

A root may not be identical to any particle, suffix or pronoun form declared in spec/grammar_rules/.

- Pattern: `ROOT not in declared particle/suffix/pronoun forms`
- Why: A root that equals a particle makes tokenizer output genuinely ambiguous: in `X do`, `do` is either the object marker or a noun, and GR-ORD-001 gives no way to tell. A root that equals a suffix is worse, since a suffix is glued to its host and a root is not.
- Known costs: Whole forms only. A root that merely ends in a suffix form -- a hypothetical `kanen` ending in `-nen` -- passes this rule and is still confusable, and only the Phase 4 morphological analyzer can resolve it. Banning every root that ends in any of the fourteen suffix forms would remove a large share of the root space, so it is recorded as an unresolved decision instead.
- Inspiration (none): none How Tanese differs: An internal consistency requirement between the Phase 1B morpheme inventory and the Phase 1C root space; neither source language is involved.

|  | Form | Note |
| --- | --- | --- |
| yes | `dhimi` | river -- resembles no declared morpheme |
| yes | `kalu` | stone -- legal even though the genitive particle `lu` is a substring of it, because the rule compares whole forms |
| no | `thon` | Equals the prohibitive particle `thon` (GR-NEG-003). As a noun it would make every negative command ambiguous between a prohibition and a noun. |
| no | `nen` | Equals the plural suffix `-nen` (GR-NOUN-001). A root spelled like a suffix is the worst case of all: the segmenter cannot tell whether it is a word or the end of one. |

*VR-ROOT-004 — a root is invariant*

A root never changes shape. There are no stem alternations, no irregular forms and no consonant or vowel changes when a suffix attaches.

- Pattern: `ROOT + SUFFIX -> concatenation, no change to ROOT`
- Why: LOCKED decision 2 makes the morphology agglutinative and suffixing only, and GR-VERB rules already declare the verb root invariant. Phase 1C states the same thing as a property of the lexicon: a dictionary entry is one form, so nothing else has to be stored, learned or predicted.
- Considered and rejected: Allow a small irregular class for the most frequent words, as every natural language has. Rejected: irregularity has to be memorised rather than derived, which costs the learner, the morphological analyzer and the dictionary format all at once, and buys nothing a v0.1 needs.
- Known costs: Perfectly regular morphology is the clearest sign that a language is constructed. This is a cost paid deliberately, and it cannot be undone later without rewriting every entry.
- Inspiration (tamil): Tamil is agglutinative but has substantial stem-level sandhi and several verb classes. How Tanese differs: The agglutination is kept; the stem classes and the sandhi are dropped entirely.

|  | Form | Note |
| --- | --- | --- |
| yes | `manduke` | eats -- the point is the join: `mandu` is identical to its citation form before the suffix, with nothing changed on either side |
| yes | `welugannen` | an illustrative n-final root plus the plural suffix: the root keeps its final moraic n and the suffix keeps its shape |
| no | `mandoke` | The root vowel has changed from `mandu` to `mando` before the suffix. That is a stem alternation, which the morphology does not have. |
| no | `mannuke` | The root consonant has geminated at the join. Gemination is legal Tanese phonology, so this is a legal word -- it is simply not a form of `mandu`, because roots do not change. |

**semantics**

*VR-SEM-001 — the semantic field selects the coining habit*

Each semantic field declares which stratum coins its words, so a concept's field determines whether it gets a new root, a compound, or a loan.

- Pattern: `field -> stratum -> coining habit`
- Why: Without this, the two inspired strata would be labels with no consequence: nothing would say when to coin a root and when to compound. Assigning habits by field also keeps the two habits from competing over the same word, which is the problem the `japanese_inspired` stratum records.
- Known costs: The field boundaries are judgement calls, and a concept can sit in two fields -- a body part used as a terrain metaphor, say. The declared field then decides the habit for a word that could reasonably have gone either way.
- Inspiration (none): Japanese lexical strata correlate strongly with semantic domain (native words for everyday things, Sino-Japanese for technical ones). How Tanese differs: The correlation is made explicit and prescriptive rather than left as a historical accident, and the fields and strata are Tanese's own.

|  | Form | Note |
| --- | --- | --- |
| yes | `thunga dhimi` | mountain river -- natural_world, so the japanese_inspired habit applies and the concept is compounded from existing roots |
| yes | `banku` | bank -- abstract_and_technical, so the loan stratum applies and the word is adapted rather than coined |
| no | `banku` | The same adapted loan filed under natural_world. Nothing in that field may be a loan, so the entry breaks the field-to-stratum mapping and quietly inflates the loan quota. |
| no | `welugan` | An illustrative coined root entered for a natural_world concept that the existing roots already compound. The field's habit is to compound, so coining a new root here spends the root budget the habit exists to protect. |

*VR-SEM-002 — kinship is finely divided*

The kinship field distinguishes elder from younger sibling, and maternal from paternal uncle and aunt, with a separate root for each.

- Pattern: `one root per kinship distinction, not one root plus a modifier`
- Why: The concrete case of the tamil_inspired habit, and the reason that stratum exists. These distinctions are socially real wherever extended families are, and a language that forces one word to cover both sides of a family has lost information its speakers have. Every root filling the distinction is coined natively, so the granularity is borrowed and no Tamil form is.
- Considered and rejected: English-style kinship: one word for uncle, one for sibling, with a modifier when the distinction matters. Rejected: it would make the tamil_inspired stratum empty of consequence, and the modifier would be needed often enough to cost more than the roots.
- Known costs: Six kinship roots where English needs two, which is about two percent of a 300-word lexicon spent on one field. It also makes translation into English lossy in the opposite direction from usual: the Tanese word says more than its English gloss.
- Inspiration (tamil): Tamil kinship terminology, which distinguishes relative age among siblings and the maternal from the paternal line. How Tanese differs: The distinctions are kept exactly; every form is coined natively, and the Tamil terms themselves are banned by VR-ORIG-001 like any other source form.

|  | Form | Note |
| --- | --- | --- |
| yes | `nanthe` | friend -- a natively coined social-relation root, standing in for the kinship roots Phase 2 will coin, since the demo wordlist has none |
| yes | `nanthenen` | friends -- the field's roots take ordinary morphology, with the plural suffix attached like any other; nothing about kinship is morphologically special |
| no | `nanthe lu nanthe` | A kinship distinction built as a possessive phrase instead of a root. The field's habit is a separate root per distinction; a phrase makes the distinction optional, which defeats the point. |
| no | `nanthenanthe` | A kinship term built by fusing two words. No entry of any kind is written fused (VR-COMP-001), and fusion is not how this field coins words either. |

**stratum**

*VR-STR-001 — every entry declares a stratum*

Every lexicon entry carries exactly one of the five strata: native, tamil_inspired, japanese_inspired, compound or loan.

- Pattern: `ENTRY + stratum in {native, tamil_inspired, japanese_inspired, compound, loan}`
- Why: The stratum records how the word was made, which is the only way to report the share quotas, to audit the originality of the lexicon later, and to answer "where does this word come from" without guessing. An entry with no stratum is an entry whose provenance has been lost, and provenance cannot be reconstructed from a form.
- Considered and rejected: Infer the stratum from the form (a loan looks like a loan). Rejected: it is false for every stratum but `loan`, because structural inspiration leaves no trace in the form.
- Known costs: Four of the five strata are unverifiable from the form, so the label is only as honest as the person who typed it. No check can catch a native root mislabelled `tamil_inspired`.
- Inspiration (none): Japanese lexical strata (wago, kango, gairaigo) are a real and linguistically active distinction, visible in the writing system and in phonotactics. How Tanese differs: Tanese borrows the idea of stratifying the lexicon and nothing else: the strata are different, the labels are metadata rather than phonologically active, and no stratum gets its own script or its own phonotactics.

|  | Form | Note |
| --- | --- | --- |
| yes | `nami` | house -- stratum: native |
| yes | `sedha nami` | restaurant -- stratum: compound (a lexicalized two-noun entry) |
| no | `nami` | Entered with no stratum at all. The form is a perfectly good word; the entry is incomplete, and nothing later can recover which method coined it. |
| no | `nami` | Entered with two strata (native and tamil_inspired). A word is coined once, by one method; two labels means the share quotas no longer sum to the lexicon size. |

*VR-STR-002 — inspiration is structural, never a form*

A tamil_inspired or japanese_inspired word borrows a structural or semantic habit from its source language. Its form is coined natively and must not resemble any source word.

- Pattern: `coined form, natively generated; habit borrowed`
- Why: LOCKED decision 3 forbids a particle form that equals a common Japanese or Tamil one. Phase 1C applies the same principle to content words, because the alternative -- a lexicon of recognisably adapted source words -- would make the claim that Tanese is an original language untrue in the place where it matters most, the vocabulary. What remains borrowable is how meaning is divided up, and that is borrowed openly: see the semantic_fields block.
- Considered and rejected: Permit adapted source forms under a similarity ceiling, with per-source quotas. Rejected: the originality claim would then rest on a threshold, defended word by word, and any threshold low enough to admit useful words is also low enough to admit obvious ones.
- Known costs: It makes the two inspired strata invisible in the words themselves, so a reader cannot hear what is Tamil-inspired about a Tamil-inspired word. The inspiration is real but it lives in the shape of the lexicon, not the shape of the word.
- Inspiration (tamil): Tamil semantic granularity, especially in kinship. How Tanese differs: The distinctions are kept and every form filling them is coined natively, so not one Tamil morpheme enters the language.

|  | Form | Note |
| --- | --- | --- |
| yes | `nanthe` | friend -- a natively coined form; its stratum may be tamil_inspired because of the semantic field it sits in, not because of how it sounds |
| yes | `nhodi` | an illustrative minimal root: coined from the phonology, at distance 3 from the nearest listed source form |
| no | `kanhnhi` | A form built to echo a Tamil kinship word. Even setting the resemblance aside, it is not a legal Tanese word -- `nh` may not be geminated (constraint PT-007) -- so it fails twice. |
| no | `desu` | A Japanese copula form taken over as a root. It equals an entry in spec/grammar_rules/_originality.yaml, so the hard gate in VR-ORIG-001 rejects it. |

*VR-STR-003 — loans are confined to one semantic field*

The loan stratum is the only one that borrows a form, and it is restricted to the abstract_and_technical field with a share target of 0.06.

- Pattern: `source word -> adaptation pipeline -> loan entry in abstract_and_technical`
- Why: A language with no loan machinery has to pretend that concepts like `computer` do not exist, which is worse than borrowing. Confining loans to one field and a small quota is what stops that concession from spreading: the restriction, not the adaptation rules, is what keeps Tanese sounding like itself.
- Considered and rejected: No loans at all in v0.1, coining a native root for every concept. Rejected: the native coinage for an imported technical concept is arbitrary, and arbitrary roots are exactly what the collision detector has the least ability to justify.
- Known costs: The word "abstract" is elastic, and the field boundary is the only real restraint. A later phase could classify almost anything as abstract and stay formally compliant.
- Inspiration (japanese): Japanese gairaigo: a large, clearly marked loan stratum with its own adaptation phonology. How Tanese differs: The adaptation machinery is kept in spirit and is entirely Tanese in content; unlike gairaigo the stratum is capped by quota and confined to one semantic field, and it gets no separate script.

|  | Form | Note |
| --- | --- | --- |
| yes | `banku` | bank -- an adapted loan (see adaptation_examples), stratum: loan |
| yes | `kotha` | coat -- an adapted loan from an Indic source form with a retroflex coda |
| no | `pilun` | "film" adapted correctly but filed in the natural_world field. The adaptation is fine; the classification is not, and misfiling a loan is how the 0.06 quota gets evaded. |
| no | `sabo` | A native root filed as a loan. Nothing was borrowed, so the entry inflates the loan share and understates the native one, making both quotas meaningless. |

## 6. Unresolved decisions

Open questions, each with the trigger that would force a decision and the cost of taking it.
Nothing here is a defect being hidden until someone notices; these are the places where v0.1
deliberately stopped.

### U-1. Negation occupies the mood slot — `docs/CHANGES.md` CH-002

**The question.** Negation is the mood suffix `-nhi`, so it cannot combine with any other
mood. Two of the three casualties are rescued analytically — the prohibitive is
`mandukenhi thon` and the negative conditional is `ikkedhonhi lun`, each two words where its
positive counterpart is one — and the third, a negative desiderative ("does not want to"),
has no form at all.

**The alternative.** A dedicated negation slot between root and aspect:
`ROOT - NEG - ASPECT - TENSE - MOOD - POLITENESS`. This would amend locked decision 6, which
itself says the slot order is reviewable "if a concrete problem is found".

**Trigger: revisit if Phase 3 shows the analytic forms do not work.** The problem is concrete
but not yet demonstrated to be fatal, so nothing is proposed now. If writing the Phase 3
corpus and conversations shows that `mandukenhi thon` is unusable in practice — too long,
ambiguous, or quietly avoided by the writer in favour of a workaround — that is the evidence
that would justify amending a locked decision.

**Cost if taken.** A fully specified verb would reach six suffixes. Every rule and example
mentioning the analytic forms would be rewritten, and the Phase 1B contradiction checker's
slot-order check would have to be re-based. This is recorded in full as CH-002 in
`docs/CHANGES.md`.

### U-2. A root that *ends* in a suffix form

**The question.** `RS-RESERVED` forbids a root identical to a declared particle or suffix,
but compares whole forms only. A root like a hypothetical `kanen`, which ends in the plural
suffix `-nen`, is legal and still confusable: a segmenter cannot tell whether it is one word
or a root plus a suffix.

**Trigger: Phase 4.** Only the morphological analyzer can establish whether this is a real
parsing problem or a theoretical one, because resolving it requires knowing what the
competing analyses are and how often they actually arise.

**Cost of the obvious fix.** Banning every root that ends in any of the fourteen suffix forms
would remove a large share of the root space, and unevenly: the suffixes are short, so the
ban would fall hardest on two-mora roots, which are the ones frequent vocabulary needs.

### U-3. Loans that exceed the root cap

**The question.** Epenthesis adds moras, so a source word can clear every phonotactic
constraint and still come out longer than the four-mora root ceiling. `strike` adapts to
`suturawiku`, which is five moras: a perfectly legal Tanese word that cannot be a root.

**Trigger: Phase 2**, the first time a wanted loan comes out oversized. Three options are
open — truncate the adapted form, refuse the loan, or exempt the loan stratum from `RS-MAX`
— and each is defensible. This specification picks none of them, because picking one without
a real case in front of you is guessing.

**Cost.** Truncation makes adaptation lossy and no longer reversible; refusal means some
concepts cannot be borrowed at all; an exemption makes the root cap mean something different
for one stratum than for the other four.

### U-4. Derivational morphology

**The question.** v0.1 has no derivational suffixes at all. There is no way to turn a verb
into an agent noun, or a noun into an adjective-like modifier, so a 300-word lexicon has to
cover every meaning with roots and compounds alone.

**Trigger: Phase 2**, if the lexicon cannot reach its target without derivation.
Deliberately not added in Phase 1C: a derivational suffix is a new morpheme and would need a
slot in the noun or verb morphology that does not currently exist, which puts it straight
into the Phase 1B contradiction checker's jurisdiction. Adding morphology to solve a
vocabulary problem that has not yet been observed is exactly the over-engineering this
project tries to avoid.

**Cost if taken.** New morphemes, new slots, and a rewrite of the word-boundary and
segmentation story, since a derived word is one word carrying two kinds of suffix.

### U-5. The two demo roots that are one edit from Japanese *desu*

**The question.** `esu`, the demo copula, is one edit from Japanese *desu* **and** has the
same grammatical function. `wesu` ("see") is one edit from it as well. Both pass the hard
gate, because the hard gate is exact equality; both would fail the new-root gate, which is
declared non-retroactive.

**Trigger: now, for Phase 2.** These are demo words rather than vocabulary, so nothing
official is affected, but Phase 2 must not re-derive either of them. The Phase 1C report
recommends retiring both outright.

**Cost.** Low: replacing them means rewriting the grammar examples that use them, and the
copula in particular appears in a fair number of them.

### U-6. Whether the stratum shares are the right shares

**The question.** The five share targets (0.60 native, 0.12 and 0.12 inspired, 0.10 compound,
0.06 loan) are a judgement with nothing behind them. They are the only mechanism restraining
the loan stratum, and the only thing keeping the lexicon from becoming mostly compounds.

**Trigger: Phase 2 reports the achieved shares against these targets.** A large gap in
either direction is evidence that the target was wrong rather than that the lexicon is.

**Cost.** None to change the numbers. The point of recording them is to make the comparison
possible at all.

## 7. Limitations

What this specification does **not** establish. The project's standing rule is that nothing
is claimed to work unless it was actually run, so the list below is as much a part of the
specification as the rules are.

### Nobody has used this language

No corpus, no conversation and no translation exists in Tanese. Every example in this
document was written to demonstrate the rule it sits under. The rules are therefore proven
consistent with each other and not proven usable together: whether anyone could say anything
in Tanese is, as of v0.1, unknown. Phase 3 is the first point at which that changes.

### Nobody has spoken it

The phonology is argued from general phonetics — which consonants can be audibly held, which
contrasts a learner could acquire — and has never been tested with a speaker. Nothing here is
evidence that Tanese is pronounceable, only that it is not obviously unpronounceable.

### There is no vocabulary

The 41 words in the grammar examples and the 12 forms this document introduces are
placeholders and illustrations. All are marked experimental, none has been through the
collision detector (which is Phase 2), and a check fails if any of them turns up in the
lexicon. Two are specifically known to be too close to a Japanese form — see U-5.

### The originality claim is bounded

Every Tanese form is checked against a list of 61 Japanese and Tamil particles, case endings,
verbal endings and honorifics, by exact equality, and newly coined roots must additionally be
at least two edits from any of them. The list is hand-enumerated. Passing both gates proves
**only** that no listed form was reused or closely approached. It is not evidence of absence
from Japanese or Tamil as wholes, and still less from any third language.

The new-root gate is also non-retroactive, and what it spares is on the record: 21 existing
forms sit one edit from a listed source form. Eighteen are Phase 1B particles and suffixes,
where the measure means little — a two-letter suffix cannot be far from a two-letter particle
— and that is the honest reason the gate applies to roots rather than to morphemes.

### Checks compare declarations, not prose

The consistency checks reason about declared forms, slots, tables and examples. Two rules
whose `reason` fields disagree, while their declarations and examples do not overlap, will
pass every check in this project. The prose is not machine-checked and cannot be.

In the same vein, a stratum label and a semantic field assignment are unverifiable from a
form. No check can catch a native root recorded as `tamil_inspired`, or a loan filed outside
the one field loans are confined to — which is exactly what the invalid examples of
`VR-STR-003` and `VR-SEM-001` describe. Those classifications are honest metadata, not
results.

### An "invalid" example means "the author says so, with a reason"

Across the grammar and the vocabulary rules, invalid examples are labelled ungrammatical or
ill-formed by the author. What is mechanically proved about them is narrower than it looks:
each is either a legal Tanese word sequence, or declared illegal and verified to be rejected
by the validator. That they are *bad Tanese* is a claim with an argument behind it, not a
measurement. The rule-based grammar checker that could test them is Phase 4.

### The loan adapter has seen fourteen inputs

Nine expected outputs and five expected rejections, all hand-derived from the repair steps
and recorded in the spec so that the test cannot simply confirm whatever the code happens to
do. That is enough to pin down the behaviour of each repair; it is not a real loanword list,
and the adapter has never been run over one.

### The glyphs have never been drawn

`spec/script.yaml` describes every atom and glyph in prose and reserves a codepoint for each
mora. No font, SVG or image exists in this project. Whether the glyphs are legible, and in
particular whether the three retroflexes are distinguishable from their alveolar
counterparts, is entirely unknown. Rendering is Phase 6.

## 8. Provenance

Every number here is printed by the command named beside it; none is typed by hand.

| What | Count | Printed by |
| --- | --- | --- |
| Vowels | 5 | `python scripts/check_yaml_schema.py` |
| Consonants | 16 | `python scripts/check_yaml_schema.py` |
| Mora glyphs | 86 | `python scripts/gen_words.py` |
| Grammar rules | 54 | `python scripts/check_grammar.py` |
| Declared morphemes | 33 | `python scripts/check_grammar.py` |
| Vocabulary rules | 20 | `python scripts/check_vocabulary.py` |
| Loan substitutions | 38 | `python scripts/check_vocabulary.py` |
| Unmapped source sounds | 14 | `python scripts/check_vocabulary.py` |
| Demo words (not vocabulary) | 41 | `python scripts/check_grammar.py` |
| Official vocabulary | 0 | Phase 2 has not run |

Generated from:

- `spec/phonology.yaml`, `spec/romanization.yaml`, `spec/script.yaml` (Phase 1A)
- `spec/grammar_rules/*.yaml` (Phase 1B)
- `spec/vocabulary_rules.yaml` (Phase 1C)
- `docs/_rationale/*.md` (hand-written narrative)
