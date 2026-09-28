"""
KPI Calculations — Kalkulasi Key Performance Indicators industri asuransi.

Menyediakan fungsi untuk menghitung KPI di level industri dan per perusahaan
menggunakan query DuckDB.
"""

from __future__ import annotations

import duckdb


def calculate_industry_kpis(con: duckdb.DuckDBPyConnection) -> dict:
    """Hitung KPI industri asuransi berdasarkan data tahun terbaru.

    Args:
        con: Koneksi DuckDB aktif.

    Returns:
        Dictionary berisi KPI industri:
        - total_perusahaan, total_perusahaan_aktif
        - total_premi_industri, avg_rbc_ratio, avg_rasio_klaim
        - total_laba_industri, perusahaan_rbc_dibawah_120
        - tahun_terbaru
    """
    # Ambil tahun terbaru
    tahun_terbaru = con.execute(
        "SELECT MAX(tahun_laporan) FROM laporan_keuangan"
    ).fetchone()[0]

    # KPI dari master data perusahaan
    total = con.execute("SELECT COUNT(*) FROM perusahaan_asuransi").fetchone()[0]
    aktif = con.execute(
        "SELECT COUNT(*) FROM perusahaan_asuransi WHERE status_izin = 'aktif'"
    ).fetchone()[0]

    # KPI dari laporan keuangan tahun terbaru
    row = con.execute(
        """
        SELECT
            ROUND(SUM(premi_bruto), 2) AS total_premi,
            ROUND(AVG(rbc_ratio), 2) AS avg_rbc,
            ROUND(AVG(rasio_klaim), 4) AS avg_klaim,
            ROUND(SUM(laba_rugi_bersih), 2) AS total_laba,
            SUM(CASE WHEN rbc_ratio < 120 THEN 1 ELSE 0 END) AS rbc_dibawah
        FROM laporan_keuangan
        WHERE tahun_laporan = ?
        """,
        [tahun_terbaru],
    ).fetchone()

    return {
        "total_perusahaan": total,
        "total_perusahaan_aktif": aktif,
        "total_premi_industri": row[0] or 0.0,
        "avg_rbc_ratio": row[1] or 0.0,
        "avg_rasio_klaim": row[2] or 0.0,
        "total_laba_industri": row[3] or 0.0,
        "perusahaan_rbc_dibawah_120": row[4] or 0,
        "tahun_terbaru": tahun_terbaru,
    }


def calculate_company_kpis(
    con: duckdb.DuckDBPyConnection,
    kode_perusahaan: str,
) -> dict:
    """Hitung KPI untuk satu perusahaan asuransi tertentu.

    Args:
        con: Koneksi DuckDB aktif.
        kode_perusahaan: Kode unik perusahaan (misal 'ASR-001').

    Returns:
        Dictionary berisi KPI perusahaan.
    """
    # Info perusahaan
    info = con.execute(
        """
        SELECT nama_perusahaan, kategori, tahun_berdiri, status_izin
        FROM perusahaan_asuransi WHERE kode_perusahaan = ?
        """,
        [kode_perusahaan],
    ).fetchone()

    if not info:
        return {"error": f"Perusahaan {kode_perusahaan} tidak ditemukan"}

    # Data keuangan terbaru
    fin = con.execute(
        """
        SELECT
            tahun_laporan,
            premi_bruto, klaim_bruto, rasio_klaim,
            rbc_ratio, total_aset, total_investasi,
            laba_rugi_bersih, ekuitas
        FROM laporan_keuangan
        WHERE kode_perusahaan = ?
        ORDER BY tahun_laporan DESC
        LIMIT 1
        """,
        [kode_perusahaan],
    ).fetchone()

    # Rata-rata historis
    avg = con.execute(
        """
        SELECT
            ROUND(AVG(premi_bruto), 2),
            ROUND(AVG(rbc_ratio), 2),
            ROUND(AVG(rasio_klaim), 4),
            COUNT(tahun_laporan)
        FROM laporan_keuangan
        WHERE kode_perusahaan = ?
        """,
        [kode_perusahaan],
    ).fetchone()

    return {
        "kode_perusahaan": kode_perusahaan,
        "nama_perusahaan": info[0],
        "kategori": info[1],
        "tahun_berdiri": info[2],
        "status_izin": info[3],
        "tahun_laporan_terbaru": fin[0] if fin else None,
        "premi_bruto": fin[1] if fin else 0.0,
        "klaim_bruto": fin[2] if fin else 0.0,
        "rasio_klaim": fin[3] if fin else 0.0,
        "rbc_ratio": fin[4] if fin else 0.0,
        "total_aset": fin[5] if fin else 0.0,
        "total_investasi": fin[6] if fin else 0.0,
        "laba_rugi_bersih": fin[7] if fin else 0.0,
        "ekuitas": fin[8] if fin else 0.0,
        "avg_premi_historis": avg[0] if avg else 0.0,
        "avg_rbc_historis": avg[1] if avg else 0.0,
        "avg_klaim_historis": avg[2] if avg else 0.0,
        "jumlah_tahun_data": avg[3] if avg else 0,
    }
