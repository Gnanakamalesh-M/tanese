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
lexicon. Two of the demo roots were replaced for being one edit from a Japanese form — see
"Closed since v0.1" in section 6 — but no demo word has had any collision checking, so two
of them may well be confusably similar to each other.

### The originality claim is bounded

Every Tanese form is checked against a list of 61 Japanese and Tamil particles, case endings,
verbal endings and honorifics, by exact equality, and newly coined roots must additionally be
at least two edits from any of them. The list is hand-enumerated. Passing both gates proves
**only** that no listed form was reused or closely approached. It is not evidence of absence
from Japanese or Tamil as wholes, and still less from any third language.

The new-root gate is also non-retroactive, and what it spares is on the record: 19 existing
forms sit one edit from a listed source form. Eighteen are Phase 1B particles and suffixes,
where the measure means little — a two-letter suffix cannot be far from a two-letter particle
— and that is the honest reason the gate applies to roots rather than to morphemes. The
nineteenth is the demo pronoun root `ano`. The two cases that were a real problem rather
than an artefact of the measure have been retired instead of spared.

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
