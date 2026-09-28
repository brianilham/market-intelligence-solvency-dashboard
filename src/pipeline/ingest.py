"""
Data Ingestion Pipeline — Ingest, Validasi, dan Load ke DuckDB.

Membaca file Parquet dari data/raw/, memvalidasi menggunakan Pandera schemas,
mengarantina baris yang tidak valid, dan memuat data valid ke DuckDB.
"""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb
import polars as pl

from contracts.schemas import (
    DataSintetisPolisSchema,
    LaporanKeuanganSchema,
    PerusahaanAsuransiSchema,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
QUARANTINE_DIR = PROJECT_ROOT / "data" / "processed" / "quarantine"
DB_PATH = PROJECT_ROOT / "data" / "asuransi.duckdb"

# Mapping: nama file → (nama tabel DuckDB, Pandera schema)
TABLE_CONFIG = {
    "perusahaan_asuransi.parquet": ("perusahaan_asuransi", PerusahaanAsuransiSchema),
    "laporan_keuangan.parquet": ("laporan_keuangan", LaporanKeuanganSchema),
    "data_sintetis_polis.parquet": ("data_sintetis_polis", DataSintetisPolisSchema),
}


def read_raw_data(file_path: Path) -> pl.DataFrame:
    """Baca file Parquet dari direktori raw.

    Args:
        file_path: Path ke file Parquet.

    Returns:
        DataFrame dari file yang dibaca.
    """
    logger.info(f"📖 Membaca {file_path.name}...")
    df = pl.read_parquet(file_path)
    logger.info(f"   Loaded {len(df)} baris, {len(df.columns)} kolom")
    return df


def validate_data(
    df: pl.DataFrame,
    schema: type,
    table_name: str,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Validasi DataFrame menggunakan Pandera schema.

    Args:
        df: DataFrame yang akan divalidasi.
        schema: Pandera schema class.
        table_name: Nama tabel untuk logging.

    Returns:
        Tuple (valid_df, invalid_df) — data yang lolos dan gagal validasi.
    """
    logger.info(f"🔍 Memvalidasi {table_name} dengan Pandera...")

    try:
        valid_df = schema.validate(df)
        n_valid = len(valid_df)
        n_invalid = len(df) - n_valid
        logger.info(f"   ✅ Valid: {n_valid} baris | ❌ Invalid: {n_invalid} baris")

        # Identifikasi baris yang gagal validasi
        if n_invalid > 0:
            valid_indices = set(range(len(valid_df)))
            all_indices = set(range(len(df)))
            invalid_indices = list(all_indices - valid_indices)
            invalid_df = df[invalid_indices] if invalid_indices else pl.DataFrame()
        else:
            invalid_df = pl.DataFrame()

        return valid_df, invalid_df

    except Exception as e:
        logger.error(f"   ⚠️ Validasi gagal untuk {table_name}: {e}")
        logger.warning("   Melanjutkan dengan data asli tanpa validasi ketat")
        return df, pl.DataFrame()


def quarantine_invalid(invalid_df: pl.DataFrame, table_name: str) -> None:
    """Simpan baris yang gagal validasi ke direktori quarantine.

    Args:
        invalid_df: DataFrame berisi baris yang gagal validasi.
        table_name: Nama tabel untuk penamaan file.
    """
    if len(invalid_df) == 0:
        return

    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    quarantine_path = QUARANTINE_DIR / f"{table_name}_quarantine.parquet"
    invalid_df.write_parquet(quarantine_path)
    logger.warning(f"   🔒 {len(invalid_df)} baris di-quarantine → {quarantine_path}")


def load_to_duckdb(
    con: duckdb.DuckDBPyConnection,
    df: pl.DataFrame,
    table_name: str,
) -> None:
    """Load DataFrame ke tabel DuckDB.

    Args:
        con: Koneksi DuckDB.
        df: DataFrame yang akan di-load.
        table_name: Nama tabel di DuckDB.
    """
    logger.info(f"💾 Loading {table_name} ke DuckDB ({len(df)} baris)...")

    # Drop table jika sudah ada, lalu buat ulang dari DataFrame
    con.execute(f"DROP TABLE IF EXISTS {table_name}")
    con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")

    # Verifikasi
    count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    logger.info(f"   ✅ {table_name}: {count} baris berhasil di-load ke DuckDB")


def main() -> None:
    """Entry point untuk pipeline ingestion."""
    print("\n" + "=" * 60)
    print("🚀 MEMULAI DATA INGESTION PIPELINE")
    print("=" * 60)

    # Validasi bahwa raw data tersedia
    if not RAW_DIR.exists():
        logger.error(f"❌ Direktori {RAW_DIR} tidak ditemukan!")
        logger.info("   Jalankan synthetic_generator.py terlebih dahulu.")
        return

    # Buka koneksi DuckDB
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    logger.info(f"🗄️  Database: {DB_PATH}")

    total_loaded = 0
    total_quarantined = 0

    for filename, (table_name, schema) in TABLE_CONFIG.items():
        file_path = RAW_DIR / filename
        if not file_path.exists():
            logger.warning(f"⏭️  Skip {filename} — file tidak ditemukan")
            continue

        # 1. Baca raw data
        df = read_raw_data(file_path)

        # 2. Validasi dengan Pandera
        valid_df, invalid_df = validate_data(df, schema, table_name)

        # 3. Quarantine invalid rows
        quarantine_invalid(invalid_df, table_name)
        total_quarantined += len(invalid_df)

        # 4. Load ke DuckDB
        load_to_duckdb(con, valid_df, table_name)
        total_loaded += len(valid_df)

    con.close()

    print("\n" + "=" * 60)
    print("✅ INGESTION SELESAI")
    print(f"   📊 Total loaded  : {total_loaded} baris")
    print(f"   🔒 Total quarantine: {total_quarantined} baris")
    print(f"   🗄️  Database      : {DB_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
