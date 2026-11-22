# Decisions

- 2026-11-22: Python 3.11+ is not preinstalled. Installed `uv` and provisioned Python 3.12 into `.venv`; `make install` prefers `uv` and falls back to `python3 -m venv`.
- 2026-11-22: `docs/source/` is empty (no research report provided). Project documents (T1.1–T1.3) are drafted from the repo and general knowledge; every external statistic is explicitly marked "dikutip dari laporan riset; verifikasi sebelum dipresentasikan" and no figure is claimed as verified.
- 2026-11-22: The SteadyMouse row from the research report's prior-art table is intentionally not reproduced anywhere (unrelated contamination per PLAN.md).
- 2026-11-22: Evaluation uses `unit_cost = 60% × price` because reference metadata has no cost column; documented in model_report and business case as illustrative only.
- 2026-11-22: HTML page routes use a `LoginRequired` exception → 303 redirect, while `/api/*` keeps 401 JSON; satisfies FR-01 for both surfaces without duplicate auth logic.
