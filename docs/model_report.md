# Laporan Evaluasi Model ColdStart Kitchen

Dokumen ini dihasilkan otomatis oleh `python scripts/evaluate.py` (target `make report`). Angka di bawah berasal dari backtest *leave-one-business-out* pada dataset referensi sintetis.

## Data dan metode

- Dataset: `data/reference_sales.csv` — 168 seri produk dari 24 usaha fiktif, 90 hari per seri.
- Backtest: untuk setiap seri, satu usaha dikeluarkan dari data referensi; model hanya melihat usaha lain. Riwayat yang dipakai: 0 hari (H0), 3 hari pertama (H3), dan 7 hari pertama (H7).
- Prediksi dibuat untuk 14 hari setelah cutoff (hari ke-31 s.d. 44), lalu dibandingkan dengan penjualan aktual seri tersebut.
- Asumsi biaya: `unit_cost = 60% × harga` karena metadata referensi tidak memuat biaya; nilai sisa = 0. Rasio kritis alpha = 0,4.
- Rata-rata global seluruh seri: **24.77 porsi/hari** (baseline a).

## Tabel metrik per tahap

| Tahap | Prediksi | WAPE model | WAPE global mean | WAPE rata-rata sendiri | Pinball P10 / P50 / P90 | Coverage P10–P90 |
|---|---|---|---|---|---|---|
| H0 | 2352 | **41.4%** | 54.1% | — | 1.83 / 5.21 / 3.09 | 86.6% |
| H3 | 2352 | **39.7%** | 54.1% | 37.9% | 1.78 / 4.99 / 2.87 | 85.1% |
| H7 | 2352 | **39.8%** | 54.1% | 37.9% | 1.76 / 5.00 / 2.78 | 82.9% |

Pinball loss: makin kecil makin baik. Coverage ideal 80% (0,80).

Catatan jujur: pada H3/H7, WAPE baseline "rata-rata sendiri" (tanpa shrinkage) sedikit lebih rendah daripada model, karena baseline tersebut sudah memakai data seri yang dievaluasi. Model tetap unggul pada laba newsvendor karena memakai sebaran penuh (P10/P90), bukan hanya rata-rata.


## Perbandingan baseline — WAPE

| Tahap | Model | Global mean | Rata-rata sendiri (tanpa shrinkage) | Selisih model vs global |
|---|---|---|---|---|
| H0 | 41.4% | 54.1% | — (tidak tersedia) | +12.6 poin persentase |
| H3 | 39.7% | 54.1% | 37.9% | +14.4 poin persentase |
| H7 | 39.8% | 54.1% | 37.9% | +14.2 poin persentase |

## Newsvendor — laba rata-rata per prediksi harian

| Tahap | Model | Qty = global mean | Qty = rata-rata sendiri | Model vs global | Model vs sendiri |
|---|---|---|---|---|---|
| H0 | **Rp56.136** | Rp35.822 | — | +56.7% | — |
| H3 | **Rp57.910** | Rp35.822 | Rp56.945 | +61.7% | +1.7% |
| H7 | **Rp57.818** | Rp35.822 | Rp56.945 | +61.4% | +1.5% |

## Kriteria penerimaan (soft)

- ✅ Lulus — WAPE H0 ≤ WAPE baseline global mean (41.4% vs 54.1%)
- ✅ Lulus — WAPE H3 ≤ WAPE H0 (39.7% vs 41.4%)
- ✅ Lulus — WAPE H7 ≤ WAPE H0 (39.8% vs 41.4%)
- ✅ Lulus — Coverage P10–P90 di antara 0,65 dan 0,92 (semua tahap) (H0=86.6%, H3=85.1%, H7=82.9%)

## Keterbatasan

1. **Data sintetis.** Seluruh data referensi dibangkitkan oleh `scripts/gen_reference.py` (seed 42). Keunggulan model dibanding baseline mencerminkan karakter generator, bukan akurasi dunia nyata. Tidak ada klaim akurasi nyata di dokumen ini.
2. **Penyesuaian stockout adalah heuristik.** Hari dengan `sold_out=true` dikalikan 1.15; ini bukan estimasi permintaan yang tervalidasi secara statistik.
3. **Belum ada validasi dengan pedagang sungguhan.** Tidak ada UAT atau data lapangan yang dipakai; hasil ini hanya bukti bahwa pipeline berjalan dan lebih baik daripada baseline pada data sintetis.
4. **Asumsi biaya.** Biaya per porsi diasumsikan 60% dari harga karena metadata referensi tidak memuat biaya; angka laba bersifat ilustratif.
