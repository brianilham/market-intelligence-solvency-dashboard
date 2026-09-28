"""
Data Transformation Pipeline — Membuat views dan tabel agregat di DuckDB.

Membaca data dari tabel DuckDB yang telah di-ingest, lalu membuat
views analitik untuk digunakan oleh modul analytics dan dashboard.
"""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "asuransi.duckdb"


def create_market_share_view(con: duckdb.DuckDBPyConnection) -> None:
    """Buat view market share per kategori per tahun."""
    con.execute("""
        CREATE OR REPLACE VIEW vw_market_share AS
        WITH total_per_tahun AS (
            SELECT
                lk.tahun_laporan,
                SUM(lk.premi_bruto) AS total_premi_industri
            FROM laporan_keuangan lk
            GROUP BY lk.tahun_laporan
        )
        SELECT
            lk.tahun_laporan,
            pa.kategori,
            SUM(lk.premi_bruto) AS total_premi_kategori,
            tpt.total_premi_industri,
            ROUND(SUM(lk.premi_bruto) / tpt.total_premi_industri * 100, 2) AS market_share_pct
        FROM laporan_keuangan lk
        JOIN perusahaan_asuransi pa ON lk.kode_perusahaan = pa.kode_perusahaan
        JOIN total_per_tahun tpt ON lk.tahun_laporan = tpt.tahun_laporan
        GROUP BY lk.tahun_laporan, pa.kategori, tpt.total_premi_industri
        ORDER BY lk.tahun_laporan, market_share_pct DESC
    """)
    logger.info("✅ View vw_market_share created")


def create_ranking_premi_view(con: duckdb.DuckDBPyConnection) -> None:
    """Buat view ranking perusahaan berdasarkan premi bruto per tahun."""
    con.execute("""
        CREATE OR REPLACE VIEW vw_ranking_premi AS
        SELECT
            lk.tahun_laporan,
            lk.kode_perusahaan,
            pa.nama_perusahaan,
            pa.kategori,
            lk.premi_bruto,
            ROW_NUMBER() OVER (
                PARTITION BY lk.tahun_laporan
                ORDER BY lk.premi_bruto DESC
            ) AS ranking
        FROM laporan_keuangan lk
        JOIN perusahaan_asuransi pa ON lk.kode_perusahaan = pa.kode_perusahaan
        ORDER BY lk.tahun_laporan, ranking
    """)
    logger.info("✅ View vw_ranking_premi created")


def create_ranking_rbc_view(con: duckdb.DuckDBPyConnection) -> None:
    """Buat view ranking perusahaan berdasarkan RBC ratio per tahun."""
    con.execute("""
        CREATE OR REPLACE VIEW vw_ranking_rbc AS
        SELECT
            lk.tahun_laporan,
            lk.kode_perusahaan,
            pa.nama_perusahaan,
            pa.kategori,
            lk.rbc_ratio,
            CASE WHEN lk.rbc_ratio >= 120 THEN 'Sehat' ELSE 'Di Bawah Minimum' END AS status_rbc,
            ROW_NUMBER() OVER (
                PARTITION BY lk.tahun_laporan
                ORDER BY lk.rbc_ratio DESC
            ) AS ranking
        FROM laporan_keuangan lk
        JOIN perusahaan_asuransi pa ON lk.kode_perusahaan = pa.kode_perusahaan
        ORDER BY lk.tahun_laporan, ranking
    """)
    logger.info("✅ View vw_ranking_rbc created")


def create_yoy_growth_view(con: duckdb.DuckDBPyConnection) -> None:
    """Buat view Year-over-Year growth rate per perusahaan."""
    con.execute("""
        CREATE OR REPLACE VIEW vw_yoy_growth AS
        SELECT
            curr.kode_perusahaan,
            pa.nama_perusahaan,
            pa.kategori,
            curr.tahun_laporan,
            curr.premi_bruto AS premi_current,
            prev.premi_bruto AS premi_previous,
            CASE
                WHEN prev.premi_bruto > 0
                THEN ROUND((curr.premi_bruto - prev.premi_bruto) / prev.premi_bruto * 100, 2)
                ELSE NULL
            END AS premi_growth_pct,
            curr.laba_rugi_bersih AS laba_current,
            prev.laba_rugi_bersih AS laba_previous,
            CASE
                WHEN prev.laba_rugi_bersih != 0
                THEN ROUND(
                    (curr.laba_rugi_bersih - prev.laba_rugi_bersih)
                    / ABS(prev.laba_rugi_bersih) * 100, 2
                )
                ELSE NULL
            END AS laba_growth_pct
        FROM laporan_keuangan curr
        JOIN perusahaan_asuransi pa ON curr.kode_perusahaan = pa.kode_perusahaan
        LEFT JOIN laporan_keuangan prev
            ON curr.kode_perusahaan = prev.kode_perusahaan
            AND curr.tahun_laporan = prev.tahun_laporan + 1
        ORDER BY curr.kode_perusahaan, curr.tahun_laporan
    """)
    logger.info("✅ View vw_yoy_growth created")


def create_industry_summary_view(con: duckdb.DuckDBPyConnection) -> None:
    """Buat view ringkasan industri per tahun."""
    con.execute("""
        CREATE OR REPLACE VIEW vw_industry_summary AS
        SELECT
            lk.tahun_laporan,
            COUNT(DISTINCT lk.kode_perusahaan) AS jumlah_perusahaan,
            ROUND(SUM(lk.premi_bruto), 2) AS total_premi,
            ROUND(AVG(lk.premi_bruto), 2) AS avg_premi,
            ROUND(AVG(lk.rasio_klaim), 4) AS avg_rasio_klaim,
            ROUND(AVG(lk.rbc_ratio), 2) AS avg_rbc_ratio,
            ROUND(MIN(lk.rbc_ratio), 2) AS min_rbc_ratio,
            ROUND(MAX(lk.rbc_ratio), 2) AS max_rbc_ratio,
            SUM(CASE WHEN lk.rbc_ratio < 120 THEN 1 ELSE 0 END) AS perusahaan_rbc_dibawah_120,
            ROUND(SUM(lk.total_aset), 2) AS total_aset_industri,
            ROUND(SUM(lk.total_investasi), 2) AS total_investasi_industri,
            ROUND(SUM(lk.laba_rugi_bersih), 2) AS total_laba_industri,
            ROUND(SUM(lk.klaim_bruto), 2) AS total_klaim
        FROM laporan_keuangan lk
        GROUP BY lk.tahun_laporan
        ORDER BY lk.tahun_laporan
    """)
    logger.info("✅ View vw_industry_summary created")


def main() -> None:
    """Entry point untuk pipeline transformasi."""
    print("\n" + "=" * 60)
    print("🔄 MEMULAI DATA TRANSFORMATION PIPELINE")
    print("=" * 60)

    if not DB_PATH.exists():
        logger.error(f"❌ Database {DB_PATH} tidak ditemukan!")
        logger.info("   Jalankan ingest.py terlebih dahulu.")
        return

    con = duckdb.connect(str(DB_PATH))
    logger.info(f"🗄️  Database: {DB_PATH}")

    # Buat semua views
    create_market_share_view(con)
    create_ranking_premi_view(con)
    create_ranking_rbc_view(con)
    create_yoy_growth_view(con)
    create_industry_summary_view(con)

    # Verifikasi views
    views = con.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_type = 'VIEW'
        ORDER BY table_name
    """).fetchall()

    print("\n📋 Views yang berhasil dibuat:")
    for (view_name,) in views:
        count = con.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()[0]
        print(f"   • {view_name}: {count} baris")

    con.close()

    print("\n" + "=" * 60)
    print("✅ TRANSFORMATION SELESAI")
    print("=" * 60)


if __name__ == "__main__":
    main()
