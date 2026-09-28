# Implementation Plan: Analisis Komprehensif Industri Asuransi Indonesia

Dokumen ini memetakan tahapan implementasi teknis, struktur repositori, dan *Architectural Decision Records* (ADR) untuk proyek analitik asuransi berbasis data publik OJK.

---

## 🚀 Fase Implementasi Proyek

### Phase 1: Environment Setup & Data Foundation
- [x] Inisialisasi lingkungan virtual Python terisolasi menggunakan `uv venv`.
- [x] Instalasi dependensi analitik: `duckdb`, `polars`, `pandera`, `streamlit`, `plotly`, `requests`, `openpyxl`.
- [x] Pembuatan data contract & skema validasi deklaratif menggunakan Pandera (`src/contracts/schemas.py`).
- [x] Pembangunan parser & builder data resmi OJK (`src/pipeline/ojk_excel_parser.py` & `src/generators/ojk_data_builder.py`).
- [x] Setup basis data lokal analitik `data/asuransi.duckdb`.

### Phase 2: Ingestion Pipeline & Data Modeling
- [x] Pipeline ingesti: Validasi data OJK via Pandera → Ingest ke DuckDB (`src/pipeline/ingest.py`).
- [x] Pemodelan views analitik di DuckDB (`src/pipeline/transform.py`):
  - `vw_market_share`: Pangsa pasar premi per kategori asuransi tahunan.
  - `vw_ranking_premi`: Peringkat perusahaan berdasarkan premi bruto.
  - `vw_ranking_rbc`: Peringkat solvabilitas modal dengan indikator ambang 120%.
  - `vw_yoy_growth`: Pertumbuhan tahunan premi dan laba per entitas.
  - `vw_industry_summary`: Rangkuman agregat makro perasuransian nasional.

### Phase 3: Analytics Engine & Key Metrics
- [x] Modul kalkulasi KPI industri & per entitas (`src/analytics/kpi.py`).
- [x] Modul ranking metrik finansial & skor komposit (`src/analytics/ranking.py`).
- [x] Modul analisis tren historis & matriks korelasi (`src/analytics/trends.py`).

### Phase 4: Executive Dashboard & Delivery
- [x] Desain ulang UI menjadi sistem 3 halaman terarah (`src/app/dashboard.py`):
  - **Halaman 1: Ringkasan Eksekutif** — Makro KPI, Donut Chart Pangsa Pasar, Top 10 Pemimpin Premi.
  - **Halaman 2: Solvabilitas & Risiko OJK** — Early Warning Watchlist (RBC < 120%, rasio klaim bengkak).
  - **Halaman 3: Profil Perusahaan** — Pencarian entitas mandiri & benchmarking vs industri.
- [x] Uji coba fungsionalitas dan eksekusi dashboard lokal.

---

## 📁 Struktur Repositori Terstandarisasi

```text
asuransi-indonesia/
├── docs/                             # Spesifikasi Teknis Proyek
│   ├── PRD.md                        # Product Requirements Document
│   ├── ARCHITECTURE.md               # Arsitektur Sistem & Data Flow
│   └── IMPLEMENTATION.md             # Rencana Implementasi & ADR
├── src/
│   ├── contracts/
│   │   └── schemas.py                # Pandera Data Contracts
│   ├── pipeline/
│   │   ├── ojk_excel_parser.py       # Parser Berkas Excel Resmi OJK
│   │   ├── ingest.py                 # Validasi & Pemuatan ke DuckDB
│   │   └── transform.py              # Pembentukan Analytical Views
│   ├── analytics/
│   │   ├── kpi.py                    # Kalkulasi Indikator Kunci
│   │   ├── ranking.py                # Perankingan & Skor Komposit
│   │   └── trends.py                 # Analisis Time-Series
│   └── app/
│       └── dashboard.py              # Streamlit Executive Dashboard
├── data/
│   ├── raw/                          # Berkas Mentah OJK (.parquet / .xlsx)
│   ├── processed/                    # Data Terverifikasi & Karantina
│   └── asuransi.duckdb               # Database OLAP Lokal DuckDB
├── tests/                            # Pytest Test Suite
├── pyproject.toml                    # Dependensi Proyek
└── README.md                         # Panduan Portofolio
```

---

## 📝 Technical Decision Log (ADR)

| Tanggal | Keputusan Teknis | Alternatif | Alasan Pemilihan |
| :--- | :--- | :--- | :--- |
| **2026-09-27** | **Peralihan ke Data Resmi Publik OJK** | Data Internal Magang, Data Sintetis Faker | Menghindari pelanggaran NDA perusahaan magang, 100% legal, dan meningkatkan kredibilitas portofolio dengan entitas riil industri. |
| **2026-09-27** | **Desain Dashboard 3 Halaman Terarah** | Dashboard 4 Halaman Padat | Mengurangi *cognitive overload* pembaca; memfokuskan narasi pada *Executive Summary* dan *Early Warning System*. |
| **2026-09-27** | **DuckDB sebagai Analytical Engine** | SQLite, PostgreSQL | Eksekusi query analitik berbasis columnar (OLAP) sangat cepat pada file lokal tanpa memerlukan server terpisah. |
| **2026-09-27** | **Pandera untuk Validasi Kontrak Data** | Pydantic murni | Mendukung validasi data tabular berbasis Polars/Pandas secara deklaratif dan berperforma tinggi. |
| **2026-09-27** | **Streamlit Mode Read-Only Connection** | Read-Write Connection | Mencegah file IO lock pada file `asuransi.duckdb` saat dashboard sedang aktif dibuka di browser. |
