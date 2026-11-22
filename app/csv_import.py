"""CSV sales import with all-or-nothing validation (T2.6 / WBS 2.6)."""
from __future__ import annotations

import csv
import io
from datetime import date

MAX_ROWS = 5000
MAX_BYTES = 1024 * 1024
REQUIRED_HEADER = ("date", "product", "qty_sold")
OPTIONAL_HEADER = ("sold_out",)


class ImportError_(Exception):
    """Raised with a list of {line, message} errors."""

    def __init__(self, message: str, errors: list[dict] | None = None):
        super().__init__(message)
        self.message = message
        self.errors = errors or []


def _truthy(raw: str) -> bool:
    return raw.strip().lower() in {"1", "true", "ya", "yes", "y", "on"}


def parse_sales_csv(
    raw: bytes, products_by_name: dict[str, int], today: date | None = None
) -> list[dict]:
    """Validate and normalize a CSV upload.

    Returns rows [{product_id, date, qty_sold, sold_out, line}], sorted by line.
    Raises ImportError_ with per-line messages for any problem.
    """
    today = today or date.today()
    if len(raw) > MAX_BYTES:
        raise ImportError_(f"Berkas terlalu besar (maksimal 1 MB).", [{"line": 0, "message": "Ukuran melebihi 1 MB."}])
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ImportError_("Berkas harus berenkode UTF-8.", [{"line": 0, "message": "Berkas bukan UTF-8."}])

    reader = csv.reader(io.StringIO(text, newline=""))
    try:
        header = next(reader)
    except StopIteration:
        raise ImportError_("Berkas kosong.", [{"line": 1, "message": "Tidak ada header."}])

    header = [h.strip().lower() for h in header]
    allowed = set(REQUIRED_HEADER) | set(OPTIONAL_HEADER)
    missing = [h for h in REQUIRED_HEADER if h not in header]
    extra = [h for h in header if h not in allowed]
    if missing or extra or len(set(header)) != len(header):
        detail = []
        if missing:
            detail.append("kolom wajib hilang: " + ", ".join(missing))
        if extra:
            detail.append("kolom tidak dikenal: " + ", ".join(extra))
        if len(set(header)) != len(header):
            detail.append("kolom duplikat")
        raise ImportError_(
            "Header tidak valid. Gunakan date,product,qty_sold[,sold_out].",
            [{"line": 1, "message": "Header tidak valid (" + "; ".join(detail) + ")."}],
        )

    index = {name: header.index(name) for name in header}
    rows: list[dict] = []
    errors: list[dict] = []
    seen: dict[tuple[str, date], int] = {}

    data_rows = 0
    for line_no, raw_row in enumerate(reader, start=2):
        if not raw_row or all(not cell.strip() for cell in raw_row):
            continue
        data_rows += 1
        if data_rows > MAX_ROWS:
            errors.append({"line": line_no, "message": "Melebihi batas 5.000 baris."})
            raise ImportError_("Berkas melebihi 5.000 baris.", errors)

        def cell(name: str) -> str:
            pos = index.get(name)
            if pos is None or pos >= len(raw_row):
                return ""
            return raw_row[pos].strip()

        raw_date = cell("date")
        try:
            day = date.fromisoformat(raw_date)
        except ValueError:
            errors.append({"line": line_no, "message": f"Tanggal tidak valid: '{raw_date}' (gunakan YYYY-MM-DD)."})
            continue
        if day > today:
            errors.append({"line": line_no, "message": "Tanggal tidak boleh di masa depan."})
            continue

        name = cell("product")
        if name not in products_by_name:
            errors.append({"line": line_no, "message": f"Produk tidak dikenal: '{name}'."})
            continue

        raw_qty = cell("qty_sold")
        try:
            qty = int(raw_qty)
        except ValueError:
            errors.append({"line": line_no, "message": f"Jumlah '{raw_qty}' bukan bilangan bulat."})
            continue
        if qty < 0:
            errors.append({"line": line_no, "message": "Jumlah tidak boleh negatif."})
            continue

        key = (name, day)
        if key in seen:
            errors.append(
                {"line": line_no, "message": f"Duplikat tanggal+produk dengan baris {seen[key]}."}
            )
            continue
        seen[key] = line_no

        sold_out_raw = cell("sold_out") if "sold_out" in index else ""
        rows.append(
            {
                "product_id": products_by_name[name],
                "date": day,
                "qty_sold": qty,
                "sold_out": _truthy(sold_out_raw),
                "line": line_no,
            }
        )

    if errors:
        raise ImportError_("Impor ditolak. Tidak ada data yang disimpan.", errors)
    if not rows:
        raise ImportError_("Berkas tidak berisi baris data.", [{"line": 2, "message": "Tidak ada baris data."}])
    return rows
