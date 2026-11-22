# ColdStart Kitchen — DONE

Level 1 (agent-complete) definition of done is met.

## (a) Completed tasks

| Task | Deliverable | Status |
|---|---|---|
| T0 | Repo, Makefile, STATUS, passing `make verify` | DONE |
| T1.4 | `docs/requirements.md` — 18 FR + 4 NFR with Given/When/Then | DONE |
| T2.1 | SQLAlchemy schema (`User`, `Business`, `Product`, `Sale`) + scrypt hashing | DONE |
| T2.2 | Seeded synthetic dataset: 168 series × 90 days = 15,120 rows, byte-identical on seed 42 | DONE |
| T1.5 | `docs/wireframe.md` + clickable `prototype/index.html` | DONE |
| T2.3 | Business/menu API + soft delete + ownership (404 cross-user) | DONE |
| T2.5 | Sales API: upsert, inclusive range filters, validation | DONE |
| T2.4 | `POST /sales/new` multi-product daily form (all-or-nothing) | DONE |
| T2.6 | CSV import: strict validation, per-line errors, all-or-nothing | DONE |
| T3.1 | Reference features, kNN (k=5), weighted-median prior, fallbacks | DONE |
| T3.2 | Shrinkage `w=n/(n+4)`, H0/H3/H7, stockout ×1.15, weekday blend at n≥7 | DONE |
| T3.3 | Negative-binomial P10/P50/P90, ordered and non-negative | DONE |
| T3.4 | Newsvendor alpha, clamping [0.05, 0.95], price≤cost → 422 | DONE |
| T3.5 | Confidence rules + Indonesian reason templates | DONE |
| T3.6 | Pure engine + product/business recommendation APIs | DONE |
| T3.7 | Leave-one-business-out evaluation + `docs/model_report.md` | DONE |
| T4.5 | Login/logout/session, env demo creds, idempotent auto-seed, rate limit | DONE |
| T4.1 | Dashboard, business selector, date picker, mobile-first CSS | DONE |
| T4.2 | Recommendation card (qty, range, confidence with text, stage, reasons) | DONE |
| T4.4 | `dashboard.js` renders from API only (no hardcoded numbers) | DONE |
| T2.3-UI / T2.4-UI | `/business` and `/sales/new` pages with inline Indonesian errors | DONE |
| T4.3 | `/sales` history table + inline SVG 14-day chart + date filter | DONE |
| T2.6-UI | `/import` page with sample CSV and per-line errors | DONE |
| T5.1 | `docs/test_cases.md` — 40 TC mapped to real pytest names (verified by test) | DONE |
| T5.3 | Edge-case regression suite + `docs/bug_log.md` | DONE |
| T5.4 | `docs/panduan_pengguna.md` (one page) | DONE |
| T1.1 / T1.2 / T1.3 | Business case, charter, project plan (DRAF, Indonesian) | DONE |
| T9 | Final audit, `DONE.md` | DONE |

## (b) BLOCKED items

None.

## (c) Remaining HUMAN steps

| Task | What a human must do |
|---|---|
| T4.6 | Choose route A (Render) or B (Mac mini + Cloudflare Tunnel), follow `docs/deploy.md`, then record the live URL. Docker build was **not verified** (Docker is not installed on this machine); Postgres compatibility was checked by code review only. |
| T5.2 | Run UAT using `docs/uat_kit.md` with 3–5 real vendors and fill the result sheet. |
| T5.5 | Review DRAFT documents and perform the live 5-minute demo using `docs/demo_script.md`. |

Also: replace `DEMO_PASSWORD` before any public deployment (production mode refuses `demo123`), and review the DRAFT documents in `docs/`.

## (d) How to run the app locally

```bash
make install
make run        # http://localhost:8000  (login: demo / demo123)
```

Optional: `make seed` (normally the app auto-seeds an empty database), `make test`, `make verify`, `make report`.

## Verification evidence

- `make verify`: 139 pytest tests pass + `scripts/smoke.py` asserts the full flow (login → create business/product → 3 days → stage H3 with ordered quantiles/confidence/reasons → 4 more days → H7 → CSV import).
- Fresh `.venv` created from `requirements.txt` only: same 139 tests + smoke pass.
- `APP_ENV=production scripts/run_prod.sh` with SQLite: `/healthz` returns `{"status":"ok","db":"ok"}`; session cookie `secure; httponly; samesite=lax`.
- Browser-checked live: H0/H3/H7 dashboards, recommendation cards, mobile single-column layout at 390 px, daily sales form, product add/edit validation, history chart/filter, CSV import valid/invalid.
- `make report`: H0 WAPE 41.4% vs global baseline 54.1%; H7 39.8%; P10–P90 coverage 82.9–86.6%. Synthetic data only — no real-world accuracy claimed.
- `requirements.txt` contains only the allowed dependencies; no TODO/FIXME placeholders outside the bug log.
