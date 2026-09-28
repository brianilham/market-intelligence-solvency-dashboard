"""
Corporate Analytical Dashboard — PT MNC Life Assurance
Indonesian Insurance Market Intelligence & Solvency Radar.

Executive Clean Light Edition (High-Contrast Corporate Polish):
- Theme: Synchronized with .streamlit/config.toml (base="light", primaryColor="#0052CC")
- Large Prominent Logo: Sized to 115px and vertically centered with company title
- 100% Light Component Hygiene: Tables, segmented controls, and selectboxes unified in white & corporate blue
- 100% High-Contrast Text: All text converted to Deep Slate (#0f172a) and Slate (#475569)
- Brand Theming: MNC Corporate Royal Blue (#0052CC / #003399) as functional accent
- Strict Zero-Emoji Rule: Completely formal enterprise standard, zero decorative symbols
- High-Legibility Large Font Scale: Metric values 2.25rem (36px+) in deep slate, metric labels 0.95rem (15px)
- Zero-Chart-Junk Plotly: 100% transparent canvas, faint horizontal gridlines, formatted hovertooltips
- In-Memory Zero-Lag OLAP: Vectorized DuckDB read-only caching (< 50ms)
- Bugfix: Preserved Streamlit Material Icon ligatures to eliminate font/arrow text overlap
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Setup Root & Paths
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "asuransi.duckdb"
LOGO_PATH = BASE_DIR / "assets" / "mnc_life_logo.png"

# MNC Life Corporate Brand Colors (Light Executive Palette)
BRAND_PRIMARY = "#0052CC"      # MNC Corporate Royal Blue
BRAND_NAVY = "#003399"         # MNC Deep Blue
BRAND_LIGHT_BLUE = "#3385FF"   # MNC Accent Blue
COLOR_ALERT = "#e11d48"        # Regulatory Critical Warning Red (OJK RBC < 120%)
COLOR_SAFE = "#0052CC"         # Solvency Compliant Blue
TEXT_PRIMARY = "#0f172a"       # Deep Slate Charcoal (High Contrast)
TEXT_SECONDARY = "#475569"     # Muted Slate
TEXT_MUTED = "#64748b"         # Light Slate
BG_CANVAS = "#f8fafc"          # Clean Slate Paper White
BG_CARD = "#ffffff"            # Pure Crisp White

# 1. Page Configuration (Corporate Standard, Zero Emoji)
st.set_page_config(
    page_title="Market Intelligence & Solvency Dashboard - PT MNC Life Assurance",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Corporate Light CSS Theme Injection (Unified Light Styling)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Scoped Typography - Deep Slate Charcoal High-Contrast Text */
    html, body, p, label, h1, h2, h3, h4, h5, h6, .stMarkdown {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: {TEXT_PRIMARY} !important;
    }}
    code, pre {{
        font-family: 'JetBrains Mono', monospace !important;
    }}

    /* Protect Streamlit icon font ligatures from overlapping/rendering as text */
    span[data-testid="stIconMaterial"], [class*="material-symbols"], [class*="material-icons"] {{
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        font-style: normal !important;
        display: inline-block !important;
        line-height: 1 !important;
    }}

    /* Corporate Paper White Canvas */
    .stApp {{
        background-color: {BG_CANVAS} !important;
        color: {TEXT_PRIMARY} !important;
    }}

    /* Elevated Pure White Surface with Subtle Micro-Borders */
    div[data-testid="stMetric"],
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stExpander"] {{
        background-color: {BG_CARD} !important;
        border: 1px solid rgba(15, 23, 42, 0.09) !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    div[data-testid="stMetric"]:hover,
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border-color: rgba(0, 82, 204, 0.40) !important;
        box-shadow: 0 4px 14px rgba(0, 82, 204, 0.05) !important;
    }}

    /* Large Metric Scale: Deep Slate Bold Numbers with Tight Kerning */
    div[data-testid="stMetricValue"] {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        color: {TEXT_PRIMARY} !important;
        line-height: 1.2 !important;
    }}
    div[data-testid="stMetricLabel"] {{
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: {TEXT_SECONDARY} !important;
    }}

    /* Corporate Tab Navigation in MNC Blue */
    button[data-baseweb="tab"] {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        padding: 10px 20px !important;
        color: {TEXT_MUTED} !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {BRAND_PRIMARY} !important;
        font-weight: 600 !important;
        border-bottom-color: {BRAND_PRIMARY} !important;
    }}

    /* Clean Corporate Dataframes in Light Mode */
    div[data-testid="stDataFrame"] {{
        border-radius: 10px !important;
        border: 1px solid rgba(15, 23, 42, 0.09) !important;
        background-color: {BG_CARD} !important;
    }}

    /* Segmented Control Styling (White container, crisp blue selection) */
    div[data-testid="stSegmentedControl"] {{
        background-color: #ffffff !important;
        border: 1px solid rgba(15, 23, 42, 0.12) !important;
        border-radius: 8px !important;
        padding: 2px !important;
    }}
    div[data-testid="stSegmentedControl"] button {{
        color: {TEXT_SECONDARY} !important;
        font-weight: 500 !important;
        border: none !important;
    }}
    div[data-testid="stSegmentedControl"] button[aria-selected="true"],
    div[data-testid="stSegmentedControl"] button[data-checked="true"] {{
        background-color: {BRAND_PRIMARY} !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
    }}

    /* Selectbox Dropdown Menu (White Background, Slate Text, Blue Selection) */
    div[data-baseweb="select"] > div {{
        background-color: #ffffff !important;
        border: 1px solid rgba(15, 23, 42, 0.14) !important;
        color: {TEXT_PRIMARY} !important;
        border-radius: 8px !important;
    }}
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {{
        background-color: #ffffff !important;
        border: 1px solid rgba(15, 23, 42, 0.12) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
        border-radius: 8px !important;
    }}
    li[role="option"] {{
        background-color: #ffffff !important;
        color: {TEXT_PRIMARY} !important;
        font-size: 0.92rem !important;
    }}
    li[role="option"]:hover, li[aria-selected="true"] {{
        background-color: #eff6ff !important;
        color: {BRAND_PRIMARY} !important;
        font-weight: 600 !important;
    }}

    /* Expander Layout Hygiene */
    div[data-testid="stExpander"] details summary {{
        padding: 12px 16px !important;
        font-weight: 600 !important;
        color: {TEXT_PRIMARY} !important;
    }}

    /* Streamlit UI Cleanup */
    #MainMenu, footer {{visibility: hidden;}}
    header {{background-color: transparent !important;}}
</style>
""", unsafe_allow_html=True)


# 3. Cached Data Layer (Rule #21)
@st.cache_resource
def get_db_connection() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(DB_PATH), read_only=True)


@st.cache_data(show_spinner=False)
def load_available_years() -> list[int]:
    con = get_db_connection()
    df = con.execute("SELECT DISTINCT tahun_laporan FROM laporan_keuangan ORDER BY tahun_laporan DESC").fetchdf()
    return df["tahun_laporan"].tolist()


@st.cache_data(show_spinner=False)
def load_macro_kpis(year: int) -> dict:
    con = get_db_connection()
    row = con.execute("""
        SELECT
            ROUND(SUM(lk.premi_bruto), 1) as total_premi,
            ROUND(AVG(lk.rbc_ratio), 1) as avg_rbc,
            ROUND(AVG(lk.rasio_klaim) * 100, 1) as avg_klaim,
            SUM(CASE WHEN lk.rbc_ratio < 120 THEN 1 ELSE 0 END) as count_rbc_warning,
            ROUND(SUM(lk.laba_rugi_bersih), 1) as total_laba
        FROM laporan_keuangan lk
        WHERE lk.tahun_laporan = ?
    """, [year]).fetchdf().iloc[0]

    prev_row = con.execute("""
        SELECT ROUND(SUM(lk.premi_bruto), 1) as prev_premi
        FROM laporan_keuangan lk
        WHERE lk.tahun_laporan = ?
    """, [year - 1]).fetchdf()

    premi_delta = None
    if not prev_row.empty and prev_row.iloc[0]["prev_premi"]:
        prev_p = prev_row.iloc[0]["prev_premi"]
        premi_delta = f"{((row['total_premi'] - prev_p) / prev_p) * 100:+.1f}% YoY"

    return {
        "total_premi": row["total_premi"],
        "premi_delta": premi_delta,
        "avg_rbc": row["avg_rbc"],
        "avg_klaim": row["avg_klaim"],
        "count_rbc_warning": int(row["count_rbc_warning"]),
        "total_laba": row["total_laba"],
    }


@st.cache_data(show_spinner=False)
def load_market_breakdown(year: int) -> pd.DataFrame:
    con = get_db_connection()
    return con.execute("""
        SELECT
            CASE
                WHEN pa.kategori = 'jiwa' THEN 'Asuransi Jiwa'
                WHEN pa.kategori = 'umum' THEN 'Asuransi Umum'
                WHEN pa.kategori = 'reasuransi' THEN 'Reasuransi'
                WHEN pa.kategori = 'syariah_jiwa' THEN 'Syariah Jiwa'
                WHEN pa.kategori = 'syariah_umum' THEN 'Syariah Umum'
                ELSE pa.kategori
            END as Sektor,
            ROUND(SUM(lk.premi_bruto), 1) as "Total Premi (M)",
            ROUND(SUM(lk.premi_bruto) / (SELECT SUM(premi_bruto) FROM laporan_keuangan WHERE tahun_laporan = ?) * 100, 1) as Pangsa_Pasar,
            ROUND(AVG(lk.rasio_klaim) * 100, 1) as "Rasio Klaim (%)"
        FROM laporan_keuangan lk
        JOIN perusahaan_asuransi pa ON lk.kode_perusahaan = pa.kode_perusahaan
        WHERE lk.tahun_laporan = ?
        GROUP BY pa.kategori
        ORDER BY "Total Premi (M)" DESC
    """, [year, year]).fetchdf()


@st.cache_data(show_spinner=False)
def load_top_performers(year: int, limit: int = 10) -> pd.DataFrame:
    con = get_db_connection()
    return con.execute("""
        SELECT
            pa.nama_perusahaan,
            pa.kategori,
            lk.premi_bruto,
            lk.rbc_ratio
        FROM laporan_keuangan lk
        JOIN perusahaan_asuransi pa ON lk.kode_perusahaan = pa.kode_perusahaan
        WHERE lk.tahun_laporan = ?
        ORDER BY lk.premi_bruto DESC
        LIMIT ?
    """, [year, limit]).fetchdf()


@st.cache_data(show_spinner=False)
def load_solvency_watchlist(year: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    con = get_db_connection()

    bottom_5 = con.execute("""
        SELECT
            pa.nama_perusahaan,
            lk.rbc_ratio,
            CASE WHEN lk.rbc_ratio < 120 THEN 'Melanggar Regulasi (<120%)' ELSE 'Zona Aman' END as status
        FROM laporan_keuangan lk
        JOIN perusahaan_asuransi pa ON lk.kode_perusahaan = pa.kode_perusahaan
        WHERE lk.tahun_laporan = ?
        ORDER BY lk.rbc_ratio ASC
        LIMIT 5
    """, [year]).fetchdf()

    watchlist = con.execute("""
        SELECT
            pa.nama_perusahaan as "Perusahaan",
            pa.kategori as "Sektor",
            ROUND(lk.premi_bruto, 1) as "Premi (M)",
            ROUND(lk.rbc_ratio, 1) as "RBC Ratio (%)",
            ROUND(lk.rasio_klaim * 100, 1) as "Klaim (%)",
            ROUND(lk.laba_rugi_bersih, 1) as "Laba/Rugi (M)",
            CASE
                WHEN lk.rbc_ratio < 120 THEN 'Kritis: Modal < 120%'
                WHEN lk.laba_rugi_bersih < 0 AND lk.rasio_klaim > 0.65 THEN 'Defisit & Beban Klaim'
                WHEN lk.laba_rugi_bersih < 0 THEN 'Defisit Keuangan'
                ELSE 'Klaim Membengkak'
            END as "Status Regulasi"
        FROM laporan_keuangan lk
        JOIN perusahaan_asuransi pa ON lk.kode_perusahaan = pa.kode_perusahaan
        WHERE lk.tahun_laporan = ? AND (lk.rbc_ratio < 120 OR lk.laba_rugi_bersih < 0 OR lk.rasio_klaim > 0.65)
        ORDER BY lk.rbc_ratio ASC
    """, [year]).fetchdf()

    return bottom_5, watchlist


@st.cache_data(show_spinner=False)
def load_company_benchmark(kode_comp: str, year: int) -> dict:
    con = get_db_connection()
    comp = con.execute("""
        SELECT lk.*, pa.nama_perusahaan, pa.kategori, pa.tahun_berdiri, pa.status_izin
        FROM laporan_keuangan lk
        JOIN perusahaan_asuransi pa ON lk.kode_perusahaan = pa.kode_perusahaan
        WHERE lk.kode_perusahaan = ? AND lk.tahun_laporan = ?
    """, [kode_comp, year]).fetchdf()

    if comp.empty:
        return {}

    c = comp.iloc[0]
    kat = c["kategori"]

    sector_avg = con.execute("""
        SELECT
            ROUND(AVG(lk.premi_bruto), 1) as avg_premi,
            ROUND(AVG(lk.rbc_ratio), 1) as avg_rbc,
            ROUND(AVG(lk.rasio_klaim) * 100, 1) as avg_klaim,
            ROUND(AVG(lk.laba_rugi_bersih), 1) as avg_laba,
            ROUND(AVG(lk.total_aset), 1) as avg_aset,
            ROUND(SUM(lk.premi_bruto), 1) as sector_total_premi
        FROM laporan_keuangan lk
        JOIN perusahaan_asuransi pa ON lk.kode_perusahaan = pa.kode_perusahaan
        WHERE lk.tahun_laporan = ? AND pa.kategori = ?
    """, [year, kat]).fetchdf().iloc[0]

    nat_avg = con.execute("""
        SELECT
            ROUND(AVG(lk.premi_bruto), 1) as avg_premi,
            ROUND(AVG(lk.rbc_ratio), 1) as avg_rbc,
            ROUND(AVG(lk.rasio_klaim) * 100, 1) as avg_klaim,
            ROUND(AVG(lk.laba_rugi_bersih), 1) as avg_laba,
            ROUND(AVG(lk.total_aset), 1) as avg_aset,
            ROUND(SUM(lk.premi_bruto), 1) as total_premi
        FROM laporan_keuangan lk
        WHERE lk.tahun_laporan = ?
    """, [year]).fetchdf().iloc[0]

    sector_total = sector_avg["sector_total_premi"] if sector_avg["sector_total_premi"] else 1.0
    nat_total = nat_avg["total_premi"] if nat_avg["total_premi"] else 1.0
    sector_share = (c["premi_bruto"] / sector_total) * 100
    national_share = (c["premi_bruto"] / nat_total) * 100

    return {
        "company": c,
        "sector_avg": sector_avg,
        "nat_avg": nat_avg,
        "sector_share": sector_share,
        "national_share": national_share,
    }


# 4. Helper Zero-Chart-Junk Plotly Formatter for Light Mode (Rules #12, #13, #14, #16)
def format_corporate_chart(fig: go.Figure, height: int = 350) -> go.Figure:
    """Applies clean light-mode corporate transparent styling with large high-contrast axis ticks (>=12px)."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_SECONDARY, family="Plus Jakarta Sans", size=12),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(
            showgrid=False,
            showline=False,
            zeroline=False,
            tickfont=dict(color=TEXT_MUTED, size=12, family="Plus Jakarta Sans")
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(15, 23, 42, 0.07)",
            gridwidth=1,
            showline=False,
            zeroline=False,
            tickfont=dict(color=TEXT_MUTED, size=12, family="Plus Jakarta Sans")
        ),
        hoverlabel=dict(
            bgcolor="#0f172a",
            font_size=12,
            font_family="Plus Jakarta Sans",
            bordercolor="rgba(15, 23, 42, 0.1)",
            font_color="#f8fafc"
        ),
    )
    return fig


def format_rupiah_human(val: float) -> str:
    """Human-friendly currency formatting (Rule #7)."""
    if abs(val) >= 1000:
        return f"Rp {val / 1000:,.1f} T"
    return f"Rp {val:,.1f} M"


# ==============================================================================
# MAIN APPLICATION
# ==============================================================================
def main() -> None:
    if not DB_PATH.exists():
        st.error("Basis data asuransi.duckdb tidak ditemukan. Jalankan pipeline data terlebih dahulu.")
        return

    years = load_available_years()
    if not years:
        st.error("Tidak ada data laporan keuangan yang ditemukan.")
        return

    # --- TIER 1: CORPORATE HEADER WITH PROMINENT LOGO & TIME CONTROLS ---
    col_logo, col_title, control_col = st.columns([0.65, 2.35, 1.2], vertical_alignment="center")

    with col_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=115)

    with col_title:
        st.markdown(
            f"""
            <div style="display:flex; flex-direction:column; justify-content:center;">
                <h1 style="margin:0; font-size: 2.15rem; font-weight: 700; color: {TEXT_PRIMARY}; letter-spacing: -0.03em; line-height: 1.15;">
                    Market Intelligence & Solvency Dashboard
                </h1>
                <p style="margin:4px 0 0 0; font-size: 0.95rem; font-weight: 600; color: {BRAND_PRIMARY};">
                    PT MNC Life Assurance <span style="font-weight: 400; color: {TEXT_MUTED};">• Official OJK Regulatory Disclosures</span>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with control_col:
        year_str_options = [str(y) for y in sorted(years, reverse=True)]
        if hasattr(st, "segmented_control"):
            selected_year_str = st.segmented_control(
                "Tahun Pelaporan",
                options=year_str_options,
                default=year_str_options[0],
                label_visibility="collapsed"
            )
        else:
            selected_year_str = st.radio(
                "Tahun Pelaporan",
                options=year_str_options,
                horizontal=True,
                label_visibility="collapsed"
            )

    selected_year = int(selected_year_str) if selected_year_str else years[0]

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # --- TIER 2: PULSE CHECK KPI CARDS (Rules #1, #5, #6, #7, #9) ---
    kpi_data = load_macro_kpis(selected_year)
    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Total Premi Industri",
        format_rupiah_human(kpi_data["total_premi"]),
        delta=kpi_data["premi_delta"],
        border=True
    )
    k2.metric(
        "Rata-rata RBC Industri",
        f"{kpi_data['avg_rbc']:.1f}%",
        delta=f"{kpi_data['avg_rbc'] - 120:.1f}% vs Ambang OJK",
        border=True
    )
    k3.metric(
        "Rata-rata Rasio Klaim",
        f"{kpi_data['avg_klaim']:.1f}%",
        delta="Batas Sehat < 65%",
        delta_color="off",
        border=True
    )
    k4.metric(
        "Entitas Dalam Pengawasan",
        f"{kpi_data['count_rbc_warning']} Perusahaan",
        delta="Perlu Tindakan OJK" if kpi_data["count_rbc_warning"] > 0 else "Semua Patuh",
        delta_color="inverse" if kpi_data["count_rbc_warning"] > 0 else "normal",
        border=True
    )

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # --- TIER 3: TABBED PROGRESSIVE DISCLOSURE (Rule #5, #10) ---
    tab_executive, tab_solvency, tab_company = st.tabs([
        "Ringkasan Eksekutif & Pangsa Pasar",
        "Solvabilitas & Pengawasan Regulasi OJK",
        "Evaluasi Benchmark MNC Life"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: RINGKASAN EKSEKUTIF (Asymmetric 70/30 Grid, Rules #2, #8, #14, #17)
    # --------------------------------------------------------------------------
    with tab_executive:
        c_left, c_right = st.columns([2.6, 1.4])

        with c_left:
            with st.container(border=True):
                st.markdown(
                    f"<h3 style='margin:0 0 8px 0; font-size:1.15rem; font-weight:600; color:{TEXT_PRIMARY};'>"
                    "Top 10 Pemimpin Pasar Berdasarkan Premi Bruto</h3>",
                    unsafe_allow_html=True
                )
                top_df = load_top_performers(selected_year, limit=10)

                # Corporate Royal Blue Gradient (Rules #1, #2)
                fig_top = px.bar(
                    top_df,
                    x="premi_bruto",
                    y="nama_perusahaan",
                    orientation="h",
                    color="premi_bruto",
                    color_continuous_scale=[BRAND_NAVY, BRAND_PRIMARY, BRAND_LIGHT_BLUE],
                    labels={"premi_bruto": "Premi Bruto (Miliar Rp)", "nama_perusahaan": ""}
                )
                fig_top.update_coloraxes(showscale=False)
                fig_top.update_layout(yaxis=dict(autorange="reversed"))
                fig_top.update_traces(
                    hovertemplate="<b>%{y}</b><br>Premi: Rp %{x:,.1f} M<extra></extra>"
                )
                st.plotly_chart(format_corporate_chart(fig_top, height=360), use_container_width=True)

        with c_right:
            with st.container(border=True):
                st.markdown(
                    f"<h3 style='margin:0 0 8px 0; font-size:1.15rem; font-weight:600; color:{TEXT_PRIMARY};'>"
                    "Distribusi Pangsa Pasar per Sektor</h3>",
                    unsafe_allow_html=True
                )
                breakdown_df = load_market_breakdown(selected_year)

                # Modern Dataframe with ProgressColumn replacing Pie Chart (Rules #14, #17, #18)
                st.dataframe(
                    breakdown_df,
                    column_config={
                        "Sektor": st.column_config.TextColumn("Sektor Asuransi"),
                        "Total Premi (M)": st.column_config.NumberColumn("Total Premi", format="Rp %d M"),
                        "Pangsa_Pasar": st.column_config.ProgressColumn(
                            "Pangsa Pasar",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100
                        ),
                        "Rasio Klaim (%)": None
                    },
                    hide_index=True,
                    use_container_width=True
                )

        # Formal Corporate Context Insight Box - Clean White Card with Blue Accent Line
        top_2_share = breakdown_df.iloc[:2]["Pangsa_Pasar"].sum() if len(breakdown_df) >= 2 else 0.0
        s1 = breakdown_df.iloc[0]["Sektor"] if len(breakdown_df) >= 1 else "Asuransi Jiwa"
        s2 = breakdown_df.iloc[1]["Sektor"] if len(breakdown_df) >= 2 else "Asuransi Umum"

        st.markdown(
            f"""
            <div style="background-color:#ffffff; border:1px solid rgba(15,23,42,0.09); border-left:4px solid {BRAND_PRIMARY}; padding:14px 18px; border-radius:8px; margin-top:10px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                <span style="font-size:0.92rem; color:{TEXT_SECONDARY}; line-height:1.6;">
                    <b style="color:{BRAND_PRIMARY};">Catatan Analisis Pasar ({selected_year})</b>: Agregasi perolehan premi industri mencapai
                    <b style="color:{TEXT_PRIMARY};">{format_rupiah_human(kpi_data['total_premi'])}</b> dengan rasio permodalan solvabilitas rata-rata
                    <b style="color:{TEXT_PRIMARY};">{kpi_data['avg_rbc']:.1f}%</b>. Sektor <b>{s1}</b> dan <b>{s2}</b> menyerap
                    <b style="color:{TEXT_PRIMARY};">{top_2_share:.1f}%</b> likuiditas premi nasional. Sebanyak
                    <b style="color:{COLOR_ALERT if kpi_data['count_rbc_warning'] > 0 else BRAND_PRIMARY};">{kpi_data['count_rbc_warning']} entitas</b> tercatat berada dalam pengawasan khusus solvabilitas regulator OJK.
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------------------------
    # TAB 2: SOLVABILITAS & PENGAWASAN REGULASI OJK (Rules #12, #13, #17)
    # --------------------------------------------------------------------------
    with tab_solvency:
        bottom_5_df, watchlist_df = load_solvency_watchlist(selected_year)

        with st.container(border=True):
            st.markdown(
                f"<h3 style='margin:0 0 4px 0; font-size:1.15rem; font-weight:600; color:{TEXT_PRIMARY};'>"
                "Entitas dengan Solvabilitas Terendah terhadap Ambang Regulasi OJK</h3>"
                f"<p style='margin:0 0 8px 0; font-size:0.86rem; color:{TEXT_MUTED};'>"
                "Garis batas merah putus-putus menandakan ambang batas minimum solvabilitas modal POJK (120%).</p>",
                unsafe_allow_html=True
            )

            fig_risk = px.bar(
                bottom_5_df,
                x="rbc_ratio",
                y="nama_perusahaan",
                orientation="h",
                color="status",
                color_discrete_map={
                    "Melanggar Regulasi (<120%)": COLOR_ALERT,
                    "Zona Aman": BRAND_PRIMARY
                },
                labels={"rbc_ratio": "RBC Ratio (%)", "nama_perusahaan": ""}
            )
            fig_risk.add_vline(
                x=120,
                line_width=2,
                line_dash="dash",
                line_color=COLOR_ALERT,
                annotation_text="Ambang OJK 120%",
                annotation_position="top right",
                annotation_font=dict(color=COLOR_ALERT, size=11, family="Plus Jakarta Sans")
            )
            fig_risk.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
            fig_risk.update_traces(hovertemplate="<b>%{y}</b><br>RBC: %{x:.1f}%<extra></extra>")
            st.plotly_chart(format_corporate_chart(fig_risk, height=250), use_container_width=True)

        with st.container(border=True):
            st.markdown(
                f"<h3 style='margin:0 0 6px 0; font-size:1.15rem; font-weight:600; color:{TEXT_PRIMARY};'>"
                "Daftar Entitas dalam Pengawasan Regulasi Khusus</h3>",
                unsafe_allow_html=True
            )
            if not watchlist_df.empty:
                st.dataframe(
                    watchlist_df,
                    column_config={
                        "Perusahaan": st.column_config.TextColumn("Nama Perusahaan"),
                        "Sektor": st.column_config.TextColumn("Sektor"),
                        "Premi (M)": st.column_config.NumberColumn("Premi (Rp M)", format="Rp %d"),
                        "RBC Ratio (%)": st.column_config.NumberColumn("RBC Ratio", format="%.1f%%"),
                        "Klaim (%)": st.column_config.ProgressColumn("Beban Klaim", format="%.1f%%", min_value=0, max_value=100),
                        "Laba/Rugi (M)": st.column_config.NumberColumn("Laba Bersih", format="Rp %d M"),
                        "Status Regulasi": st.column_config.TextColumn("Kondisi Perhatian")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info(f"Kondisi prima: Tidak ada perusahaan yang masuk kriteria pengawasan khusus pada tahun {selected_year}.")

    # --------------------------------------------------------------------------
    # TAB 3: EVALUASI BENCHMARK MNC LIFE (Default Spotlight on MNC Life)
    # --------------------------------------------------------------------------
    with tab_company:
        con = get_db_connection()
        company_records = con.execute("""
            SELECT kode_perusahaan, nama_perusahaan, kategori, status_izin
            FROM perusahaan_asuransi
            ORDER BY nama_perusahaan
        """).fetchdf()

        company_dict = {f"{r['nama_perusahaan']} ({r['kategori'].upper()})": r["kode_perusahaan"] for _, r in company_records.iterrows()}
        company_labels = list(company_dict.keys())

        default_index = 0
        for idx, lbl in enumerate(company_labels):
            if "MNC Life" in lbl:
                default_index = idx
                break

        col_select, _ = st.columns([2.5, 1.5])
        with col_select:
            selected_company_label = st.selectbox(
                "Pilih Entitas Perusahaan:",
                company_labels,
                index=default_index,
                label_visibility="collapsed"
            )

        if selected_company_label:
            kode_comp = company_dict[selected_company_label]
            bench_data = load_company_benchmark(kode_comp, selected_year)

            if bench_data:
                c_row = bench_data["company"]
                s_avg = bench_data["sector_avg"]
                n_avg = bench_data["nat_avg"]
                sec_share = bench_data["sector_share"]
                nat_share = bench_data["national_share"]

                is_compliant = c_row["rbc_ratio"] >= 120 and c_row["laba_rugi_bersih"] >= 0

                badge_bg = "#eff6ff" if is_compliant else "#fff1f2"
                badge_border = BRAND_PRIMARY if is_compliant else COLOR_ALERT
                badge_text_color = BRAND_PRIMARY if is_compliant else COLOR_ALERT
                status_title = "Status Solvabilitas: Sehat & Memenuhi Ketentuan OJK" if is_compliant else "Status Solvabilitas: Dalam Pemantauan Khusus Regulator"

                st.markdown(
                    f"""
                    <div style="background-color:{badge_bg}; border:1px solid {badge_border}; border-radius:10px; padding:14px 18px; margin-bottom:14px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                        <span style="font-weight:700; color:{badge_text_color}; font-size:1.05rem;">{status_title}</span>
                        <div style="font-size:0.88rem; color:{TEXT_SECONDARY}; margin-top:4px;">
                            Entitas: <b style="color:{TEXT_PRIMARY};">{c_row['nama_perusahaan']}</b> • Sektor: <b>{c_row['kategori'].replace('_', ' ').title()}</b> • Tahun Pendirian: <b>{c_row['tahun_berdiri']}</b> • Status Izin Operasional: <b>{c_row['status_izin'].title()}</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Company Pulse KPI Metrics with contextual comparative deltas
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(
                    "Pendapatan Premi",
                    format_rupiah_human(c_row["premi_bruto"]),
                    delta=f"{nat_share:.1f}% Pangsa Nasional",
                    delta_color="normal",
                    border=True
                )
                c2.metric(
                    "RBC Solvabilitas",
                    f"{c_row['rbc_ratio']:.1f}%",
                    delta=f"{c_row['rbc_ratio'] - 120:+.1f}% vs Batas POJK",
                    delta_color="normal" if c_row["rbc_ratio"] >= 120 else "inverse",
                    border=True
                )
                c3.metric(
                    "Rasio Beban Klaim",
                    f"{c_row['rasio_klaim'] * 100:.1f}%",
                    delta=f"{(c_row['rasio_klaim'] * 100) - n_avg['avg_klaim']:+.1f}% vs Industri",
                    delta_color="inverse" if (c_row['rasio_klaim'] * 100) > 65 else "normal",
                    border=True
                )
                c4.metric(
                    "Laba/Rugi Bersih",
                    format_rupiah_human(c_row["laba_rugi_bersih"]),
                    delta=f"{c_row['laba_rugi_bersih'] - n_avg['avg_laba']:+.1f} M vs Rata-rata",
                    delta_color="normal" if c_row["laba_rugi_bersih"] >= 0 else "inverse",
                    border=True
                )

                # Asymmetric Split: Historical Trend & Benchmarking Matrix
                c_chart, c_table = st.columns([1.5, 1.5])

                with c_chart:
                    with st.container(border=True):
                        st.markdown(
                            f"<h3 style='margin:0 0 6px 0; font-size:1.15rem; font-weight:600; color:{TEXT_PRIMARY};'>"
                            f"Tren Historis Kinerja Finansial ({c_row['nama_perusahaan']})</h3>",
                            unsafe_allow_html=True
                        )
                        history_df = con.execute("""
                            SELECT tahun_laporan, premi_bruto, laba_rugi_bersih, rbc_ratio
                            FROM laporan_keuangan
                            WHERE kode_perusahaan = ?
                            ORDER BY tahun_laporan ASC
                        """, [kode_comp]).fetchdf()

                        fig_hist = go.Figure()
                        fig_hist.add_trace(go.Scatter(
                            x=history_df["tahun_laporan"],
                            y=history_df["premi_bruto"],
                            name="Premi Bruto (M)",
                            line=dict(color=BRAND_PRIMARY, width=3),
                            fill="tozeroy",
                            fillcolor="rgba(0, 82, 204, 0.07)"
                        ))
                        fig_hist.add_trace(go.Bar(
                            x=history_df["tahun_laporan"],
                            y=history_df["laba_rugi_bersih"],
                            name="Laba Bersih (M)",
                            marker_color=[BRAND_LIGHT_BLUE if v >= 0 else COLOR_ALERT for v in history_df["laba_rugi_bersih"]],
                            opacity=0.85
                        ))
                        fig_hist.update_layout(
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        st.plotly_chart(format_corporate_chart(fig_hist, height=330), use_container_width=True)

                with c_table:
                    with st.container(border=True):
                        st.markdown(
                            f"<h3 style='margin:0 0 6px 0; font-size:1.15rem; font-weight:600; color:{TEXT_PRIMARY};'>"
                            f"Matriks Benchmarking Komparatif ({selected_year})</h3>",
                            unsafe_allow_html=True
                        )
                        sektor_name = c_row['kategori'].replace('_', ' ').title()
                        benchmark_matrix = pd.DataFrame([
                            {
                                "Metrik Finansial": "Premi Bruto",
                                "Entitas Terpilih": format_rupiah_human(c_row["premi_bruto"]),
                                f"Rata-rata Sektor ({sektor_name})": format_rupiah_human(s_avg["avg_premi"]),
                                "Rata-rata Nasional": format_rupiah_human(n_avg["avg_premi"]),
                                "Posisi Evaluasi": "Di Atas Industri" if c_row["premi_bruto"] >= n_avg["avg_premi"] else "Di Bawah Industri"
                            },
                            {
                                "Metrik Finansial": "Solvabilitas (RBC)",
                                "Entitas Terpilih": f"{c_row['rbc_ratio']:.1f}%",
                                f"Rata-rata Sektor ({sektor_name})": f"{s_avg['avg_rbc']:.1f}%",
                                "Rata-rata Nasional": f"{n_avg['avg_rbc']:.1f}%",
                                "Posisi Evaluasi": "Memenuhi POJK (>=120%)" if c_row["rbc_ratio"] >= 120 else "Di Bawah Ambang (<120%)"
                            },
                            {
                                "Metrik Finansial": "Rasio Beban Klaim",
                                "Entitas Terpilih": f"{c_row['rasio_klaim'] * 100:.1f}%",
                                f"Rata-rata Sektor ({sektor_name})": f"{s_avg['avg_klaim']:.1f}%",
                                "Rata-rata Nasional": f"{n_avg['avg_klaim']:.1f}%",
                                "Posisi Evaluasi": "Zona Sehat (<=65%)" if c_row["rasio_klaim"] <= 0.65 else "Beban Klaim Tinggi"
                            },
                            {
                                "Metrik Finansial": "Laba/Rugi Bersih",
                                "Entitas Terpilih": format_rupiah_human(c_row["laba_rugi_bersih"]),
                                f"Rata-rata Sektor ({sektor_name})": format_rupiah_human(s_avg["avg_laba"]),
                                "Rata-rata Nasional": format_rupiah_human(n_avg["avg_laba"]),
                                "Posisi Evaluasi": "Profitabel" if c_row["laba_rugi_bersih"] >= 0 else "Defisit Operasional"
                            },
                            {
                                "Metrik Finansial": "Total Aset",
                                "Entitas Terpilih": format_rupiah_human(c_row["total_aset"]),
                                f"Rata-rata Sektor ({sektor_name})": format_rupiah_human(s_avg["avg_aset"]),
                                "Rata-rata Nasional": format_rupiah_human(n_avg["avg_aset"]),
                                "Posisi Evaluasi": "Skala Besar" if c_row["total_aset"] >= n_avg["avg_aset"] else "Skala Menengah"
                            },
                            {
                                "Metrik Finansial": "Pangsa Sektor",
                                "Entitas Terpilih": f"{sec_share:.1f}%",
                                f"Rata-rata Sektor ({sektor_name})": "100.0% (Total)",
                                "Rata-rata Nasional": f"{nat_share:.1f}% (Nasional)",
                                "Posisi Evaluasi": f"Pangsa {sektor_name}"
                            },
                        ])

                        st.dataframe(
                            benchmark_matrix,
                            hide_index=True,
                            use_container_width=True
                        )

    # --- TIER 4: FORMAL GOVERNANCE EXPANDER (Rule #11) ---
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    with st.expander("Data Governance & Calculation Methodology", expanded=False):
        st.markdown("""
        - **Risk-Based Capital (RBC)**: Rasio solvabilitas yang mengukur ketahanan modal perusahaan asuransi terhadap total risiko keuangan dan operasional. Berdasarkan **POJK No. 71/POJK.05/2016**, batas minimum solvabilitas tingkat pertama adalah **120.0%**.
        - **Rasio Beban Klaim (Loss Ratio)**: Persentase perbandingan beban klaim bruto terhadap penerimaan premi bruto. Ambang batas operasional sehat industri dipertahankan pada batas maksimal **65.0%**.
        - **Data Lineage**: Diolah dari publikasi terbuka Statistik Perasuransian OJK menggunakan engine analitik in-memory kolumnar **DuckDB** dengan validasi deklaratif **Pandera**.
        """)


if __name__ == "__main__":
    main()
