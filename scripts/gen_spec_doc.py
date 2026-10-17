"""Generate docs/language-specification.md from spec/*.yaml plus docs/_rationale/*.md.

Usage (from any working directory):
    python scripts/gen_spec_doc.py            write docs/language-specification.md
    python scripts/gen_spec_doc.py --check    fail if the committed file is out of date

CLAUDE.md: docs are generated from spec/, never the reverse. Everything factual in the
document -- every inventory, table, rule, count and example -- is read from spec/*.yaml at
generation time, so the document cannot drift from the language. What cannot be derived from
a YAML field, because it belongs to no single rule, is written by hand in docs/_rationale/
and spliced in: the narrative, the unresolved decisions, and the limitations.

The output is deterministic. It carries no timestamp and iterates in spec order or sorted
order throughout, so `--check` is a byte comparison and a regeneration with no spec change
is a no-op.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tanese_nlp.grammar import rules as G  # noqa: E402
from tanese_nlp.phonology import spec_load as S  # noqa: E402
from tanese_nlp.vocabulary import consistency as C  # noqa: E402
from tanese_nlp.vocabulary import rules as V  # noqa: E402

OUTPUT = REPO_ROOT / "docs" / "language-specification.md"
RATIONALE_DIR = REPO_ROOT / "docs" / "_rationale"

# Section slug -> the rationale file that opens it. A missing file is an error, not a
# silent omission: a generated document with the prose quietly dropped would still look
# complete.
RATIONALE = {
    "intro": "00_intro.md",
    "sounds": "10_phonology.md",
    "script": "20_script.md",
    "grammar": "30_grammar.md",
    "vocabulary": "40_vocabulary.md",
    "unresolved": "90_unresolved.md",
    "limitations": "95_limitations.md",
}


def prose(slug: str) -> list[str]:
    """The hand-written rationale for one section."""
    path = RATIONALE_DIR / RATIONALE[slug]
    if not path.is_file():
        raise SystemExit(f"missing rationale file: {path.relative_to(REPO_ROOT)}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit(f"empty rationale file: {path.relative_to(REPO_ROOT)}")
    return [text, ""]


def table(headers: list[str], rows: list[list[str]]) -> list[str]:
    if not rows:
        return ["(none)", ""]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    out += ["| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |" for row in rows]
    out.append("")
    return out


def flow(text: str) -> str:
    """Collapse a YAML block scalar to one line, for use inside a table cell."""
    return " ".join(str(text).split())


# --------------------------------------------------------------------------------------
# sections
# --------------------------------------------------------------------------------------


def header() -> list[str]:
    return [
        "# The Tanese Language Specification",
        "",
        f"**Version {V.document()['version']}**",
        "",
        "> This file is generated. Do not edit it.",
        ">",
        "> Run `python scripts/gen_spec_doc.py` to rebuild it from `spec/*.yaml` (the",
        "> machine-readable source of truth for the language) and `docs/_rationale/*.md`",
        "> (the hand-written narrative). `python scripts/gen_spec_doc.py --check` fails if",
        "> this file and `spec/` disagree, and `python scripts/run_checks.py` runs that check.",
        "",
        *prose("intro"),
    ]


def sounds() -> list[str]:
    phonology = S.phonology()
    out = ["## 1. Sounds", "", *prose("sounds"), "### 1.1 Vowels", ""]
    out += table(
        ["Letter", "IPA", "Height", "Backness"],
        [[v["id"], v["ipa"], v["height"], v["backness"]] for v in phonology["vowels"]],
    )
    out += [
        f"Length is contrastive: {flow(phonology['vowel_length']['reason'])}",
        "",
        "### 1.2 Consonants",
        "",
    ]
    out += table(
        ["Letter", "IPA", "Place", "Manner", "Voiced", "Geminable"],
        [
            [
                c["id"],
                c["ipa"],
                c["place"],
                c["manner"],
                "yes" if c["voiced"] else "no",
                "yes" if c["geminable"] else "no",
            ]
            for c in phonology["consonants"]
        ],
    )
    out += ["### 1.3 Moras and syllables", ""]
    out += table(
        ["Mora kind", "Description", "Glyph role"],
        [[m["id"], flow(m["description"]), m["glyph_role"]] for m in phonology["mora_kinds"]],
    )
    out += [
        f"Syllable template: `{phonology['syllable']['template']}`. "
        f"{flow(phonology['syllable']['reason'])}",
        "",
        f"Accent is {phonology['accent']['type']}, on the "
        f"{phonology['accent']['position'].replace('_', ' ')}, and not contrastive. "
        f"{flow(phonology['accent']['reason'])}",
        "",
        "### 1.4 What is not a legal word",
        "",
        "Every rejection names the constraint it broke, so it can be explained rather than",
        "merely counted.",
        "",
    ]
    out += table(
        ["Id", "Name", "Constraint"],
        [[c["id"], c["name"], flow(c["description"])] for c in phonology["constraints"]],
    )
    out += ["### 1.5 Gaps in the mora inventory", ""]
    out += table(
        ["Mora", "Why it does not exist"],
        [[g["mora"], flow(g["reason"])] for g in phonology["gaps"]],
    )
    return out


def spelling() -> list[str]:
    romanization = S.romanization()
    alphabet = romanization["alphabet"]
    out = [
        "## 2. Spelling",
        "",
        "The romanization is the canonical written form of Tanese (locked decision 12); the",
        "script in section 3 is a mapping layer on top of it, never the other way round. Every",
        "rule in this document is stated in the romanization.",
        "",
        f"- Letters ({alphabet['case']}): "
        + " ".join(f"`{letter}`" for letter in alphabet["letters"]),
        f"- Syllable-boundary marker: `{alphabet['separator']}`",
        f"- Word separator: a single space, as declared by "
        f"{G.WORD_BOUNDARY_RULE}",
        "",
        flow(alphabet["reason"]),
        "",
        flow(alphabet["note"]),
        "",
        "### 2.1 Length, gemination and the moraic nasal",
        "",
    ]
    out += table(
        ["Feature", "How it is written", "Why"],
        [
            [
                name.replace("_", " "),
                flow(romanization[name]["rule"]),
                flow(romanization[name]["reason"]),
            ]
            for name in ("long_vowels", "gemination", "moraic_nasal")
        ],
    )
    out += [
        "### 2.2 Worked cases that pin the parse down",
        "",
        "The parse is deterministic longest-match, so every legal word has exactly one",
        "spelling and every spelling exactly one reading. These are the cases that fix it.",
        "",
    ]
    out += table(
        ["Spelling", "Moras", "Why that reading and no other"],
        [
            [f"`{entry['roman']}`", " . ".join(entry["moras"]), flow(entry["why"])]
            for entry in romanization["ambiguity_cases"]
        ],
    )
    out += ["The parse order, as the lexer applies it:", ""]
    steps = romanization["parse_order"]["steps"]
    out += [f"{index}. {flow(step)}" for index, step in enumerate(steps, start=1)]
    out += [""]
    return out


def script() -> list[str]:
    script_spec = S.script()
    out = ["## 3. The script", "", *prose("script")]

    design = script_spec.get("design")
    if isinstance(design, dict):
        out += table(
            ["Property", "Value"],
            [[key.replace("_", " "), flow(value)] for key, value in design.items()],
        )
    out += [
        f"- Inherent vowel: {script_spec['inherent_vowel']}",
        f"- Virama: {script_spec['virama']}",
        "",
        flow(script_spec["inherent_vowel_reason"]),
        "",
        "### 3.1 Atoms",
        "",
        "The hand-designed pieces every glyph is composed from.",
        "",
    ]
    atoms = script_spec["atoms"]
    for group in sorted(atoms):
        out += [f"**{group}**", ""]
        out += table(
            ["Id", "Shape"],
            [
                [entry["id"], flow(entry.get("shape", entry.get("description", "")))]
                for entry in atoms[group]
            ],
        )

    out += [
        "### 3.2 Bases",
        "",
        f"{len(script_spec['bases'])} bases, each a frame plus a manner mark.",
        "",
    ]
    out += table(
        ["Id", "Composition"],
        [
            [entry["id"], " + ".join(entry.get("composition", []))]
            for entry in script_spec["bases"]
        ],
    )

    out += [
        "### 3.3 The mora table",
        "",
        f"One glyph per legal mora: {len(script_spec['moras'])} in total, each with a reserved",
        "Private Use Area codepoint for later rendering. The canonical script form of a word is",
        "the dot-joined sequence of its mora ids.",
        "",
    ]
    out += table(
        ["Id", "Mora", "Kind", "Composition", "PUA"],
        [
            [
                entry["id"],
                f"`{entry['mora']}`" if entry.get("mora") else "--",
                entry["kind"],
                " + ".join(entry.get("composition", [])),
                entry["pua"],
            ]
            for entry in script_spec["moras"]
        ],
    )
    return out


def grammar() -> list[str]:
    out = ["## 4. Grammar", "", *prose("grammar")]

    out += ["### 4.1 The morpheme inventory", "", "Particles (separate words):", ""]
    particles = sorted(
        (m for m in G.morphemes() if m.kind == "particle"), key=lambda m: (m.slot, m.form)
    )
    out += table(
        ["Form", "Slot", "Function", "Rule"],
        [[m.form, m.slot, m.function.replace("_", " "), m.rule_id] for m in particles],
    )
    out += ["Suffixes (attached to the root):", ""]
    suffixes = sorted(
        (m for m in G.morphemes() if m.kind == "suffix"), key=lambda m: (m.slot, m.form)
    )
    out += table(
        ["Form", "Slot", "Function", "Tense", "Rule"],
        [
            [m.form, m.slot, m.function.replace("_", " "), m.tense or "--", m.rule_id]
            for m in suffixes
        ],
    )
    out += ["Pronouns (whole words):", ""]
    words = sorted((m for m in G.morphemes() if m.kind == "word"), key=lambda m: m.form)
    out += table(
        ["Form", "Function", "Rule"],
        [[m.form, m.function.replace("_", " "), m.rule_id] for m in words],
    )

    declared = [rule for rule in G.load_rules() if rule.slot_order]
    if declared:
        out += [
            "Verb suffix order (locked decision 6), as declared by "
            + ", ".join(rule.id for rule in declared)
            + ":",
            "",
            "    " + " - ".join(part.upper() for part in declared[0].slot_order),
            "",
        ]

    out += ["### 4.2 The rules", ""]
    by_category: dict[str, list] = {}
    for rule in G.load_rules():
        by_category.setdefault(rule.category, []).append(rule)
    for category in sorted(by_category):
        out += [f"**{category.replace('_', ' ')}**", ""]
        out += table(
            ["Id", "Name", "Pattern", "Rule"],
            [
                [rule.id, rule.name, f"`{rule.raw['pattern']}`", flow(rule.raw["description"])]
                for rule in by_category[category]
            ],
        )
    return out


def vocabulary() -> list[str]:
    out = ["## 5. Vocabulary", "", *prose("vocabulary")]

    out += ["### 5.1 Strata", ""]
    out += table(
        ["Stratum", "Borrows", "Borrows a form?", "Share target", "What it is"],
        [
            [
                entry["id"],
                ", ".join(entry["borrows"]) or "--",
                "yes" if entry["borrows_form"] else "no",
                f"{entry['share_target']:.2f}",
                flow(entry["description"]),
            ]
            for entry in V.strata()
        ],
    )

    counts = V.mora_counts()
    out += [
        "### 5.2 Root shapes",
        "",
        f"A root is {counts['min']} to {counts['max']} moras long and ends in "
        f"{' or '.join(f'`{final}`' for final in V.permitted_finals())}.",
        "",
    ]
    out += table(
        ["Id", "Shape rule", "Why"],
        [
            [entry["id"], flow(entry["description"]), flow(entry["reason"])]
            for entry in V.root_shapes()
        ],
    )

    gate = V.originality()
    out += [
        "### 5.3 Originality",
        "",
        f"- **Hard gate**: `{gate['hard_gate']}`. {flow(gate['hard_gate_reason'])}",
        f"- **New-root gate**: {gate['new_root_gate']['metric'].replace('_', ' ')} of at least"
        f" {gate['new_root_gate']['min_edit_distance']}, measured against the"
        f" {gate['new_root_gate']['measured_against']}, applying to"
        f" {gate['new_root_gate']['applies_to']}."
        f" Retroactive: {'yes' if gate['new_root_gate']['retroactive'] else 'no'}.",
        "",
        flow(gate["new_root_gate_reason"]),
        "",
        f"Known costs: {flow(gate['problems'])}",
        "",
        "### 5.4 Semantic fields",
        "",
    ]
    out += table(
        ["Field", "Stratum", "Habit", "Distinctions it keeps"],
        [
            [
                entry["id"].replace("_", " "),
                entry["stratum"],
                flow(entry["habit"]),
                ", ".join(d.replace("_", " ") for d in entry["distinctions"]) or "--",
            ]
            for entry in V.semantic_fields()
        ],
    )

    out += ["### 5.5 Compounds", ""]
    out += table(
        ["Id", "Pattern", "Head", "Written", "What it is"],
        [
            [
                entry["id"],
                f"`{entry['pattern']}`",
                entry["head"],
                entry["written"].replace("_", " "),
                flow(entry["description"]),
            ]
            for entry in V.compound_patterns()
        ],
    )

    out += [
        "### 5.6 Loanword adaptation",
        "",
        "Source sounds that have a Tanese equivalent:",
        "",
    ]
    out += table(
        ["Source", "Becomes", "Why"],
        [
            [
                f"`{entry['source']}`",
                f"`{entry['tanese']}`" if entry["tanese"] else "(deleted)",
                flow(entry["reason"]),
            ]
            for entry in V.document()["loan_substitutions"]
        ],
    )
    out += [
        "Source sounds with **no** mapping. These are rejected by name, never approximated:",
        "",
    ]
    out += table(
        ["Source", "Code", "Why it is left undecided"],
        [
            [f"`{entry['source']}`", entry["code"], flow(entry["reason"])]
            for entry in V.document()["unmapped"]
        ],
    )
    out += ["The repair steps, applied in this order:", ""]
    out += table(
        ["Step", "Id", "What it does"],
        [
            [str(entry["step"]), entry["id"], flow(entry["description"])]
            for entry in V.repairs()
        ],
    )
    out += ["Worked examples, with the output each is required to produce:", ""]
    out += table(
        ["Source", "Segments", "Tanese", "Steps that fired"],
        [
            [
                entry["source_word"],
                " ".join(f"`{segment}`" for segment in entry["segments"]),
                f"**{entry['expect']}**",
                ", ".join(step.split("-", 2)[-1].lower() for step in entry["steps_fired"]),
            ]
            for entry in V.adaptation_examples()
        ],
    )
    out += ["Inputs that must be refused:", ""]
    out += table(
        ["Source", "Code", "Offending sound", "Why"],
        [
            [entry["source_word"], entry["code"], f"`{entry['offending']}`", flow(entry["reason"])]
            for entry in V.adaptation_rejections()
        ],
    )

    out += [
        "### 5.7 How a word becomes official",
        "",
        "Locked decision 14, as ordered stages. The LLM may act at the first stage and",
        "nowhere else; the last stage cannot be automated.",
        "",
    ]
    out += table(
        ["Id", "Stage", "Automated", "LLM may act", "What happens"],
        [
            [
                entry["id"],
                entry["stage"].replace("_", " "),
                "yes" if entry["automated"] else "no",
                "yes" if entry["llm_allowed"] else "no",
                flow(entry["description"]),
            ]
            for entry in V.pipeline()
        ],
    )

    out += ["### 5.8 The vocabulary rules", ""]
    by_category: dict[str, list] = {}
    for rule in V.load_rules():
        by_category.setdefault(rule.category, []).append(rule)
    for category in sorted(by_category):
        out += [f"**{category.replace('_', ' ')}**", ""]
        for rule in by_category[category]:
            out += [f"*{rule.id} — {rule.name}*", "", flow(rule.raw["description"]), ""]
            out += [f"- Pattern: `{rule.raw['pattern']}`"]
            out += [f"- Why: {flow(rule.raw['reason'])}"]
            if "alternatives" in rule.raw:
                out += [f"- Considered and rejected: {flow(rule.raw['alternatives'])}"]
            if "problems" in rule.raw:
                out += [f"- Known costs: {flow(rule.raw['problems'])}"]
            inspiration = rule.raw["inspiration"]
            out += [
                f"- Inspiration ({inspiration['source']}): "
                f"{flow(inspiration['original_feature'])} "
                f"How Tanese differs: {flow(inspiration['how_modified'])}"
            ]
            examples = rule.examples
            good = [e for e in examples if e.polarity == "valid"]
            bad = [e for e in examples if e.polarity == "invalid"]
            out += [""]
            out += table(
                ["", "Form", "Note"],
                [["yes", f"`{e.roman}`", flow(e.note)] for e in good]
                + [["no", f"`{e.roman}`", flow(e.note)] for e in bad],
            )
    return out


def unresolved() -> list[str]:
    return ["## 6. Unresolved decisions", "", *prose("unresolved")]


def limitations() -> list[str]:
    return ["## 7. Limitations", "", *prose("limitations")]


def provenance() -> list[str]:
    stats = C.stats()
    return [
        "## 8. Provenance",
        "",
        "Every number here is printed by the command named beside it; none is typed by hand.",
        "",
        *table(
            ["What", "Count", "Printed by"],
            [
                ["Vowels", str(len(S.vowels())), "`python scripts/check_yaml_schema.py`"],
                ["Consonants", str(len(S.consonants())), "`python scripts/check_yaml_schema.py`"],
                ["Mora glyphs", str(len(S.script_glyphs())), "`python scripts/gen_words.py`"],
                ["Grammar rules", str(len(G.load_rules())), "`python scripts/check_grammar.py`"],
                [
                    "Declared morphemes",
                    str(len(list(G.morphemes()))),
                    "`python scripts/check_grammar.py`",
                ],
                ["Vocabulary rules", str(stats["rules"]), "`python scripts/check_vocabulary.py`"],
                [
                    "Loan substitutions",
                    str(stats["substitutions"]),
                    "`python scripts/check_vocabulary.py`",
                ],
                [
                    "Unmapped source sounds",
                    str(stats["unmapped"]),
                    "`python scripts/check_vocabulary.py`",
                ],
                [
                    "Demo words (not vocabulary)",
                    str(len(G.load_example_lexicon())),
                    "`python scripts/check_grammar.py`",
                ],
                ["Official vocabulary", "0", "Phase 2 has not run"],
            ],
        ),
        "Generated from:",
        "",
        "- `spec/phonology.yaml`, `spec/romanization.yaml`, `spec/script.yaml` (Phase 1A)",
        "- `spec/grammar_rules/*.yaml` (Phase 1B)",
        "- `spec/vocabulary_rules.yaml` (Phase 1C)",
        "- `docs/_rationale/*.md` (hand-written narrative)",
        "",
    ]


def build() -> str:
    lines: list[str] = []
    for section in (
        header,
        sounds,
        spelling,
        script,
        grammar,
        vocabulary,
        unresolved,
        limitations,
        provenance,
    ):
        lines.extend(section())
    text = "\n".join(lines).rstrip() + "\n"
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text


def main(argv: list[str]) -> int:
    text = build()
    if "--check" in argv:
        if not OUTPUT.is_file():
            print(f"FAIL  {OUTPUT.relative_to(REPO_ROOT)} does not exist")
            print("      run: python scripts/gen_spec_doc.py")
            return 1
        current = OUTPUT.read_text(encoding="utf-8")
        if current != text:
            print(f"FAIL  {OUTPUT.relative_to(REPO_ROOT)} is out of date with spec/")
            print("      run: python scripts/gen_spec_doc.py")
            return 1
        print(f"ok    {OUTPUT.relative_to(REPO_ROOT)} matches spec/ ({len(text)} bytes)")
        return 0

    OUTPUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT.relative_to(REPO_ROOT)} ({len(text)} bytes,"
          f" {text.count(chr(10))} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
