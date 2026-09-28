"""
Ranking Module — Perankingan perusahaan asuransi berdasarkan berbagai metrik.

Menyediakan fungsi ranking berdasarkan premi bruto, RBC ratio,
profitabilitas, dan composite score.
"""

from __future__ import annotations

import duckdb
import polars as pl


def rank_by_premi(
    con: duckdb.DuckDBPyConnection,
    tahun: int,
    kategori: str | None = None,
    top_n: int = 20,
) -> pl.DataFrame:
    """Ranking perusahaan berdasarkan premi bruto.

    Args:
        con: Koneksi DuckDB.
        tahun: Tahun pelaporan.
        kategori: Filter kategori (opsional).
        top_n: Jumlah perusahaan teratas.

    Returns:
        DataFrame dengan kolom: ranking, kode_perusahaan, nama_perusahaan,
        kategori, premi_bruto.
    """
    query = """
        SELECT
            ROW_NUMBER() OVER (ORDER BY lk.premi_bruto DESC) AS ranking,
            lk.kode_perusahaan,
            pa.nama_perusahaan,
            pa.kategori,
            lk.premi_bruto
        FROM laporan_keuangan lk
        JOIN perusahaan_asuransi pa ON lk.kode_perusahaan = pa.kode_perusahaan
        WHERE lk.tahun_laporan = ?
    """
    params: list = [tahun]

    if kategori:
        query += " AND pa.kategori = ?"
        params.append(kategori)

    query += f" ORDER BY lk.premi_bruto DESC LIMIT {top_n}"

    return pl.from_pandas(con.execute(query, params).fetchdf())


def rank_by_rbc(
    con: duckdb.DuckDBPyConnection,
    tahun: int,
    kategori: str | None = None,
    top_n: int = 20,
) -> pl.DataFrame:
    """Ranking perusahaan berdasarkan RBC ratio.

    Args:
        con: Koneksi DuckDB.
        tahun: Tahun pelaporan.
        kategori: Filter kategori (opsional).
        top_n: Jumlah perusahaan teratas.

    Returns:
        DataFrame dengan kolom ranking dan metrik RBC.
    """
    query = """
        SELECT
            ROW_NUMBER() OVER (ORDER BY lk.rbc_ratio DESC) AS ranking,
            lk.kode_perusahaan,
            pa.nama_perusahaan,
            pa.kategori,
            lk.rbc_ratio,
            CASE WHEN lk.rbc_ratio >= 120 THEN '✅ Sehat' ELSE '⚠️ Di Bawah Minimum' END AS status
        FROM laporan_keuangan lk
        JOIN perusahaan_asuransi pa ON lk.kode_perusahaan = pa.kode_perusahaan
        WHERE lk.tahun_laporan = ?
    """
    params: list = [tahun]

    if kategori:
        query += " AND pa.kategori = ?"
        params.append(kategori)

    query += f" ORDER BY lk.rbc_ratio DESC LIMIT {top_n}"

    return pl.from_pandas(con.execute(query, params).fetchdf())


def rank_by_profitabilitas(
    con: duckdb.DuckDBPyConnection,
    tahun: int,
    kategori: str | None = None,
    top_n: int = 20,
) -> pl.DataFrame:
    """Ranking perusahaan berdasarkan profitabilitas (laba/rugi bersih).

    Args:
        con: Koneksi DuckDB.
        tahun: Tahun pelaporan.
        kategori: Filter kategori (opsional).
        top_n: Jumlah perusahaan teratas.

    Returns:
        DataFrame dengan kolom ranking dan metrik profitabilitas.
    """
    query = """
        SELECT
            ROW_NUMBER() OVER (ORDER BY lk.laba_rugi_bersih DESC) AS ranking,
            lk.kode_perusahaan,
            pa.nama_perusahaan,
            pa.kategori,
            lk.laba_rugi_bersih,
            lk.premi_bruto,
            ROUND(lk.laba_rugi_bersih / NULLIF(lk.premi_bruto, 0) * 100, 2) AS profit_margin_pct
        FROM laporan_keuangan lk
        JOIN perusahaan_asuransi pa ON lk.kode_perusahaan = pa.kode_perusahaan
        WHERE lk.tahun_laporan = ?
    """
    params: list = [tahun]

    if kategori:
        query += " AND pa.kategori = ?"
        params.append(kategori)

    query += f" ORDER BY lk.laba_rugi_bersih DESC LIMIT {top_n}"

    return pl.from_pandas(con.execute(query, params).fetchdf())


def rank_composite(
    con: duckdb.DuckDBPyConnection,
    tahun: int,
    weights: dict[str, float] | None = None,
) -> pl.DataFrame:
    """Ranking komposit berdasarkan kombinasi metrik berbobot.

    Skor komposit dihitung dari normalisasi (0-100) tiap metrik
    dikalikan bobot masing-masing.

    Args:
        con: Koneksi DuckDB.
        tahun: Tahun pelaporan.
        weights: Bobot per metrik (default: premi=0.3, rbc=0.3, profit=0.2, aset=0.2).

    Returns:
        DataFrame dengan kolom ranking dan composite score.
    """
    if weights is None:
        weights = {
            "premi_bruto": 0.30,
            "rbc_ratio": 0.30,
            "laba_rugi_bersih": 0.20,
            "total_aset": 0.20,
        }

    # Normalisasi min-max per metrik dan hitung skor komposit
    query = f"""
        WITH raw_data AS (
            SELECT
                lk.kode_perusahaan,
                pa.nama_perusahaan,
                pa.kategori,
                lk.premi_bruto,
                lk.rbc_ratio,
                lk.laba_rugi_bersih,
                lk.total_aset
            FROM laporan_keuangan lk
            JOIN perusahaan_asuransi pa ON lk.kode_perusahaan = pa.kode_perusahaan
            WHERE lk.tahun_laporan = ?
        ),
        normalized AS (
            SELECT *,
                (premi_bruto - MIN(premi_bruto) OVER()) /
                    NULLIF(MAX(premi_bruto) OVER() - MIN(premi_bruto) OVER(), 0) * 100
                    AS norm_premi,
                (rbc_ratio - MIN(rbc_ratio) OVER()) /
                    NULLIF(MAX(rbc_ratio) OVER() - MIN(rbc_ratio) OVER(), 0) * 100
                    AS norm_rbc,
                (laba_rugi_bersih - MIN(laba_rugi_bersih) OVER()) /
                    NULLIF(MAX(laba_rugi_bersih) OVER() - MIN(laba_rugi_bersih) OVER(), 0) * 100
                    AS norm_laba,
                (total_aset - MIN(total_aset) OVER()) /
                    NULLIF(MAX(total_aset) OVER() - MIN(total_aset) OVER(), 0) * 100
                    AS norm_aset
            FROM raw_data
        )
        SELECT
            ROW_NUMBER() OVER (ORDER BY composite_score DESC) AS ranking,
            kode_perusahaan,
            nama_perusahaan,
            kategori,
            ROUND(composite_score, 2) AS composite_score,
            premi_bruto,
            rbc_ratio,
            laba_rugi_bersih,
            total_aset
        FROM (
            SELECT *,
                COALESCE(norm_premi, 0) * {weights['premi_bruto']} +
                COALESCE(norm_rbc, 0) * {weights['rbc_ratio']} +
                COALESCE(norm_laba, 0) * {weights['laba_rugi_bersih']} +
                COALESCE(norm_aset, 0) * {weights['total_aset']}
                AS composite_score
            FROM normalized
        ) sub
        ORDER BY composite_score DESC
    """

    return pl.from_pandas(con.execute(query, [tahun]).fetchdf())
