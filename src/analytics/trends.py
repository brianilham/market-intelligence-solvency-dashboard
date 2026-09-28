"""
Trends Module — Analisis tren dan time-series industri asuransi.

Menyediakan fungsi untuk analisis tren industri, pertumbuhan YoY,
market share, dan korelasi antar metrik keuangan.
"""

from __future__ import annotations

import duckdb
import polars as pl


def get_industry_trend(
    con: duckdb.DuckDBPyConnection,
    metric: str = "premi_bruto",
    tahun_mulai: int = 2016,
    tahun_akhir: int = 2025,
) -> pl.DataFrame:
    """Ambil tren metrik industri secara keseluruhan (time-series).

    Args:
        con: Koneksi DuckDB.
        metric: Nama kolom metrik (premi_bruto, rbc_ratio, rasio_klaim, dll).
        tahun_mulai: Tahun awal range.
        tahun_akhir: Tahun akhir range.

    Returns:
        DataFrame dengan kolom: tahun_laporan, total, average, min, max.
    """
    valid_metrics = [
        "premi_bruto", "klaim_bruto", "rasio_klaim", "rbc_ratio",
        "total_aset", "total_investasi", "laba_rugi_bersih", "ekuitas",
    ]
    if metric not in valid_metrics:
        raise ValueError(f"Metrik '{metric}' tidak valid. Pilih dari: {valid_metrics}")

    query = f"""
        SELECT
            tahun_laporan,
            ROUND(SUM({metric}), 2) AS total,
            ROUND(AVG({metric}), 2) AS average,
            ROUND(MIN({metric}), 2) AS minimum,
            ROUND(MAX({metric}), 2) AS maximum,
            COUNT(*) AS jumlah_perusahaan
        FROM laporan_keuangan
        WHERE tahun_laporan BETWEEN ? AND ?
        GROUP BY tahun_laporan
        ORDER BY tahun_laporan
    """

    return pl.from_pandas(con.execute(query, [tahun_mulai, tahun_akhir]).fetchdf())


def get_company_trend(
    con: duckdb.DuckDBPyConnection,
    kode_perusahaan: str,
    metrics: list[str] | None = None,
) -> pl.DataFrame:
    """Ambil tren metrik keuangan untuk satu perusahaan.

    Args:
        con: Koneksi DuckDB.
        kode_perusahaan: Kode unik perusahaan.
        metrics: List metrik yang diinginkan (default: semua metrik).

    Returns:
        DataFrame time-series per tahun untuk perusahaan tersebut.
    """
    if metrics is None:
        metrics = [
            "premi_bruto", "klaim_bruto", "rasio_klaim", "rbc_ratio",
            "total_aset", "total_investasi", "laba_rugi_bersih", "ekuitas",
        ]

    cols = ", ".join(metrics)
    query = f"""
        SELECT tahun_laporan, {cols}
        FROM laporan_keuangan
        WHERE kode_perusahaan = ?
        ORDER BY tahun_laporan
    """

    return pl.from_pandas(con.execute(query, [kode_perusahaan]).fetchdf())


def get_yoy_growth(
    con: duckdb.DuckDBPyConnection,
    kode_perusahaan: str | None = None,
) -> pl.DataFrame:
    """Ambil data Year-over-Year growth dari view vw_yoy_growth.

    Args:
        con: Koneksi DuckDB.
        kode_perusahaan: Filter perusahaan tertentu (opsional).

    Returns:
        DataFrame dengan data YoY growth.
    """
    query = "SELECT * FROM vw_yoy_growth"
    params: list = []

    if kode_perusahaan:
        query += " WHERE kode_perusahaan = ?"
        params.append(kode_perusahaan)

    query += " ORDER BY kode_perusahaan, tahun_laporan"

    return pl.from_pandas(con.execute(query, params).fetchdf())


def get_market_share_trend(con: duckdb.DuckDBPyConnection) -> pl.DataFrame:
    """Ambil data market share per kategori dari view vw_market_share.

    Args:
        con: Koneksi DuckDB.

    Returns:
        DataFrame dengan kolom: tahun_laporan, kategori, market_share_pct.
    """
    query = """
        SELECT tahun_laporan, kategori, total_premi_kategori, market_share_pct
        FROM vw_market_share
        ORDER BY tahun_laporan, market_share_pct DESC
    """
    return pl.from_pandas(con.execute(query).fetchdf())


def get_correlation_matrix(
    con: duckdb.DuckDBPyConnection,
    tahun: int,
) -> pl.DataFrame:
    """Hitung correlation matrix antar metrik keuangan untuk tahun tertentu.

    Args:
        con: Koneksi DuckDB.
        tahun: Tahun pelaporan.

    Returns:
        DataFrame berisi correlation matrix.
    """
    query = """
        SELECT
            premi_bruto, klaim_bruto, rasio_klaim, rbc_ratio,
            total_aset, total_investasi, laba_rugi_bersih, ekuitas
        FROM laporan_keuangan
        WHERE tahun_laporan = ?
    """

    df = pl.from_pandas(con.execute(query, [tahun]).fetchdf())

    # Hitung korelasi Pearson menggunakan Polars
    metrics = df.columns
    corr_data = {}
    for col in metrics:
        corr_row = []
        for other_col in metrics:
            corr_val = df.select(pl.corr(col, other_col)).item()
            corr_row.append(round(corr_val, 4) if corr_val is not None else 0.0)
        corr_data[col] = corr_row

    corr_df = pl.DataFrame(corr_data)
    corr_df = corr_df.with_columns(pl.Series("metric", metrics)).select(
        ["metric"] + metrics
    )

    return corr_df


def get_industry_summary(con: duckdb.DuckDBPyConnection) -> pl.DataFrame:
    """Ambil ringkasan industri per tahun dari view vw_industry_summary.

    Args:
        con: Koneksi DuckDB.

    Returns:
        DataFrame ringkasan industri.
    """
    return pl.from_pandas(
        con.execute("SELECT * FROM vw_industry_summary ORDER BY tahun_laporan").fetchdf()
    )
