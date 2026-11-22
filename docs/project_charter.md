# Project Charter ColdStart Kitchen

> **Status: DRAF.** Perlu tinjauan manusia.

## 1. Tujuan

Membangun aplikasi web yang membantu pedagang makanan/minuman tanpa riwayat penjualan menentukan jumlah produksi harian, dengan rentang ketidakpastian, label keyakinan, dan alasan yang dapat dipahami.

## 2. Measurable Organizational Value (MOV)

| MOV | Target | Cara verifikasi |
|---|---|---|
| Rekomendasi tersedia sejak Hari 0 | 100% produk aktif mendapat rekomendasi H0 | Tes API + dashboard demo |
| Model belajar dari data sendiri | Tahap berubah H0→H3 pada 3 hari, H3→H7 pada 7 hari | Tes engine + smoke test |
| Kualitas statistik pada data sintetis | WAPE H0 ≤ baseline global; coverage P10–P90 0,65–0,92 | `make report` |
| Keandalan | `make verify` hijau (≥ 40 tes + smoke) | CI lokal |
| Kesiapan produksi | Tolak start tanpa SECRET_KEY / password default; `/healthz` ok | Tes T4.6 |
| Kesiapan operasional | Panduan pengguna 1 halaman + kit UAT | Dokumen + UAT manusia |

## 3. Pemangku kepentingan

| Peran | Kepentingan |
|---|---|
| Pemilik warung/kafe/gerobak (pengguna) | Keputusan produksi cepat dan masuk akal |
| Tim produk/analis bisnis | Kebutuhan pengguna terwakili di FR |
| Developer | Lingkup jelas, tanpa dependensi berlebih |
| ML engineer | Model dapat diuji dan dilaporkan jujur |
| Dosen/penguji | Traceability WBS, dokumen, dan bukti uji |

## 4. Asumsi

- Pengguna memiliki ponsel/browser modern dan koneksi minimal untuk membuka halaman.
- Data referensi sintetis cukup untuk mendemonstrasikan mekanisme; bukan pengganti data lapangan.
- Satu akun demo cukup untuk demonstrasi; tidak ada registrasi mandiri.
- Harga dan biaya per porsi diisi manual oleh pemilik usaha.

## 5. Kendala

- **Waktu:** 5 sprint, total 200 person-hours pada WBS asli; implementasi agen dipadatkan namun seluruh 29 deliverable tetap ada.
- **Teknologi:** FastAPI, SQLAlchemy, numpy/scipy, vanilla JS; tanpa npm/CDN/LLM.
- **Data:** tidak ada data pelanggan nyata; dataset referensi sintetis.
- **Lingkungan:** satu sesi otonom tanpa pengguna yang menjawab pertanyaan.

## 6. Ruang lingkup tingkat tinggi

Termasuk: login demo, profil usaha, menu, pencatatan penjualan, impor CSV, rekomendasi H0/H3/H7, riwayat, dashboard, deploy, dokumen.
Tidak termasuk: multi-tenancy, pembayaran, integrasi POS/WhatsApp/GrabFood, feed cuaca, deep learning, aplikasi mobile native, panel admin, email, worker latar belakang.

## 7. Kriteria sukses dan serah terima

Level 1 (agen): `make verify` hijau, smoke membuktikan alur penuh, seluruh dokumen ada, aplikasi berjalan lokal, artefak deploy siap.
Level 2 (manusia): deploy publik, UAT dengan pedagang, tinjauan dokumen DRAF, demo langsung.

## 8. Otoritas dan keputusan

Keputusan teknis harian diambil oleh developer pelaksana dan dicatat di `docs/DECISIONS.md`. Perubahan lingkup memerlukan pembaruan PLAN.md dan persetujuan pemilik proyek (manusia).
