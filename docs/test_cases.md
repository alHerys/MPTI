# Kasus Uji Fungsional ColdStart Kitchen

Setiap FR dari `docs/requirements.md` dipetakan ke minimal satu kasus uji. Kolom **Tes otomatis** berisi nama fungsi pytest yang benar-benar ada di folder `tests/`; `tests/test_t5_1_doc_links.py` memverifikasi tautan ini.

Cara menjalankan: `make test` (seluruh suite) atau `.venv/bin/python -m pytest -q tests/test_t3_6_engine_api.py`.

| TC | FR | Skenario | Langkah | Hasil yang diharapkan | Tes otomatis |
|---|---|---|---|---|---|
| TC-01 | FR-01 | Halaman tanpa sesi | Buka `/` tanpa login | Redirect 303 ke `/login`; API menjawab 401 | `test_fr01_unauthenticated_pages_redirect_and_api_401` |
| TC-02 | FR-01 | Login salah | Kirim kredensial salah | 401 dan pesan "Nama pengguna atau kata sandi salah." | `test_fr01_wrong_password_rejected` |
| TC-03 | FR-01 | Login & logout | Login benar lalu logout | 303 ke dashboard; setelah logout API 401 | `test_fr01_login_and_logout` |
| TC-04 | FR-02 | Buat/ubah profil usaha | POST lalu PUT `/api/businesses/{id}` | 201/200, data berubah | `test_fr02_create_read_update_business` |
| TC-05 | FR-02 | Validasi kosakata | Kirim `business_type=restoran` | 422 | `test_fr02_validation_rejects_bad_vocabulary_and_name` |
| TC-06 | FR-03 | CRUD menu & soft delete | Tambah produk, ubah, hapus | `active=false`, hilang dari daftar aktif | `test_fr03_product_crud_and_soft_delete` |
| TC-07 | FR-03 | Validasi produk | Harga 0 / biaya negatif / kategori asing | 422 | `test_fr03_product_validation` |
| TC-08 | FR-04 | Isolasi kepemilikan | Akses usaha pengguna lain | 404 | `test_fr04_cross_user_access_is_404` |
| TC-09 | FR-05 | Upsert penjualan | POST tanggal sama dua kali | Satu baris, nilai terbaru | `test_fr05_upsert_is_idempotent` |
| TC-10 | FR-05 | Validasi penjualan | Tanggal masa depan, qty negatif/pecahan | 422 | `test_fr05_validation_rejects_negative_and_future` |
| TC-11 | FR-06 | Filter rentang | `from`/`to` inklusif | Hanya baris dalam rentang | `test_fr06_range_filter_is_inclusive` |
| TC-12 | FR-06 | Filter halaman riwayat | Buka `/sales?start=&end=` | Baris di luar rentang tidak tampil | `test_fr06_history_date_filter` |
| TC-13 | FR-07 | CSV valid | Unggah 3 baris valid | 200, `accepted=3`, tersimpan | `test_fr07_valid_file_accepted` |
| TC-14 | FR-08 | CSV header salah | Header `tanggal,produk,jumlah` | 422 + `errors[].line/message`, tidak ada data | `test_fr08_invalid_files_rejected_with_nothing_stored` |
| TC-15 | FR-08 | CSV terlalu besar | > 5.000 baris atau > 1 MB | 422, tidak ada data | `test_reject_too_many_rows`, `test_reject_oversized_file` |
| TC-16 | FR-08 | CSV non-UTF-8 | Byte `0xFF` | 422, pesan UTF-8 | `test_reject_non_utf8` |
| TC-17 | FR-08 | CSV CRLF + BOM | Berkas Excel | 200, 1 baris diterima | `test_accepts_crlf_and_bom` |
| TC-18 | FR-09 | H0 tanpa data | GET rekomendasi produk tanpa penjualan | `stage=H0`, mean > 0, P10≤P50≤P90 | `test_fr09_recommendation_with_zero_sales_positive` |
| TC-19 | FR-10 | H3 | Tiga hari data | `stage=H3`, `n_days=3` | `test_fr09_fr10_fr11_stage_by_history` |
| TC-20 | FR-11 | H7 | Tujuh hari data | `stage=H7` | `test_fr09_fr10_fr11_stage_by_history` |
| TC-21 | FR-11 | Hasil berubah | Tambah penjualan baru | `n_days`/`p50`/`recommended_qty` berubah | `test_fr11_results_change_with_new_sales` |
| TC-22 | FR-12 | Struktur kartu | Buka dashboard | Template kartu berisi qty, P10/P50/P90, badge, alasan | `test_fr12_card_template_has_required_parts` |
| TC-23 | FR-13 | Aturan keyakinan | n=0/3/7 dan rasio lebar > 1,2 | rendah/sedang/tinggi, turun satu tingkat, paksa rendah | `test_confidence_base_levels`, `test_confidence_downgrade_on_wide_ratio`, `test_confidence_force_low_when_low_reference` |
| TC-24 | FR-14 | Alasan Indonesia | Rekomendasi dengan stockout & margin | Urutan template sesuai spesifikasi | `test_reason_order_is_fixed` |
| TC-25 | FR-15 | Responsif | Lebar < 640 px | Grid satu kolom, media query ada | `test_fr15_css_has_mobile_first_media_query` |
| TC-26 | FR-16 | Seed demo | DB kosong saat start | 3 usaha, 5 produk, tahap H0/H3/H7 | `test_fr16_seed_creates_demo_user_and_three_stages` |
| TC-27 | FR-16 | Idempoten | Start ulang | Tidak ada duplikasi | `test_seed_is_idempotent` |
| TC-28 | FR-17 | Produksi tanpa SECRET_KEY | `APP_ENV=production` tanpa kunci | RuntimeError, aplikasi tidak start | `test_missing_secret_key_refused` |
| TC-29 | FR-17 | Password demo default | `DEMO_PASSWORD=demo123` | RuntimeError | `test_default_demo_password_refused` |
| TC-30 | FR-17 | Rate limit login | 11 percobaan gagal | Percobaan ke-11 → 429 | `test_fr17_login_rate_limit_returns_429` |
| TC-31 | FR-17 | Health check | `GET /healthz` | `{"status":"ok","db":"ok"}` | `test_healthz_shape` |
| TC-32 | FR-18 | Halaman formulir | Buka `/business`, `/sales/new`, `/import` | 200 + teks Indonesia | `test_fr18_all_pages_render` |
| TC-33 | FR-05 | Form 5 produk | POST `/sales/new` satu tanggal | 5 baris tersimpan | `test_form_posts_five_products_at_once` |
| TC-34 | FR-05 | Form ulang tanggal | POST tanggal sama | Update, bukan duplikat | `test_repost_same_date_updates_not_duplicates` |
| TC-35 | NFR-01 | Kinerja rekomendasi | 50 produk satu usaha | < 3 detik (ambang CI) | `test_nfr01_recommendations_under_three_seconds` |
| TC-36 | NFR-02 | Tanpa aset eksternal | Pindai templat | Tidak ada URL `http(s)://` | `test_no_external_resources_in_templates` |
| TC-37 | NFR-03 | Normalisasi Postgres | `postgres://u:p@h/db` | Menjadi `postgresql+psycopg2://` | `test_database_url_normalizes_postgres` |
| TC-38 | NFR-04 | Dependensi | Baca `requirements.txt` | Hanya daftar yang diizinkan | `test_requirements_only_allowed_dependencies` |
| TC-39 | — | Laporan model | `make report` | `docs/model_report.md` berisi tabel + Keterbatasan | `test_report_exists_with_required_sections` |
| TC-40 | — | Dataset referensi | Regenerasi seed 42 | Hash identik | `test_seed_42_reproduces_identical_files` |
