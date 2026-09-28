# Analisis Kinerja dan Solvabilitas Industri Asuransi Indonesia

Dashboard eksekutif dan sistem deteksi dini untuk memantau solvabilitas modal (*Risk-Based Capital* / RBC), rasio klaim, dan dinamika pangsa pasar industri asuransi di Indonesia.

---

## Latar Belakang

Dashboard ini saya kembangkan saat menjalani magang di PT MNC Life Assurance. Tujuannya adalah membantu divisi Business Development dan jajaran eksekutif dalam memantau lanskap persaingan industri, mengevaluasi posisi pasar perusahaan melalui *benchmarking*, serta mendeteksi risiko solvabilitas dan permodalan kompetitor secara tepat waktu.

Untuk menjaga kerahasiaan data internal perusahaan (*Non-Disclosure Agreement* / NDA) dan mematuhi UU Perlindungan Data Pribadi (UU PDP No. 27/2022), data yang digunakan pada repositori publik ini sepenuhnya bersumber dari publikasi resmi terbuka Otoritas Jasa Keuangan (Statistik Perasuransian Indonesia).

---

## Fitur Utama

1. **Ringkasan Eksekutif**
   - 4 metrik makro: Total Premi Industri, Rata-rata RBC Industri, Rata-rata Rasio Klaim, dan Entitas Dalam Pengawasan.
   - Distribusi pangsa pasar per sektor (Asuransi Jiwa, Umum, Reasuransi, Syariah Jiwa, dan Syariah Umum).
   - Peringkat 10 perusahaan teratas berdasarkan perolehan premi bruto.
   - Ringkasan narasi pasar dinamis berdasarkan tahun pelaporan yang dipilih.

2. **Solvabilitas dan Pengawasan Regulasi OJK**
   - Deteksi dini entitas dengan modal di bawah batas minimum POJK (RBC < 120%), rasio klaim tinggi (> 65%), atau rugi bersih.
   - Grafik 5 entitas dengan rasio modal terendah dan garis batas regulasi 120%.
   - Tabel daftar pengawasan khusus beserta klasifikasi status regulasi.

3. **Evaluasi dan Benchmarking Perusahaan**
   - Pemilihan entitas asuransi terdaftar dengan profil default PT MNC Life Assurance.
   - Status kepatuhan solvabilitas modal dan izin operasional.
   - Matriks perbandingan metrik kunci perusahaan terhadap rata-rata sektor dan rata-rata industri nasional.
   - Grafik tren historis premi bruto dan laba/rugi bersih (2016–2025).

---

## Tech Stack

| Komponen | Teknologi | Keterangan |
|:---|:---|:---|
| **Data Source** | Statistik Perasuransian OJK | Data agregat dan laporan publikasi resmi |
| **Data Contract** | `Pandera` | Validasi tipe data, format ID, dan batas nilai keuangan |
| **OLAP Engine** | `DuckDB` + `Polars` | Pemrosesan analitik lokal dan pembentukan *analytical views* |
| **Visualisasi** | `Plotly` | Visualisasi bar chart, tren historis, dan distribusi |
| **User Interface** | `Streamlit` | Dashboard eksekutif interaktif |
| **Package Manager** | `uv` | Manajemen dependensi dan virtual environment |

---

## Cara Menjalankan

### 1. Inisialisasi Environment

```powershell
# Masuk ke folder proyek
cd "C:\Users\USER\Downloads\Project Portfolio Data\market-intelligence-solvency-dashboard"

# Aktifkan virtual environment
.venv\Scripts\activate

# Pasang dependensi
uv pip install -e ".[dev]"
```

### 2. Muat Basis Data OJK

```powershell
$env:PYTHONIOENCODING='utf-8'

# Generate dataset entitas resmi OJK
python src/generators/ojk_data_builder.py

# Jalankan pipeline ingesti dan transformasi DuckDB
python src/pipeline/ingest.py
python src/pipeline/transform.py
```

### 3. Jalankan Dashboard

```powershell
streamlit run src/app/dashboard.py
```

Buka browser di **http://localhost:8501**.

---

## Struktur Berkas

```text
market-intelligence-solvency-dashboard/
├── docs/                      # Dokumentasi teknis proyek
│   ├── PRD.md                 # Product Requirements Document
│   ├── ARCHITECTURE.md        # Arsitektur sistem dan data flow
│   └── IMPLEMENTATION.md      # Rencana implementasi dan catatan keputusan
├── src/
│   ├── contracts/             # Skema validasi Pandera
│   ├── pipeline/              # Ingesti, parser Excel OJK, dan transformasi DuckDB
│   ├── analytics/             # Perhitungan KPI, ranking, dan tren
│   └── app/                   # Kode dashboard Streamlit
├── data/
│   ├── raw/                   # Berkas data mentah (.parquet)
│   └── asuransi.duckdb        # Database analitik DuckDB
└── tests/                     # Test suite pytest
```

---

## Kepatuhan dan Privasi Data

- Tidak menggunakan data internal atau operasional rahasia dari tempat kerja maupun magang.
- Bebas PII (*Personally Identifiable Information*). Analisis dilakukan pada level korporat yang telah diaudit dan dipublikasikan secara terbuka oleh regulator.
