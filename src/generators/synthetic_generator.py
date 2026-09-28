"""
Generator Data Sintetis Industri Asuransi Indonesia.

Menghasilkan 3 dataset sintetis menggunakan Faker:
1. Master data perusahaan asuransi (~80 perusahaan)
2. Laporan keuangan tahunan (2016-2025, ~800 baris)
3. Data polis sintetis untuk augmentasi (~5000 baris)

Semua data sintetis diberi label jelas agar tidak disalahartikan sebagai data riil.
Output disimpan sebagai file Parquet di data/raw/.
"""

from __future__ import annotations

import random
from pathlib import Path

import polars as pl
from faker import Faker

# --- Konfigurasi ---
SEED = 42
NUM_PERUSAHAAN = 80
TAHUN_MULAI = 2016
TAHUN_AKHIR = 2025
NUM_POLIS_SINTETIS = 5000
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

KATEGORI_ASURANSI = ["jiwa", "umum", "reasuransi", "syariah_jiwa", "syariah_umum"]
KATEGORI_WEIGHTS = [0.30, 0.35, 0.10, 0.12, 0.13]  # Distribusi realistis

STATUS_IZIN = ["aktif", "dicabut", "dalam_pengawasan"]
STATUS_WEIGHTS = [0.85, 0.08, 0.07]

JENIS_PRODUK = [
    "jiwa_tradisional",
    "unit_link",
    "kesehatan",
    "kendaraan",
    "properti",
    "marine",
]

fake = Faker("id_ID")
Faker.seed(SEED)
random.seed(SEED)


def generate_perusahaan(n: int = NUM_PERUSAHAAN) -> pl.DataFrame:
    """Generate master data perusahaan asuransi."""
    records = []
    for i in range(1, n + 1):
        kategori = random.choices(KATEGORI_ASURANSI, weights=KATEGORI_WEIGHTS, k=1)[0]

        # Prefix nama berdasarkan kategori
        prefix_map = {
            "jiwa": "Asuransi Jiwa",
            "umum": "Asuransi",
            "reasuransi": "Reasuransi",
            "syariah_jiwa": "Asuransi Jiwa Syariah",
            "syariah_umum": "Asuransi Syariah",
        }
        prefix = prefix_map[kategori]
        nama = f"PT {prefix} {fake.company_suffix()} {fake.last_name()}"

        records.append(
            {
                "kode_perusahaan": f"ASR-{i:03d}",
                "nama_perusahaan": nama,
                "kategori": kategori,
                "tahun_berdiri": random.randint(1955, 2020),
                "status_izin": random.choices(STATUS_IZIN, weights=STATUS_WEIGHTS, k=1)[0],
            }
        )

    return pl.DataFrame(records)


def generate_laporan_keuangan(
    df_perusahaan: pl.DataFrame,
    tahun_mulai: int = TAHUN_MULAI,
    tahun_akhir: int = TAHUN_AKHIR,
) -> pl.DataFrame:
    """Generate data laporan keuangan tahunan untuk setiap perusahaan."""
    records = []
    kode_list = df_perusahaan["kode_perusahaan"].to_list()
    kategori_map = dict(
        zip(
            df_perusahaan["kode_perusahaan"].to_list(),
            df_perusahaan["kategori"].to_list(),
        )
    )

    for kode in kode_list:
        kategori = kategori_map[kode]

        # Base values bervariasi per kategori (dalam miliar Rupiah)
        base_premi = {
            "jiwa": random.uniform(500, 15000),
            "umum": random.uniform(200, 8000),
            "reasuransi": random.uniform(1000, 20000),
            "syariah_jiwa": random.uniform(100, 3000),
            "syariah_umum": random.uniform(50, 2000),
        }[kategori]

        for tahun in range(tahun_mulai, tahun_akhir + 1):
            # Simulasi pertumbuhan tahunan dengan noise
            growth = random.uniform(-0.05, 0.15)
            premi_bruto = max(0.1, base_premi * (1 + growth))
            base_premi = premi_bruto  # Compound growth

            rasio_klaim = random.uniform(0.25, 0.85)
            klaim_bruto = premi_bruto * rasio_klaim
            rbc_ratio = random.uniform(100, 500)  # Beberapa di bawah 120% (bermasalah)
            total_aset = premi_bruto * random.uniform(1.5, 5.0)
            total_investasi = total_aset * random.uniform(0.4, 0.8)
            margin = random.uniform(-0.1, 0.2)
            laba_rugi = premi_bruto * margin
            ekuitas = total_aset * random.uniform(0.15, 0.5)

            records.append(
                {
                    "kode_perusahaan": kode,
                    "tahun_laporan": tahun,
                    "premi_bruto": round(premi_bruto, 2),
                    "klaim_bruto": round(klaim_bruto, 2),
                    "rasio_klaim": round(rasio_klaim, 4),
                    "rbc_ratio": round(rbc_ratio, 2),
                    "total_aset": round(total_aset, 2),
                    "total_investasi": round(total_investasi, 2),
                    "laba_rugi_bersih": round(laba_rugi, 2),
                    "ekuitas": round(ekuitas, 2),
                }
            )

    return pl.DataFrame(records)


def generate_data_polis(
    df_perusahaan: pl.DataFrame,
    n: int = NUM_POLIS_SINTETIS,
) -> pl.DataFrame:
    """Generate data polis sintetis untuk augmentasi."""
    kode_aktif = (
        df_perusahaan.filter(pl.col("status_izin") == "aktif")["kode_perusahaan"]
        .to_list()
    )

    records = []
    for i in range(1, n + 1):
        jenis = random.choice(JENIS_PRODUK)

        # Premi bervariasi per jenis produk (dalam juta Rupiah)
        premi_range = {
            "jiwa_tradisional": (2, 50),
            "unit_link": (5, 100),
            "kesehatan": (3, 30),
            "kendaraan": (1, 15),
            "properti": (5, 80),
            "marine": (10, 200),
        }[jenis]

        records.append(
            {
                "polis_id": f"POL-{i:06d}",
                "kode_perusahaan": random.choice(kode_aktif),
                "jenis_produk": jenis,
                "premi_tahunan": round(random.uniform(*premi_range), 2),
                "is_synthetic": True,
            }
        )

    return pl.DataFrame(records)


def main() -> None:
    """Generate semua dataset sintetis dan simpan ke data/raw/."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("🏗️  Generating master data perusahaan asuransi...")
    df_perusahaan = generate_perusahaan()
    perusahaan_path = OUTPUT_DIR / "perusahaan_asuransi.parquet"
    df_perusahaan.write_parquet(perusahaan_path)
    print(f"   ✅ {len(df_perusahaan)} perusahaan → {perusahaan_path}")

    print("📊 Generating laporan keuangan tahunan...")
    df_laporan = generate_laporan_keuangan(df_perusahaan)
    laporan_path = OUTPUT_DIR / "laporan_keuangan.parquet"
    df_laporan.write_parquet(laporan_path)
    print(f"   ✅ {len(df_laporan)} baris → {laporan_path}")

    print("📋 Generating data polis sintetis...")
    df_polis = generate_data_polis(df_perusahaan)
    polis_path = OUTPUT_DIR / "data_sintetis_polis.parquet"
    df_polis.write_parquet(polis_path)
    print(f"   ✅ {len(df_polis)} polis → {polis_path}")

    print("\n🎉 Semua data sintetis berhasil di-generate!")
    print(f"   📂 Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
