"""
OJK Web Scraper — Scraping data statistik perasuransian dari website OJK.

Catatan: Scraper ini menggunakan placeholder CSS selectors yang perlu disesuaikan
dengan struktur aktual website OJK. Scraper dirancang dengan retry mechanism
dan fallback ke cached data jika scraping gagal.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

import polars as pl
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://www.ojk.go.id"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
CACHE_DIR = Path(__file__).resolve().parents[2] / "data" / "cache"


class OJKScraper:
    """Scraper untuk data statistik perasuransian dari OJK.

    Attributes:
        base_url: URL dasar website OJK.
        output_dir: Direktori output untuk menyimpan hasil scraping.
        max_retries: Jumlah maksimum percobaan ulang saat scraping gagal.
    """

    def __init__(
        self,
        base_url: str = BASE_URL,
        output_dir: Path = OUTPUT_DIR,
        max_retries: int = 3,
    ) -> None:
        self.base_url = base_url
        self.output_dir = output_dir
        self.cache_dir = CACHE_DIR
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
            }
        )

    def _fetch_page(self, url: str) -> str:
        """Fetch halaman HTML dengan retry dan exponential backoff.

        Args:
            url: URL halaman yang akan di-fetch.

        Returns:
            Konten HTML sebagai string.

        Raises:
            requests.HTTPError: Jika semua percobaan gagal.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Fetching {url} (attempt {attempt}/{self.max_retries})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                wait_time = 2**attempt
                logger.warning(f"Attempt {attempt} gagal: {e}. Retry dalam {wait_time}s...")
                if attempt < self.max_retries:
                    time.sleep(wait_time)
                else:
                    raise

        return ""  # Unreachable, tapi untuk type checker

    def scrape_daftar_perusahaan(self) -> pl.DataFrame:
        """Scrape daftar perusahaan asuransi dari OJK.

        Returns:
            DataFrame berisi daftar perusahaan asuransi.

        Note:
            CSS selectors di bawah adalah PLACEHOLDER. Sesuaikan dengan
            struktur aktual halaman OJK saat implementasi.
        """
        url = f"{self.base_url}/id/kanal/iknb/Pages/Asuransi.aspx"

        try:
            html = self._fetch_page(url)
            soup = BeautifulSoup(html, "lxml")

            # PLACEHOLDER: Sesuaikan selector dengan struktur website OJK
            rows = soup.select("table.data-table tbody tr")
            records = []

            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 3:
                    records.append(
                        {
                            "nama_perusahaan": cols[0].get_text(strip=True),
                            "kategori": cols[1].get_text(strip=True),
                            "status_izin": cols[2].get_text(strip=True),
                        }
                    )

            if records:
                df = pl.DataFrame(records)
                logger.info(f"Berhasil scrape {len(df)} perusahaan dari OJK")
                return df

        except Exception as e:
            logger.error(f"Gagal scrape daftar perusahaan: {e}")

        # Fallback ke cached data
        return self._load_cache("perusahaan_asuransi")

    def scrape_statistik_keuangan(self, tahun: int) -> pl.DataFrame:
        """Scrape statistik keuangan perasuransian untuk tahun tertentu.

        Args:
            tahun: Tahun pelaporan yang akan di-scrape.

        Returns:
            DataFrame berisi statistik keuangan perusahaan asuransi.
        """
        url = f"{self.base_url}/id/kanal/iknb/data-dan-statistik/asuransi/Pages/{tahun}.aspx"

        try:
            html = self._fetch_page(url)
            soup = BeautifulSoup(html, "lxml")

            # PLACEHOLDER: Sesuaikan selector dengan struktur website OJK
            rows = soup.select("table.statistik-table tbody tr")
            records = []

            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 6:
                    records.append(
                        {
                            "nama_perusahaan": cols[0].get_text(strip=True),
                            "tahun_laporan": tahun,
                            "premi_bruto": self._parse_number(cols[1].get_text(strip=True)),
                            "klaim_bruto": self._parse_number(cols[2].get_text(strip=True)),
                            "rbc_ratio": self._parse_number(cols[3].get_text(strip=True)),
                            "total_aset": self._parse_number(cols[4].get_text(strip=True)),
                            "laba_rugi_bersih": self._parse_number(cols[5].get_text(strip=True)),
                        }
                    )

            if records:
                df = pl.DataFrame(records)
                logger.info(f"Berhasil scrape statistik {tahun}: {len(df)} perusahaan")
                return df

        except Exception as e:
            logger.error(f"Gagal scrape statistik tahun {tahun}: {e}")

        return self._load_cache(f"statistik_{tahun}")

    def run(
        self, tahun_mulai: int = 2016, tahun_akhir: int = 2025
    ) -> dict[str, pl.DataFrame]:
        """Orkestrasi proses scraping lengkap.

        Args:
            tahun_mulai: Tahun awal rentang scraping.
            tahun_akhir: Tahun akhir rentang scraping.

        Returns:
            Dictionary berisi DataFrames hasil scraping.
        """
        logger.info(f"Memulai scraping OJK ({tahun_mulai}-{tahun_akhir})...")

        data: dict[str, pl.DataFrame] = {}

        # Scrape daftar perusahaan
        data["perusahaan"] = self.scrape_daftar_perusahaan()

        # Scrape statistik per tahun
        statistik_frames = []
        for tahun in range(tahun_mulai, tahun_akhir + 1):
            df = self.scrape_statistik_keuangan(tahun)
            if len(df) > 0:
                statistik_frames.append(df)
            time.sleep(1)  # Rate limiting

        if statistik_frames:
            data["statistik_keuangan"] = pl.concat(statistik_frames)

        logger.info(f"Scraping selesai. Total dataset: {len(data)}")
        return data

    def save_to_parquet(self, data: dict[str, pl.DataFrame], output_dir: Path | None = None) -> None:
        """Simpan hasil scraping ke file Parquet.

        Args:
            data: Dictionary berisi DataFrames yang akan disimpan.
            output_dir: Direktori output (default: self.output_dir).
        """
        out = output_dir or self.output_dir
        out.mkdir(parents=True, exist_ok=True)

        for name, df in data.items():
            path = out / f"ojk_{name}.parquet"
            df.write_parquet(path)
            logger.info(f"Saved {name} ({len(df)} rows) → {path}")

        # Cache data untuk fallback
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        for name, df in data.items():
            cache_path = self.cache_dir / f"{name}.parquet"
            df.write_parquet(cache_path)

    def _load_cache(self, name: str) -> pl.DataFrame:
        """Load cached data sebagai fallback saat scraping gagal."""
        cache_path = self.cache_dir / f"{name}.parquet"
        if cache_path.exists():
            logger.warning(f"Menggunakan cached data: {cache_path}")
            return pl.read_parquet(cache_path)
        logger.warning(f"Tidak ada cache untuk '{name}'. Mengembalikan DataFrame kosong.")
        return pl.DataFrame()

    @staticmethod
    def _parse_number(text: str) -> float:
        """Parse angka dari teks (menghapus pemisah ribuan Indonesia)."""
        cleaned = text.replace(".", "").replace(",", ".").replace(" ", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return 0.0


def main() -> None:
    """Entry point untuk menjalankan scraper OJK."""
    print("=" * 60)
    print("⚠️  CATATAN: Scraper ini menggunakan placeholder selectors.")
    print("   Sesuaikan CSS selectors dengan struktur website OJK aktual.")
    print("   Untuk development, gunakan synthetic_generator.py terlebih dahulu.")
    print("=" * 60)

    scraper = OJKScraper()
    data = scraper.run()
    scraper.save_to_parquet(data)

    print("\n✅ Scraping selesai. Hasil disimpan di data/raw/")


if __name__ == "__main__":
    main()
