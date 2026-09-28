# 🛡️ Analisis Komprehensif Industri Asuransi Indonesia

> **Executive Dashboard & Early Warning System Kinerja Perasuransian Nasional Berbasis Data Resmi OJK**

Repositori ini menyajikan pipeline analitik data dan dashboard eksekutif untuk menganalisis performa keuangan, ketahanan solvabilitas modal (*Risk-Based Capital* / RBC), serta dinamika pangsa pasar industri asuransi di Indonesia.

Proyek ini dikembangkan sebagai karya portofolio profesional berbasis pengalaman magang di industri asuransi. Untuk menjamin kepatuhan terhadap regulasi kerahasiaan (*Non-Disclosure Agreement* / NDA) serta UU Perlindungan Data Pribadi (UU PDP No. 27/2022), seluruh data operasional privat **100% dialihkan menggunakan data publikasi resmi Otoritas Jasa Keuangan (OJK)**.

---

## 🎯 Fitur & Modul Utama Dashboard

1. **📊 Ringkasan Eksekutif (*Executive Summary*)**
   - 4 Metrik Makro: Total Premi Nasional, Rata-rata RBC Industri, Rasio Klaim, dan Total Laba Bersih.
   - Komposisi Pangsa Pasar (*Donut Chart*) lintas 5 kategori: Asuransi Jiwa, Umum, Reasuransi, Syariah Jiwa, dan Syariah Umum.
   - *Top 10 Leaderboard*: Peringkat 10 perusahaan teratas penguasa premi.
   - *Automated Storytelling*: Narasi otomatis kondisi industri pada tahun pelaporan aktif.

2. **⚠️ Solvabilitas & Pengawasan Risiko OJK (*Early Warning System*)**
   - Deteksi Dini: Entitas dengan RBC di bawah ketentuan minimum OJK (< 120%), beban klaim tinggi (> 65%), atau defisit laba.
   - *Priority Watchlist*: Visualisasi bar chart 5 entitas dengan modal terendah lengkap dengan garis batas regulasi 120%.
   - Tabel Daftar Pengawasan Khusus dengan penandaan alasan risiko (*Risk Badges*).

3. **🔍 Profil & Evaluasi Perusahaan (*Company Inspector*)**
   - Pencarian mandiri (*self-service search*) nama perusahaan asuransi resmi di Indonesia.
   - Penilaian status kepatuhan: `[✅ Sehat & Memenuhi Ketentuan OJK]` vs `[⚠️ Dalam Perhatian Khusus Regulator]`.
   - Benchmarking instan metrik kunci perusahaan terhadap rata-rata industri nasional.
   - Grafik riwayat kinerja historis premi dan laba/rugi bersih.

---

## 🛠️ Arsitektur & Tech Stack

| Lapisan | Teknologi | Peran |
|:---|:---|:---|
| **Data Source** | Publikasi OJK (*Statistik Perasuransian*) | Sumber data resmi terbuka |
| **Data Contract** | `Pandera` | Validasi skema, batasan nilai, dan tipe kolom |
| **Engine OLAP** | `DuckDB` + `Polars` | Pemrosesan analitik lokal berkecepatan tinggi |
| **Visualisasi** | `Plotly` | Visualisasi grafik interaktif & responsif |
| **Aplikasi UI** | `Streamlit` | Antarmuka dashboard eksekutif berbasis Python |
| **Environment** | `uv` | Manajemen virtual environment & paket ultra-cepat |

---

## 🚀 Panduan Menjalankan Proyek

### 1. Inisialisasi Lingkungan (PowerShell)
```powershell
cd "C:\Users\USER\Downloads\Project Portfolio Data\asuransi-indonesia"

# Aktifkan virtual environment
.venv\Scripts\activate

# Pastikan dependensi terpasang
uv pip install -e ".[dev]"
```

### 2. Muat Basis Data Resmi OJK
```powershell
$env:PYTHONIOENCODING='utf-8'

# Bangun dataset entitas resmi OJK
python src/generators/ojk_data_builder.py

# Jalankan pipeline ingesti & transform ke DuckDB
python src/pipeline/ingest.py
python src/pipeline/transform.py
```

### 3. Buka Dashboard
```powershell
streamlit run src/app/dashboard.py
```
Akses melalui browser di **http://localhost:8501** (atau port yang tertera di terminal).

---

## 📁 Struktur Berkas

```text
asuransi-indonesia/
├── docs/                      # Dokumentasi Spesifikasi Proyek
│   ├── PRD.md                 # Product Requirements Document
│   ├── ARCHITECTURE.md        # Arsitektur Aliran Data & Kontrak
│   └── IMPLEMENTATION.md      # Checklist Fase & Log Keputusan (ADR)
├── src/
│   ├── contracts/             # Skema Validasi Pandera
│   ├── pipeline/              # Ingesti, Parser OJK, & Transformasi DuckDB
│   ├── analytics/             # Logika Kalkulasi KPI, Ranking, & Tren
│   └── app/                   # Kode Aplikasi Dashboard Streamlit
├── data/
│   ├── raw/                   # Berkas Data Asuransi OJK
│   └── asuransi.duckdb        # Database OLAP DuckDB
└── tests/                     # Test Suite Pytest
```

---

## ⚖️ Kepatuhan & Etika Data

Proyek ini dibangun dengan memegang teguh integritas data profesional:
- Tidak ada data rahasia/operasional internal perusahaan tempat magang yang dipublikasikan.
- Bebas PII (*Personally Identifiable Information*); seluruh analitik dilakukan pada tingkat korporat yang telah diaudit secara terbuka oleh regulator.
