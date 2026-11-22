# Laporan Akhir ColdStart Kitchen

> **Status: DRAF + HUMAN.** Ringkasan ini perlu ditinjau manusia; demonstrasi langsung dilakukan manusia.

## 1. Apa yang dibangun

ColdStart Kitchen adalah aplikasi web untuk pedagang makanan/minuman tanpa riwayat penjualan. Pengguna mengisi profil usaha, menu (harga, biaya, nilai sisa), dan penjualan harian. Aplikasi menampilkan rekomendasi jumlah produksi besok dengan:

- kuantitas produksi yang dioptimalkan terhadap margin (`recommended_qty`);
- rentang **P10 – P50 – P90** dari distribusi Negative Binomial;
- label keyakinan **rendah / sedang / tinggi** (dengan teks, bukan hanya warna);
- tahap data **H0 / H3 / H7**;
- daftar alasan berbahasa Indonesia yang bisa dibuka pengguna.

Tidak ada panggilan AI eksternal. Seluruh "kecerdasan" adalah model statistik di `app/ml/` (numpy + scipy).

## 2. Peta ke WBS (29 deliverable)

| WBS | Deliverable | Bukti |
|---|---|---|
| 1.1 | Business Case | `docs/business_case.md` |
| 1.2 | Project Charter | `docs/project_charter.md` |
| 1.3 | Project Plan & Risks | `docs/project_plan.md` |
| 1.4 | Requirements & acceptance | `docs/requirements.md` (18 FR + NFR, Given/When/Then) |
| 1.5 | Wireframe & prototype | `docs/wireframe.md`, `prototype/index.html` |
| 2.1 | DB schema | `app/models.py`, `tests/test_t2_1_models.py` |
| 2.2 | Reference dataset | `data/reference_sales.csv` (15.120 baris), `data/README_data.md`, `scripts/gen_reference.py` |
| 2.3 | Business profile & menu | `app/routers/businesses.py`, `/business`, `app/static/forms.js` |
| 2.4 | Daily sales entry | `POST /sales/new`, `app/templates/sales_new.html` |
| 2.5 | Sales API | `app/routers/sales.py` |
| 2.6 | CSV import | `app/csv_import.py`, `/import` |
| 3.1 | Cold-start model | `app/ml/priors.py`, `app/ml/reference.py` |
| 3.2 | Update H0/H3/H7 | `app/ml/update.py` |
| 3.3 | Distribution & quantiles | `app/ml/distribution.py` |
| 3.4 | Cost optimization | `app/ml/optimize.py` |
| 3.5 | Explanation & confidence | `app/ml/explain.py` |
| 3.6 | Recommendation API | `app/ml/engine.py`, `app/routers/recommendations.py` |
| 3.7 | Evaluation report | `scripts/evaluate.py` → `docs/model_report.md` |
| 4.1 | Dashboard | `app/templates/dashboard.html` |
| 4.2 | Recommendation card | `<template id="rec-card-template">` + `dashboard.js` |
| 4.3 | Sales history | `app/templates/sales_history.html` (inline SVG) |
| 4.4 | Frontend–API integration | `GET /api/businesses/{id}/recommendations` |
| 4.5 | Demo account | `scripts/seed_demo.py`, auto-seed saat start |
| 4.6 | Deployment | `Dockerfile`, `render.yaml`, `scripts/run_prod.sh`, `deploy/*.plist`, `docs/deploy.md` (go-live: manusia) |
| 5.1 | Functional test cases | `docs/test_cases.md` (40 TC), tes memverifikasi tautan |
| 5.2 | UAT results | `docs/uat_kit.md` (pelaksanaan: manusia) |
| 5.3 | Regression & bugs | 134 tes, `docs/bug_log.md` |
| 5.4 | User guide | `docs/panduan_pengguna.md` |
| 5.5 | Final report & demo | dokumen ini, `docs/demo_script.md` (demo: manusia) |

## 3. Ringkasan evaluasi

Dari `docs/model_report.md` (backtest leave-one-business-out, data sintetis, horizon 14 hari):

| Tahap | WAPE model | WAPE global mean | Coverage P10–P90 |
|---|---|---|---|
| H0 | 41,4% | 54,1% | 86,6% |
| H3 | 39,7% | 54,1% | 85,1% |
| H7 | 39,8% | 54,1% | 82,9% |

Laba newsvendor rata-rata per prediksi harian: model H0 Rp56.136 vs baseline global Rp35.822 (+56,7%); pada H7 model Rp57.818 vs rata-rata sendiri Rp56.945 (+1,5%). Seluruh kriteria soft lulus. Angka ini mencerminkan generator sintetis, **bukan akurasi dunia nyata**.

## 4. Keterbatasan

1. Data referensi sintetis; tidak ada klaim akurasi nyata.
2. Penyesuaian hari kehabisan stok (×1,15) adalah heuristik.
3. Belum ada validasi dengan pedagang sungguhan (UAT belum dijalankan).
4. Asumsi biaya 60% harga pada evaluasi; angka laba ilustratif.
5. Deploy publik belum dilakukan; Postgres belum diuji langsung (hanya tinjauan kode).

## 5. Langkah berikutnya

1. Jalankan UAT dengan 3–5 pedagang (`docs/uat_kit.md`), catat hasil.
2. Deploy ke Render atau Mac mini + Cloudflare Tunnel; ganti `DEMO_PASSWORD`.
3. Validasi lapangan: bandingkan rekomendasi dengan keputusan pedagang selama 2–4 minggu; ukur sisa produksi.
4. Bila data nyata terkumpul, ganti/dukung dataset referensi dan kalibrasi ulang dispersi.
5. Tinjau dokumen DRAF dan demo langsung sesuai `docs/demo_script.md`.
