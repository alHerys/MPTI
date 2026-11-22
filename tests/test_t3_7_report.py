"""T3.7: model evaluation report regenerates and stays honest (WBS 3.7)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "model_report.md"


def test_report_exists_with_required_sections():
    text = REPORT.read_text(encoding="utf-8")
    for heading in ("Tabel metrik per tahap", "Perbandingan baseline", "Keterbatasan"):
        assert heading in text
    assert "H0" in text and "H3" in text and "H7" in text
    assert "WAPE" in text and "Coverage" in text and "Pinball" in text
    assert "data sintetis" in text.lower()
    assert "bukan akurasi dunia nyata" in text.lower()


def test_report_regenerates_with_real_numbers(tmp_path):
    out = tmp_path / "report.md"
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "evaluate.py"), "--horizon", "5", "--out", str(out)],
        capture_output=True, text=True, cwd=ROOT, check=True,
    )
    text = out.read_text(encoding="utf-8")
    assert "| H0 |" in text and "| H7 |" in text
    assert "Keterbatasan" in text
    assert "H0: WAPE=" in result.stdout
