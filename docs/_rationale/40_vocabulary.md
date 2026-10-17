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
