"""
Data Contract & Validation Schemas menggunakan Pandera.

Mendefinisikan skema validasi untuk 3 entitas utama:
1. PerusahaanAsuransiSchema - Master data perusahaan
2. LaporanKeuanganSchema - Data keuangan tahunan
3. DataSintetisPolis - Data polis sintetis (augmentasi)
"""

import pandera.polars as pa
import polars as pl


class PerusahaanAsuransiSchema(pa.DataFrameModel):
    """Skema validasi untuk master data perusahaan asuransi."""

    kode_perusahaan: pl.Utf8 = pa.Field(
        str_matches=r"^ASR-\d{3}$",
        description="ID unik perusahaan, format 'ASR-XXX'",
    )
    nama_perusahaan: pl.Utf8 = pa.Field(
        str_length={"min_value": 3, "max_value": 200},
        description="Nama resmi perusahaan",
    )
    kategori: pl.Utf8 = pa.Field(
        isin=["jiwa", "umum", "reasuransi", "syariah_jiwa", "syariah_umum"],
        description="Kategori asuransi",
    )
    tahun_berdiri: pl.Int64 = pa.Field(
        ge=1945,
        le=2026,
        description="Tahun pendirian perusahaan",
    )
    status_izin: pl.Utf8 = pa.Field(
        isin=["aktif", "dicabut", "dalam_pengawasan"],
        description="Status operasional perusahaan",
    )

    class Config:
        coerce = True
        strict = "filter"


class LaporanKeuanganSchema(pa.DataFrameModel):
    """Skema validasi untuk data keuangan tahunan perusahaan asuransi."""

    kode_perusahaan: pl.Utf8 = pa.Field(
        str_matches=r"^ASR-\d{3}$",
        description="FK ke perusahaan_asuransi",
    )
    tahun_laporan: pl.Int64 = pa.Field(
        ge=2015,
        le=2026,
        description="Tahun pelaporan fiskal",
    )
    premi_bruto: pl.Float64 = pa.Field(
        ge=0.0,
        description="Total premi bruto dalam miliar Rupiah",
    )
    klaim_bruto: pl.Float64 = pa.Field(
        ge=0.0,
        description="Total klaim bruto dalam miliar Rupiah",
    )
    rasio_klaim: pl.Float64 = pa.Field(
        ge=0.0,
        le=2.0,
        description="Rasio klaim terhadap premi (Klaim/Premi)",
    )
    rbc_ratio: pl.Float64 = pa.Field(
        ge=0.0,
        description="Risk-Based Capital ratio (minimum regulasi OJK: 120%)",
    )
    total_aset: pl.Float64 = pa.Field(
        ge=0.0,
        description="Total aset dalam miliar Rupiah",
    )
    total_investasi: pl.Float64 = pa.Field(
        ge=0.0,
        description="Total investasi dalam miliar Rupiah",
    )
    laba_rugi_bersih: pl.Float64 = pa.Field(
        description="Laba (+) atau Rugi (-) dalam miliar Rupiah",
    )
    ekuitas: pl.Float64 = pa.Field(
        description="Total ekuitas dalam miliar Rupiah",
    )

    class Config:
        coerce = True
        strict = "filter"


class DataSintetisPolisSchema(pa.DataFrameModel):
    """Skema validasi untuk data sintetis polis (augmentasi).

    PENTING: Data ini selalu berlabel is_synthetic=True.
    """

    polis_id: pl.Utf8 = pa.Field(
        description="ID polis sintetis",
    )
    kode_perusahaan: pl.Utf8 = pa.Field(
        str_matches=r"^ASR-\d{3}$",
        description="FK ke perusahaan_asuransi",
    )
    jenis_produk: pl.Utf8 = pa.Field(
        isin=[
            "jiwa_tradisional",
            "unit_link",
            "kesehatan",
            "kendaraan",
            "properti",
            "marine",
        ],
        description="Kategori produk asuransi",
    )
    premi_tahunan: pl.Float64 = pa.Field(
        ge=0.0,
        description="Premi tahunan dalam juta Rupiah",
    )
    is_synthetic: pl.Boolean = pa.Field(
        eq=True,
        description="Watermark: selalu True untuk data sintetis",
    )

    class Config:
        coerce = True
        strict = "filter"
