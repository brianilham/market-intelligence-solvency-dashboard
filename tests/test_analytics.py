"""
Unit Tests — Analytics Modules (KPI, Ranking, Trends).

Memvalidasi kalkulasi KPI, ranking, dan tren menggunakan
test database DuckDB dengan data sample.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pytest

from analytics.kpi import calculate_company_kpis, calculate_industry_kpis
from analytics.ranking import rank_by_premi, rank_composite
from analytics.trends import get_company_trend, get_industry_trend
from generators.synthetic_generator import (
    generate_laporan_keuangan,
    generate_perusahaan,
)
from pipeline.transform import (
    create_industry_summary_view,
    create_market_share_view,
    create_ranking_premi_view,
    create_yoy_growth_view,
)


@pytest.fixture
def analytics_db(tmp_path: Path):
    """Buat test database lengkap dengan views untuk analytics."""
    db_path = tmp_path / "analytics_test.duckdb"
    con = duckdb.connect(str(db_path))

    # Generate data
    df_perusahaan = generate_perusahaan(n=20)
    df_laporan = generate_laporan_keuangan(df_perusahaan, tahun_mulai=2022, tahun_akhir=2025)  # noqa: F841

    con.execute("CREATE TABLE perusahaan_asuransi AS SELECT * FROM df_perusahaan")
    con.execute("CREATE TABLE laporan_keuangan AS SELECT * FROM df_laporan")

    # Buat views
    create_market_share_view(con)
    create_ranking_premi_view(con)
    create_yoy_growth_view(con)
    create_industry_summary_view(con)

    yield con
    con.close()


class TestKPI:
    """Test suite untuk modul KPI."""

    def test_industry_kpis_keys(self, analytics_db: duckdb.DuckDBPyConnection) -> None:
        """Industry KPIs harus mengandung semua key yang diharapkan."""
        kpis = calculate_industry_kpis(analytics_db)
        expected_keys = {
            "total_perusahaan", "total_perusahaan_aktif",
            "total_premi_industri", "avg_rbc_ratio",
            "avg_rasio_klaim", "total_laba_industri",
            "perusahaan_rbc_dibawah_120", "tahun_terbaru",
        }
        assert set(kpis.keys()) == expected_keys

    def test_industry_kpis_types(self, analytics_db: duckdb.DuckDBPyConnection) -> None:
        """Tipe data KPI harus sesuai."""
        kpis = calculate_industry_kpis(analytics_db)
        assert isinstance(kpis["total_perusahaan"], int)
        assert isinstance(kpis["total_premi_industri"], float)
        assert isinstance(kpis["tahun_terbaru"], int)

    def test_company_kpis_valid(self, analytics_db: duckdb.DuckDBPyConnection) -> None:
        """KPI perusahaan valid harus mengembalikan data lengkap."""
        kpis = calculate_company_kpis(analytics_db, "ASR-001")
        assert kpis["kode_perusahaan"] == "ASR-001"
        assert "nama_perusahaan" in kpis

    def test_company_kpis_not_found(self, analytics_db: duckdb.DuckDBPyConnection) -> None:
        """KPI perusahaan yang tidak ada harus mengembalikan error."""
        kpis = calculate_company_kpis(analytics_db, "ASR-999")
        assert "error" in kpis


class TestRanking:
    """Test suite untuk modul ranking."""

    def test_rank_by_premi_ordering(self, analytics_db: duckdb.DuckDBPyConnection) -> None:
        """Ranking premi harus terurut descending."""
        df = rank_by_premi(analytics_db, tahun=2025, top_n=10)
        premi_values = df["premi_bruto"].to_list()
        assert premi_values == sorted(premi_values, reverse=True)

    def test_rank_by_premi_columns(self, analytics_db: duckdb.DuckDBPyConnection) -> None:
        """Ranking premi harus memiliki kolom yang benar."""
        df = rank_by_premi(analytics_db, tahun=2025)
        assert "ranking" in df.columns
        assert "nama_perusahaan" in df.columns
        assert "premi_bruto" in df.columns

    def test_rank_composite_has_score(self, analytics_db: duckdb.DuckDBPyConnection) -> None:
        """Composite ranking harus memiliki composite_score."""
        df = rank_composite(analytics_db, tahun=2025)
        assert "composite_score" in df.columns
        assert len(df) > 0


class TestTrends:
    """Test suite untuk modul trends."""

    def test_industry_trend_columns(self, analytics_db: duckdb.DuckDBPyConnection) -> None:
        """Industry trend harus memiliki kolom time-series."""
        df = get_industry_trend(analytics_db, metric="premi_bruto")
        assert "tahun_laporan" in df.columns
        assert "total" in df.columns
        assert len(df) > 0

    def test_company_trend(self, analytics_db: duckdb.DuckDBPyConnection) -> None:
        """Company trend harus mengembalikan data per tahun."""
        df = get_company_trend(analytics_db, "ASR-001")
        assert "tahun_laporan" in df.columns
        assert len(df) > 0

    def test_invalid_metric_raises(self, analytics_db: duckdb.DuckDBPyConnection) -> None:
        """Metrik yang tidak valid harus raise ValueError."""
        with pytest.raises(ValueError):
            get_industry_trend(analytics_db, metric="metrik_palsu")
