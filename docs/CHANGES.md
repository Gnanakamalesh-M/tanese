# Change proposals
Any change to a LOCKED decision or official rule goes here first: what, why, alternatives, impact. Wait for approval.

---

## CH-001 — Grammar rule format: add machine-readable fields (Phase 1B)

**Status: applied with approval, 2026-10-16. No LOCKED decision changed.**

**What.** `docs/SPEC.md` documents the grammar rule format. Phase 1B adds these fields to
`spec/schemas/grammar_rule.schema.json`:

| Field | Required? | Purpose |
| --- | --- | --- |
| `morphemes` | required for `particle`, `pronoun`, `politeness`; a `morphology` rule must have this **or** `slot_order` | declares each form with its slot, function and kind, so forms can be compared mechanically |
| `slot_order` | optional | the verb suffix slot order a rule asserts |
| `word_boundary` | optional, declared by exactly one rule (GR-ORD-001) | what counts as one word: the single definition used by the tokenizer, the validator calls and the script conversion |
| `asserts` | optional | `requires` / `forbids` feature keys, so two rules can be checked for opposing claims |
| `alternatives`, `problems` | optional | designs rejected, and known costs — already the convention in `spec/phonology.yaml` |
| `gloss` on an example | optional | morpheme-by-morpheme gloss |

`category` was also closed to an enum (`word_order`, `syntax`, `morphology`, `particle`,
`pronoun`, `politeness`, `discourse`). Without that, a typo'd category would silently skip
the conditional `morphemes` requirement.

**Why.** The Phase 1B done-criterion is "no two rules contradict (checked by a script)". A
rule format of prose plus examples gives a script nothing to compare: it can only match
example strings, which catches a direct clash and nothing else. With the fields above, the
checker in `tanese_nlp/grammar/contradictions.py` detects a form claimed for two functions,
two forms claimed for one function, a slot order that disagrees with LOCKED decision 6, a
suffix in a slot that does not exist, and a feature required by one rule and forbidden by
another — none of which is visible in prose.

**Alternatives considered.** Keep the format exactly as documented and write a prose-only
checker. Rejected: it would have reduced the contradiction check to string comparison of
examples, and the done-criterion would have been met in letter only.

**Impact.** Additive. Every field in the original format is still required, so a rule
written to the SPEC.md format still validates — except that `category` must now be one of
the seven listed names. The only file that changed outside Phase 1B's own additions is
`tests/unit/test_speccheck.py`, whose fixture used `category: test`.

**What is NOT changed.** No LOCKED decision. In particular decision 6 (the verb slot order)
stands as written, which is why negation shares the mood slot and prohibition and negative
conditionals are analytic — see CH-002 below for the consequence that may need revisiting.

---

## CH-002 — Possible future proposal: a dedicated negation slot

**Status: not proposed. Recorded so Phase 3 has somewhere to point.**

Negation is the mood suffix `-nhi` (GR-NEG-001), which keeps LOCKED decision 6 intact but
means negation cannot co-occur with any other mood. Two of the three casualties are rescued
analytically — the prohibitive (`mandukenhi thon`, GR-NEG-003) and the negative conditional
(`ikkedhonhi lun`, GR-NEG-004) — and the third, a negative desiderative ("does not want
to"), is simply not expressible in v0.1.

If Phase 3 corpus work shows the analytic forms are unusable in practice, the change to
propose here is a negation slot between root and aspect:

    ROOT - NEG - ASPECT - TENSE - MOOD - POLITENESS

That would amend LOCKED decision 6, which decision 6 itself says is reviewable in Phase 1B
"if a concrete problem is found". The problem above is concrete but not yet demonstrated to
be fatal, so nothing is proposed now. Cost if it is: a fully specified verb would reach six
suffixes, and every rule and example mentioning the analytic forms would be rewritten.
