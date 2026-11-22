# Panduan Pengguna ColdStart Kitchen

Panduan satu halaman untuk pedagang makanan/minuman yang belum punya catatan penjualan rapi.

1. **Masuk.** Buka aplikasi, isi nama pengguna `demo` dan kata sandi `demo123` (akun demo), lalu klik **Masuk**.
2. **Pilih usaha.** Di bagian atas dashboard, pilih usaha pada menu **Usaha**. Tanggal produksi otomatis besok; ubah bila perlu.
3. **Baca rekomendasi.** Tiap kartu menampilkan jumlah produksi yang disarankan ("Produksi ± 24 porsi"), rentang **P10–P90**, label keyakinan (Rendah/Sedang/Tinggi), dan tahap data **H0/H3/H7**.
4. **Lihat alasan.** Klik **Mengapa rekomendasi ini?** untuk melihat dasar perhitungan: jumlah hari data, pola hari, hari kehabisan stok, dan margin per porsi.
5. **Lengkapi menu.** Buka **Usaha & Menu**, isi nama produk, kategori, harga jual, dan biaya per porsi. Harga jual harus lebih besar dari biaya.
6. **Catat penjualan harian.** Buka **Catat Penjualan**, pilih tanggal (tidak boleh besok/lusa), isi jumlah terjual tiap produk, centang **Kehabisan stok** bila dagangan habis sebelum tutup, lalu **Simpan penjualan**.
7. **Impor data lama (opsional).** Buka **Impor CSV**, unduh contoh, isi `date,product,qty_sold,sold_out`, unggah. Bila ada galat, aplikasi menampilkan nomor baris yang bermasalah dan tidak menyimpan apa pun.
8. **Pantau riwayat.** Buka **Riwayat** untuk melihat tabel penjualan dan grafik 14 hari terakhir; atur rentang tanggal lalu klik **Filter**.
9. **Ulangi tiap hari.** Setelah 3 hari data, tahap naik ke **H3**; setelah 7 hari menjadi **H7**, dan rekomendasi makin mengikuti pola usaha Anda.

## Tiga tips

- Catat **setiap hari**, termasuk hari libur dan hari sepi; data kosong membuat rekomendasi tetap di tahap awal.
- Centang **Kehabisan stok** hanya bila benar-benar habis; aplikasi menaikkan estimasi permintaan 15% untuk hari itu.
- Perbarui harga dan biaya bila berubah — target peluang cukup stok dihitung dari margin, bukan hanya dari rata-rata penjualan.
