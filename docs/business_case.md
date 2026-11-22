# Business Case ColdStart Kitchen

> **Status: DRAF.** Dokumen ini belum ditinjau manusia. Setiap angka eksternal ditandai **"dikutip dari laporan riset; verifikasi sebelum dipresentasikan"** dan tidak boleh dianggap terverifikasi.

## 1. Masalah

Warung, kafe kecil, gerobak, dan pembuat kue rumahan umumnya memutuskan jumlah produksi harian berdasarkan perasaan. Tanpa catatan penjualan, keputusan ini menghasilkan dua kerugian sekaligus: **kelebihan produksi** (bahan terbuang, modal tertahan) dan **kekurangan produksi** (peluang penjualan hilang, pelanggan kecewa). Masalahnya bukan sekadar alat pencatatan: pada hari-hari pertama, pedagang memang belum punya data apa pun, sehingga aplikasi statistik biasa tidak bisa menolong.

Data pendukung yang lazim dikutip:
- Sekitar sepertiga pangan yang diproduksi dunia terbuang atau hilang setiap tahun. *Dikutip dari laporan riset; verifikasi sebelum dipresentasikan.*
- UMKM menyumbang mayoritas tenaga kerja dan sekitar 60% PDB Indonesia. *Dikutip dari laporan riset; verifikasi sebelum dipresentasikan.*
- Studi kasus vendor makanan menunjukkan sisa produksi harian 10–20% dari total porsi. *Dikutip dari laporan riset; verifikasi sebelum dipresentasikan.*

Angka di atas berguna untuk membingkai masalah, bukan untuk menjanjikan hasil. Klaim manfaat ColdStart Kitchen dibatasi pada mekanisme yang bisa diuji: rekomendasi berbasis data serupa, pembaruan bertahap, dan keputusan kuantitas berbasis biaya.

## 2. Solusi yang diusulkan

ColdStart Kitchen adalah aplikasi web ringan yang:
1. meminta profil usaha, menu, harga, dan biaya;
2. meminjam pola dari **dataset referensi usaha serupa** (k-nearest neighbours + prior) ketika pedagang belum punya data;
3. memperbarui estimasi dengan data penjualan sendiri memakai **shrinkage Bayesian** (H0 → H3 → H7);
4. memilih jumlah produksi dengan **aturan newsvendor** yang mempertimbangkan margin dan kerugian sisa;
5. menampilkan rentang P10/P50/P90, label keyakinan, dan alasan berbahasa Indonesia.

Aplikasi berjalan offline, tanpa panggilan LLM atau API eksternal, dan hanya memakai numpy/scipy.

## 3. Manfaat

| Manfaat | Bagi siapa | Cara diukur |
|---|---|---|
| Keputusan produksi lebih sadar biaya | Pemilik usaha | Rasio sisa produksi harian sebelum/sesudah (UAT) |
| Titik awal tanpa data | Usaha baru | Rekomendasi tetap tersedia di Hari 0 (H0) |
| Belajar dari data sendiri | Pemilik usaha | Tahap naik H0→H3→H7 dalam 7 hari pencatatan |
| Transparansi | Pemilik usaha | Alasan dan rentang ditampilkan setiap kartu |
| Bukti teknis | Tim proyek | Backtest pada data sintetis: WAPE H0 41,4% vs baseline 54,1% |

**Penting:** angka backtest berasal dari data sintetis dan tidak membuktikan pengurangan limbah di dunia nyata. Lihat `docs/model_report.md` bagian Keterbatasan.

## 4. Kelayakan

- **Teknis:** satu aplikasi FastAPI + SQLite/Postgres, model numpy/scipy, tanpa GPU. Sudah berjalan dengan 134 tes otomatis dan smoke test.
- **Operasional:** satu akun demo dan tiga usaha contoh; pedagang hanya perlu mencatat penjualan harian atau mengimpor CSV.
- **Biaya:** tidak ada biaya API. Opsi deploy gratis (Render) atau Mac mini yang sudah ada + Cloudflare Tunnel. Tidak ada klaim anggaran pasti.
- **Risiko utama:** adopsi rendah, data masukan berisik, dan overconfidence model. Mitigasi ada di `docs/project_plan.md`.

## 5. Rekomendasi

Lanjutkan ke UAT dengan 3–5 pedagang nyata sebelum investasi lebih besar. Ukur: (a) apakah rekomendasi dipahami tanpa pelatihan, (b) apakah pencatatan harian bertahan minimal 7 hari, (c) apakah sisa produksi turun dibanding minggu sebelumnya. Bila salah satu gagal, perbaiki alur pencatatan sebelum menambah fitur.
