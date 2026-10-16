# CLAUDE.md - standing rules for Tanese

## Project in one line
Tanese = constructed language (Tamil + Japanese inspired) + NLP/LLM toolkit. Student GitHub project: finishable, honest, well evaluated.

## Source of truth
- docs/VISION.md = context only. Do NOT build from it directly.
- docs/SPEC.md = locked decisions + current phase + done criteria. Follow it.
- spec/*.yaml = the machine-readable language rules. Docs are generated/derived from these, not the reverse.
- Rules define Tanese. The LLM assists but never changes official rules or vocabulary.

## Workflow rules
1. ONE phase per session. Stop at the end of the phase. Do not start the next one.
2. Start every phase in plan mode. Ask design questions with options; do not guess.
3. Do NOT run git push. Do not add Co-Authored-By trailers. Commit only when I say, one commit per phase/sub-phase.
4. Never weaken, skip, or delete tests just to get green. If a test is wrong, tell me why first.
5. Do not test placeholders (e.g. LICENSE name, TODO text).
6. No `make`. Every script runs with plain `python scripts/<name>.py` (I am on Windows cmd).
7. Target Python 3.11 (same as CI). Do not use features newer than 3.11.
8. No data leakage: detectors/validators/LLM prompts must never read data/evaluation/ answer keys.
9. Never change a LOCKED decision in SPEC.md. Propose a change in docs/CHANGES.md and wait for my approval.
10. Avoid over-engineering. Prefer deterministic rules; use LLMs only where meaning is needed.

## Honesty rules
- Every number in README/docs must name the command that produced it. Do not invent counts.
- Never claim something works unless it was actually run in this session. Anything not run goes under "Not verified" in README.
- Always compare against a fair baseline (plain rules / keyword search / no-RAG) and report it even if the fancy method loses.
- Translation metrics (BLEU/chrF) are self-referential because Tanese has no native speakers. Say so.

## End-of-phase checklist (do before stopping)
- [ ] Phase done-criteria in SPEC.md all met (list each with evidence)
- [ ] python scripts/run_checks.py passes
- [ ] README "Not verified" section updated
- [ ] Summary: what was built, shortcuts taken, known limitations
