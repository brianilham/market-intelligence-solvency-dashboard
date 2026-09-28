# Product Requirements Document (PRD)

## 1. Informasi Proyek

- **Nama Proyek:** Analisis Kinerja Keuangan dan Solvabilitas Industri Asuransi Indonesia
- **Fokus:** Pure Analytics, Business Intelligence, dan Regulatory Reporting
- **Dasar Regulasi:** Batas minimum Risk-Based Capital (RBC) 120% sesuai POJK No. 71/POJK.05/2016
- **Format Delivery:** Dashboard interaktif Streamlit
- **Pengguna Target:** Analis Keuangan, Tim Manajemen Risiko, Regulator, dan Evaluator Kinerja

---

## 2. Masalah

Laporan statistik dan keuangan industri asuransi yang dipublikasikan OJK tersebar dalam berkas tahunan dan tabel terpisah. Hal ini menyulitkan:
1. Pemantauan rasio solvabilitas (RBC) seluruh entitas secara serempak.
2. Analisis perbandingan pangsa pasar (*market share*) antar sektor (Jiwa, Umum, Reasuransi, Syariah).
3. Deteksi dini entitas yang melanggar batas modal minimum (RBC < 120%) atau mengalami pembengkakan rasio klaim (> 65%).

---

## 3. Ruang Lingkup

### Termasuk (In-Scope)
- **Data Resmi OJK:** Menggunakan data Statistik Perasuransian Indonesia untuk entitas berizin resmi.
- **Indikator Keuangan Kunci:**
  - Pendapatan Premi Bruto
  - Beban Klaim Bruto dan Rasio Klaim (%)
  - Risk-Based Capital (RBC Ratio, ambang minimum OJK: 120%)
  - Total Aset, Total Investasi, dan Laba/Rugi Bersih
- **Struktur Dashboard 3 Halaman:**
  - Halaman 1: Ringkasan Eksekutif (Makro KPI, pangsa pasar per sektor, Top 10 Leaders).
  - Halaman 2: Solvabilitas & Pengawasan OJK (Watchlist entitas berisiko RBC < 120%, klaim > 65%, defisit laba).
  - Halaman 3: Profil & Evaluasi Perusahaan (Pencarian entitas, benchmarking vs rata-rata sektor dan nasional).

### Tidak Termasuk (Out-of-Scope)
- **Data Internal Perusahaan:** Tidak menggunakan data privat operasional demi kepatuhan terhadap Non-Disclosure Agreement (NDA).
- **Data Nasabah / PII:** Tidak menggunakan polis individual riil. Seluruh analisis berada pada level entitas korporat.
- **Pemodelan Prediktif:** Menghindari model probabilistik spekulatif; evaluasi berbasis aturan deterministik POJK.

---

## 4. Metrik Keberhasilan

### Analitik dan Bisnis
- Menampilkan seluruh kategori asuransi (Jiwa, Umum, Reasuransi, Syariah Jiwa, Syariah Umum).
- Mendeteksi secara akurat seluruh entitas yang melanggar batas RBC 120% pada tahun pelaporan aktif.
- Menyajikan perbandingan metrik perusahaan terhadap rata-rata sektor secara instan.

### Teknis
- **Kualitas Data:** 100% data lolos validasi skema Pandera.
- **Performa Query:** Waktu eksekusi agregasi DuckDB di bawah 50 ms.
- **Waktu Muat UI:** Dashboard awal siap digunakan di bawah 2 detik.

---

## 5. Sumber dan Tata Kelola Data

- **Sumber:** Publikasi resmi Otoritas Jasa Keuangan (OJK) — Statistik Perasuransian Indonesia.
- **Format:** Parquet terstruktur yang diintegrasikan ke DuckDB.
- **Privasi:** Zero Personally Identifiable Information (PII) sesuai UU PDP No. 27/2022. Seluruh data merupakan data publikasi terbuka.
