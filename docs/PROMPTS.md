# Prompts to paste into Claude Code (one per session)

## Before the first session (manual)
1. Create folder, `git init`.
2. `git config --local user.name "YourName"` and `git config --local user.email "ID+username@users.noreply.github.com"`
3. Turn off the co-author trailer in Claude Code settings.
4. Create the GitHub repo at github.com/new (nothing ticked: no README/.gitignore/license).
5. `python -m venv .venv` using Python 3.11 if possible, then `.venv\Scripts\activate`.
6. Paste your student-scoped Tanese brief into docs/VISION.md.

## PHASE 0 prompt
Read CLAUDE.md, docs/SPEC.md, and docs/VISION.md (context only). Work ONLY on Phase 0.
Use plan mode first. Show me the plan and ask your design questions with options.
Goal: working skeleton, scripts/run_checks.py (plain python: ruff + pytest + YAML schema check), CI on Python 3.11.
Do not write any language content yet. Do not git push. No co-author trailers.
Stop at the end of Phase 0 and report evidence for each done-criterion.

## PHASE 1A prompt
Read CLAUDE.md and docs/SPEC.md. Work ONLY on Phase 1A (phonology, romanization, script).
Plan mode first. Respect every LOCKED decision. For choices not locked (exact consonant set, glyph design concept, romanization digraphs), give me 2-3 options with trade-offs and ask me to choose.
Output machine-readable YAML in spec/, plus the phonotactic validator and roman<->script converter with tests.
For each decision: reason, alternatives, possible problems. Stop at the end of the phase.

## PHASE 1B prompt
Read CLAUDE.md, docs/SPEC.md, spec/phonology.yaml. Work ONLY on Phase 1B (grammar core).
Plan mode first. Write rules as YAML per the schema in SPEC.md, >= 2 valid + 2 invalid examples each. Particle forms must be original, not Japanese/Tamil. Build the schema checker and a contradiction checker.
Stop at the end of the phase.

## PHASE 1C prompt
Read CLAUDE.md, docs/SPEC.md, and the spec/ folder. Work ONLY on Phase 1C.
Write spec/vocabulary_rules.yaml and generate docs/language-specification.md (v0.1) from the YAML plus rationale. End with: design decisions, unresolved decisions, potential problems, recommended corrections, next milestone.

## Later phases (2 to 7)
Same pattern: "Read CLAUDE.md and docs/SPEC.md. Work ONLY on Phase N. Plan mode first. Stop at end of phase."

## END-OF-PROJECT prompt
Explain this whole project to me like I'm preparing for an interview. Quiz me with 15 questions. List every shortcut, limitation, and unverified claim. Check every number in README against real command output.
