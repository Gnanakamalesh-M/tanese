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
