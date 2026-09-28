"""
Unit Tests — Validasi Pandera Data Contracts.

Memastikan skema validasi bekerja dengan benar untuk data valid dan invalid.
"""

from __future__ import annotations

import pandera.errors as pa_errors
import polars as pl
import pytest

from contracts.schemas import (
    DataSintetisPolisSchema,
    LaporanKeuanganSchema,
    PerusahaanAsuransiSchema,
)


# =====================================================
# Tests: PerusahaanAsuransiSchema
# =====================================================
class TestPerusahaanAsuransiSchema:
    """Test suite untuk skema perusahaan asuransi."""

    def test_valid_data(self) -> None:
        """Data valid harus lolos validasi tanpa error."""
        df = pl.DataFrame(
            {
                "kode_perusahaan": ["ASR-001", "ASR-002"],
                "nama_perusahaan": ["PT Asuransi ABC", "PT Asuransi XYZ"],
                "kategori": ["jiwa", "umum"],
                "tahun_berdiri": [1990, 2005],
                "status_izin": ["aktif", "aktif"],
            }
        )
        result = PerusahaanAsuransiSchema.validate(df)
        assert len(result) == 2

    def test_invalid_kode_format(self) -> None:
        """Kode perusahaan yang tidak sesuai format harus ditolak."""
        df = pl.DataFrame(
            {
                "kode_perusahaan": ["INVALID-01"],
                "nama_perusahaan": ["PT Test"],
                "kategori": ["jiwa"],
                "tahun_berdiri": [2000],
                "status_izin": ["aktif"],
            }
        )
        with pytest.raises(pa_errors.SchemaError):
            PerusahaanAsuransiSchema.validate(df)

    def test_invalid_kategori(self) -> None:
        """Kategori yang tidak ada di enum harus ditolak."""
        df = pl.DataFrame(
            {
                "kode_perusahaan": ["ASR-001"],
                "nama_perusahaan": ["PT Test"],
                "kategori": ["kategori_tidak_valid"],
                "tahun_berdiri": [2000],
                "status_izin": ["aktif"],
            }
        )
        with pytest.raises(pa_errors.SchemaError):
            PerusahaanAsuransiSchema.validate(df)

    def test_invalid_tahun_range(self) -> None:
        """Tahun berdiri di luar range harus ditolak."""
        df = pl.DataFrame(
            {
                "kode_perusahaan": ["ASR-001"],
                "nama_perusahaan": ["PT Test"],
                "kategori": ["jiwa"],
                "tahun_berdiri": [1800],  # Di bawah minimum 1945
                "status_izin": ["aktif"],
            }
        )
        with pytest.raises(pa_errors.SchemaError):
            PerusahaanAsuransiSchema.validate(df)


# =====================================================
# Tests: LaporanKeuanganSchema
# =====================================================
class TestLaporanKeuanganSchema:
    """Test suite untuk skema laporan keuangan."""

    def test_valid_data(self) -> None:
        """Data keuangan valid harus lolos validasi."""
        df = pl.DataFrame(
            {
                "kode_perusahaan": ["ASR-001"],
                "tahun_laporan": [2023],
                "premi_bruto": [500.0],
                "klaim_bruto": [200.0],
                "rasio_klaim": [0.4],
                "rbc_ratio": [250.0],
                "total_aset": [2000.0],
                "total_investasi": [1500.0],
                "laba_rugi_bersih": [100.0],
                "ekuitas": [800.0],
            }
        )
        result = LaporanKeuanganSchema.validate(df)
        assert len(result) == 1

    def test_negative_premi_rejected(self) -> None:
        """Premi bruto negatif harus ditolak."""
        df = pl.DataFrame(
            {
                "kode_perusahaan": ["ASR-001"],
                "tahun_laporan": [2023],
                "premi_bruto": [-100.0],  # Negatif
                "klaim_bruto": [50.0],
                "rasio_klaim": [0.5],
                "rbc_ratio": [150.0],
                "total_aset": [1000.0],
                "total_investasi": [500.0],
                "laba_rugi_bersih": [50.0],
                "ekuitas": [300.0],
            }
        )
        with pytest.raises(pa_errors.SchemaError):
            LaporanKeuanganSchema.validate(df)

    def test_rasio_klaim_out_of_range(self) -> None:
        """Rasio klaim di atas 2.0 harus ditolak."""
        df = pl.DataFrame(
            {
                "kode_perusahaan": ["ASR-001"],
                "tahun_laporan": [2023],
                "premi_bruto": [500.0],
                "klaim_bruto": [200.0],
                "rasio_klaim": [3.5],  # Di atas max 2.0
                "rbc_ratio": [250.0],
                "total_aset": [2000.0],
                "total_investasi": [1500.0],
                "laba_rugi_bersih": [100.0],
                "ekuitas": [800.0],
            }
        )
        with pytest.raises(pa_errors.SchemaError):
            LaporanKeuanganSchema.validate(df)


# =====================================================
# Tests: DataSintetisPolisSchema
# =====================================================
class TestDataSintetisPolisSchema:
    """Test suite untuk skema data sintetis polis."""

    def test_valid_data(self) -> None:
        """Data polis valid harus lolos validasi."""
        df = pl.DataFrame(
            {
                "polis_id": ["POL-000001"],
                "kode_perusahaan": ["ASR-001"],
                "jenis_produk": ["kesehatan"],
                "premi_tahunan": [15.0],
                "is_synthetic": [True],
            }
        )
        result = DataSintetisPolisSchema.validate(df)
        assert len(result) == 1

    def test_synthetic_flag_must_be_true(self) -> None:
        """is_synthetic harus selalu True."""
        df = pl.DataFrame(
            {
                "polis_id": ["POL-000001"],
                "kode_perusahaan": ["ASR-001"],
                "jenis_produk": ["kesehatan"],
                "premi_tahunan": [15.0],
                "is_synthetic": [False],  # Harus True
            }
        )
        with pytest.raises(pa_errors.SchemaError):
            DataSintetisPolisSchema.validate(df)

    def test_invalid_jenis_produk(self) -> None:
        """Jenis produk yang tidak valid harus ditolak."""
        df = pl.DataFrame(
            {
                "polis_id": ["POL-000001"],
                "kode_perusahaan": ["ASR-001"],
                "jenis_produk": ["produk_tidak_ada"],
                "premi_tahunan": [15.0],
                "is_synthetic": [True],
            }
        )
        with pytest.raises(pa_errors.SchemaError):
            DataSintetisPolisSchema.validate(df)
