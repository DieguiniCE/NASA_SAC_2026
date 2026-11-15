"""
AgroClima Costa Rica — NASA Space Apps Challenge 2026
Polished final-product UI aligned with GEMINI.md blueprint.
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
from src.components.sidebar import render_sidebar, PAGE_ANALYZE, PAGE_CROPS, PAGE_SCIENCE
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
)


# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown(get_tooltip_css(), unsafe_allow_html=True)
st.markdown("""
<style>
/* ── Typography & Base ── */
html, body, [class*="css"] {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* ── App header banner ── */
.agro-header {
    background: linear-gradient(135deg, #0A2611 0%, #1B5E20 55%, #33691E 100%);
    color: white;
    padding: 18px 24px 14px 24px;
    border-radius: 10px;
    margin-bottom: 18px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}
.agro-header h1 {
    margin: 0 0 2px 0;
    font-size: 22px;
    font-weight: 800;
    color: white !important;
    letter-spacing: -0.3px;
}
.agro-header .subtitle {
    font-size: 12px;
    opacity: 0.88;
    color: #C8E6C9;
    margin: 0;
}
.mission-pill {
    display: inline-block;
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.22);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 700;
    color: #E8F5E9;
    margin: 2px 2px 0 0;
    letter-spacing: 0.3px;
}

/* ── Section headers ── */
.section-title {
    font-size: 15px;
    font-weight: 700;
    color: #1B5E20;
    margin: 16px 0 10px 0;
    padding-bottom: 5px;
    border-bottom: 2px solid #A5D6A7;
    letter-spacing: -0.2px;
}

/* ── Info notice box ── */
.info-notice {
    background: #F1F8E9;
    border-left: 4px solid #43A047;
    padding: 10px 14px;
    border-radius: 5px;
    font-size: 12.5px;
    color: #2E7D32;
    margin-bottom: 14px;
    line-height: 1.5;
}

/* ── Crop viability card ── */
.crop-card {
    background: #FFFFFF;
    border: 1px solid #E8E8E8;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.crop-card:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.09);
}
.crop-card-name {
    font-size: 15px;
    font-weight: 700;
    color: #212121;
}
.crop-card-name-es {
    font-size: 12px;
    color: #757575;
    margin-left: 4px;
}
.crop-score {
    font-size: 30px;
    font-weight: 900;
    line-height: 1;
}
.crop-status-badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    color: white;
    margin-top: 4px;
}
.progress-bg {
    background: #EEEEEE;
    border-radius: 4px;
    height: 7px;
    width: 100%;
    margin: 8px 0 6px 0;
}
.delta-row {
    font-size: 11px;
    color: #616161;
    display: flex;
    justify-content: space-between;
    gap: 4px;
    flex-wrap: wrap;
}
.delta-pill {
    background: #F5F5F5;
    border: 1px solid #E0E0E0;
    border-radius: 3px;
    padding: 1px 5px;
    font-size: 10px;
    font-weight: 600;
    color: #424242;
}

/* ── Parameter info card ── */
.param-card {
    background: #FAFAFA;
    border: 1px solid #EEEEEE;
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 10px;
}
.param-card h4 {
    margin: 0 0 10px 0;
    font-size: 13px;
    font-weight: 700;
    color: #333;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}

/* ── Climate scenario card ── */
.climate-card {
    background: white;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 16px;
    height: 100%;
}

/* ── Satellite data row ── */
.sat-row {
    display: flex;
    align-items: center;
    padding: 7px 0;
    border-bottom: 1px solid #F0F0F0;
    font-size: 13px;
}
.sat-row:last-child { border-bottom: none; }
.sat-label {
    flex: 1;
    color: #555;
    font-weight: 500;
}
.sat-value {
    font-weight: 700;
    color: #1B5E20;
    font-family: "JetBrains Mono", "Consolas", monospace;
    font-size: 13px;
}

/* ── Erosion risk box ── */
.erosion-box {
    border-radius: 8px;
    padding: 16px;
    border-left-width: 6px;
    border-left-style: solid;
}

/* ── Mission table ── */
.mission-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.mission-table th {
    background: #1B5E20;
    color: white;
    padding: 8px 12px;
    text-align: left;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.mission-table td {
    padding: 8px 12px;
    border-bottom: 1px solid #EEEEEE;
    vertical-align: top;
}
.mission-table tr:nth-child(even) td { background: #F9FBF9; }
.mission-table tr:hover td { background: #E8F5E9; }

/* Hide streamlit default elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_env_profile(lat: float, lon: float) -> Dict[str, Any]:
    return get_unified_environmental_profile(lat, lon)


def score_color(pct: int) -> str:
    if pct >= 80: return "#2E7D32"
    if pct >= 60: return "#1565C0"
    if pct >= 40: return "#E65100"
    return "#B71C1C"


def score_bg(pct: int) -> str:
    if pct >= 80: return "#2E7D32"
    if pct >= 60: return "#1565C0"
    if pct >= 40: return "#E65100"
    return "#B71C1C"


def render_crop_card(res: Dict[str, Any]):
    """Renders a single crop viability card — no raw data, fully styled HTML."""
    pct  = res["success_percentage"]
    col  = score_color(pct)
    name = res["crop"]
    name_es = res.get("common_name", name)
    icon = res["icon"]
    status = res["status"].split("(")[0].strip()
    s_score = res["sensitivity"]["composite_sensitivity"]
    deltas = res["deltas"]

    st.markdown(f"""
    <div class="crop-card" style="border-left: 5px solid {col};">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <span class="crop-card-name">{icon} {name}</span>
                <span class="crop-card-name-es">({name_es})</span><br>
                <span class="crop-status-badge" style="background:{col};">{status}</span>
            </div>
            <div style="text-align:right;">
                <span class="crop-score" style="color:{col};">{pct}%</span><br>
                <span style="font-size:10px; color:#888; font-weight:600;">S = {s_score}</span>
            </div>
        </div>
        <div class="progress-bg">
            <div style="background:{col}; height:7px; border-radius:4px; width:{pct}%;"></div>
        </div>
        <div class="delta-row">
            <span class="delta-pill">Δ Temp {deltas['temperature_delta_c']:+.1f}°C</span>
            <span class="delta-pill">Δ Lluvia {deltas['precipitation_delta_mm']:+.0f} mm</span>
            <span class="delta-pill">Δ Alt {deltas['altitude_delta_m']:+.0f} m</span>
            <span class="delta-pill">Δ Hum {deltas['soil_moisture_delta']:+.3f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Main App ─────────────────────────────────────────────────────────────────
def main():
    active_page, lat, lon, loc_name, show_zones = render_sidebar()

    with st.spinner("Consultando satélites (SMAP · GPM · ECOSTRESS · SRTM) y bases IMN…"):
        env = load_env_profile(lat, lon)

    # Environmental parameters
    actual_t   = env["temperatures"]["air_temperature_mean_c"]
    actual_p   = env["precipitation"]["gpm_annual_total_mm"]
    actual_alt = env["topography_and_erosion"]["elevation_msnm"]
    actual_sm  = env["humidity_and_moisture"]["smap_root_zone_moisture_m3_m3"]
    actual_soil= env["soil"]["order"]

    # Viability results for all 5 crops
    all_results: List[Dict[str, Any]] = SensitivityViabilityModel.calculate_all_crops(
        actual_temp_c=actual_t,
        actual_precip_mm=actual_p,
        actual_altitude_m=actual_alt,
        actual_soil_moisture_m3_m3=actual_sm,
        actual_soil_type=actual_soil,
    )

    # ── App Header ──────────────────────────────────────────────────────────
    tooltip_fusion = render_term("Satellite vs. Ground Data", "Fusión Satelital + Tierra (IMN)")
    st.markdown(f"""
    <div class="agro-header">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <h1>🌱 {APP_TITLE}</h1>
                <p class="subtitle">{APP_SUBTITLE} &mdash; Modelo de Viabilidad de Cultivos por Satélite y Datos IMN</p>
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
        Los satélites de la NASA brindan cobertura continua; las estaciones del IMN aportan precisión local.
        La fusión de ambas fuentes produce el perfil ambiental más exacto para cada coordenada de Costa Rica.
        <i>(Pase el cursor sobre el texto subrayado para ver la ficha explicativa flotante).</i>
    </div>
    """, unsafe_allow_html=True)

    # ===========================================================================
    #  PAGE 1 — Analizar Ubicación
    # ===========================================================================
    if active_page == PAGE_ANALYZE:

        col_map, col_cards = st.columns([1.35, 1.0], gap="medium")

        # ── LEFT: Interactive Map ──────────────────────────────────────────
        with col_map:
            st.markdown("<div class='section-title'>🗺️ Mapa Interactivo de Costa Rica</div>", unsafe_allow_html=True)
            st.caption("Toque o haga clic en cualquier punto para colocar el pin y recalcular la viabilidad.")

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
                f"<div class='section-title'>🌾 Viabilidad de los 5 Cultivos</div>"
                f"<p style='font-size:12px; color:#666; margin-top:-6px; margin-bottom:10px;'>"
                f"<b>{loc_name}</b> &middot; {actual_alt} msnm &middot; Suelo: {actual_soil}"
                f"</p>",
                unsafe_allow_html=True,
            )
            for res in all_results:
                render_crop_card(res)

        # ── Full-width: Environmental Parameters ──────────────────────────
        st.markdown("---")
        term_wb  = render_term("Water-Balance Indicators", "Balance Hídrico")
        term_sma = render_term("Soil Moisture Anomalies", "Anomalías de Humedad del Suelo")
        st.markdown(
            f"<div class='section-title'>📊 Parámetros Físicos del Punto — {term_wb} & {term_sma}</div>",
            unsafe_allow_html=True,
        )
        render_climate_metrics(env)

        # ── Climadiagram ──────────────────────────────────────────────────
        st.markdown("---")
        st.plotly_chart(create_climadiagram(env["raw_services"]["nasa_power"]), use_container_width=True)

        # ── Quick comparison bar ──────────────────────────────────────────
        st.plotly_chart(create_viability_bar_chart(all_results), use_container_width=True)

    # ===========================================================================
    #  PAGE 2 — Fichas de Cultivo & Sensibilidad
    # ===========================================================================
    elif active_page == PAGE_CROPS:
        st.markdown("<div class='section-title'>🌾 Fichas de Cultivo & Algoritmo de Sensibilidad (GEMINI.md)</div>", unsafe_allow_html=True)

        # Algorithm explanation panel
        with st.expander("📐 ¿Cómo funciona el modelo? — Fórmula del Sensitivity Score", expanded=False):
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

        # Crop selector
        crop_names = [f"{c['icon']} {c['crop']} / {c.get('common_name_es', c['crop'])}" for c in CROPS_LIST]
        idx = st.selectbox("Seleccione el cultivo:", range(len(CROPS_LIST)),
                           format_func=lambda i: crop_names[i], label_visibility="visible")

        crop_data = CROPS_LIST[idx]
        crop_res  = all_results[idx]
        pct       = crop_res["success_percentage"]
        col_hex   = score_color(pct)
        sens      = crop_res["sensitivity"]
        deltas    = crop_res["deltas"]
        penalties = crop_res["penalties"]
        actual    = crop_res["actual_values"]
        sweet     = crop_res["sweet_spots"]

        col_L, col_R = st.columns([1, 1], gap="large")

        # ── Left: Score + Sensitivity breakdown ───────────────────────────
        with col_L:
            # Score header card
            st.markdown(f"""
            <div style="background:white; border:2px solid {col_hex}; border-radius:10px; padding:18px; margin-bottom:14px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; color:#888;">
                            Porcentaje de Viabilidad
                        </div>
                        <div style="font-size:40px; font-weight:900; color:{col_hex}; line-height:1.1;">{pct}%</div>
                        <div style="font-size:13px; font-weight:700; color:#333; margin-top:2px;">{crop_res['status'].split('(')[0].strip()}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:10px; font-weight:800; text-transform:uppercase; color:#888;">Composite S</div>
                        <div style="font-size:32px; font-weight:900; color:#E65100;">{sens['composite_sensitivity']}</div>
                        <div style="font-size:10px; color:#999;">S = k / (Max − Min)</div>
                    </div>
                </div>
                <div style="background:#EEE; border-radius:4px; height:8px; margin:14px 0 10px 0;">
                    <div style="background:{col_hex}; height:8px; border-radius:4px; width:{pct}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Sensitivity sub-scores
            st.markdown("<div class='param-card'><h4>Sensitivity Sub-Scores (S = k / rango)</h4>", unsafe_allow_html=True)
            s_rows = [
                ("🌡️ Temperatura",  sens["s_temperature"],  "k=10, rango T°"),
                ("🌧️ Precipitación", sens["s_precipitation"], "k=1000, rango mm"),
                ("💧 Hum. Suelo",    sens["s_soil_moisture"], "k=0.20, rango m³/m³"),
                ("⛰️ Altitud",       sens["s_altitude"],      "k=800, rango m"),
            ]
            for lbl, val, note in s_rows:
                bar_w = min(100, int(val / 2.5 * 100))
                st.markdown(f"""
                <div style="margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; font-size:12px;">
                        <span style="font-weight:600; color:#333;">{lbl}</span>
                        <span style="font-weight:800; color:#E65100;">S = {val}</span>
                    </div>
                    <div style="background:#EEE; border-radius:3px; height:5px; margin:3px 0;">
                        <div style="background:#E65100; height:5px; border-radius:3px; width:{bar_w}%;"></div>
                    </div>
                    <div style="font-size:10px; color:#999;">{note}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Watering & soil requirements
            st.markdown(f"""
            <div class="param-card" style="margin-top:10px;">
                <h4>Requerimientos Agronómicos</h4>
                <div class="sat-row">
                    <span class="sat-label">💧 Necesidades de Riego</span>
                    <span style="font-size:12px; color:#333; font-weight:600; max-width:55%; text-align:right;">{crop_data['watering_needs']}</span>
                </div>
                <div class="sat-row">
                    <span class="sat-label">🪨 Suelos Recomendados</span>
                    <span class="sat-value" style="font-family:inherit; font-size:12px;">{', '.join(crop_data['soil_type'])}</span>
                </div>
                <div class="sat-row">
                    <span class="sat-label">🌡️ Rango Tolerable T°</span>
                    <span class="sat-value">{crop_data.get('tolerable_temp_c', {}).get('min', '?')}°C – {crop_data.get('tolerable_temp_c', {}).get('max', '?')}°C</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Right: Delta table + comparison chart ─────────────────────────
        with col_R:
            st.markdown("<div class='section-title' style='margin-top:0;'>📊 Deltas y Penalizaciones</div>", unsafe_allow_html=True)

            df = pd.DataFrame([
                {
                    "Parámetro": "🌡️ Temperatura",
                    "Actual": f"{actual['temperature_c']:.1f} °C",
                    "Sweet Spot": f"{sweet['temperature_c']} °C",
                    "Δ": f"{deltas['temperature_delta_c']:+.2f} °C",
                    "−Puntos": f"{penalties['temp']:.1f}",
                },
                {
                    "Parámetro": "🌧️ Precipitación",
                    "Actual": f"{actual['precipitation_mm']:.0f} mm",
                    "Sweet Spot": f"{sweet['precipitation_mm']} mm",
                    "Δ": f"{deltas['precipitation_delta_mm']:+.0f} mm",
                    "−Puntos": f"{penalties['precip']:.1f}",
                },
                {
                    "Parámetro": "⛰️ Altitud",
                    "Actual": f"{actual['altitude_m']:.0f} m",
                    "Sweet Spot": f"{sweet['altitude_m']} m",
                    "Δ": f"{deltas['altitude_delta_m']:+.0f} m",
                    "−Puntos": f"{penalties['altitude']:.1f}",
                },
                {
                    "Parámetro": "💧 Hum. Suelo",
                    "Actual": f"{actual['soil_moisture_m3_m3']:.3f} m³/m³",
                    "Sweet Spot": f"{sweet['soil_moisture_m3_m3']} m³/m³",
                    "Δ": f"{deltas['soil_moisture_delta']:+.3f}",
                    "−Puntos": f"{penalties['soil_moisture']:.1f}",
                },
                {
                    "Parámetro": "🪨 Tipo de Suelo",
                    "Actual": actual['soil_type'],
                    "Sweet Spot": "Compatible",
                    "Δ": "—",
                    "−Puntos": f"{penalties['soil_modifier']:+.1f}",
                },
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Gauge chart
            st.plotly_chart(
                create_viability_gauge(pct, crop_res["crop"], crop_res["icon"]),
                use_container_width=True,
            )

            # Delta comparison chart (actual vs sweet spot)
            st.plotly_chart(create_delta_comparison_chart(crop_res), use_container_width=True)

        # ── Full-width comparative summary table ──────────────────────────
        st.markdown("---")
        st.markdown("<div class='section-title'>📋 Matriz Comparativa — Todos los Cultivos</div>", unsafe_allow_html=True)
        summary = []
        for r in all_results:
            summary.append({
                "Cultivo": f"{r['icon']} {r['crop']} ({r.get('common_name', r['crop'])})",
                "Viabilidad": f"{r['success_percentage']}%",
                "Diagnóstico": r['status'].split('(')[0].strip(),
                "S Compuesto": r['sensitivity']['composite_sensitivity'],
                "Δ Temp (°C)": f"{r['deltas']['temperature_delta_c']:+.2f}",
                "Δ Lluvia (mm)": f"{r['deltas']['precipitation_delta_mm']:+.0f}",
                "Δ Alt (m)": f"{r['deltas']['altitude_delta_m']:+.0f}",
                "Δ Hum.Suelo": f"{r['deltas']['soil_moisture_delta']:+.3f}",
            })
        st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

    # ===========================================================================
    #  PAGE 3 — Datos Científicos & Metodología
    # ===========================================================================
    elif active_page == PAGE_SCIENCE:
        tab_sat, tab_soil, tab_climate, tab_glossary = st.tabs([
            "🛰️ Sensores Satelitales",
            "🪨 Suelos & Erosión",
            "📈 Proyecciones Climáticas",
            "📖 Glosario Científico",
        ])

        # ── TAB 1: Satellite Sensors ───────────────────────────────────────
        with tab_sat:
            term_et   = render_term("Evapotranspiration", "Evapotranspiración")
            term_anom = render_term("Soil Moisture Anomalies", "Anomalías de Humedad")
            st.markdown(
                f"<div class='section-title'>🛰️ Parámetros Satelitales — {term_et} & {term_anom}</div>",
                unsafe_allow_html=True,
            )
            st.caption(f"Variables físicas extraídas para: **{loc_name}** (Lat {lat:.4f} · Lon {lon:.4f})")

            smap = env["raw_services"]["smap"]["products"]
            gpm  = env["raw_services"]["gpm"]
            eco  = env["raw_services"]["ecostress"]
            srtm = env["raw_services"]["srtm"]

            col1, col2 = st.columns(2, gap="medium")

            with col1:
                # SMAP card
                st.markdown("""
                <div class="param-card">
                    <h4>🛰️ NASA SMAP — Humedad del Suelo</h4>
                """, unsafe_allow_html=True)
                smap_rows = [
                    ("Humedad Superficial L2 (0–5 cm)", f"{smap['L2_SM_AP']['value_m3_m3']} m³/m³"),
                    ("Humedad Radicular L4 (0–100 cm)", f"{smap['L4_SM']['value_m3_m3']} m³/m³"),
                    ("Temperatura Suelo L4 (capa 1)", f"{smap['L4_SM']['ground_temperature_c']} °C"),
                    ("Producto L2", smap["L2_SM_AP"].get("product", "L2_SM_A/P")),
                    ("Producto L4", smap["L4_SM"].get("product", "L4_SM")),
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
                    ),
                    use_container_width=True,
                )

            with col2:
                # ECOSTRESS card
                t_air    = env["temperatures"]["air_temperature_mean_c"]
                t_ground = env["temperatures"]["ground_surface_temperature_c"]
                t_max    = env["temperatures"]["air_temperature_max_c"]
                t_min    = env["temperatures"]["air_temperature_min_c"]

                st.markdown("""
                <div class="param-card">
                    <h4>🌿 NASA ECOSTRESS / VIIRS — Estrés Evaporativo & Temperatura</h4>
                """, unsafe_allow_html=True)
                eco_rows = [
                    ("Índice de Estrés Evaporativo (ESI)", str(eco["evaporative_stress_index"])),
                    ("Evaluación del Estrés", eco["stress_evaluation"]),
                    ("Temperatura Sup. Terrestre (LST)", f"{eco['land_surface_temp_c']} °C"),
                    ("Temperatura Aire Media (POWER)", f"{t_air:.1f} °C"),
                    ("Rango Temperatura Aire", f"{t_min:.1f}°C – {t_max:.1f}°C"),
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
                    create_temperature_breakdown_chart(t_air, t_ground, t_max, t_min),
                    use_container_width=True,
                )

            st.markdown("---")
            col3, col4 = st.columns(2, gap="medium")

            with col3:
                st.markdown("""
                <div class="param-card">
                    <h4>🌧️ NASA GPM DPR Monthly — Precipitación por Radar</h4>
                """, unsafe_allow_html=True)
                gpm_rows = [
                    ("Precipitación Anual Acumulada", f"{gpm['annual_precipitation_mm']} mm/año"),
                    ("Mes Pico de Lluvias", gpm["peak_rainfall_month"]),
                    ("Precipitación en Mes Pico", f"{gpm['peak_monthly_mm']} mm"),
                    ("Factor Erosividad Pluvial (R)", f"{gpm['rainfall_erosivity_R']} MJ·mm/(ha·h·año)"),
                    ("Producto Radar", "GPM DPR L3 Monthly (3IMERGM)"),
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
                st.markdown("""
                <div class="param-card">
                    <h4>⛰️ NASA SRTM 30m Global — Topografía Digital</h4>
                """, unsafe_allow_html=True)
                srtm_rows = [
                    ("Elevación Global DEM", f"{srtm['elevation_msnm']} msnm"),
                    ("Pendiente Topográfica", f"{srtm['slope_percent']}% ({srtm['slope_degrees']}°)"),
                    ("Clasificación del Relieve", srtm["landform_classification"]),
                    ("Aptitud de Mecanización", srtm["mechanization_capacity"]),
                    ("Producto DEM", "SRTMGL1 (1 arcsec · ~30 m)"),
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
            st.markdown("<div class='section-title'>🪨 Suelos de Costa Rica — IMN / MAG / CIA-UCR</div>", unsafe_allow_html=True)
            soil   = env["soil"]["details"]
            erosion= env["topography_and_erosion"]

            col_s1, col_s2 = st.columns([1.1, 1.0], gap="large")

            with col_s1:
                st.markdown(f"<b style='font-size:15px; color:#1B5E20;'>Orden de Suelo: {soil['order']}</b>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:13px; color:#555; margin-top:4px;'>{soil['description']}</p>", unsafe_allow_html=True)

                soil_params = [
                    ("Textura",                   soil["texture"]),
                    ("Rango de pH",               f"{soil['ph_range'][0]} – {soil['ph_range'][1]}"),
                    ("Materia Orgánica",           soil["organic_matter"]),
                    ("Potencial de Absorción",     soil["absorption_potential"]),
                    ("Tasa de Infiltración",       f"{soil['infiltration_rate_mm_h']} mm/h"),
                    ("Capacidad de Agua (AWC)",    f"{soil['available_water_capacity_mm_m']} mm/m"),
                ]
                st.markdown('<div class="param-card"><h4>Propiedades Físico-Químicas</h4>', unsafe_allow_html=True)
                for lbl, val in soil_params:
                    st.markdown(f"""
                    <div class="sat-row">
                        <span class="sat-label">{lbl}</span>
                        <span class="sat-value" style="font-family:inherit;">{val}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_s2:
                st.markdown("<b style='font-size:14px;'>🛡️ Riesgo de Erosión Hídrica — Modelo RUSLE</b>", unsafe_allow_html=True)
                risk_color = erosion.get("erosion_risk_color", "#757575")
                st.markdown(f"""
                <div class="erosion-box" style="background:#FAFAFA; border-left-color:{risk_color}; margin-top:8px;">
                    <div style="font-size:11px; font-weight:800; text-transform:uppercase; color:#888; letter-spacing:0.6px;">Nivel de Riesgo</div>
                    <div style="font-size:22px; font-weight:900; color:{risk_color}; margin:4px 0;">{erosion['erosion_risk_level']}</div>
                    <div style="font-size:13px; color:#333; margin-bottom:8px;">
                        <b>Pérdida de Suelo Estimada:</b> {erosion['soil_loss_estimated_ton_ha_yr']} ton/ha/año
                    </div>
                    <div style="font-size:12px; color:#555; border-top:1px dashed #DDD; padding-top:8px; margin-top:4px;">
                        <b>Recomendación:</b> {erosion['conservation_advice']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<div class='param-card' style='margin-top:14px;'><h4>Factores Topográficos</h4>", unsafe_allow_html=True)
                topo_rows = [
                    ("Elevación (SRTM)", f"{erosion['elevation_msnm']} msnm"),
                    ("Pendiente", f"{erosion['slope_percent']:.1f}%"),
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
            st.markdown("<div class='section-title'>📈 Proyecciones de Cambio Climático — IMN Costa Rica</div>", unsafe_allow_html=True)
            proj    = env["precipitation"]["imn_projections"]
            imn_reg = env["location"]["imn_region"]

            st.markdown(f"""
            <div style="font-size:14px; font-weight:700; color:#1B5E20; margin-bottom:14px;">
                Región Meteorológica: <span style="color:#0D47A1;">{imn_reg}</span>
            </div>
            """, unsafe_allow_html=True)

            cp1, cp2 = st.columns(2, gap="medium")
            with cp1:
                st.markdown(f"""
                <div class="climate-card">
                    <h4 style="color:#E65100; margin:0 0 12px 0; font-size:15px;">📅 Escenario 2030 <span style="font-size:11px; font-weight:400; color:#888;">(Corto Plazo)</span></h4>
                    <div class="sat-row">
                        <span class="sat-label">Aumento de Temperatura (ΔT)</span>
                        <span class="sat-value" style="font-family:inherit; color:#E65100;">{proj['temp_change_2030']}</span>
                    </div>
                    <div class="sat-row">
                        <span class="sat-label">Variación Precipitación (ΔP)</span>
                        <span class="sat-value" style="font-family:inherit; color:#1565C0;">{proj['precip_change_2030']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with cp2:
                st.markdown(f"""
                <div class="climate-card">
                    <h4 style="color:#B71C1C; margin:0 0 12px 0; font-size:15px;">📅 Escenario 2050 <span style="font-size:11px; font-weight:400; color:#888;">(Mediano Plazo)</span></h4>
                    <div class="sat-row">
                        <span class="sat-label">Aumento de Temperatura (ΔT)</span>
                        <span class="sat-value" style="font-family:inherit; color:#B71C1C;">{proj['temp_change_2050']}</span>
                    </div>
                    <div class="sat-row">
                        <span class="sat-label">Variación Precipitación (ΔP)</span>
                        <span class="sat-value" style="font-family:inherit; color:#1565C0;">{proj['precip_change_2050']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("""
            <div class="param-card" style="margin-top:0;">
                <h4>⚠️ Desafíos Climáticos Regionales</h4>
            """, unsafe_allow_html=True)
            st.markdown(f"<div class='sat-row'><span class='sat-label'>☀️ Impacto Estación Seca</span><span style='font-size:12px; color:#333; max-width:65%; text-align:right;'>{proj['dry_season_impact']}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sat-row'><span class='sat-label'>🌧️ Lluvias Extremas</span><span style='font-size:12px; color:#333; max-width:65%; text-align:right;'>{proj['extreme_rain_impact']}</span></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── TAB 4: Scientific Glossary ────────────────────────────────────
        with tab_glossary:
            render_glossary_panel()

            st.markdown("---")
            st.markdown("<div class='section-title'>🛰️ Resumen de Misiones y Productos</div>", unsafe_allow_html=True)

            st.markdown("""
            <table class="mission-table">
                <thead>
                    <tr>
                        <th>Misión / Base de Datos</th>
                        <th>Producto</th>
                        <th>Parámetro en el Modelo</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td><b>NASA SMAP</b></td><td><code>L2_SM_A/P</code></td><td>Humedad de suelo superficial (0–5 cm)</td></tr>
                    <tr><td><b>NASA SMAP</b></td><td><code>L4_SM</code></td><td>Humedad zona radicular (0–100 cm) + Temperatura suelo capa 1</td></tr>
                    <tr><td><b>NASA GPM</b></td><td><code>DPR Monthly · 3IMERGM</code></td><td>Precipitación mensual por radar y factor de erosividad R</td></tr>
                    <tr><td><b>NASA ECOSTRESS</b></td><td><code>ECO_L4T_ESI · ECO2LSTE</code></td><td>Índice de Estrés Evaporativo (ESI) y LST</td></tr>
                    <tr><td><b>NASA SRTM</b></td><td><code>SRTMGL1 (30m)</code></td><td>Altitud digital, pendiente del terreno y aptitud de mecanización</td></tr>
                    <tr><td><b>IMN Costa Rica</b></td><td>Cartografía Suelos · Escenarios CC</td><td>Órdenes de suelo, absorción hídrica y proyecciones 2030–2050</td></tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
