# STATUS
Last updated: 2026-11-22T14:31:49Z   Current task: none (complete)

| Task | WBS | Type | Status | Notes |
|---|---|---|---|---|
| T0 | - | AUTO | DONE | make verify: 2 passed, smoke ok; commit T0 |
| T1.4 | 1.4 | DRAFT | DONE | 18 FR + NFR with GWT criteria; tests tagged by FR id |
| T1.5 | 1.5 | AUTO | DONE | ASCII wireframes + static prototype (6 screens, no external assets) |
| T2.1 | 2.1 | AUTO | DONE | 6 tests: CRUD roundtrip, unique(product,date), qty check, scrypt |
| T2.2 | 2.2 | AUTO | DONE | 168 series x 90 days = 15,120 rows; seed-42 hash test; README declares synthetic |
| T2.3 | 2.3 | AUTO | DONE | CRUD + soft delete + validation 422 + cross-user 404; 17 tests total |
| T2.4 | 2.4 | AUTO | DONE | POST /sales/new all-or-nothing multi-product form; 27 tests |
| T2.5 | 2.5 | AUTO | DONE | upsert idempotent, inclusive range filter, validation, ownership; 23 tests |
| T2.6 | 2.6 | AUTO | DONE | strict CSV parser (header/date/future/qty/product/dup/size/UTF-8) all-or-nothing; 41 tests |
| T3.1 | 3.1 | AUTO | DONE | reference features + kNN + weighted-median prior, fallbacks; 7 tests |
| T3.2 | 3.2 | AUTO | DONE | shrinkage w=n/(n+4), stages, stockout 1.15 uplift, weekday blend n>=7; 6 tests |
| T3.3 | 3.3 | AUTO | DONE | nbinom P10/P50/P90 over 504 combos, width non-increasing; 4 tests |
| T3.4 | 3.4 | AUTO | DONE | newsvendor alpha, clamping, worked examples, 422 path; 8 tests |
| T3.5 | 3.5 | AUTO | DONE | confidence rules + Indonesian reason templates in fixed order; 6 tests |
| T3.6 | 3.6 | AUTO | DONE | pure engine + product/business recommendation APIs, ownership; 84 tests total |
| T3.7 | 3.7 | AUTO | DONE | LOO-business backtest: H0 WAPE 41.4% vs global 54.1%, H7 39.8%, coverage 82.9-86.6%; make report |
| T4.1 | 4.1 | AUTO | DONE | dashboard layout, business selector, date default, mobile-first CSS (640px), viewport meta |
| T4.2 | 4.2 | AUTO | DONE | card template partial: qty, range track+marker, confidence badge w/ text, stage, reasons |
| T4.3 | 4.3 | AUTO | DONE | /sales history table + 14-day inline SVG bars + date filter; verified live |
| T4.4 | 4.4 | AUTO | DONE | dashboard.js fetches /api/businesses/{id}/recommendations?date=; verified live in browser for H0/H3/H7 |
| T4.5 | 4.5 | AUTO | DONE | login/logout/session, env demo creds, idempotent auto-seed H0/H3/H7, rate limit 429; 95 tests |
| T4.6 | 4.6 | AUTO+HUMAN | HUMAN | Code+artifacts DONE (prod refusals, secure cookie, 429, healthz, run_prod.sh verified on sqlite; docker build UNVERIFIED — docker absent; Postgres checked by review only). HUMAN: perform deploy and record live URL. |
| T5.1 | 5.1 | AUTO | DONE | 40 TC mapping all FR; test parses doc and verifies referenced pytest names exist |
| T5.2 | 5.2 | HUMAN | HUMAN | docs/uat_kit.md created (7 scenarios + result sheet); execution needs human testers |
| T5.3 | 5.3 | AUTO | DONE | edge cases (price<=cost, zero sales, dup dates, future, huge qty, unicode, CRLF+BOM) + bug_log.md; 134 tests |
| T5.4 | 5.4 | DRAFT | DONE | one-page Indonesian guide, 9 steps + 3 tips, self-tested live |
| T5.5 | 5.5 | DRAFT+HUMAN | HUMAN | laporan_akhir.md + demo_script.md (DRAF); live demo HUMAN |
| T1.1 | 1.1 | DRAFT | DONE | business_case.md (DRAF): problem/benefit/feasibility, external stats marked unverified, no SteadyMouse row |
| T1.2 | 1.2 | DRAFT | DONE | project_charter.md (DRAF): objectives, MOV, stakeholders, assumptions, constraints |
| T1.3 | 1.3 | DRAFT | DONE | project_plan.md (DRAF): scope, WBS summary, 5-sprint schedule, cost note, 8-risk register |
| T9 | - | AUTO | DONE | DoD audit passed: make verify 139 tests + smoke; fresh-venv verify; all docs; no placeholders; prod healthz ok; DONE.md written |

## Blocked log
(none)
