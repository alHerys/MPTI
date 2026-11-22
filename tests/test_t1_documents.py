"""T1.1/T1.2/T1.3/T5.5: required documents exist and stay honest."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_all_required_docs_from_plan_section_4_exist():
    required = [
        "DECISIONS.md", "requirements.md", "wireframe.md", "model_report.md", "test_cases.md",
        "bug_log.md", "panduan_pengguna.md", "deploy.md", "business_case.md", "project_charter.md",
        "project_plan.md", "uat_kit.md", "laporan_akhir.md", "demo_script.md",
    ]
    missing = [name for name in required if not (DOCS / name).exists()]
    assert not missing, missing


def test_business_case_marks_external_stats_unverified():
    text = (DOCS / "business_case.md").read_text(encoding="utf-8")
    assert "dikutip dari laporan riset; verifikasi sebelum dipresentasikan" in text
    assert "SteadyMouse" not in text


def test_project_plan_has_six_risks():
    text = (DOCS / "project_plan.md").read_text(encoding="utf-8")
    for risk in ("R1", "R2", "R3", "R4", "R5", "R6"):
        assert risk in text
    assert "Tidak ada klaim anggaran pasti" in text


def test_drafts_are_marked_as_drafts():
    for name in ("business_case.md", "project_charter.md", "project_plan.md"):
        assert "DRAF" in (DOCS / name).read_text(encoding="utf-8")


def test_no_todo_fixme_placeholders_in_app_and_docs():
    import re

    offenders = []
    for folder in (ROOT / "app", DOCS, ROOT / "scripts"):
        for path in folder.rglob("*"):
            if path.suffix not in {".py", ".html", ".js", ".css", ".md", ".sh", ".yaml"}:
                continue
            if path.name == "bug_log.md":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"\b(TODO|FIXME|XXX)\b", text):
                offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, offenders
