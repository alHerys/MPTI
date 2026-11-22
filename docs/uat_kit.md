# Kit UAT ColdStart Kitchen

Dokumen ini disiapkan untuk pengujian oleh pengguna nyata. **Pelaksanaan UAT adalah tugas manusia**; agen tidak dapat menjalankannya.

## Persiapan

- Aplikasi berjalan (lokal: `make run`, atau URL hasil deploy).
- Akun demo: `demo` / `demo123`.
- Penguji tidak perlu pengetahuan teknis.

## Skenario

### UAT-01 Masuk dan melihat rekomendasi
1. Buka alamat aplikasi.
2. Masuk dengan akun demo.
3. Perhatikan kartu rekomendasi pada dashboard.

**Diharapkan:** dashboard tampil, setiap produk punya angka produksi, rentang P10–P90, label keyakinan, dan tahap data.

### UAT-02 Memahami alasan rekomendasi
1. Pada salah satu kartu, klik **Mengapa rekomendasi ini?**
2. Baca kalimat yang muncul.

**Diharapkan:** penjelasan berbahasa Indonesia yang mudah dipahami, menyebut jumlah hari data dan/atau pola hari serta margin.

### UAT-03 Menambah produk baru
1. Buka **Usaha & Menu**.
2. Klik **+ Tambah produk**, isi nama, kategori, harga jual, dan biaya.
3. Simpan, lalu kembali ke dashboard.

**Diharapkan:** produk baru muncul di tabel menu dan di dashboard dengan rekomendasi tahap H0.

### UAT-04 Mencatat penjualan harian
1. Buka **Catat Penjualan**.
2. Pilih tanggal hari ini, isi jumlah terjual untuk tiap produk, centang kehabisan stok pada satu produk.
3. Simpan, lalu buka dashboard.

**Diharapkan:** pesan sukses muncul; setelah 3 hari data, tahap berubah menjadi H3 dan angka produksi ikut berubah.

### UAT-05 Impor CSV
1. Buka **Impor CSV**, unduh contoh CSV.
2. Isi 3 baris data, unggah, lalu impor.
3. Ulangi dengan berkas yang tanggalnya salah.

**Diharapkan:** berkas valid diterima dengan jumlah baris; berkas tidak valid ditolak, menampilkan nomor baris dan pesan galat, serta tidak menambah data.

### UAT-06 Melihat riwayat
1. Buka **Riwayat**.
2. Ubah rentang tanggal, klik **Filter**.

**Diharapkan:** tabel dan grafik 14 hari tampil; filter mengubah baris yang terlihat.

### UAT-07 Tampilan ponsel
1. Buka dashboard dari ponsel atau perkecil jendela browser.

**Diharapkan:** kartu tersusun satu kolom, teks tidak terpotong, tombol mudah ditekan.

## Lembar hasil

| Skenario | Hasil (Lulus/Gagal) | Catatan | Penguji | Tanggal |
|---|---|---|---|---|
| UAT-01 | | | | |
| UAT-02 | | | | |
| UAT-03 | | | | |
| UAT-04 | | | | |
| UAT-05 | | | | |
| UAT-06 | | | | |
| UAT-07 | | | | |

**Ringkasan:** ____ dari 7 skenario lulus. Kendala utama: ______________________________.

Tanda tangan penguji: ____________________  Tanggal: __________
