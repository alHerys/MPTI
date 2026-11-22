# STATUS
Last updated: 2026-11-22T00:10:00Z   Current task: T4.1

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
| T4.1 | 4.1 | AUTO | TODO | |
| T4.2 | 4.2 | AUTO | TODO | |
| T4.3 | 4.3 | AUTO | TODO | |
| T4.4 | 4.4 | AUTO | TODO | |
| T4.5 | 4.5 | AUTO | DONE | login/logout/session, env demo creds, idempotent auto-seed H0/H3/H7, rate limit 429; 95 tests |
| T4.6 | 4.6 | AUTO+HUMAN | TODO | |
| T5.1 | 5.1 | AUTO | TODO | |
| T5.2 | 5.2 | HUMAN | TODO | |
| T5.3 | 5.3 | AUTO | TODO | |
| T5.4 | 5.4 | DRAFT | TODO | |
| T5.5 | 5.5 | DRAFT+HUMAN | TODO | |
| T1.1 | 1.1 | DRAFT | TODO | |
| T1.2 | 1.2 | DRAFT | TODO | |
| T1.3 | 1.3 | DRAFT | TODO | |
| T9 | - | AUTO | TODO | |

## Blocked log
(none)
