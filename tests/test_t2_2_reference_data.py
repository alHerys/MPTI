"""T2.2: synthetic reference dataset tests (WBS 2.2)."""
import csv
import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SALES = ROOT / "data" / "reference_sales.csv"
META = ROOT / "data" / "reference_meta.csv"
SCRIPT = ROOT / "scripts" / "gen_reference.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


@pytest.mark.skipif(not SALES.exists() or not META.exists(), reason="dataset not generated")
def test_dataset_shape_and_vocabularies():
    meta = _rows(META)
    sales = _rows(SALES)
    assert 150 <= len(meta) <= 180
    assert abs(len(sales) - 15120) <= 1512
    assert len(sales) == len(meta) * 90
    assert set(r["business_type"] for r in meta) == {"warung", "cafe", "gerobak", "bakery", "kantin"}
    assert set(r["location_type"] for r in meta) == {"kampus", "kantor", "permukiman", "pasar"}
    assert set(r["category"] for r in meta) == {"nasi", "mie", "snack", "minuman", "roti"}
    per_series = {r["series_id"] for r in sales}
    assert len(per_series) == len(meta)
    assert all(int(r["qty"]) >= 0 for r in sales)


def test_seed_42_reproduces_identical_files(tmp_path):
    if not SALES.exists():
        pytest.skip("dataset not generated")
    subprocess.run(
        [sys.executable, str(SCRIPT), "--seed", "42", "--out", str(tmp_path)],
        check=True,
        capture_output=True,
        cwd=ROOT,
    )
    assert _sha(tmp_path / "reference_sales.csv") == _sha(SALES)
    assert _sha(tmp_path / "reference_meta.csv") == _sha(META)


def test_different_seed_changes_output(tmp_path):
    subprocess.run(
        [sys.executable, str(SCRIPT), "--seed", "7", "--out", str(tmp_path)],
        check=True,
        capture_output=True,
        cwd=ROOT,
    )
    assert _sha(tmp_path / "reference_sales.csv") != _sha(SALES)


def test_readme_declares_synthetic_data():
    text = (ROOT / "data" / "README_data.md").read_text(encoding="utf-8")
    lower = text.lower()
    assert "sintetis" in lower
    assert "seed 42" in lower
    assert "bukan data asli" in lower or "bukan data nyata" in lower
