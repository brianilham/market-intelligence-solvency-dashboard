# Rencana Implementasi dan Log Keputusan (ADR)

Dokumen ini memetakan tahapan implementasi teknis, struktur repositori, dan *Architectural Decision Records* (ADR) pada proyek analitik industri asuransi berbasis data OJK.

---

## Fase Implementasi

### Fase 1: Setup Lingkungan dan Fondasi Data
- [x] Inisialisasi lingkungan virtual Python terisolasi menggunakan `uv venv`.
- [x] Pemasangan dependensi: `duckdb`, `polars`, `pandera`, `streamlit`, `plotly`, `requests`, `openpyxl`.
- [x] Pembuatan skema validasi deklaratif dengan Pandera (`src/contracts/schemas.py`).
- [x] Pembangunan parser dan generator data resmi OJK (`src/pipeline/ojk_excel_parser.py` dan `src/generators/ojk_data_builder.py`).
- [x] Inisialisasi basis data analitik lokal `data/asuransi.duckdb`.

### Fase 2: Pipeline Ingesti dan Pemodelan Data
- [x] Pipeline ingesti: Validasi data OJK via Pandera ke DuckDB (`src/pipeline/ingest.py`).
- [x] Pembentukan views analitik di DuckDB (`src/pipeline/transform.py`):
  - `vw_market_share`: Pangsa pasar premi per sektor tahunan.
  - `vw_ranking_premi`: Peringkat perusahaan berdasarkan premi bruto.
  - `vw_ranking_rbc`: Peringkat solvabilitas modal dengan indikator ambang batas 120%.
  - `vw_yoy_growth`: Pertumbuhan tahunan premi dan laba per entitas.
  - `vw_industry_summary`: Rangkuman agregat industri perasuransian nasional.

### Fase 3: Modul Analitik dan Kalkulasi Metrik
- [x] Kalkulasi KPI industri dan per entitas (`src/analytics/kpi.py`).
- [x] Modul ranking metrik finansial dan skor komposit (`src/analytics/ranking.py`).
- [x] Analisis tren historis dan matriks perbandingan (`src/analytics/trends.py`).

### Fase 4: Dashboard Eksekutif dan Delivery
- [x] Desain sistem dashboard 3 tab terarah (`src/app/dashboard.py`):
  - **Tab 1: Ringkasan Eksekutif** — Makro KPI, distribusi pangsa pasar per sektor, Top 10 Leaders.
  - **Tab 2: Solvabilitas & Pengawasan OJK** — Early Warning Watchlist (RBC < 120%, rasio klaim > 65%, defisit laba).
  - **Tab 3: Profil & Evaluasi Perusahaan** — Pencarian entitas dan matriks benchmarking vs rata-rata industri.
- [x] Pengujian fungsionalitas dan eksekusi test suite pytest.

---

## Struktur Repositori

```text
market-intelligence-solvency-dashboard/
├── docs/                             # Dokumentasi teknis proyek
│   ├── PRD.md                        # Product Requirements Document
│   ├── ARCHITECTURE.md               # Arsitektur sistem dan data flow
│   └── IMPLEMENTATION.md             # Rencana implementasi dan ADR
├── src/
│   ├── contracts/
│   │   └── schemas.py                # Kontrak data Pandera
│   ├── pipeline/
│   │   ├── ojk_excel_parser.py       # Parser berkas Excel OJK
│   │   ├── ingest.py                 # Validasi dan pemuatan ke DuckDB
│   │   └── transform.py              # Pembentukan analytical views
│   ├── analytics/
│   │   ├── kpi.py                    # Kalkulasi indikator kunci
│   │   ├── ranking.py                # Perankingan dan skor komposit
│   │   └── trends.py                 # Analisis time-series
│   └── app/
│       └── dashboard.py              # Dashboard eksekutif Streamlit
├── data/
│   ├── raw/                          # Berkas data mentah (.parquet)
│   ├── processed/                    # Data terverifikasi dan karantina
│   └── asuransi.duckdb               # Database analitik lokal DuckDB
├── tests/                            # Pytest test suite
├── pyproject.toml                    # Konfigurasi dependensi dan linter
└── README.md                         # Panduan proyek
```

---

## Architectural Decision Records (ADR)

| Tanggal | Keputusan Teknis | Alternatif | Alasan Pemilihan |
|:---|:---|:---|:---|
| **2026-09-27** | **Penggunaan Data Publikasi Resmi OJK** | Data internal magang, data sintetis Faker | Menjaga kepatuhan NDA, memenuhi transparansi publik, dan menggunakan entitas asuransi riil di Indonesia. |
| **2026-09-27** | **Struktur Dashboard 3 Tab Terarah** | Halaman tunggal panjang atau 4 halaman padat | Memisahkan fokus analitik secara teratur antara agregasi makro, early warning solvabilitas, dan profiling individual. |
| **2026-09-27** | **DuckDB sebagai Analytical Engine** | SQLite, PostgreSQL server | Pemrosesan kolom (OLAP) cepat pada berkas lokal tanpa memerlukan instalasi server database eksternal. |
| **2026-09-27** | **Pandera untuk Validasi Kontrak Data** | Validasi manual atau Pydantic murni | Mendukung validasi data tabular berbasis Polars/DataFrames secara deklaratif dengan penegakan tipe kolom dan rentang numerik. |
| **2026-09-27** | **Koneksi Read-Only pada Dashboard** | Mode Read-Write | Mencegah file IO lock pada `asuransi.duckdb` ketika aplikasi dibuka secara bersamaan di browser. |
