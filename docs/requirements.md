# Kebutuhan Fungsional dan Kriteria Penerimaan

Dokumen ini menjadi kontrak pengujian untuk ColdStart Kitchen. Setiap kebutuhan fungsional (FR) memiliki kriteria penerimaan dalam format **Given/When/Then**. ID FR dipakai sebagai awalan nama tes pytest (contoh: `test_fr01_...`).

Aplikasi melayani satu akun demo dan tiga usaha contoh (H0, H3, H7). Tidak ada registrasi mandiri, pembayaran, atau integrasi eksternal.

## FR-01 Login, logout, dan sesi

**Given** pengguna belum masuk, **when** membuka halaman apa pun selain `/login` dan `/healthz`, **then** pengguna diarahkan ke `/login` (halaman) atau menerima 401 (API).
**Given** kredensial demo yang benar, **when** `POST /login` dikirim, **then** sesi dibuat dan pengguna diarahkan ke dashboard.
**Given** kata sandi salah, **when** login dikirim, **then** respons 401 dengan pesan Indonesia dan tidak ada sesi.
**Given** pengguna sudah masuk, **when** `POST /logout`, **then** sesi dihapus dan pengguna diarahkan ke `/login`.

## FR-02 Profil usaha

**Given** pengguna masuk, **when** `POST /api/businesses` dengan nama, tipe usaha, tipe lokasi, dan `capacity_factor` valid, **then** usaha dibuat dan dimiliki pengguna tersebut.
**Given** usaha milik pengguna, **when** `GET /api/businesses/{id}` atau `PUT`, **then** data terbaca/diperbarui.
**Given** tipe usaha/tipe lokasi di luar kosakata, **when** menyimpan, **then** respons 422 dengan pesan validasi.

## FR-03 Menu: tambah, ubah, nonaktifkan

**Given** usaha milik pengguna, **when** `POST /api/businesses/{id}/products` dengan nama, kategori, harga, biaya, harga sisa, **then** produk aktif dibuat.
**Given** produk aktif, **when** `DELETE /api/products/{id}`, **then** produk menjadi `active=false` (soft delete) dan hilang dari daftar aktif serta rekomendasi.
**Given** `price <= 0` atau `unit_cost < 0` atau kategori di luar kosakata, **when** menyimpan, **then** 422.

## FR-04 Isolasi kepemilikan data

**Given** pengguna A masuk, **when** mengakses usaha/produk/penjualan milik pengguna B lewat API, **then** respons 404 (bukan 403, agar keberadaan data tidak bocor).

## FR-05 Pencatatan penjualan harian

**Given** usaha dengan 5 produk aktif, **when** `POST /sales/new` untuk satu tanggal dengan kuantitas tiap produk dan centang `sold_out` opsional, **then** 5 baris tersimpan.
**Given** tanggal yang sama dikirim ulang, **when** disimpan, **then** baris diperbarui (upsert), bukan diduplikasi.
**Given** tanggal di masa depan atau kuantitas negatif/non-integer, **when** menyimpan, **then** 422 dan tidak ada baris tersimpan.

## FR-06 Riwayat penjualan

**Given** data penjualan tersimpan, **when** membuka `/sales` dengan filter tanggal, **then** tabel per produk dan grafik batang 14 hari terakhir tampil sesuai rentang.
**Given** parameter `from`/`to`, **when** `GET /api/products/{id}/sales`, **then** hanya baris dalam rentang (inklusif) yang dikembalikan.

## FR-07 Impor CSV valid

**Given** berkas CSV berheader `date,product,qty_sold[,sold_out]` dengan baris valid, **when** `POST /api/businesses/{id}/sales/import`, **then** semua baris tersimpan dalam satu transaksi dan jumlah baris yang diterima dikembalikan.

## FR-08 Impor CSV tidak valid

**Given** berkas dengan header salah, tanggal buruk/masa depan, kuantitas negatif/non-integer, nama produk tidak dikenal, duplikat `(date, product)`, lebih dari 5.000 baris, lebih dari 1 MB, atau bukan UTF-8, **when** diimpor, **then** respons 422 berisi `errors: [{line, message}]` dan **tidak ada** baris yang tersimpan (all-or-nothing).

## FR-09 Rekomendasi H0 (tanpa data)

**Given** produk tanpa satu pun baris penjualan, **when** `GET /api/products/{id}/recommendation`, **then** `stage="H0"`, `n_days=0`, rata-rata positif, `p10 ≤ p50 ≤ p90`, `recommended_qty` bilangan bulat ≥ 0, dan `neighbor_count ≥ 1` bila data referensi tersedia.

## FR-10 Rekomendasi H3

**Given** produk dengan tepat 3 hari penjualan, **when** rekomendasi diminta, **then** `stage="H3"` dan `n_days=3`.

## FR-11 Rekomendasi H7 dan pembaruan dengan data baru

**Given** produk dengan 7 hari penjualan, **when** rekomendasi diminta, **then** `stage="H7"`.
**Given** rekomendasi awal, **when** pengguna menambah penjualan baru, **then** `mean`, `p50`, atau `n_days` berubah (hasil tidak statis).

## FR-12 Tampilan rentang P10–P90

**Given** kartu rekomendasi, **when** dashboard dirender, **then** kartu menampilkan kuantitas produksi, rentang `P10 … – P90 …`, tahap H0/H3/H7, dan lencana keyakinan dengan teks (bukan hanya warna).

## FR-13 Aturan label keyakinan

**Given** `n < 3`, **then** label `rendah`; `3 ≤ n < 7` → `sedang`; `n ≥ 7` → `tinggi`. **Given** rasio `(P90−P10)/max(P50,1) > 1.2`, **then** label turun satu tingkat (minimum `rendah`). **Given** `low_reference`, **then** label dipaksa `rendah`.

## FR-14 Alasan dalam Bahasa Indonesia

**Given** rekomendasi, **when** JSON dikembalikan, **then** `reasons` berisi minimal satu kalimat Indonesia yang menjelaskan tahap/data, dan memuat alasan hari kerja, kehabisan stok, serta margin bila kondisinya terpenuhi.

## FR-15 Tata letak responsif

**Given** lebar layar < 640 px, **when** dashboard dibuka, **then** kartu tersusun satu kolom; **given** lebar ≥ 640 px, **then** tersusun grid. Halaman memuat meta viewport dan CSS memiliki media query.

## FR-16 Data demo otomatis

**Given** basis data kosong, **when** aplikasi mulai, **then** pengguna `demo` (dapat diubah lewat `DEMO_USER`/`DEMO_PASSWORD`) dan tiga usaha dengan 5 produk serta riwayat 0/3/7 hari dibuat. **Given** basis data sudah berisi pengguna, **when** aplikasi mulai ulang, **then** seed tidak menggandakan data.

## FR-17 Kesiapan produksi

**Given** `APP_ENV=production` tanpa `SECRET_KEY`, **when** aplikasi mulai, **then** aplikasi menolak start dengan pesan jelas.
**Given** `APP_ENV=production` dengan `DEMO_PASSWORD=demo123`, **then** aplikasi menolak start.
**Given** 10 percobaan login gagal dalam 15 menit untuk IP+username yang sama, **when** percobaan ke-11, **then** 429.
**Given** aplikasi berjalan, **when** `GET /healthz`, **then** `{"status":"ok","db":"ok"}`.

## FR-18 Halaman formulir dan impor

**Given** pengguna masuk, **when** membuka `/business`, `/sales/new`, dan `/import`, **then** ketiganya 200, formulir memakai teks Indonesia, dan galat validasi ditampilkan sebaris (inline) tanpa memuat ulang seluruh halaman.

## Kebutuhan non-fungsional

- **NFR-01 Kinerja:** satu permintaan rekomendasi untuk usaha dengan 50 produk selesai < 1 detik pada laptop pengembangan (diukur di tes, ambang longgar 3 detik untuk CI).
- **NFR-02 Offline:** tidak ada panggilan jaringan eksternal saat aplikasi berjalan; seluruh aset dilayani lokal.
- **NFR-03 Basis data:** SQLite untuk pengembangan, PostgreSQL untuk produksi melalui `DATABASE_URL`; tidak ada SQL khusus SQLite.
- **NFR-04 Ukuran:** backend ≤ ~1.500 LOC, ML ≤ ~400 LOC, ≤ 7 templat HTML, 1 CSS, ≤ 3 JS.
