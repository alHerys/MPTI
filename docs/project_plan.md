# Project Plan ColdStart Kitchen

> **Status: DRAF.** Ringkasan rencana; sumber otoritatif tetap `PLAN.md`.

## 1. Lingkup

Sesuai `PLAN.md` bagian 2: satu aplikasi web, satu basis data, satu akun demo, tiga usaha contoh (H0/H3/H7), hingga 50 produk dan 365 hari per produk, impor CSV 5.000 baris/1 MB, dataset referensi sintetis 24 usaha, model numpy/scipy.

Di luar lingkup: multi-tenancy, registrasi, pembayaran, integrasi eksternal, feed cuaca/event, deep learning, GPU, aplikasi native, i18n selain Indonesia, panel admin, email, worker, microservices, audit fairness, data pelanggan nyata.

## 2. Ringkasan WBS (29 deliverable)

| WBS | Deliverable | Status |
|---|---|---|
| 1.1–1.5 | Business case, charter, plan, requirements, wireframe/prototipe | DRAF / selesai |
| 2.1–2.6 | Skema DB, dataset referensi, profil+menu, penjualan harian, API penjualan, impor CSV | selesai |
| 3.1–3.7 | Prior cold-start, update H0/H3/H7, distribusi, optimasi alpha, penjelasan, API rekomendasi, laporan evaluasi | selesai |
| 4.1–4.6 | Dashboard, kartu rekomendasi, riwayat, integrasi frontend, akun demo, deploy | selesai (deploy go-live: manusia) |
| 5.1–5.5 | Kasus uji, UAT, regresi, panduan pengguna, laporan akhir + demo | selesai (UAT/demo: manusia) |

## 3. Jadwal sprint

| Sprint | Fokus | Deliverable utama |
|---|---|---|
| Sprint 1 | Fondasi & analisis | 1.1–1.4, 2.1 |
| Sprint 2 | Data & UI dasar | 2.2–2.6, 1.5 |
| Sprint 3 | Model | 3.1–3.4 |
| Sprint 4 | Penjelasan, evaluasi, web app | 3.5–3.7, 4.1–4.5 |
| Sprint 5 | Deploy, uji, dokumen, demo | 4.6, 5.1–5.5 |

## 4. Biaya

Tidak ada klaim anggaran pasti. Biaya kas minimum: hosting gratis (Render free) atau listrik Mac mini yang sudah ada. Biaya utama adalah waktu pengembangan dan waktu pengujian manusia.

## 5. Register risiko

| ID | Risiko | Dampak | Kemungkinan | Mitigasi |
|---|---|---|---|---|
| R1 | Data awal terlalu sedikit (sparse) | Rekomendasi kabur | Tinggi | Prior dari usaha serupa; rentang lebar ditampilkan jujur; label keyakinan rendah |
| R2 | Model terlalu percaya diri | Keputusan produksi salah | Sedang | Lebar interval menurunkan label; koreksi dispersi `CV0²·K/(n+K)`; tinjauan berkala |
| R3 | Masukan berisik/salah (qty salah, hari terlewat) | Estimasi menyimpang | Tinggi | Validasi form/CSV, upsert, tampilan riwayat, alasan eksplisit |
| R4 | Batas data sintetis | Klaim berlebihan | Tinggi | Keterbatasan di laporan model; tidak ada klaim akurasi nyata |
| R5 | Adopsi rendah | Manfaat tidak terwujud | Sedang | Alur 1 layar, impor CSV, panduan 1 halaman, UAT |
| R6 | Kegagalan deploy | Aplikasi tidak dapat diakses | Sedang | Dua rute deploy, `/healthz`, launchd KeepAlive, checklist |
| R7 | Kebocoran data antar pengguna | Kepercayaan rusak | Rendah | Kepemilikan dicek di setiap endpoint; tes 404 lintas pengguna |
| R8 | Kehilangan data saat restart (Render) | Riwayat hilang | Sedang | Postgres pada `render.yaml`; dokumentasi backup SQLite |

## 6. Kualitas dan verifikasi

- `make verify` = `pytest -q` + `scripts/smoke.py`.
- `docs/test_cases.md` memetakan setiap FR ke tes nyata; tes memverifikasi nama tes yang dirujuk.
- `docs/bug_log.md` mencatat bug yang ditemukan dan perbaikannya.
- Laporan evaluasi dihasilkan ulang oleh `make report`, bukan angka manual.

## 7. Serah terima

Agen menyerahkan repo siap jalan, dokumen DRAF, artefak deploy, dan bukti uji. Manusia melakukan go-live, UAT, tinjauan dokumen, dan demo langsung.
