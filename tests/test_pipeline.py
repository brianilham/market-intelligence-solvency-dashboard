"""
Unit Tests — Data Pipeline (Ingestion & Transformation).

Memvalidasi bahwa synthetic generator menghasilkan data yang benar,
dan pipeline dapat memuat data ke DuckDB serta membuat views.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import polars as pl
import pytest

from generators.synthetic_generator import (
    generate_data_polis,
    generate_laporan_keuangan,
    generate_perusahaan,
)


@pytest.fixture
def sample_perusahaan() -> pl.DataFrame:
    """Generate sample perusahaan data."""
    return generate_perusahaan(n=10)


@pytest.fixture
def sample_laporan(sample_perusahaan: pl.DataFrame) -> pl.DataFrame:
    """Generate sample laporan keuangan."""
    return generate_laporan_keuangan(sample_perusahaan, tahun_mulai=2023, tahun_akhir=2025)


@pytest.fixture
def sample_polis(sample_perusahaan: pl.DataFrame) -> pl.DataFrame:
    """Generate sample polis sintetis."""
    return generate_data_polis(sample_perusahaan, n=50)


@pytest.fixture
def test_db(tmp_path: Path, sample_perusahaan, sample_laporan, sample_polis):
    """Buat test database DuckDB dengan sample data."""
    db_path = tmp_path / "test.duckdb"
    con = duckdb.connect(str(db_path))

    # Load data ke DuckDB
    con.execute("CREATE TABLE perusahaan_asuransi AS SELECT * FROM sample_perusahaan")
    con.execute("CREATE TABLE laporan_keuangan AS SELECT * FROM sample_laporan")
    con.execute("CREATE TABLE data_sintetis_polis AS SELECT * FROM sample_polis")

    yield con
    con.close()


class TestSyntheticGenerator:
    """Test suite untuk synthetic data generator."""

    def test_perusahaan_columns(self, sample_perusahaan: pl.DataFrame) -> None:
        """Perusahaan DataFrame harus memiliki kolom yang benar."""
        expected = {"kode_perusahaan", "nama_perusahaan", "kategori", "tahun_berdiri", "status_izin"}
        assert set(sample_perusahaan.columns) == expected

    def test_perusahaan_count(self, sample_perusahaan: pl.DataFrame) -> None:
        """Jumlah perusahaan harus sesuai parameter."""
        assert len(sample_perusahaan) == 10

    def test_kode_format(self, sample_perusahaan: pl.DataFrame) -> None:
        """Kode perusahaan harus mengikuti format ASR-XXX."""
        for kode in sample_perusahaan["kode_perusahaan"].to_list():
            assert kode.startswith("ASR-")
            assert len(kode) == 7

    def test_laporan_row_count(self, sample_laporan: pl.DataFrame) -> None:
        """Laporan harus memiliki baris = perusahaan × tahun."""
        assert len(sample_laporan) == 10 * 3  # 10 perusahaan × 3 tahun

    def test_polis_synthetic_flag(self, sample_polis: pl.DataFrame) -> None:
        """Semua polis sintetis harus memiliki is_synthetic = True."""
        assert sample_polis["is_synthetic"].all()


class TestPipelineIntegration:
    """Test suite untuk pipeline DuckDB integration."""

    def test_tables_created(self, test_db: duckdb.DuckDBPyConnection) -> None:
        """Semua tabel harus berhasil dibuat di DuckDB."""
        tables = test_db.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'"
        ).fetchall()
        table_names = {t[0] for t in tables}
        assert "perusahaan_asuransi" in table_names
        assert "laporan_keuangan" in table_names
        assert "data_sintetis_polis" in table_names

    def test_perusahaan_data_loaded(self, test_db: duckdb.DuckDBPyConnection) -> None:
        """Data perusahaan harus ter-load dengan benar."""
        count = test_db.execute("SELECT COUNT(*) FROM perusahaan_asuransi").fetchone()[0]
        assert count == 10

    def test_laporan_data_loaded(self, test_db: duckdb.DuckDBPyConnection) -> None:
        """Data laporan keuangan harus ter-load dengan benar."""
        count = test_db.execute("SELECT COUNT(*) FROM laporan_keuangan").fetchone()[0]
        assert count == 30  # 10 × 3

    def test_polis_data_loaded(self, test_db: duckdb.DuckDBPyConnection) -> None:
        """Data polis harus ter-load dengan benar."""
        count = test_db.execute("SELECT COUNT(*) FROM data_sintetis_polis").fetchone()[0]
        assert count == 50

    def test_join_works(self, test_db: duckdb.DuckDBPyConnection) -> None:
        """JOIN antara perusahaan dan laporan keuangan harus berfungsi."""
        result = test_db.execute(
            """
            SELECT COUNT(*) FROM laporan_keuangan lk
            JOIN perusahaan_asuransi pa ON lk.kode_perusahaan = pa.kode_perusahaan
            """
        ).fetchone()[0]
        assert result == 30
