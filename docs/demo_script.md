# Skrip Demo 5 Menit ColdStart Kitchen

> **Status: DRAF + HUMAN.** Naskah siap; pelaksanaan demo langsung adalah tugas manusia.

## Persiapan (sebelum waktu demo)

- Aplikasi berjalan: `make run` (lokal) atau URL deploy.
- Data demo ter-seed otomatis (`demo` / `demo123`).
- Buka browser pada `/login`, ukuran jendela seperti ponsel (opsional untuk penutup).

## Alur 5 menit

**0:00–0:30 — Masalah.**
"Warung tanpa catatan penjualan menebak jumlah masak. Kelebihan = bahan terbuang; kekurangan = pelanggan kecewa."

**0:30–1:00 — Masuk dan tunjukkan tiga usaha.**
Masuk `demo` / `demo123`. Tunjukkan pemilih usaha: **Warung Bu Sari (H0)**, **Kafe Kampus (H3)**, **Gerobak Pak Joko (H7)**.

**1:00–2:00 — H0: titik awal tanpa data.**
Pilih Warung Bu Sari. Tunjuk kartu "Nasi Ayam": angka produksi, rentang P10–P90, label **Rendah**, tahap **H0**. Buka **Mengapa rekomendasi ini?** — "estimasi dari 5 usaha serupa".

**2:00–3:00 — H3: data mulai masuk.**
Pilih Kafe Kampus. Tunjukkan tahap **H3** dan alasan "Berdasarkan 3 hari data Anda dan usaha serupa". Sebutkan 3 hari data sudah mengubah estimasi.

**3:00–3:45 — H7: pola sendiri.**
Pilih Gerobak Pak Joko. Tunjukkan **H7**, label yang lebih tinggi, dan alasan pola hari serta stockout. Sebutkan bahwa rentang menyempit saat data bertambah.

**3:45–4:30 — Catat penjualan.**
Buka **Catat Penjualan**, isi angka hari ini untuk beberapa produk, centang satu **Kehabisan stok**, simpan. Kembali ke dashboard dan tunjukkan angka berubah.

**4:30–5:00 — Transparansi dan penutup.**
Buka **Riwayat** (grafik 14 hari). Tutup dengan: "Model hanya numpy/scipy, tanpa API eksternal; rentang dan keyakinan ditampilkan jujur, dan data sintetis diuji terbuka di laporan evaluasi."

## Cadangan bila sesuatu gagal

- Dashboard kosong: muat ulang; cek `/healthz`.
- Lupa kata sandi demo: cek `DEMO_PASSWORD` pada environment.
- Tidak ada koneksi: jalankan lokal (`make run`) karena aplikasi tidak butuh internet.
