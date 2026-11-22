# Wireframe ColdStart Kitchen

Wireframe teks (ASCII). Prototipe yang bisa diklik ada di `prototype/index.html` (data contoh statis, tanpa sumber daya eksternal, responsif).

Alur utama: **Login → Dashboard (rekomendasi) → Usaha & Menu → Catat Penjualan → Riwayat → Impor CSV**.

## 1. Login (`/login`)

```
+-------------------------------------------------------+
|  ColdStart Kitchen                                    |
|  Rekomendasi produksi untuk warung tanpa data histori |
|                                                       |
|  +-------------------------------------------------+  |
|  | Nama pengguna  [ demo                    ]      |  |
|  | Kata sandi     [ ********                ]      |  |
|  | [ Masuk ]                       (galat inline)   |  |
|  +-------------------------------------------------+  |
|  Akun demo: demo / demo123                            |
+-------------------------------------------------------+
```

Mobile: kartu penuh lebar, margin 16 px.

## 2. Dashboard (`/`)

```
+---------------------------------------------------------------+
| ColdStart Kitchen      Dashboard  Usaha  Catat  Riwayat  Impor |
| Keluar (demo)                                                  |
+---------------------------------------------------------------+
| Usaha: [ Warung Bu Sari v ]   Tanggal: [ 2026-11-23 ]          |
| Tahap data: H0 — belum ada penjualan                           |
+---------------------------------------------------------------+
| +---------------------------+  +---------------------------+   |
| | Nasi Ayam                 |  | Es Teh                    |   |
| | Produksi ± 24 porsi       |  | Produksi ± 30 porsi       |   |
| | P10 16 ======#==== P90 35 |  | P10 22 =====#===== P90 41 |   |
| | [Sedang]  H0              |  | [Rendah]  H0              |   |
| | v Mengapa?                |  | v Mengapa?                |   |
| |  - Belum ada data ...     |  |  - ...                    |   |
| +---------------------------+  +---------------------------+   |
+---------------------------------------------------------------+
```

- < 640 px: satu kolom.
- ≥ 640 px: grid dua kolom (atau lebih pada layar lebar).
- Kartu diisi JavaScript dari `/api/businesses/{id}/recommendations?date=`.

## 3. Usaha & Menu (`/business`)

```
+---------------------------------------------------------------+
| Profil Usaha                                                   |
| Nama [ Warung Bu Sari ]  Tipe [ warung v ]                     |
| Lokasi [ kampus v ]      Kapasitas [ 1.0 ]    [ Simpan ]       |
+---------------------------------------------------------------+
| Menu                                        [ + Tambah Produk ] |
| Nama          Kategori   Harga    Biaya   Sisa   Status  Aksi  |
| Nasi Ayam     nasi       12000    6000    0      aktif   [U][X]|
| Es Teh        minuman     5000    1500    0      aktif   [U][X]|
+---------------------------------------------------------------+
```

Form tambah/ubah muncul sebaris (expandable) dengan galat validasi di bawah tiap kolom.

## 4. Catat Penjualan (`/sales/new`)

```
+---------------------------------------------------------------+
| Catat Penjualan     Tanggal [ 2026-11-22 ]                     |
| Produk          Terjual   Kehabisan stok                       |
| Nasi Ayam       [  24  ]  [x]                                  |
| Es Teh          [  30  ]  [ ]                                  |
| ...                                                            |
| [ Simpan penjualan ]   (pesan sukses Indonesia)                |
+---------------------------------------------------------------+
```

Satu tanggal, satu baris per produk aktif. Mengirim ulang tanggal yang sama memperbarui data.

## 5. Riwayat (`/sales`)

```
+---------------------------------------------------------------+
| Riwayat Penjualan   Dari [2026-11-01] Sampai [2026-11-22] [Filter] |
+---------------------------------------------------------------+
| 14 hari terakhir (batang = porsi)                              |
|   |     #                                                      |
|   |  #  #  #     #                                              |
|   +-------------------                                         |
+---------------------------------------------------------------+
| Produk     Tanggal      Terjual   Kehabisan                    |
| Nasi Ayam  2026-11-22   24        ya                           |
+---------------------------------------------------------------+
```

## 6. Impor CSV (`/import`)

```
+---------------------------------------------------------------+
| Impor Penjualan CSV                                            |
| Format: date,product,qty_sold[,sold_out]      [Unduh contoh]   |
| [ Pilih berkas ]  [ Impor ]                                    |
| Hasil: 120 baris diterima.                                     |
| -- atau --                                                     |
| Galat:                                                         |
|  baris 7: tanggal tidak valid                                  |
|  baris 12: produk tidak dikenal                                |
+---------------------------------------------------------------+
```
