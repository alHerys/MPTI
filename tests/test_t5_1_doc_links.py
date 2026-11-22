"""T5.1: every FR has a test case and every referenced test name exists (WBS 5.1)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "test_cases.md"
REQUIREMENTS = ROOT / "docs" / "requirements.md"


def _collect_test_names() -> set[str]:
    names = set()
    for path in (ROOT / "tests").glob("test_*.py"):
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"^def (test_\w+)", text, re.M):
            names.add(match.group(1))
        for match in re.finditer(r'^def (test_\w+)\(', text, re.M):
            names.add(match.group(1))
    return names


def test_every_fr_in_requirements_has_test_case():
    requirements = REQUIREMENTS.read_text(encoding="utf-8")
    fr_ids = set(re.findall(r"^## (FR-\d+)", requirements, re.M))
    doc = DOC.read_text(encoding="utf-8")
    documented = set(re.findall(r"\| (FR-\d+) \|", doc))
    missing = sorted(fr_ids - documented)
    assert not missing, f"FR tanpa TC: {missing}"


def test_every_referenced_pytest_name_exists():
    doc = DOC.read_text(encoding="utf-8")
    referenced = set(re.findall(r"`(test_\w+)`", doc))
    available = _collect_test_names()
    missing = sorted(referenced - available)
    assert not missing, f"Tes yang dirujuk tidak ada: {missing}"


def test_doc_covers_end_to_end_flow():
    doc = DOC.read_text(encoding="utf-8")
    for phrase in ("Login", "CSV", "H0", "H3", "H7", "Responsif", "Health check"):
        assert phrase in doc
