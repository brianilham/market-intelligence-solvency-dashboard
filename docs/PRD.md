# Product Requirements Document (PRD)

## 1. Informasi Proyek
- **Project Title:** Analisis Komprehensif Industri Asuransi Indonesia — Kinerja Keuangan, Solvabilitas OJK, dan Benchmarking Perusahaan
- **Konteks Asal Proyek:** Proyek portofolio berbasis pengalaman magang di industri asuransi Indonesia.
- **Selected Track:** Pure Analytics & BI (Business Intelligence & Regulatory Reporting).
  - *Alasan:* Fokus pada analisis deskriptif, kepatuhan regulasi OJK (POJK No. 71/POJK.05/2016), benchmarking solvabilitas (RBC), dan early warning system, bukan pemodelan prediktif black-box.
- **Target Delivery:** Executive Dashboard interaktif berbasis Streamlit.
- **Stakeholders:** Analis Keuangan, Manajemen Risiko, Regulator (OJK), Investor, serta Rekruter/Hiring Manager.

---

## 2. Problem Statement
Laporan keuangan dan statistik industri asuransi di Indonesia yang dipublikasikan oleh Otoritas Jasa Keuangan (OJK) tersebar dalam berbagai berkas laporan tahunan dan portal data sektoral yang terpisah. 
Kondisi ini menyulitkan para pengambil keputusan dan analis untuk:
1. Memantau kesehatan solvabilitas (RBC Ratio) seluruh entitas secara serempak.
2. Membandingkan performa pangsa pasar (*market share*) lintas kategori (Jiwa, Umum, Reasuransi, Syariah).
3. Mendeteksi secara dini perusahaan-perusahaan yang berada di bawah batas minimum kesehatan modal OJK (RBC < 120%) atau mengalami beban rasio klaim yang membengkak.

---

## 3. Scope of Work (Ruang Lingkup)

### In-Scope
- **Pemanfaatan Data Resmi OJK**: Analisis berbasis data publikasi resmi OJK (Statistik Perasuransian Indonesia) yang mencakup seluruh entitas terdaftar.
- **Indikator Kesehatan Finansial Utama**:
  - Pendapatan Premi Bruto
  - Beban Klaim Bruto & Rasio Klaim (%)
  - Rasio Pencapaian Solvabilitas / *Risk-Based Capital* (RBC Ratio, threshold batas aman regulasi: 120%)
  - Total Aset, Total Investasi, dan Laba/Rugi Bersih
- **Executive & Early Warning System**:
  - Halaman 1: Ringkasan Eksekutif (Makro KPIs, Donut Market Share, Top 10 Leaders).
  - Halaman 2: Solvabilitas & Risiko OJK (Watchlist entitas kritis RBC < 120% dan defisit laba).
  - Halaman 3: Profil Perusahaan (Pencarian mandiri, benchmarking vs rata-rata industri).

### Out-of-Scope
- **Data Internal Privat Tempat Magang**: Tidak menggunakan data rahasia/operasional internal perusahaan tempat magang demi kepatuhan terhadap Non-Disclosure Agreement (NDA).
- **Data Nasabah / PII**: Tidak menggunakan data individual polis riil nasabah. Seluruh analitik berada pada level perusahaan (*entity-level*).
- **Prediksi Machine Learning Spekulatif**: Menghindari model prediksi gagal bayar berbasis ML yang berpotensi bias, berfokus murni pada kepatuhan aturan regulasi keuangan (deterministic rules).

---

## 4. Success Metrics

### Business & Analytical KPI
- **Kelengkapan Cakupan Industri**: Menampilkan performa entitas-entitas resmi asuransi di Indonesia lintas kategori (Jiwa, Umum, Reasuransi, dan Syariah).
- **Deteksi Dini Akurat**: Mengidentifikasi secara instan seluruh perusahaan yang melanggar ketentuan RBC < 120% pada tahun pelaporan aktif.

### Technical Metrics
- **Data Quality & Contract**: 100% data lolos validasi skema deklaratif *Pandera*.
- **Query Performance**: Agregasi data time-series instan (< 100ms) menggunakan engine *DuckDB* lokal berbasis columnar storage.
- **Dashboard Load Time**: Waktu muat awal dashboard < 2 detik.

---

## 5. Data Strategy & Provenance
- **Sumber Data Resmi**: Publikasi Terbuka Otoritas Jasa Keuangan (OJK) — *Statistik Perasuransian Indonesia* dan *Portal Data Sektor Jasa Keuangan (SJK Public)*.
- **Legalitas & Kepatuhan**: 100% bebas dari risiko pelanggaran kerahasiaan data perusahaan magang. Menggunakan data yang memang ditujukan untuk transparansi publik.
- **Format Ingesti**: Format tabular (Parquet & Excel `.xlsx` OJK standard) yang diintegrasikan ke basis data analytical *DuckDB*.

---

## 6. Data Governance, Ethics & Compliance
- **Kepatuhan NDA**: Menghormati klausul kerahasiaan perusahaan tempat magang dengan sepenuhnya mengalihkan data ke domain publik OJK.
- **Perlindungan Data Pribadi (UU PDP No. 27/2022)**: Zero PII (Personally Identifiable Information). Seluruh data merupakan data keuangan korporasi yang telah diaudit dan dipublikasikan secara terbuka.
