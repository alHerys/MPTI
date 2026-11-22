# Data Referensi ColdStart Kitchen

## Pernyataan penting

**Seluruh data di folder ini adalah data sintetis (buatan).** Data ini **bukan data asli** pedagang, bukan hasil survei, dan tidak merepresentasikan penjualan nyata di lapangan. Dataset dibuat hanya untuk menguji dan mendemonstrasikan model rekomendasi produksi.

## Cara pembuatan

Data dibangkitkan oleh `scripts/gen_reference.py` dengan **seed 42**, sehingga hasilnya dapat direproduksi persis (byte-per-byte) dengan perintah:

```bash
python scripts/gen_reference.py --seed 42
```

Proses pembangkitan:

1. 24 usaha fiktif dibuat, masing-masing memiliki 6 sampai 8 produk (total 168 seri produk).
2. Setiap usaha diberi kombinasi `business_type` (`warung, cafe, gerobak, bakery, kantin`), `location_type` (`kampus, kantor, permukiman, pasar`), dan `capacity_factor` (0,8–2,0).
3. Setiap produk diberi kategori (`nasi, mie, snack, minuman, roti`), harga dalam rentang wajar per kategori, rata-rata dasar penjualan, dan dispersi acak 0,05–0,30.
4. Penjualan harian selama 90 hari (mulai 1 Juni 2026) dibangkitkan dari distribusi **Negative Binomial** dengan rata-rata:

   `rata-rata = base_mean × faktor_hari[kategori][hari] × noise`

   dan dispersi per produk. `noise` adalah faktor lognormal kecil (σ = 0,08) untuk variasi antarhari.
5. Faktor hari kerja per kategori berkisar sekitar 1,0; kategori makanan berat (nasi, mie) lebih ramai pada Jumat–Sabtu dan lebih sepi pada Minggu, sedangkan `minuman` dan `roti` lebih landai.

## Berkas

| Berkas | Isi |
|---|---|
| `reference_sales.csv` | `series_id,date,qty` — 15.120 baris (168 seri × 90 hari) |
| `reference_meta.csv` | `series_id,business_type,location_type,category,price,capacity_factor,base_mean,dispersion` — 168 baris |

## Batasan

Karena data sintetis, selisih performa model dibandingkan baseline dalam `docs/model_report.md` mencerminkan karakter generator, **bukan** akurasi dunia nyata. Validasi dengan pedagang sungguhan belum dilakukan.
