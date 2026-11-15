"""
AgroClima Costa Rica — NASA Space Apps Challenge 2026
Production-ready UI with Black font for Light Mode & White font for Dark Mode,
English/Spanish bilingual toggle, and Crop Rotation Decision Engine aligned with GEMINI.md.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List

from src.config import (
    APP_TITLE, APP_SUBTITLE, APP_ICON,
    CR_LAT_MIN, CR_LAT_MAX, CR_LON_MIN, CR_LON_MAX,
)
from src.data.costa_rica_locations import find_closest_location
from src.data.crops_catalog import CROPS_LIST
from src.services.data_lake import get_unified_environmental_profile
from src.models.sensitivity_viability_model import SensitivityViabilityModel
from src.services.rotation_service import (
    RotationAnalysisService,
    MULTI_STRATEGY_CATALOG,
    ROTATION_PARTNERS,
)
from src.components.sidebar import (
    render_sidebar,
    PAGE_ANALYZE,
    PAGE_CROPS,
    PAGE_ROTATION,
    PAGE_SCIENCE,
)
from src.components.map_view import render_costa_rica_map
from src.components.metrics_display import render_climate_metrics
from src.components.tooltips import get_tooltip_css, render_term, render_glossary_panel
from src.components.charts import (
    create_climadiagram,
    create_moisture_comparison_chart,
    create_temperature_breakdown_chart,
    create_viability_gauge,
    create_viability_bar_chart,
    create_delta_comparison_chart,
    create_rotation_radar_chart,
    create_multi_rotation_radar_chart,
    create_vulnerability_timeline_chart,
    create_climate_scenario_chart,
    create_rotation_gauge,
)
from src.i18n import t, lang


# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_app_css(dark_mode: bool = False) -> str:
    """Generates dynamic CSS enforcing black font for Light mode and white font for Dark mode."""
    if dark_mode:
        bg_app = "#0E1318"
        bg_card = "#182028"
        bg_subcard = "#141A22"
        border_card = "#2B3542"
        text_color = "#FFFFFF"
        notice_bg = "#12251A"
        notice_border = "#2E7D32"
        section_border = "#2E7D32"
        delta_pill_bg = "#222C38"
        delta_pill_border = "#364354"
        table_border = "#2B3542"
        table_even = "#131921"
    else:
        bg_app = "#FFFFFF"
        bg_card = "#FFFFFF"
        bg_subcard = "#FAFAFA"
        border_card = "#D1D5DB"
        text_color = "#000000"
        notice_bg = "#F1F8E9"
        notice_border = "#43A047"
        section_border = "#A5D6A7"
        delta_pill_bg = "#F3F4F6"
        delta_pill_border = "#D1D5DB"
        table_border = "#E5E7EB"
        table_even = "#F9FAFB"

    return f"""
    <style>
    /* ── Root & Typography ── */
    html, body, [class*="css"] {{
        font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}

    /* Global Dark/Light mode overrides */
    [data-testid="stAppViewContainer"] {{
        background-color: {bg_app} !important;
        color: {text_color} !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: {"#141920" if dark_mode else "#F9FAFB"} !important;
        border-right: 1px solid {border_card} !important;
        color: {text_color} !important;
    }}
    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}

    /* Strict font color: Pure Black for Light Mode, Pure White for Dark Mode */
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] span:not(.crop-status-badge):not(.mission-pill),
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] h1:not(.header-title),
    [data-testid="stAppViewContainer"] h2,
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] h4,
    [data-testid="stAppViewContainer"] h5,
    [data-testid="stAppViewContainer"] h6,
    [data-testid="stAppViewContainer"] th,
    [data-testid="stAppViewContainer"] td,
    [data-testid="stAppViewContainer"] caption,
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"],
    [data-testid="stCaptionContainer"] p,
    .stMarkdown p,
    .stMarkdown span,
    .crop-card-name,
    .crop-card-name-es,
    .delta-row,
    .delta-pill,
    .sat-label,
    .sat-value {{
        color: {text_color} !important;
    }}

    /* ── App header banner ── */
    .agro-header {{
        background: linear-gradient(135deg, #0A2611 0%, #1B5E20 55%, #33691E 100%);
        color: white;
        padding: 18px 24px 14px 24px;
        border-radius: 10px;
        margin-bottom: 18px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.18);
    }}
    .agro-header h1 {{
        margin: 0 0 2px 0;
        font-size: 22px;
        font-weight: 800;
        color: white !important;
        letter-spacing: -0.3px;
    }}
    .agro-header .subtitle {{
        font-size: 12px;
        opacity: 0.92;
        color: #C8E6C9 !important;
        margin: 0;
    }}
    .mission-pill {{
        display: inline-block;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.25);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 700;
        color: #FFFFFF !important;
        margin: 2px 2px 0 0;
        letter-spacing: 0.3px;
    }}

    /* ── Section headers ── */
    .section-title {{
        font-size: 15px;
        font-weight: 800;
        color: {text_color} !important;
        margin: 16px 0 10px 0;
        padding-bottom: 5px;
        border-bottom: 2px solid {section_border};
        letter-spacing: -0.2px;
    }}

    /* ── Info notice box ── */
    .info-notice {{
        background: {notice_bg};
        border-left: 4px solid {notice_border};
        padding: 10px 14px;
        border-radius: 5px;
        font-size: 12.5px;
        color: {text_color} !important;
        margin-bottom: 14px;
        line-height: 1.5;
    }}

    /* ── Crop viability card ── */
    .crop-card {{
        background: {bg_card};
        border: 1px solid {border_card};
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .crop-card:hover {{
        transform: translateY(-1px);
        box-shadow: 0 5px 14px rgba(0,0,0,0.14);
    }}
    .crop-card-name {{
        font-size: 15px;
        font-weight: 800;
        color: {text_color} !important;
    }}
    .crop-card-name-es {{
        font-size: 12px;
        color: {text_color} !important;
        margin-left: 4px;
    }}
    .crop-score {{
        font-size: 30px;
        font-weight: 900;
        line-height: 1;
    }}
    .crop-status-badge {{
        display: inline-block;
        padding: 2px 9px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        color: white !important;
        margin-top: 4px;
    }}
    .progress-bg {{
        background: {"#263342" if dark_mode else "#E5E7EB"};
        border-radius: 4px;
        height: 7px;
        width: 100%;
        margin: 8px 0 6px 0;
    }}
    .delta-row {{
        font-size: 11px;
        color: {text_color} !important;
        display: flex;
        justify-content: space-between;
        gap: 4px;
        flex-wrap: wrap;
    }}
    .delta-pill {{
        background: {delta_pill_bg};
        border: 1px solid {delta_pill_border};
        border-radius: 3px;
        padding: 1px 5px;
        font-size: 10px;
        font-weight: 700;
        color: {text_color} !important;
    }}

    /* ── Parameter info card ── */
    .param-card {{
        background: {bg_subcard};
        border: 1px solid {border_card};
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
        color: {text_color} !important;
    }}
    .param-card h4 {{
        margin: 0 0 10px 0;
        font-size: 13px;
        font-weight: 800;
        color: {text_color} !important;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }}

    /* ── Rotation schedule card ── */
    .rotation-card {{
        background: {bg_card};
        border: 1px solid {border_card};
        border-radius: 9px;
        padding: 15px;
        margin-bottom: 12px;
        color: {text_color} !important;
    }}
    .rotation-card-highlight {{
        background: {notice_bg};
        border: 1.5px solid {notice_border};
        border-radius: 9px;
        padding: 16px;
        margin-bottom: 14px;
        color: {text_color} !important;
    }}

    /* ── Climate scenario card ── */
    .climate-card {{
        background: {bg_card};
        border: 1px solid {border_card};
        border-radius: 8px;
        padding: 16px;
        height: 100%;
        color: {text_color} !important;
    }}

    /* ── Satellite data row ── */
    .sat-row {{
        display: flex;
        align-items: center;
        padding: 7px 0;
        border-bottom: 1px solid {border_card};
        font-size: 13px;
        color: {text_color} !important;
    }}
    .sat-row:last-child {{ border-bottom: none; }}
    .sat-label {{
        flex: 1;
        color: {text_color} !important;
        font-weight: 600;
    }}
    .sat-value {{
        font-weight: 800;
        color: {text_color} !important;
        font-family: "JetBrains Mono", "Consolas", monospace;
        font-size: 13px;
    }}

    /* ── Erosion risk box ── */
    .erosion-box {{
        background: {bg_subcard};
        border-radius: 8px;
        padding: 16px;
        border-left-width: 6px;
        border-left-style: solid;
        color: {text_color} !important;
    }}

    /* ── Mission table ── */
    .mission-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    .mission-table th {{
        background: #1B5E20;
        color: white !important;
        padding: 8px 12px;
        text-align: left;
        font-weight: 800;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .mission-table td {{
        padding: 8px 12px;
        border-bottom: 1px solid {table_border};
        vertical-align: top;
        color: {text_color} !important;
    }}
    .mission-table tr:nth-child(even) td {{ background: {table_even}; }}

    /* Hide streamlit default elements */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    </style>
    """


# ─── Helpers ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_env_profile(lat: float, lon: float) -> Dict[str, Any]:
    return get_unified_environmental_profile(lat, lon)


def score_color(pct: int, dark_mode: bool = False) -> str:
    if pct >= 80: return "#2E7D32" if not dark_mode else "#4CAF50"
    if pct >= 60: return "#1565C0" if not dark_mode else "#42A5F5"
    if pct >= 40: return "#E65100" if not dark_mode else "#FFA726"
    return "#B71C1C" if not dark_mode else "#EF5350"


def render_crop_card(res: Dict[str, Any], dark_mode: bool = False):
    """Renders a single crop viability card with font color enforcing black for light, white for dark."""
    pct  = res["success_percentage"]
    col  = score_color(pct, dark_mode)
    name = res["crop"]
    name_es = res.get("common_name", name)
    icon = res["icon"]
    status = res["status"].split("(")[0].strip()
    s_score = res["sensitivity"]["composite_sensitivity"]
    deltas = res["deltas"]
    txt_col = "#FFFFFF" if dark_mode else "#000000"
    bg_card = "#182028" if dark_mode else "#FFFFFF"
    border_card = "#2B3542" if dark_mode else "#D1D5DB"
    notice_bg = "#12251A" if dark_mode else "#F1F8E9"
    notice_border = "#2E7D32" if dark_mode else "#43A047"

    st.markdown(f"""
    <div class="crop-card" style="border-left: 5px solid {col};">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <span class="crop-card-name" style="color:{txt_col};">{icon} {name}</span>
                <span class="crop-card-name-es" style="color:{txt_col};">({name_es})</span><br>
                <span class="crop-status-badge" style="background:{col};">{status}</span>
            </div>
            <div style="text-align:right;">
                <span class="crop-score" style="color:{col};">{pct}%</span><br>
                <span style="font-size:10px; color:{txt_col}; font-weight:700;">S = {s_score}</span>
            </div>
        </div>
        <div class="progress-bg">
            <div style="background:{col}; height:7px; border-radius:4px; width:{pct}%;"></div>
        </div>
        <div class="delta-row" style="color:{txt_col};">
            <span class="delta-pill" style="color:{txt_col};">Δ Temp {deltas['temperature_delta_c']:+.1f}°C</span>
            <span class="delta-pill" style="color:{txt_col};">Δ Lluvia {deltas['precipitation_delta_mm']:+.0f} mm</span>
            <span class="delta-pill" style="color:{txt_col};">Δ Alt {deltas['altitude_delta_m']:+.0f} m</span>
            <span class="delta-pill" style="color:{txt_col};">Δ Hum {deltas['soil_moisture_delta']:+.3f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Main Application ─────────────────────────────────────────────────────────
def main():
    # Sidebar
    active_page, lat, lon, loc_name, show_zones, dark_mode, current_lang = render_sidebar()

    # Apply Tooltips CSS & Global Theme CSS (Dark / Light)
    st.markdown(get_tooltip_css(dark_mode), unsafe_allow_html=True)
    st.markdown(get_app_css(dark_mode), unsafe_allow_html=True)

    txt_col = "#FFFFFF" if dark_mode else "#000000"
    bg_card = "#182028" if dark_mode else "#FFFFFF"
    border_card = "#2B3542" if dark_mode else "#D1D5DB"
    notice_bg = "#12251A" if dark_mode else "#F1F8E9"
    notice_border = "#2E7D32" if dark_mode else "#43A047"

    with st.spinner("Consultando satélites (SMAP · GPM · ECOSTRESS · SRTM) y bases IMN…" if current_lang == "es" else "Querying satellites (SMAP · GPM · ECOSTRESS · SRTM) & IMN databases…"):
        env = load_env_profile(lat, lon)

    # Environmental parameters
    actual_t   = env["temperatures"]["air_temperature_mean_c"]
    actual_p   = env["precipitation"]["gpm_annual_total_mm"]
    actual_alt = env["topography_and_erosion"]["elevation_msnm"]
    actual_sm  = env["humidity_and_moisture"]["smap_root_zone_moisture_m3_m3"]
    actual_soil= env["soil"]["order"]
    actual_slope = float(env["topography_and_erosion"].get("slope_percent", 8.0))

    # Viability results for all 5 crops
    all_results: List[Dict[str, Any]] = SensitivityViabilityModel.calculate_all_crops(
        actual_temp_c=actual_t,
        actual_precip_mm=actual_p,
        actual_altitude_m=actual_alt,
        actual_soil_moisture_m3_m3=actual_sm,
        actual_soil_type=actual_soil,
    )

    # ── App Header ──────────────────────────────────────────────────────────
    tooltip_fusion = render_term("Satellite vs. Ground Data", "Fusión Satelital + Tierra (IMN)" if current_lang == "es" else "Satellite + Ground Fusion (IMN)")
    st.markdown(f"""
    <div class="agro-header">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <h1>🌱 {t('app_title')}</h1>
                <p class="subtitle">{t('app_subtitle')}</p>
            </div>
            <div>
                <span class="mission-pill">🛰️ SMAP L2/L4</span>
                <span class="mission-pill">🛰️ GPM DPR</span>
                <span class="mission-pill">🛰️ ECOSTRESS</span>
                <span class="mission-pill">🛰️ SRTM 30m</span>
                <span class="mission-pill">🇨🇷 IMN Suelos</span>
            </div>
        </div>
    </div>
    <div class="info-notice">
        📡 <b>{tooltip_fusion}:</b>
        {t('data_fusion_notice')}
        <i>{t('tooltip_hint')}</i>
    </div>
    """, unsafe_allow_html=True)

    # ===========================================================================
    #  PAGE 1 — Analizar Ubicación / Analyze Location
    # ===========================================================================
    if active_page == PAGE_ANALYZE:
        col_map, col_cards = st.columns([1.35, 1.0], gap="medium")

        # ── LEFT: Interactive Map ──────────────────────────────────────────
        with col_map:
            st.markdown(f"<div class='section-title'>{t('map_title')}</div>", unsafe_allow_html=True)
            st.caption(t("map_caption"))

            clicked = render_costa_rica_map(
                selected_lat=lat,
                selected_lon=lon,
                location_name=loc_name,
                elevation_m=actual_alt,
                show_reference_zones=show_zones,
                map_height=490,
            )
            if clicked:
                c_lat, c_lon = clicked
                if abs(c_lat - lat) > 0.005 or abs(c_lon - lon) > 0.005:
                    if CR_LAT_MIN <= c_lat <= CR_LAT_MAX and CR_LON_MIN <= c_lon <= CR_LON_MAX:
                        nearest = find_closest_location(c_lat, c_lon)
                        st.session_state["selected_lat"] = c_lat
                        st.session_state["selected_lon"] = c_lon
                        st.session_state["location_name"] = f"({c_lat:.3f}, {c_lon:.3f}) · {nearest['canton']}"
                        st.rerun()

        # ── RIGHT: Crop Viability Cards ────────────────────────────────────
        with col_cards:
            st.markdown(
                f"<div class='section-title'>{t('cards_title')}</div>"
                f"<p style='font-size:12px; color:{txt_col}; margin-top:-6px; margin-bottom:10px; font-weight:600;'>"
                f"<b>{loc_name}</b> &middot; {actual_alt} msnm &middot; {t('soil_label')}: {actual_soil}"
                f"</p>",
                unsafe_allow_html=True,
            )
            for res in all_results:
                render_crop_card(res, dark_mode)

        # ── Full-width: Environmental Parameters ──────────────────────────
        st.markdown("---")
        term_wb  = render_term("Water-Balance Indicators", "Balance Hídrico" if current_lang == "es" else "Water Balance")
        term_sma = render_term("Soil Moisture Anomalies", "Anomalías de Humedad del Suelo" if current_lang == "es" else "Soil Moisture Anomalies")
        st.markdown(
            f"<div class='section-title'>{t('params_title')} — {term_wb} & {term_sma}</div>",
            unsafe_allow_html=True,
        )
        render_climate_metrics(env)

        # ── Climadiagram ──────────────────────────────────────────────────
        st.markdown("---")
        st.plotly_chart(
            create_climadiagram(env["raw_services"]["nasa_power"], dark_mode=dark_mode, lang=current_lang),
            use_container_width=True
        )

        # ── Quick comparison bar ──────────────────────────────────────────
        st.plotly_chart(
            create_viability_bar_chart(all_results, dark_mode=dark_mode, lang=current_lang),
            use_container_width=True
        )

    # ===========================================================================
    #  PAGE 2 — Fichas de Cultivo & Sensibilidad / Crop Profiles
    # ===========================================================================
    elif active_page == PAGE_CROPS:
        title_crops = "🌾 Fichas de Cultivo & Algoritmo de Sensibilidad (GEMINI.md)" if current_lang == "es" else "🌾 Crop Profiles & Sensitivity Algorithm (GEMINI.md)"
        st.markdown(f"<div class='section-title'>{title_crops}</div>", unsafe_allow_html=True)

        # Algorithm explanation panel
        with st.expander(t("how_it_works"), expanded=False):
            if current_lang == "es":
                st.markdown("""
**El modelo de viabilidad implementa directamente el Project Blueprint (GEMINI.md):**

| Paso | Descripción | Fórmula |
|------|-------------|---------|
| **1. Ficha del Cultivo** | Parámetros ideales: rango `[min, max]` y `sweet_spot` óptimo | — |
| **2. Sensitivity Score** | Rango estrecho → Alta Sensibilidad | $S_{temp} = \\dfrac{k}{T_{max} - T_{min}}$ |
| **3. Delta** | Desviación del dato real respecto al sweet spot | $\\Delta = | \\text{Actual} - \\text{Sweet Spot} |$ |
| **4. Éxito** | Base 100 menos penalidad amplificada por sensibilidad | $\\text{Éxito} = 100 - \\sum (\\Delta_i \\times S_i \\times w_i)$ |

**Pesos del modelo compuesto:** Temperatura 35% · Precipitación 30% · Humedad del Suelo 20% · Altitud 15%
                """)
            else:
                st.markdown("""
**The viability model directly implements the Project Blueprint (GEMINI.md):**

| Step | Description | Formula |
|------|-------------|---------|
| **1. Crop Profile** | Ideal parameters: range `[min, max]` and optimal `sweet_spot` | — |
| **2. Sensitivity Score** | Narrow range → High Sensitivity | $S_{temp} = \\dfrac{k}{T_{max} - T_{min}}$ |
| **3. Delta** | Deviation of actual observation from sweet spot | $\\Delta = | \\text{Actual} - \\text{Sweet Spot} |$ |
| **4. Success Score** | 100 baseline minus penalty amplified by sensitivity | $\\text{Success} = 100 - \\sum (\\Delta_i \\times S_i \\times w_i)$ |

**Composite Model Weights:** Temperature 35% · Precipitation 30% · Soil Moisture 20% · Altitude 15%
                """)

        # Crop selector
        crop_names = [f"{c['icon']} {c['crop']} / {c.get('common_name_es', c['crop'])}" for c in CROPS_LIST]
        idx = st.selectbox(
            t("select_crop"),
            range(len(CROPS_LIST)),
            format_func=lambda i: crop_names[i],
            label_visibility="visible"
        )

        crop_data = CROPS_LIST[idx]
        crop_res  = all_results[idx]
        pct       = crop_res["success_percentage"]
        col_hex   = score_color(pct, dark_mode)
        sens      = crop_res["sensitivity"]
        deltas    = crop_res["deltas"]
        penalties = crop_res["penalties"]
        actual    = crop_res["actual_values"]
        sweet     = crop_res["sweet_spots"]

        col_L, col_R = st.columns([1, 1], gap="large")

        # ── Left: Score + Sensitivity breakdown ───────────────────────────
        with col_L:
            st.markdown(f"""
            <div style="background:{'#182028' if dark_mode else 'white'}; border:2px solid {col_hex}; border-radius:10px; padding:18px; margin-bottom:14px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; color:{txt_col};">
                            {t('viability_pct')}
                        </div>
                        <div style="font-size:40px; font-weight:900; color:{col_hex}; line-height:1.1;">{pct}%</div>
                        <div style="font-size:13px; font-weight:800; color:{txt_col}; margin-top:2px;">{crop_res['status'].split('(')[0].strip()}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:10px; font-weight:800; text-transform:uppercase; color:{txt_col};">{t('composite_s')}</div>
                        <div style="font-size:32px; font-weight:900; color:#E65100;">{sens['composite_sensitivity']}</div>
                        <div style="font-size:10px; color:{txt_col};">S = k / (Max − Min)</div>
                    </div>
                </div>
                <div style="background:{'#263342' if dark_mode else '#E5E7EB'}; border-radius:4px; height:8px; margin:14px 0 10px 0;">
                    <div style="background:{col_hex}; height:8px; border-radius:4px; width:{pct}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Sensitivity sub-scores
            st.markdown(f"<div class='param-card'><h4>{t('sensitivity_title')}</h4>", unsafe_allow_html=True)
            s_rows = [
                ("🌡️ " + ("Temperatura" if current_lang == "es" else "Temperature"), sens["s_temperature"], "k=10, " + ("rango T°" if current_lang == "es" else "T° range")),
                ("🌧️ " + ("Precipitación" if current_lang == "es" else "Precipitation"), sens["s_precipitation"], "k=1000, " + ("rango mm" if current_lang == "es" else "mm range")),
                ("💧 " + ("Hum. Suelo" if current_lang == "es" else "Soil Moisture"), sens["s_soil_moisture"], "k=0.20, " + ("rango m³/m³" if current_lang == "es" else "m³/m³ range")),
                ("⛰️ " + ("Altitud" if current_lang == "es" else "Altitude"), sens["s_altitude"], "k=800, " + ("rango m" if current_lang == "es" else "m range")),
            ]
            for lbl, val, note in s_rows:
                bar_w = min(100, int(val / 2.5 * 100))
                st.markdown(f"""
                <div style="margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; font-size:12px;">
                        <span style="font-weight:700; color:{txt_col};">{lbl}</span>
                        <span style="font-weight:900; color:#E65100;">S = {val}</span>
                    </div>
                    <div style="background:{'#263342' if dark_mode else '#E5E7EB'}; border-radius:3px; height:5px; margin:3px 0;">
                        <div style="background:#E65100; height:5px; border-radius:3px; width:{bar_w}%;"></div>
                    </div>
                    <div style="font-size:10px; color:{txt_col};">{note}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Watering & soil requirements
            st.markdown(f"""
            <div class="param-card" style="margin-top:10px;">
                <h4>{t('agro_req_title')}</h4>
                <div class="sat-row">
                    <span class="sat-label" style="color:{txt_col};">{t('watering_label')}</span>
                    <span style="font-size:12px; color:{txt_col}; font-weight:700; max-width:55%; text-align:right;">{crop_data['watering_needs']}</span>
                </div>
                <div class="sat-row">
                    <span class="sat-label" style="color:{txt_col};">{t('soil_rec_label')}</span>
                    <span class="sat-value" style="font-family:inherit; font-size:12px; color:{txt_col};">{', '.join(crop_data['soil_type'])}</span>
                </div>
                <div class="sat-row">
                    <span class="sat-label" style="color:{txt_col};">{t('tolerable_t_label')}</span>
                    <span class="sat-value" style="color:{txt_col};">{crop_data.get('tolerable_temp_c', {}).get('min', '?')}°C – {crop_data.get('tolerable_temp_c', {}).get('max', '?')}°C</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Right: Delta table + comparison chart ─────────────────────────
        with col_R:
            st.markdown(f"<div class='section-title' style='margin-top:0;'>{t('deltas_title')}</div>", unsafe_allow_html=True)

            p_temp = "🌡️ " + ("Temperatura" if current_lang == "es" else "Temperature")
            p_rain = "🌧️ " + ("Precipitación" if current_lang == "es" else "Precipitation")
            p_alt  = "⛰️ " + ("Altitud" if current_lang == "es" else "Altitude")
            p_sm   = "💧 " + ("Hum. Suelo" if current_lang == "es" else "Soil Moisture")
            p_soil = "🪨 " + ("Tipo de Suelo" if current_lang == "es" else "Soil Type")

            df = pd.DataFrame([
                {
                    t("param_col"): p_temp,
                    t("actual_col"): f"{actual['temperature_c']:.1f} °C",
                    t("sweet_col"): f"{sweet['temperature_c']} °C",
                    t("delta_col"): f"{deltas['temperature_delta_c']:+.2f} °C",
                    t("points_col"): f"{penalties['temp']:.1f}",
                },
                {
                    t("param_col"): p_rain,
                    t("actual_col"): f"{actual['precipitation_mm']:.0f} mm",
                    t("sweet_col"): f"{sweet['precipitation_mm']} mm",
                    t("delta_col"): f"{deltas['precipitation_delta_mm']:+.0f} mm",
                    t("points_col"): f"{penalties['precip']:.1f}",
                },
                {
                    t("param_col"): p_alt,
                    t("actual_col"): f"{actual['altitude_m']:.0f} m",
                    t("sweet_col"): f"{sweet['altitude_m']} m",
                    t("delta_col"): f"{deltas['altitude_delta_m']:+.0f} m",
                    t("points_col"): f"{penalties['altitude']:.1f}",
                },
                {
                    t("param_col"): p_sm,
                    t("actual_col"): f"{actual['soil_moisture_m3_m3']:.3f} m³/m³",
                    t("sweet_col"): f"{sweet['soil_moisture_m3_m3']} m³/m³",
                    t("delta_col"): f"{deltas['soil_moisture_delta']:+.3f}",
                    t("points_col"): f"{penalties['soil_moisture']:.1f}",
                },
                {
                    t("param_col"): p_soil,
                    t("actual_col"): actual['soil_type'],
                    t("sweet_col"): "Compatible",
                    t("delta_col"): "—",
                    t("points_col"): f"{penalties['soil_modifier']:+.1f}",
                },
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Gauge chart
            st.plotly_chart(
                create_viability_gauge(pct, crop_res["crop"], crop_res["icon"], dark_mode=dark_mode),
                use_container_width=True,
            )

            # Delta comparison chart (actual vs sweet spot)
            st.plotly_chart(
                create_delta_comparison_chart(crop_res, dark_mode=dark_mode, lang=current_lang),
                use_container_width=True
            )

        # ── Full-width comparative summary table ──────────────────────────
        st.markdown("---")
        st.markdown(f"<div class='section-title'>{t('matrix_title')}</div>", unsafe_allow_html=True)
        summary = []
        for r in all_results:
            summary.append({
                t("crop_label"): f"{r['icon']} {r['crop']} ({r.get('common_name', r['crop'])})",
                t("viability_col"): f"{r['success_percentage']}%",
                t("diagnosis_col"): r['status'].split('(')[0].strip(),
                "S Compuesto" if current_lang == "es" else "Composite S": r['sensitivity']['composite_sensitivity'],
                "Δ Temp (°C)": f"{r['deltas']['temperature_delta_c']:+.2f}",
                "Δ Lluvia (mm)" if current_lang == "es" else "Δ Rain (mm)": f"{r['deltas']['precipitation_delta_mm']:+.0f}",
                "Δ Alt (m)": f"{r['deltas']['altitude_delta_m']:+.0f}",
                "Δ Hum.Suelo" if current_lang == "es" else "Δ Soil Moist.": f"{r['deltas']['soil_moisture_delta']:+.3f}",
            })
        st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

    # ===========================================================================
    #  PAGE 3 — Rotación de Cultivos / Crop Rotation
    # ===========================================================================
    elif active_page == PAGE_ROTATION:
        st.markdown(f"<div class='section-title'>{t('rotation_title')}</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-notice">
            🌱 <b>{t('rotation_title')}:</b> {t('rotation_intro')}
        </div>
        <div style="background:{notice_bg}; border:1.5px solid {notice_border}; border-radius:8px; padding:12px 16px; margin-bottom:18px; font-size:12.5px; color:{txt_col};">
            {t('rotation_disclaimer')}
        </div>
        """, unsafe_allow_html=True)

        # ── Primary Crop & Farmer Priorities Controls ─────────────────────────
        c_col1, c_col2 = st.columns([1.1, 1.3], gap="medium")
        with c_col1:
            crop_choices = [c["crop"] for c in CROPS_LIST]
            selected_primary = st.selectbox(
                t("rotation_select_primary"),
                crop_choices,
                index=0,
                format_func=lambda c: f"{next(x['icon'] for x in CROPS_LIST if x['crop'] == c)} {c} ({next(x.get('common_name_es', x['crop']) for x in CROPS_LIST if x['crop'] == c)})"
            )
        with c_col2:
            priority_options = [
                ("balanced", t("priority_balanced")),
                ("soil_health", t("priority_soil")),
                ("water_conservation", t("priority_water")),
                ("income", t("priority_income")),
                ("pest_control", t("priority_pest")),
                ("erosion_control", t("priority_erosion")),
            ]
            selected_p_tuple = st.selectbox(
                t("rotation_priority_title"),
                priority_options,
                format_func=lambda x: x[1],
                index=0,
            )
            farmer_priority = selected_p_tuple[0]

        # ── Satellite & In-situ Context Indicators ────────────────────────────
        term_smap = render_term("Soil Moisture Anomalies", "SMAP L4")
        term_gpm = render_term("Water-Balance Indicators", "GPM DPR")
        term_et = render_term("Evapotranspiration", "ECOSTRESS ESI")
        term_grid = render_term("Harmonized Resolution Grid", "Cuadrícula NASA/IMN" if current_lang == "es" else "NASA/IMN Grid")
        st.markdown(f"""
        <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:16px;">
            <span class="mission-pill">⛰️ {actual_alt} msnm (SRTM 30m)</span>
            <span class="mission-pill">🌧️ {actual_p:.0f} mm/año ({term_gpm})</span>
            <span class="mission-pill">🌱 {actual_sm:.3f} m³/m³ ({term_smap})</span>
            <span class="mission-pill">🪨 {actual_soil} (IMN Suelos)</span>
            <span class="mission-pill">📐 Pendiente: {actual_slope:.1f}% ({env['topography_and_erosion']['landform_classification']})</span>
            <span class="mission-pill">🛰️ {term_grid}</span>
        </div>
        """, unsafe_allow_html=True)

        # ── Climate Scenario Simulator (What-If Sliders) ───────────────────────
        with st.expander(t("simulation_title"), expanded=False):
            st.markdown(
                ("💡 **Simulación de Resiliencia Climática:** Ajuste los controles para evaluar el comportamiento "
                 "de las estrategias ante eventos de estrés (ej. sequías por El Niño, canículas prolongadas o excesos pluviales).")
                if current_lang == "es" else
                ("💡 **Climate Resilience Simulation:** Adjust controls to evaluate strategy performance under "
                 "stress events (e.g., El Niño droughts, heatwaves, or extreme cloudbursts).")
            )
            sim_col1, sim_col2 = st.columns(2)
            with sim_col1:
                sim_delta_t = st.slider(
                    "🌡️ " + ("Variación de Temperatura (ΔT °C):" if current_lang == "es" else "Temperature Variation (ΔT °C):"),
                    min_value=-2.0, max_value=4.0, value=0.0, step=0.5,
                    format="%+.1f °C"
                )
            with sim_col2:
                sim_delta_p = st.slider(
                    "🌧️ " + ("Variación de Precipitación (ΔP %):" if current_lang == "es" else "Precipitation Variation (ΔP %):"),
                    min_value=-50, max_value=50, value=0, step=5,
                    format="%+d%%"
                )

        # ── Evaluate Multi-Strategy Rotation Engine ───────────────────────────
        primary_result = next(r for r in all_results if r["crop"] == selected_primary)
        primary_viability = primary_result["success_percentage"]

        rot_analysis = RotationAnalysisService.evaluate_rotation_strategies(
            primary_crop=selected_primary,
            primary_viability=primary_viability,
            actual_temp_c=actual_t,
            actual_precip_mm=actual_p,
            actual_altitude_m=actual_alt,
            actual_soil_moisture_m3_m3=actual_sm,
            actual_soil_type=actual_soil,
            actual_slope_pct=actual_slope,
            farmer_priority=farmer_priority,
            delta_temp_c=sim_delta_t,
            delta_precip_pct=sim_delta_p,
        )

        evaluated_strats = rot_analysis["strategies"]
        rec_strat = rot_analysis["recommended_strategy"]
        calendar_timeline = rot_analysis["vulnerability_calendar"]
        baseline_score = rot_analysis["baseline_viability"]

        # ── Strategy Comparison Overview Cards ────────────────────────────────
        st.markdown(f"<div class='section-title'>{t('strategy_comparison_title')}</div>", unsafe_allow_html=True)

        cols_strats = st.columns(len(evaluated_strats), gap="small")
        for idx, (c_strat, col) in enumerate(zip(evaluated_strats, cols_strats)):
            is_base = c_strat.get("is_baseline", False)
            is_rec = c_strat.get("is_top_recommendation", False)
            viab = c_strat["viability_score"]
            v_col = score_color(viab, dark_mode)
            align = c_strat["farmer_alignment_score"]

            if is_rec:
                badge_html = f"<span style='background:#2E7D32; color:white !important; font-size:10px; font-weight:800; padding:2px 7px; border-radius:10px;'>{t('top_recommended_badge')}</span>"
                border_style = "2px solid #2E7D32"
                card_bg = notice_bg
            elif is_base:
                badge_html = f"<span style='background:#757575; color:white !important; font-size:10px; font-weight:800; padding:2px 7px; border-radius:10px;'>{t('baseline_badge')}</span>"
                border_style = f"1px solid {border_card}"
                card_bg = bg_card
            else:
                badge_html = f"<span style='background:#1565C0; color:white !important; font-size:10px; font-weight:800; padding:2px 7px; border-radius:10px;'>{'ALTERNATIVA VIABLE' if current_lang == 'es' else 'VIABLE OPTION'}</span>"
                border_style = f"1px solid {border_card}"
                card_bg = bg_card

            strat_title = c_strat["name_es"] if current_lang == "es" else c_strat["name_en"]
            strat_tag = c_strat["tag_es"] if current_lang == "es" else c_strat["tag_en"]
            net_vs_base = c_strat["net_advantage_vs_baseline"]
            net_txt = f"+{net_vs_base}%" if net_vs_base > 0 else f"{net_vs_base}%"
            net_color = "#2E7D32" if net_vs_base > 0 else ("#757575" if net_vs_base == 0 else "#D32F2F")

            with col:
                st.markdown(f"""
                <div style="background:{card_bg}; border:{border_style}; border-radius:9px; padding:13px; height:100%; display:flex; flex-direction:column; justify-content:space-between;">
                    <div>
                        <div style="margin-bottom:6px;">{badge_html}</div>
                        <h4 style="margin:2px 0 4px 0; font-size:14px; font-weight:800; color:{txt_col};">{c_strat.get('icon', '🌱')} {strat_title.split(':')[0]}</h4>
                        <div style="font-size:11px; font-weight:700; color:#E65100; margin-bottom:8px;">{strat_tag}</div>
                    </div>
                    <div>
                        <div style="display:flex; justify-content:space-between; align-items:baseline; margin:6px 0;">
                            <span style="font-size:11px; color:{txt_col};">{'Viabilidad' if current_lang == 'es' else 'Viability'}:</span>
                            <span style="font-size:22px; font-weight:900; color:{v_col};">{viab}%</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
                            <span style="color:{txt_col};">{'Ventaja neta' if current_lang == 'es' else 'Net advantage'}:</span>
                            <b style="color:{net_color};">{net_txt}</b>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:11px;">
                            <span style="color:{txt_col};">{'Alineación Meta' if current_lang == 'es' else 'Goal fit'}:</span>
                            <b style="color:{txt_col};">{align}%</b>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)

        # ── Detailed Strategy Inspector (The 5 Mandatory NASA Pillars) ────────
        strat_display_names = [
            f"{s.get('icon', '🌱')} {s['name_es'] if current_lang == 'es' else s['name_en']}"
            for s in evaluated_strats
        ]
        rec_index = next((i for i, s in enumerate(evaluated_strats) if s["strategy_id"] == rec_strat["strategy_id"]), 1)

        st.markdown(f"<div class='section-title'>{t('rotation_schedule_title')}</div>", unsafe_allow_html=True)
        selected_strat_label = st.radio(
            "Seleccionar Estrategia para Inspección Detallada:" if current_lang == "es" else "Select Strategy for In-Depth Inspection:",
            strat_display_names,
            index=rec_index,
            horizontal=True,
        )
        active_strat_idx = strat_display_names.index(selected_strat_label)
        active_strat = evaluated_strats[active_strat_idx]

        # Inspector layout: 2 Columns (Pillars on Left, Schedule on Right)
        col_pills_L, col_pills_R = st.columns([1.15, 0.95], gap="large")

        with col_pills_L:
            # Pillar 1: Why it was suggested
            st.markdown(f"#### {t('why_suggested_title')}")
            why_txt = active_strat["why_suggested_es"] if current_lang == "es" else active_strat["why_suggested_en"]
            st.markdown(f"""
            <div style="background:{bg_card}; border:1px solid {border_card}; border-left:4px solid #1565C0; border-radius:6px; padding:12px 14px; margin-bottom:12px; font-size:13px; color:{txt_col}; line-height:1.45;">
                {why_txt}
            </div>
            """, unsafe_allow_html=True)

            # Pillar 2: Supporting Evidence (NASA + IMN)
            st.markdown(f"#### {t('evidence_title')}")
            ev_txt = active_strat["evidence_supporting_es"] if current_lang == "es" else active_strat["evidence_supporting_en"]
            st.markdown(f"""
            <div style="background:{bg_card}; border:1px solid {border_card}; border-left:4px solid #2E7D32; border-radius:6px; padding:12px 14px; margin-bottom:12px; font-size:13px; color:{txt_col}; line-height:1.45;">
                {ev_txt}
            </div>
            """, unsafe_allow_html=True)

            # Pillar 3: Agronomic & Environmental Benefits
            st.markdown(f"#### {t('benefits_title')}")
            b_list = active_strat["benefits_es"] if current_lang == "es" else active_strat["benefits_en"]
            for b in b_list:
                st.markdown(f"- ✅ **{b}**")

            # Pillar 4: Information Gaps & Uncertainty
            st.markdown(f"#### {t('gaps_title')}")
            gap_txt = active_strat["information_gaps_es"] if current_lang == "es" else active_strat["information_gaps_en"]
            st.markdown(f"""
            <div style="background:{bg_card}; border:1px solid {border_card}; border-left:4px solid #FF8F00; border-radius:6px; padding:12px 14px; margin-bottom:12px; font-size:12.5px; color:{txt_col};">
                ℹ️ {gap_txt}
            </div>
            """, unsafe_allow_html=True)

            # Pillar 5: Critical Points for Farmer Local Review
            st.markdown(f"#### {t('farmer_review_title')}")
            r_list = active_strat["risks_and_farmer_review_es"] if current_lang == "es" else active_strat["risks_and_farmer_review_en"]
            for r in r_list:
                st.markdown(f"- ⚠️ {r}")

        with col_pills_R:
            # Agronomic Sequence Table
            st.markdown(f"#### {'📅 Secuencia Cronológica de Cultivos' if current_lang == 'es' else '📅 Chronological Crop Sequence'}")
            sched_rows = []
            for item in active_strat["schedule"]:
                p_lbl = item["period_es"] if current_lang == "es" else item["period_en"]
                pr_lbl = item["practice_es"] if current_lang == "es" else item["practice_en"]
                r_lbl = item["role_es"] if current_lang == "es" else item["role_en"]
                sched_rows.append({
                    t("year_label"): p_lbl,
                    "Práctica / Cultivo" if current_lang == "es" else "Practice / Crop": pr_lbl,
                    "Función Ecológica" if current_lang == "es" else "Ecological Role": r_lbl,
                })
            st.dataframe(pd.DataFrame(sched_rows), use_container_width=True, hide_index=True)

            # Associated Rotational Partner Species
            if active_strat["partners"]:
                st.markdown(f"<div style='margin-top:14px;'><b>{t('rotation_partner_title')}:</b></div>", unsafe_allow_html=True)
                for p_key in active_strat["partners"]:
                    if p_key in ROTATION_PARTNERS:
                        part = ROTATION_PARTNERS[p_key]
                        p_name = part["name_es"] if current_lang == "es" else part["name_en"]
                        p_cat = part["category_es"] if current_lang == "es" else part["category_en"]
                        p_soil = part["soil_benefit_es"] if current_lang == "es" else part["soil_benefit_en"]
                        p_pest = part["pest_break_es"] if current_lang == "es" else part["pest_break_en"]
                        st.markdown(f"""
                        <div class="rotation-card" style="margin-bottom:8px; padding:10px 12px; border-left:4px solid #2E7D32;">
                            <div style="font-weight:800; font-size:13px; color:{txt_col};">{part['icon']} {p_name}</div>
                            <div style="font-size:10.5px; font-weight:700; color:#E65100; text-transform:uppercase;">{p_cat}</div>
                            <div style="font-size:11.5px; margin-top:4px; color:{txt_col};">🌱 {p_soil}</div>
                            <div style="font-size:11.5px; color:{txt_col};">🛡️ {p_pest}</div>
                        </div>
                        """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Visual Analytics: Radar Comparison & Climate Scenario Simulation ───
        col_chart_L, col_chart_R = st.columns([1.1, 1.0], gap="large")
        with col_chart_L:
            st.plotly_chart(
                create_multi_rotation_radar_chart(evaluated_strats, selected_primary, dark_mode=dark_mode, lang=current_lang),
                use_container_width=True
            )
        with col_chart_R:
            st.plotly_chart(
                create_climate_scenario_chart(
                    evaluated_strats,
                    selected_primary,
                    delta_temp=sim_delta_t,
                    delta_precip=sim_delta_p,
                    dark_mode=dark_mode,
                    lang=current_lang
                ),
                use_container_width=True
            )

        st.markdown("---")

        # ── 12-Month Agro-Climatic Vulnerability & Bare-Field Transition Calendar ──
        st.markdown(f"<div class='section-title'>{t('timeline_title')}</div>", unsafe_allow_html=True)
        st.caption(
            "Visualiza la correlación entre las precipitaciones satelitales (GPM), el estrés térmico/hídrico, "
            "los períodos de suelo desnudo en monocultivo y la protección continua que brinda la cobertura viva rotacional."
            if current_lang == "es" else
            "Visualizes the correlation between satellite rainfall (GPM), climate stress, bare-soil vulnerability "
            "under monoculture, and the continuous living armor provided by rotational covers."
        )

        st.plotly_chart(
            create_vulnerability_timeline_chart(calendar_timeline, dark_mode=dark_mode, lang=current_lang),
            use_container_width=True
        )

        # Contextual Interpretation of Seasonal Windows
        c_win1, c_win2, c_win3 = st.columns(3)
        with c_win1:
            st.markdown(f"""
            <div class="rotation-card" style="border-top: 3px solid #E65100; height:100%;">
                <b style="color:#E65100;">☀️ {'Períodos de Suelo Desnudo' if current_lang == 'es' else 'Bare-Soil Vulnerability'}</b>
                <p style="font-size:12px; margin-top:6px; color:{txt_col};">
                {'En monocultivos, los meses secos (Ene-Abr) y post-cosecha dejan el terreno sin cobertura. La radiación directa degrada la materia orgánica y el viento acelera la erosión.' if current_lang == 'es' else 'Under monoculture, dry months (Jan-Apr) leave ground completely bare. Solar radiation oxidizes organic matter and trade winds accelerate erosion.'}
                </p>
            </div>
            """, unsafe_allow_html=True)
        with c_win2:
            st.markdown(f"""
            <div class="rotation-card" style="border-top: 3px solid #2E7D32; height:100%;">
                <b style="color:#2E7D32;">🌱 {'Ventana Óptima de Siembra' if current_lang == 'es' else 'Optimal Sowing Window'}</b>
                <p style="font-size:12px; margin-top:6px; color:{txt_col};">
                {'Con la entrada de las lluvias en mayo (registradas por GPM), la siembra inmediata de leguminosas (Canavalia, Caupí) asegura rápida germinación y fijación simbiótica de nitrógeno.' if current_lang == 'es' else 'With monsoon onset in May (tracked by GPM), immediate legume sowing ensures rapid establishment and symbiotic biological nitrogen fixation.'}
                </p>
            </div>
            """, unsafe_allow_html=True)
        with c_win3:
            st.markdown(f"""
            <div class="rotation-card" style="border-top: 3px solid #1565C0; height:100%;">
                <b style="color:#1565C0;">✂️ {'Acolchado & Veranillo' if current_lang == 'es' else 'Mulch & Dry Spell Buffering'}</b>
                <p style="font-size:12px; margin-top:6px; color:{txt_col};">
                {'Segar la cobertura viva en julio antes del Veranillo de San Juan crea un colchón de mulch que reduce la evapotranspiración (ECOSTRESS) y mantiene la humedad radicular (SMAP).' if current_lang == 'es' else 'Slashing living cover in July prior to the midsummer drought forms a thick mulch that curbs evapotranspiration (ECOSTRESS) and preserves root moisture (SMAP).'}
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Cross-crop rotation comparison matrix ──────────────────────────
        st.markdown(f"<div class='section-title'>{'📊 Resumen de Rotaciones para los 5 Cultivos en este Punto' if current_lang == 'es' else '📊 Rotation Summary for All 5 Crops at this Location'}</div>", unsafe_allow_html=True)
        rot_summary = []
        for c in CROPS_LIST:
            c_name = c["crop"]
            c_viab = next(r["success_percentage"] for r in all_results if r["crop"] == c_name)
            c_analysis = RotationAnalysisService.evaluate_rotation_strategies(
                primary_crop=c_name,
                primary_viability=c_viab,
                actual_temp_c=actual_t,
                actual_precip_mm=actual_p,
                actual_altitude_m=actual_alt,
                actual_soil_moisture_m3_m3=actual_sm,
                actual_soil_type=actual_soil,
                actual_slope_pct=actual_slope,
                farmer_priority=farmer_priority,
                delta_temp_c=sim_delta_t,
                delta_precip_pct=sim_delta_p,
            )
            top_strat = c_analysis["recommended_strategy"]
            rot_summary.append({
                t("crop_label"): f"{c['icon']} {c_name}",
                "Viabilidad Monocultivo" if current_lang == "es" else "Monoculture Viability": f"{c_analysis['baseline_viability']}%",
                "Viabilidad con Rotación" if current_lang == "es" else "Rotation Viability": f"{top_strat['viability_score']}%",
                "Ventaja Neta" if current_lang == "es" else "Net Advantage": f"+{top_strat['net_advantage_vs_baseline']}%" if top_strat['net_advantage_vs_baseline'] > 0 else f"{top_strat['net_advantage_vs_baseline']}%",
                "Estrategia Recomendada" if current_lang == "es" else "Recommended Strategy": top_strat["name_es"].split(":")[1].strip() if current_lang == "es" else top_strat["name_en"].split(":")[1].strip(),
                "Alineación con Meta" if current_lang == "es" else "Farmer Goal Alignment": f"{top_strat['farmer_alignment_score']}%",
            })
        st.dataframe(pd.DataFrame(rot_summary), use_container_width=True, hide_index=True)

    # ===========================================================================
    #  PAGE 4 — Datos Científicos & Metodología / Scientific Data
    # ===========================================================================
    elif active_page == PAGE_SCIENCE:
        tab_sat, tab_soil, tab_climate, tab_glossary = st.tabs([
            t("tab_satellites"),
            t("tab_soil"),
            t("tab_climate"),
            t("tab_glossary"),
        ])

        # ── TAB 1: Satellite Sensors ───────────────────────────────────────
        with tab_sat:
            term_et   = render_term("Evapotranspiration", "Evapotranspiración" if current_lang == "es" else "Evapotranspiration")
            term_anom = render_term("Soil Moisture Anomalies", "Anomalías de Humedad" if current_lang == "es" else "Soil Moisture Anomalies")
            st.markdown(
                f"<div class='section-title'>{t('sat_title')} — {term_et} & {term_anom}</div>",
                unsafe_allow_html=True,
            )
            st.caption(f"{'Variables físicas extraídas para' if current_lang == 'es' else 'Physical variables extracted for'}: **{loc_name}** (Lat {lat:.4f} · Lon {lon:.4f})")

            smap = env["raw_services"]["smap"]["products"]
            gpm  = env["raw_services"]["gpm"]
            eco  = env["raw_services"]["ecostress"]
            srtm = env["raw_services"]["srtm"]

            col1, col2 = st.columns(2, gap="medium")

            with col1:
                st.markdown(f"""
                <div class="param-card">
                    <h4>{t('smap_title')}</h4>
                """, unsafe_allow_html=True)
                smap_rows = [
                    ("Humedad Superficial L2 (0–5 cm)" if current_lang == "es" else "Surface Moisture L2 (0–5 cm)", f"{smap['L2_SM_AP']['value_m3_m3']} m³/m³"),
                    ("Humedad Radicular L4 (0–100 cm)" if current_lang == "es" else "Root Zone Moisture L4 (0–100 cm)", f"{smap['L4_SM']['value_m3_m3']} m³/m³"),
                    ("Temperatura Suelo L4 (capa 1)" if current_lang == "es" else "Ground Temperature L4 (layer 1)", f"{smap['L4_SM']['ground_temperature_c']} °C"),
                    ("Producto L2" if current_lang == "es" else "L2 Product", smap["L2_SM_AP"].get("product", "L2_SM_A/P")),
                    ("Producto L4" if current_lang == "es" else "L4 Product", smap["L4_SM"].get("product", "L4_SM")),
                ]
                for lbl, val in smap_rows:
                    st.markdown(f"""
                    <div class="sat-row">
                        <span class="sat-label">{lbl}</span>
                        <span class="sat-value">{val}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.plotly_chart(
                    create_moisture_comparison_chart(
                        smap["L2_SM_AP"]["value_m3_m3"],
                        smap["L4_SM"]["value_m3_m3"],
                        eco["evaporative_stress_index"],
                        dark_mode=dark_mode,
                        lang=current_lang,
                    ),
                    use_container_width=True,
                )

            with col2:
                t_air    = env["temperatures"]["air_temperature_mean_c"]
                t_ground = env["temperatures"]["ground_surface_temperature_c"]
                t_max    = env["temperatures"]["air_temperature_max_c"]
                t_min    = env["temperatures"]["air_temperature_min_c"]

                st.markdown(f"""
                <div class="param-card">
                    <h4>{t('eco_title')}</h4>
                """, unsafe_allow_html=True)
                eco_rows = [
                    ("Índice de Estrés Evaporativo (ESI)" if current_lang == "es" else "Evaporative Stress Index (ESI)", str(eco["evaporative_stress_index"])),
                    ("Evaluación del Estrés" if current_lang == "es" else "Stress Evaluation", eco["stress_evaluation"]),
                    ("Temperatura Sup. Terrestre (LST)" if current_lang == "es" else "Land Surface Temp. (LST)", f"{eco['land_surface_temp_c']} °C"),
                    ("Temperatura Aire Media (POWER)" if current_lang == "es" else "Mean Air Temp. (POWER)", f"{t_air:.1f} °C"),
                    ("Rango Temperatura Aire" if current_lang == "es" else "Air Temp. Range", f"{t_min:.1f}°C – {t_max:.1f}°C"),
                ]
                for lbl, val in eco_rows:
                    st.markdown(f"""
                    <div class="sat-row">
                        <span class="sat-label">{lbl}</span>
                        <span class="sat-value">{val}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.plotly_chart(
                    create_temperature_breakdown_chart(t_air, t_ground, t_max, t_min, dark_mode=dark_mode, lang=current_lang),
                    use_container_width=True,
                )

            st.markdown("---")
            col3, col4 = st.columns(2, gap="medium")

            with col3:
                st.markdown(f"""
                <div class="param-card">
                    <h4>{t('gpm_title')}</h4>
                """, unsafe_allow_html=True)
                gpm_rows = [
                    ("Precipitación Anual Acumulada" if current_lang == "es" else "Annual Accumulated Rainfall", f"{gpm['annual_precipitation_mm']} mm/año"),
                    ("Mes Pico de Lluvias" if current_lang == "es" else "Peak Rainfall Month", gpm["peak_rainfall_month"]),
                    ("Precipitación en Mes Pico" if current_lang == "es" else "Rainfall in Peak Month", f"{gpm['peak_monthly_mm']} mm"),
                    ("Factor Erosividad Pluvial (R)" if current_lang == "es" else "Rainfall Erosivity Factor (R)", f"{gpm['rainfall_erosivity_R']} MJ·mm/(ha·h·año)"),
                    ("Producto Radar" if current_lang == "es" else "Radar Product", "GPM DPR L3 Monthly (3IMERGM)"),
                ]
                for lbl, val in gpm_rows:
                    st.markdown(f"""
                    <div class="sat-row">
                        <span class="sat-label">{lbl}</span>
                        <span class="sat-value">{val}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="param-card">
                    <h4>{t('srtm_title')}</h4>
                """, unsafe_allow_html=True)
                srtm_rows = [
                    ("Elevación Global DEM" if current_lang == "es" else "Global DEM Elevation", f"{srtm['elevation_msnm']} msnm"),
                    ("Pendiente Topográfica" if current_lang == "es" else "Topographic Slope", f"{srtm['slope_percent']}% ({srtm['slope_degrees']}°)"),
                    ("Clasificación del Relieve" if current_lang == "es" else "Landform Classification", srtm["landform_classification"]),
                    ("Aptitud de Mecanización" if current_lang == "es" else "Mechanization Suitability", srtm["mechanization_capacity"]),
                    ("Producto DEM" if current_lang == "es" else "DEM Product", "SRTMGL1 (1 arcsec · ~30 m)"),
                ]
                for lbl, val in srtm_rows:
                    st.markdown(f"""
                    <div class="sat-row">
                        <span class="sat-label">{lbl}</span>
                        <span class="sat-value">{val}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # ── TAB 2: Soil & Erosion ──────────────────────────────────────────
        with tab_soil:
            st.markdown(f"<div class='section-title'>{t('soil_tab_title')}</div>", unsafe_allow_html=True)
            soil   = env["soil"]["details"]
            erosion= env["topography_and_erosion"]

            col_s1, col_s2 = st.columns([1.1, 1.0], gap="large")

            with col_s1:
                st.markdown(f"<b style='font-size:15px; color:{txt_col};'>{'Orden de Suelo' if current_lang == 'es' else 'Soil Order'}: {soil['order']}</b>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:13px; color:{txt_col}; margin-top:4px;'>{soil['description']}</p>", unsafe_allow_html=True)

                soil_params = [
                    ("Textura" if current_lang == "es" else "Texture", soil["texture"]),
                    ("Rango de pH" if current_lang == "es" else "pH Range", f"{soil['ph_range'][0]} – {soil['ph_range'][1]}"),
                    ("Materia Orgánica" if current_lang == "es" else "Organic Matter", soil["organic_matter"]),
                    ("Potencial de Absorción" if current_lang == "es" else "Absorption Potential", soil["absorption_potential"]),
                    ("Tasa de Infiltración" if current_lang == "es" else "Infiltration Rate", f"{soil['infiltration_rate_mm_h']} mm/h"),
                    ("Capacidad de Agua (AWC)" if current_lang == "es" else "Available Water Capacity", f"{soil['available_water_capacity_mm_m']} mm/m"),
                ]
                st.markdown(f'<div class="param-card"><h4>{"Propiedades Físico-Químicas" if current_lang == "es" else "Physicochemical Properties"}</h4>', unsafe_allow_html=True)
                for lbl, val in soil_params:
                    st.markdown(f"""
                    <div class="sat-row">
                        <span class="sat-label">{lbl}</span>
                        <span class="sat-value" style="font-family:inherit;">{val}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_s2:
                st.markdown(f"<b style='font-size:14px; color:{txt_col};'>{t('erosion_title')}</b>", unsafe_allow_html=True)
                risk_color = erosion.get("erosion_risk_color", "#757575")
                st.markdown(f"""
                <div class="erosion-box" style="border-left-color:{risk_color}; margin-top:8px;">
                    <div style="font-size:11px; font-weight:800; text-transform:uppercase; color:{txt_col}; letter-spacing:0.6px;">{t('erosion_level_label')}</div>
                    <div style="font-size:22px; font-weight:900; color:{risk_color}; margin:4px 0;">{erosion['erosion_risk_level']}</div>
                    <div style="font-size:13px; color:{txt_col}; margin-bottom:8px;">
                        <b>{t('soil_loss_label')}:</b> {erosion['soil_loss_estimated_ton_ha_yr']} ton/ha/año
                    </div>
                    <div style="font-size:12px; color:{txt_col}; border-top:1px dashed {'#374151' if dark_mode else '#DDD'}; padding-top:8px; margin-top:4px;">
                        <b>{t('recommendation_label')}:</b> {erosion['conservation_advice']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"<div class='param-card' style='margin-top:14px;'><h4>{t('topo_title')}</h4>", unsafe_allow_html=True)
                topo_rows = [
                    (t("metric_elevation"), f"{erosion['elevation_msnm']} msnm"),
                    (t("metric_slope"), f"{erosion['slope_percent']:.1f}%"),
                ]
                for lbl, val in topo_rows:
                    st.markdown(f"""
                    <div class="sat-row">
                        <span class="sat-label">{lbl}</span>
                        <span class="sat-value" style="font-family:inherit;">{val}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # ── TAB 3: Climate Projections ─────────────────────────────────────
        with tab_climate:
            st.markdown(f"<div class='section-title'>{t('climate_tab_title')}</div>", unsafe_allow_html=True)
            proj    = env["precipitation"]["imn_projections"]
            imn_reg = env["location"]["imn_region"]

            st.markdown(f"""
            <div style="font-size:14px; font-weight:700; color:{txt_col}; margin-bottom:14px;">
                {t('met_region_label')}: <span style="color:#42A5F5;">{imn_reg}</span>
            </div>
            """, unsafe_allow_html=True)

            cp1, cp2 = st.columns(2, gap="medium")
            with cp1:
                st.markdown(f"""
                <div class="climate-card">
                    <h4 style="color:#E65100; margin:0 0 12px 0; font-size:15px;">{t('scenario_2030')} <span style="font-size:11px; font-weight:400; color:{txt_col};">({t('short_term')})</span></h4>
                    <div class="sat-row">
                        <span class="sat-label">{t('delta_t_label')}</span>
                        <span class="sat-value" style="font-family:inherit; color:#E65100;">{proj['temp_change_2030']}</span>
                    </div>
                    <div class="sat-row">
                        <span class="sat-label">{t('delta_p_label')}</span>
                        <span class="sat-value" style="font-family:inherit; color:#42A5F5;">{proj['precip_change_2030']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with cp2:
                st.markdown(f"""
                <div class="climate-card">
                    <h4 style="color:#EF5350; margin:0 0 12px 0; font-size:15px;">{t('scenario_2050')} <span style="font-size:11px; font-weight:400; color:{txt_col};">({t('medium_term')})</span></h4>
                    <div class="sat-row">
                        <span class="sat-label">{t('delta_t_label')}</span>
                        <span class="sat-value" style="font-family:inherit; color:#EF5350;">{proj['temp_change_2050']}</span>
                    </div>
                    <div class="sat-row">
                        <span class="sat-label">{t('delta_p_label')}</span>
                        <span class="sat-value" style="font-family:inherit; color:#42A5F5;">{proj['precip_change_2050']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown(f"""
            <div class="param-card" style="margin-top:0;">
                <h4>{t('regional_challenges')}</h4>
            """, unsafe_allow_html=True)
            st.markdown(f"<div class='sat-row'><span class='sat-label'>{t('dry_season_label')}</span><span style='font-size:12px; color:{txt_col}; max-width:65%; text-align:right;'>{proj['dry_season_impact']}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sat-row'><span class='sat-label'>{t('extreme_rain_label')}</span><span style='font-size:12px; color:{txt_col}; max-width:65%; text-align:right;'>{proj['extreme_rain_impact']}</span></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── TAB 4: Scientific Glossary ────────────────────────────────────
        with tab_glossary:
            render_glossary_panel(lang=current_lang)

            st.markdown("---")
            st.markdown(f"<div class='section-title'>{t('missions_title')}</div>", unsafe_allow_html=True)

            p_smap_l2 = "Humedad de suelo superficial (0–5 cm)" if current_lang == "es" else "Surface soil moisture (0–5 cm)"
            p_smap_l4 = "Humedad zona radicular (0–100 cm) + Temperatura suelo capa 1" if current_lang == "es" else "Root-zone moisture (0–100 cm) + Soil temp layer 1"
            p_gpm     = "Precipitación mensual por radar y factor de erosividad R" if current_lang == "es" else "Monthly radar precipitation & R-erosivity factor"
            p_eco     = "Índice de Estrés Evaporativo (ESI) y LST" if current_lang == "es" else "Evaporative Stress Index (ESI) & LST"
            p_srtm    = "Altitud digital, pendiente del terreno y aptitud de mecanización" if current_lang == "es" else "Digital elevation, slope, and mechanization aptitude"
            p_imn     = "Órdenes de suelo, absorción hídrica y proyecciones 2030–2050" if current_lang == "es" else "Soil orders, water absorption & 2030–2050 scenarios"

            st.markdown(f"""
            <table class="mission-table">
                <thead>
                    <tr>
                        <th>{t('mission_col')}</th>
                        <th>{t('product_col')}</th>
                        <th>{t('param_model_col')}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td><b>NASA SMAP</b></td><td><code>L2_SM_A/P</code></td><td>{p_smap_l2}</td></tr>
                    <tr><td><b>NASA SMAP</b></td><td><code>L4_SM</code></td><td>{p_smap_l4}</td></tr>
                    <tr><td><b>NASA GPM</b></td><td><code>DPR Monthly · 3IMERGM</code></td><td>{p_gpm}</td></tr>
                    <tr><td><b>NASA ECOSTRESS</b></td><td><code>ECO_L4T_ESI · ECO2LSTE</code></td><td>{p_eco}</td></tr>
                    <tr><td><b>NASA SRTM</b></td><td><code>SRTMGL1 (30m)</code></td><td>{p_srtm}</td></tr>
                    <tr><td><b>IMN Costa Rica</b></td><td>Cartografía Suelos · Escenarios CC</td><td>{p_imn}</td></tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
