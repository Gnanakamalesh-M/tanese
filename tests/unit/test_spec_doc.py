"""Is docs/language-specification.md still the document spec/ generates?

The specification is generated, so the committed file is a build artefact: if it drifts from
spec/*.yaml the project has two sources of truth, which is exactly what CLAUDE.md forbids.
These tests regenerate it in memory and compare byte for byte.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _load_generator():
    """Import scripts/gen_spec_doc.py, which is a script rather than a package module."""
    path = REPO_ROOT / "scripts" / "gen_spec_doc.py"
    spec = importlib.util.spec_from_file_location("gen_spec_doc", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["gen_spec_doc"] = module
    spec.loader.exec_module(module)
    return module


GEN = _load_generator()


def test_the_document_exists():
    assert GEN.OUTPUT.is_file(), (
        "docs/language-specification.md is missing; run python scripts/gen_spec_doc.py"
    )


def test_the_document_is_up_to_date_with_the_spec():
    expected = GEN.build()
    actual = GEN.OUTPUT.read_text(encoding="utf-8")
    assert actual == expected, (
        "docs/language-specification.md is out of date with spec/; "
        "run python scripts/gen_spec_doc.py"
    )


def test_generating_twice_gives_the_same_bytes():
    """No timestamp, no set iteration: the build has to be deterministic to be checkable."""
    assert GEN.build() == GEN.build()


@pytest.mark.parametrize("slug,filename", sorted(GEN.RATIONALE.items()))
def test_every_rationale_file_exists_and_is_not_empty(slug: str, filename: str):
    path = GEN.RATIONALE_DIR / filename
    assert path.is_file(), f"missing rationale file for section {slug!r}: {filename}"
    assert path.read_text(encoding="utf-8").strip(), f"rationale file {filename} is empty"


def test_a_missing_rationale_file_is_an_error_not_a_silent_omission(monkeypatch):
    monkeypatch.setitem(GEN.RATIONALE, "intro", "does_not_exist.md")
    with pytest.raises(SystemExit, match="missing rationale file"):
        GEN.build()


def test_the_document_names_the_unresolved_decisions():
    text = GEN.OUTPUT.read_text(encoding="utf-8")
    assert "## 6. Unresolved decisions" in text
    # CH-002 is the open question the grammar left behind; it must be named, not implied.
    assert "CH-002" in text


def test_the_document_states_its_limitations():
    text = GEN.OUTPUT.read_text(encoding="utf-8")
    assert "## 7. Limitations" in text
    assert "There is no vocabulary" in text


def test_the_document_says_it_is_generated():
    first_lines = GEN.OUTPUT.read_text(encoding="utf-8").split("\n")[:12]
    assert any("generated" in line.lower() for line in first_lines)
    assert any("gen_spec_doc.py" in line for line in first_lines)


def test_check_mode_passes_for_the_committed_document():
    assert GEN.main(["--check"]) == 0
