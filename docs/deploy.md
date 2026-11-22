# Panduan Deploy ColdStart Kitchen

Dokumen ini menjelaskan dua cara menayangkan aplikasi secara publik. **Langkah go-live dilakukan oleh manusia**; berkas dan skrip sudah disiapkan di repositori.

| Variabel | Wajib | Contoh | Keterangan |
|---|---|---|---|
| `APP_ENV` | ya (produksi) | `production` | Mode produksi mengaktifkan pemeriksaan keamanan. |
| `SECRET_KEY` | ya | string acak ≥ 32 karakter | Kunci tanda tangan cookie sesi. Aplikasi menolak start bila kosong atau < 16 karakter. |
| `DATABASE_URL` | tidak | `postgresql://user:pass@host/db` | Default SQLite `sqlite:///./var/coldstart.db`. Skema `postgres://` dan `postgresql://` dinormalisasi otomatis. |
| `DEMO_USER` | tidak | `demo` | Nama akun demo. |
| `DEMO_PASSWORD` | ya di produksi | kata sandi kuat | Produksi menolak start bila masih `demo123`. |
| `PORT` | tidak | `8000` | Port HTTP aplikasi. |

## Route A — Render (cloud)

1. Push repositori ke GitHub.
2. Buat akun di [render.com](https://render.com), hubungkan repositori.
3. Render membaca `render.yaml`: satu web service Docker + satu Postgres gratis. Saat membuat service, isi `DEMO_PASSWORD` dengan kata sandi kuat (nilai ini sengaja tidak disimpan di repo; isiannya `sync: false`).
4. Tunggu build. Buka URL `https://<nama-service>.onrender.com/healthz`; harus muncul `{"status":"ok","db":"ok"}`.
5. Buka `/login`, masuk dengan `DEMO_USER` / `DEMO_PASSWORD`, pastikan tiga usaha tampil dengan tahap H0, H3, dan H7.
6. Segera ganti `DEMO_PASSWORD` setelah demo selesai.

Build Docker juga bisa diuji lokal (bila Docker terpasang):

```bash
docker build -t coldstart .
docker run --rm -p 8000:8000 -e APP_ENV=production -e SECRET_KEY=$(openssl rand -hex 24) -e DEMO_PASSWORD=rahasia-kuat coldstart
curl localhost:8000/healthz
```

### Catatan penting Render

- Paket **free** tidur setelah ± 15 menit tanpa trafik; permintaan pertama butuh ± 1 menit untuk bangun.
- Filesystem **ephemeral**: data SQLite hilang saat restart. Karena itu `render.yaml` memakai Postgres.
- Postgres gratis **kedaluwarsa setelah 30 hari**; data hilang kecuali di-upgrade/di-backup.

## Route B — Mac mini + Cloudflare Tunnel

1. Siapkan Python 3.11+ dan `make install` di Mac.
2. Salin `.env.prod.example` menjadi `.env.prod`, isi `SECRET_KEY` (`openssl rand -hex 32`) dan `DEMO_PASSWORD` yang kuat. Berkas ini di-gitignore.
3. Jalankan manual untuk uji: `scripts/run_prod.sh`. Lalu `curl localhost:8000/healthz`.
4. Pasang Cloudflare Tunnel (`cloudflared tunnel login`, `cloudflared tunnel create coldstart`), arahkan hostname ke `http://127.0.0.1:8000`.
5. Agar otomatis hidup lagi: salin `deploy/com.coldstart.app.plist` ke `~/Library/LaunchAgents/`, ganti `USERNAME` dengan nama pengguna Mac, lalu `launchctl load ~/Library/LaunchAgents/com.coldstart.app.plist`. `KeepAlive` membuat aplikasi dijalankan ulang bila berhenti.

### Catatan penting Route B

- Situs hanya hidup selama Mac menyala dan tunnel berjalan.
- `launchd` tidak menghidupkan Mac setelah mati listrik; aktifkan auto-restart di System Settings bila perlu.
- Backup berkala `var/coldstart.db` (atau pakai Postgres).

## Checklist pasca-deploy

- [ ] `GET /healthz` mengembalikan `{"status":"ok","db":"ok"}`.
- [ ] Login demo berhasil dan tiga usaha tampil.
- [ ] Kartu rekomendasi H0, H3, H7 tampil (dashboard tidak kosong).
- [ ] Rentang P10–P50–P90 dan lencana keyakinan terlihat di ponsel (satu kolom).
- [ ] Catat penjualan satu hari, dashboard berubah.
- [ ] `DEMO_PASSWORD` sudah diganti dari nilai contoh.
- [ ] HTTPS aktif (cookie sesi memakai `https_only` di produksi).
