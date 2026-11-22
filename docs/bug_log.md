# Bug Log

| ID | Deskripsi | Keparahan | Status | Perbaikan (commit) |
|---|---|---|---|---|
| BUG-01 | Uji awal ekspektasi alpha salah tulis (0,70 vs formula 2/3 saat nilai sisa 4.000 pada harga 10.000/biaya 6.000). Implementasi sesuai spesifikasi; tes diperbaiki. | Rendah | Closed | T3.4 |
| BUG-02 | Uji shrinkage mengharapkan mean mencapai ȳ persis pada n=10; rumus w=n/(n+4) tidak pernah mencapai 1. Tes dikoreksi. | Rendah | Closed | T3.2 |
| BUG-03 | Uji weekday blend memakai tanggal yang salah sehingga hari target tidak punya observasi. Fixture diperbaiki. | Rendah | Closed | T3.2 |
| BUG-04 | Pencarian tombol submit generik saat verifikasi browser menekan tombol "Keluar" di header, bukan submit form. Bukan bug aplikasi; selector dipersempit saat pengujian. | Rendah | Closed | T4.x verification |
| BUG-05 | `csv_import` menghitung baris maksimum termasuk baris kosong; batas 5.000 baris kini menghitung baris data non-kosong. | Sedang | Closed | T2.6 |
| BUG-06 | Test `/products/{id}/sales` memakai nama parameter `from_` yang tidak bisa dikirim klien; diganti `Query(alias="from")`. | Sedang | Closed | T2.5 |
| BUG-07 | Halaman terautentikasi memakai dependency API yang mengembalikan 401 JSON; pengguna tanpa sesi melihat JSON, bukan halaman login. Ditambahkan exception `LoginRequired` → redirect 303. | Sedang | Closed | T4.5 |
| BUG-08 | Template dashboard awalnya membangun DOM kartu di JS; dipindah ke `<template>` agar struktur HTML dapat diuji tanpa duplikasi. | Rendah | Closed | T4.2 |
