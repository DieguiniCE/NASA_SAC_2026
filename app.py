"""
AgroClima Costa Rica - NASA Space Apps Challenge 2026
Unified Multi-Satellite & IMN Environmental Intelligence Engine
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

from src.config import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_ICON,
    MONTH_NAMES,
    CR_LAT_MIN,
    CR_LAT_MAX,
    CR_LON_MIN,
    CR_LON_MAX,
)
from src.data.costa_rica_locations import find_closest_location
from src.data.crops_catalog import CROPS_CATALOG
from src.services.data_lake import get_unified_environmental_profile
from src.models.basic_viability import calculate_basic_viability
from src.components.sidebar import render_sidebar
from src.components.map_view import render_costa_rica_map
from src.components.metrics_display import render_climate_metrics
from src.components.charts import (
    create_climadiagram,
    create_moisture_comparison_chart,
    create_viability_radar_chart,
    create_temperature_breakdown_chart,
)


# 1. Page Configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Custom CSS for polished scientific styling
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #0D3814 0%, #1B5E20 50%, #2E7D32 100%);
        color: white;
        padding: 16px 24px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
    }
    .main-header h1 {
        margin: 0;
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: white !important;
    }
    .main-header p {
        margin: 4px 0 0 0;
        font-size: 13px;
        opacity: 0.92;
        color: #E8F5E9 !important;
    }
    .mission-badge {
        display: inline-block;
        background-color: rgba(255,255,255,0.18);
        border: 1px solid rgba(255,255,255,0.3);
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        margin: 2px;
        color: white;
    }
    .card-box {
        background: white;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 15px;
    }
    .chip {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=3600, show_spinner=False)
def load_environmental_profile(lat: float, lon: float) -> Dict[str, Any]:
    """Cached wrapper around unified multi-mission environmental data lake."""
    return get_unified_environmental_profile(lat, lon)


def main():
    # Render sidebar and retrieve user selections
    active_page, lat, lon, loc_name, show_zones = render_sidebar()

    # Query Unified Multi-Database Environmental Profile
    with st.spinner("Integrando bases satelitales (SMAP, GPM, ECOSTRESS, SRTM) e IMN Costa Rica..."):
        env_profile = load_environmental_profile(lat, lon)

    # Top Application Header
    st.markdown(
        f"""
        <div class="main-header">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h1>🌱 {APP_TITLE}</h1>
                    <p>{APP_SUBTITLE} — Diagnóstico Biofísico Multifuente</p>
                </div>
                <div style="text-align: right;">
                    <span class="mission-badge">🛰️ SMAP (L2/L4)</span>
                    <span class="mission-badge">🛰️ GPM DPR</span>
                    <span class="mission-badge">🛰️ ECOSTRESS/VIIRS</span>
                    <span class="mission-badge">🛰️ SRTM 30m</span>
                    <span class="mission-badge">🇨🇷 IMN / MAG</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # PAGE 1: EXPLORADOR MULTIBASE & MAPA CR (Página Principal)
    # =========================================================================
    if active_page == "📍 Explorador Multibase & Mapa CR":
        col_map, col_info = st.columns([1.5, 1.0], gap="medium")

        elev = env_profile["topography_and_erosion"]["elevation_msnm"]
        closest_loc = find_closest_location(lat, lon)

        with col_map:
            st.markdown("### 🗺️ Mapa de Costa Rica (Selección Interactiva)")
            st.caption("💡 Toque o haga clic directamente en cualquier punto para consultar los satélites e IMN.")

            # Render Folium Map
            clicked_coords = render_costa_rica_map(
                selected_lat=lat,
                selected_lon=lon,
                location_name=loc_name,
                elevation_m=elev,
                show_reference_zones=show_zones,
                map_height=480,
            )

            # If user clicked on the map, update coordinates in session_state and rerun
            if clicked_coords:
                c_lat, c_lon = clicked_coords
                if abs(c_lat - lat) > 0.005 or abs(c_lon - lon) > 0.005:
                    if CR_LAT_MIN <= c_lat <= CR_LAT_MAX and CR_LON_MIN <= c_lon <= CR_LON_MAX:
                        nearest = find_closest_location(c_lat, c_lon)
                        st.session_state["selected_lat"] = c_lat
                        st.session_state["selected_lon"] = c_lon
                        st.session_state["location_name"] = f"Punto ({c_lat:.3f}, {c_lon:.3f}) próx. a {nearest['canton']}"
                        st.rerun()

        with col_info:
            st.markdown("### 📍 Ficha Biofísica del Punto")
            soil_info = env_profile["soil"]
            topo = env_profile["topography_and_erosion"]
            imn_region = env_profile["location"]["imn_region"]

            st.markdown(
                f"""
                <div class="card-box">
                    <h4 style="margin: 0 0 8px 0; color: #1B5E20;">{loc_name}</h4>
                    <p style="margin: 3px 0; font-size: 13px;"><b>Coordenadas:</b> <code>{lat:.4f}° N</code>, <code>{lon:.4f}° W</code></p>
                    <p style="margin: 3px 0; font-size: 13px;"><b>Región Climática IMN:</b> {imn_region}</p>
                    <p style="margin: 3px 0; font-size: 13px;"><b>Elevación SRTM 30m:</b> {topo['elevation_msnm']} msnm (Pendiente: {topo['slope_percent']}%)</p>
                    <p style="margin: 3px 0; font-size: 13px;"><b>Tipo de Suelo IMN:</b> <span style="color: #2E7D32; font-weight: bold;">{soil_info['order']}</span></p>
                    <p style="margin: 3px 0; font-size: 13px;"><b>Potencial de Absorción:</b> {env_profile['humidity_and_moisture']['soil_absorption_potential']} ({soil_info['details']['infiltration_rate_mm_h']} mm/h)</p>
                    <p style="margin: 3px 0; font-size: 13px;"><b>Riesgo de Erosión Hídrica:</b> <span style="font-weight: bold; color: {topo['erosion_risk_color']};">{topo['erosion_risk_level']}</span></p>
                    <div style="margin-top: 10px;">
                        <span style="font-size: 11px; font-weight: bold; color: #555;">Cultivos observados en la zona:</span><br>
                        {''.join(f'<span class="chip" style="background:#E8F5E9; color:#1B5E20;">{crop}</span>' for crop in closest_loc.get('primary_crops', []))}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Quick summary alert
            root_status = env_profile["humidity_and_moisture"]["smap_root_status"]
            st.info(f"🌿 **Estado Hídrico Radicular (SMAP L4):** {root_status}")

        # Metrics Display Section
        st.markdown("---")
        st.markdown("### 📊 Indicadores Ambientales Integrados (Satélites NASA + IMN)")
        render_climate_metrics(env_profile)

        # Plotly Walter-Lieth Climadiagram
        st.markdown("---")
        st.plotly_chart(create_climadiagram(env_profile["raw_services"]["nasa_power"]), use_container_width=True)

    # =========================================================================
    # PAGE 2: SENSORES SATELITALES (SMAP, GPM, ECOSTRESS, SRTM)
    # =========================================================================
    elif active_page == "🛰️ Sensores Satelitales (SMAP, GPM, ECOSTRESS, SRTM)":
        st.markdown("### 🛰️ Diagnóstico Específico por Misión Satelital")
        st.caption("Extracción de variables físicas directas para las coordenadas seleccionadas:")

        smap_p = env_profile["raw_services"]["smap"]["products"]
        gpm_p = env_profile["raw_services"]["gpm"]
        eco_p = env_profile["raw_services"]["ecostress"]
        srtm_p = env_profile["raw_services"]["srtm"]

        col_s1, col_s2 = st.columns(2)

        # 1. NASA SMAP
        with col_s1:
            st.markdown("#### 1. NASA SMAP (Soil Moisture Active Passive)")
            st.markdown(
                """
                - **L2_SM_A/P (Superficial 0-5 cm):** Mide la reflectividad de microondas en banda L.
                - **L4_SM (Zona Radicular 0-100 cm):** Asimila observaciones satelitales en el modelo hidrológico NASA Catchment.
                """
            )
            st.plotly_chart(
                create_moisture_comparison_chart(
                    smap_p["L2_SM_AP"]["value_m3_m3"],
                    smap_p["L4_SM"]["value_m3_m3"],
                    eco_p["evaporative_stress_index"]
                ),
                use_container_width=True
            )
            st.markdown(
                f"""
                - **Humedad Superficial (L2_SM_A/P):** `{smap_p['L2_SM_AP']['value_m3_m3']} m³/m³` (Saturación: `{smap_p['L2_SM_AP']['saturation_pct']}%`)
                - **Humedad en Raíces (L4_SM):** `{smap_p['L4_SM']['value_m3_m3']} m³/m³` (Saturación: `{smap_p['L4_SM']['saturation_pct']}%`)
                - **Temp. del Suelo (L4 layer 1):** `{smap_p['L4_SM']['ground_temperature_c']} °C`
                """
            )

        # 2. NASA ECOSTRESS / VIIRS
        with col_s2:
            st.markdown("#### 2. NASA ECOSTRESS & VIIRS (Estrés y Temperatura LST)")
            st.markdown(
                """
                - **ECO_L4T_ESI (70m Tiled):** Ratio de evapotranspiración real a potencial ($ET/PET$).
                - **ECO2LSTE (Land Surface Temperature):** Temperatura superficial del suelo y dosel mediante radiometría térmica infrarroja.
                """
            )
            t_air = env_profile["temperatures"]["air_temperature_mean_c"]
            t_ground = env_profile["temperatures"]["ground_surface_temperature_c"]
            t_max = env_profile["temperatures"]["air_temperature_max_c"]
            t_min = env_profile["temperatures"]["air_temperature_min_c"]

            st.plotly_chart(create_temperature_breakdown_chart(t_air, t_ground, t_max, t_min), use_container_width=True)

            st.markdown(
                f"""
                - **Índice de Estrés Evaporativo (ESI):** `{eco_p['evaporative_stress_index']}` ({eco_p['stress_evaluation']})
                - **Temperatura del Suelo (LST):** `{eco_p['land_surface_temp_c']} °C` (Diferencial suelo-aire: `{eco_p['air_to_ground_delta_c']:+.1f} °C`)
                - **Eficiencia en Uso del Agua (WUE):** `{eco_p['water_use_efficiency_g_kg']} g C / kg H₂O`
                """
            )

        st.markdown("---")
        col_s3, col_s4 = st.columns(2)

        # 3. NASA GPM DPR Monthly
        with col_s3:
            st.markdown("#### 3. NASA GPM (Dual-frequency Precipitation Radar)")
            st.markdown(
                """
                El radar DPR (bandas Ku y Ka) mide la estructura vertical de las gotas de lluvia tropicales.
                """
            )
            st.markdown(
                f"""
                - **Precipitación Anual Acumulada:** `{gpm_p['annual_precipitation_mm']} mm/año`
                - **Mes con Mayor Pluviosidad:** `{gpm_p['peak_rainfall_month']}` (`{gpm_p['peak_monthly_mm']} mm`)
                - **Intensidad de Tormenta Estimada:** `{gpm_p['est_max_daily_storm_mm']} mm / 24h`
                - **Factor de Erosividad Pluvial (R):** `{gpm_p['rainfall_erosivity_R']} MJ·mm/(ha·h·año)` ({gpm_p['erosivity_classification']})
                """
            )

        # 4. NASA SRTM 30m Global Topography
        with col_s4:
            st.markdown("#### 4. NASA SRTM (Shuttle Radar Topography Mission 30m)")
            st.markdown(
                """
                Mapeo interferométrico de radar en banda C a 30 metros de resolución espacial.
                """
            )
            st.markdown(
                f"""
                - **Elevación Exacta:** `{srtm_p['elevation_msnm']} msnm`
                - **Pendiente del Terreno:** `{srtm_p['slope_percent']}%` (`{srtm_p['slope_degrees']}°`)
                - **Tipo de Relieve:** `{srtm_p['landform_classification']}`
                - **Aptitud para Mecanización:** {srtm_p['mechanization_capacity']}
                - **Factor Topográfico LS (Erosión):** `{srtm_p['topographic_ls_factor']}`
                """
            )

    # =========================================================================
    # PAGE 3: SUELOS, ABSORCIÓN Y EROSIÓN (IMN / MAG)
    # =========================================================================
    elif active_page == "🪨 Suelos, Absorción y Erosión (IMN / MAG)":
        st.markdown("### 🪨 Caracterización de Suelos y Riesgo de Erosión Hídrica")
        st.caption("Datos compilados en concordancia con el Instituto Meteorológico Nacional (IMN), MAG y CIA-UCR:")

        soil = env_profile["soil"]["details"]
        erosion = env_profile["topography_and_erosion"]

        c_soil1, c_soil2 = st.columns([1.1, 1.0])

        with c_soil1:
            st.markdown(f"#### 🧪 Orden de Suelo: **{soil['order']}**")
            st.markdown(f"*{soil['description']}*")

            df_soil_props = pd.DataFrame({
                "Propiedad Edafológica": [
                    "Textura Dominante",
                    "Rango de pH",
                    "Contenido de Materia Orgánica",
                    "Potencial de Absorción",
                    "Tasa de Infiltración Hidráulica",
                    "Capacidad de Agua Disponible (AWC)",
                    "Drenaje Natural",
                    "Factor de Erodabilidad (K)"
                ],
                "Valor Característico": [
                    soil["texture"],
                    f"{soil['ph_range'][0]} - {soil['ph_range'][1]}",
                    soil["organic_matter"],
                    soil["absorption_potential"],
                    f"{soil['infiltration_rate_mm_h']} mm/h",
                    f"{soil['available_water_capacity_mm_m']} mm de agua / m suelo",
                    soil["drainage"],
                    f"{soil['erodibility_K']} (Resistencia a desprendimiento)"
                ]
            })
            st.table(df_soil_props)
            st.success(f"🌱 **Recomendación de Manejo Agronómico:** {soil['agronomic_recommendation']}")

        with c_soil2:
            st.markdown("#### 🛡️ Análisis de Riesgo de Erosión Hídrica (Modelo RUSLE)")
            st.markdown(
                """
                El modelo paramétrico RUSLE calcula la pérdida de suelo anual:
                $$\\text{Pérdida } (A) = R \\times K \\times LS \\times C \\times P$$
                """
            )

            rusle_factors = env_profile["raw_services"]["imn"]["erosion_risk_analysis"]["rusle_factors"]
            st.markdown(
                f"""
                - **$R$ (Erosividad de lluvia GPM):** `{rusle_factors['R_rainfall_erosivity']}`
                - **$K$ (Erodabilidad del suelo IMN):** `{rusle_factors['K_soil_erodibility']}`
                - **$LS$ (Longitud y gradiente de pendiente SRTM):** `{rusle_factors['LS_topographic']}`
                - **$C$ (Factor de cobertura vegetal media):** `{rusle_factors['C_cover_factor']}`
                - **$P$ (Prácticas de soporte/conservación):** `{rusle_factors['P_conservation_factor']}`
                """
            )

            # Erosion Result Box
            st.markdown(
                f"""
                <div style="background-color: #FAFAFA; border-left: 6px solid {erosion['erosion_risk_color']}; padding: 14px; border-radius: 6px; margin: 15px 0;">
                    <span style="font-size: 13px; font-weight: bold; color: #555;">NIVEL DE RIESGO DE EROSIÓN</span>
                    <h3 style="margin: 4px 0; color: {erosion['erosion_risk_color']};">{erosion['erosion_risk_level']}</h3>
                    <p style="margin: 2px 0; font-size: 14px;"><b>Pérdida Estimada:</b> {erosion['soil_loss_estimated_ton_ha_yr']} ton / ha / año</p>
                    <p style="margin: 6px 0 0 0; font-size: 13px; color: #333;"><b>Medida Preventiva:</b> {erosion['conservation_advice']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =========================================================================
    # PAGE 4: MODELO BÁSICO DE VIABILIDAD DE CULTIVO
    # =========================================================================
    elif active_page == "🌱 Modelo Básico de Viabilidad de Cultivo":
        st.markdown("### 🌱 Modelo Básico de Viabilidad Agroclimática (Baseline)")
        st.info(
            "📌 **Nota técnica**: Este es un modelo heurístico preliminar de evaluación multivariable "
            "(temperatura aire/suelo, humedad radicular SMAP, precipitación GPM, orden de suelo IMN, pendiente SRTM y proyecciones). "
            "Está estructurado modularmente para ser modificado o sustituido por modelos predictivos avanzados en fases posteriores."
        )

        crop_ids = list(CROPS_CATALOG.keys())
        crop_names = [f"{CROPS_CATALOG[cid]['icon']} {CROPS_CATALOG[cid]['name']}" for cid in crop_ids]

        sel_crop_idx = st.selectbox(
            "Seleccione el cultivo a evaluar:",
            range(len(crop_ids)),
            format_func=lambda i: crop_names[i],
        )
        target_crop_id = crop_ids[sel_crop_idx]

        # Calculate viability with basic model
        viability = calculate_basic_viability(target_crop_id, env_profile)

        col_v1, col_v2 = st.columns([1.1, 1.0])

        with col_v1:
            badge_c = viability["badge_color"]
            color_hex = "#2E7D32" if badge_c == "green" else "#1565C0" if badge_c == "blue" else "#E65100" if badge_c == "orange" else "#C62828"

            st.markdown(
                f"""
                <div style="background: white; border: 2px solid {color_hex}; border-radius: 8px; padding: 18px; margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 12px; color: #777; font-weight: bold; text-transform: uppercase;">Diagnóstico de Viabilidad</span>
                            <h3 style="margin: 2px 0; color: #222;">{viability['crop_icon']} {viability['crop_name']}</h3>
                            <span style="font-size: 16px; font-weight: bold; color: {color_hex};">{viability['verdict']}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 38px; font-weight: 800; color: {color_hex};">{viability['overall_score']}</span>
                            <span style="font-size: 16px; color: #888;">/ 100</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("#### 🎯 Factores Favorables Detectados:")
            if viability["positive_factors"]:
                for pos in viability["positive_factors"]:
                    st.write(f"✅ {pos}")
            else:
                st.write("Ningún factor sobresaliente en rango óptimo.")

            st.markdown("#### ⚠️ Factores Limitantes o de Riesgo:")
            if viability["limiting_factors"]:
                for lim in viability["limiting_factors"]:
                    st.write(f"⚠️ {lim}")
            else:
                st.write("No se identificaron restricciones agronómicas severas.")

        with col_v2:
            st.plotly_chart(
                create_viability_radar_chart(
                    viability["score_breakdown"],
                    viability["crop_name"].split("(")[0].strip(),
                    viability["overall_score"]
                ),
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("### 📊 Matriz Comparativa de Todos los Cultivos en esta Zona")

        all_crops_summary = []
        for cid in crop_ids:
            res = calculate_basic_viability(cid, env_profile)
            all_crops_summary.append({
                "Cultivo": f"{res['crop_icon']} {res['crop_name'].split('(')[0].strip()}",
                "Viabilidad Global": f"{res['overall_score']}%",
                "Veredicto": res["verdict"],
                "Térmico": f"{res['score_breakdown']['Térmico (Aire y Suelo)']}%",
                "Hídrico / Raíces": f"{res['score_breakdown']['Hídrico (Lluvia y Raíces)']}%",
                "Suelo IMN": f"{res['score_breakdown']['Edafológico (Suelo y Absorción)']}%",
                "Topografía & Pendiente": f"{res['score_breakdown']['Topográfico y Erosión']}%",
                "Resiliencia Cambio Climático": f"{res['score_breakdown']['Resiliencia Climática (2050)']}%",
            })

        st.dataframe(pd.DataFrame(all_crops_summary), use_container_width=True)

    # =========================================================================
    # PAGE 5: PROYECCIONES DE CAMBIO CLIMÁTICO (IMN)
    # =========================================================================
    elif active_page == "📈 Proyecciones de Cambio Climático (IMN)":
        st.markdown("### 📈 Escenarios de Cambio Climático Regionalizados (IMN Costa Rica)")
        proj = env_profile["precipitation"]["imn_projections"]
        imn_reg = env_profile["location"]["imn_region"]

        st.markdown(f"#### Subregión Meteorológica Activa: **{imn_reg}**")

        c_p1, c_p2 = st.columns(2)
        with c_p1:
            st.markdown(
                f"""
                <div class="card-box">
                    <h4 style="margin: 0 0 10px 0; color: #E65100;">Horizonte Temporal 2030 (Corto Plazo)</h4>
                    <p><b>Aumento de Temperatura Proyectado (ΔT):</b> <code>{proj['temp_change_2030']}</code></p>
                    <p><b>Variación de Precipitación Proyectada (ΔP):</b> <code>{proj['precip_change_2030']}</code></p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c_p2:
            st.markdown(
                f"""
                <div class="card-box">
                    <h4 style="margin: 0 0 10px 0; color: #C62828;">Horizonte Temporal 2050 (Mediano Plazo)</h4>
                    <p><b>Aumento de Temperatura Proyectado (ΔT):</b> <code>{proj['temp_change_2050']}</code></p>
                    <p><b>Variación de Precipitación Proyectada (ΔP):</b> <code>{proj['precip_change_2050']}</code></p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("#### 🔍 Impactos Biofísicos Proyectados por el IMN en esta Región:")
        st.write(f"- **Patrón de Estación Seca:** {proj['dry_season_impact']}")
        st.write(f"- **Eventos Hidrometeorológicos Extremos:** {proj['extreme_rain_impact']}")

    # =========================================================================
    # PAGE 6: CATÁLOGO DE BASES DE DATOS
    # =========================================================================
    elif active_page == "ℹ️ Catálogo de Bases de Datos":
        st.markdown("### ℹ️ Catálogo de Bases de Datos y Misiones Satelitales")
        st.markdown(
            """
            Esta aplicación implementa las siguientes fuentes de datos oficiales para el análisis agroambiental en Costa Rica:

            | Base de Datos / Misión | Instrumento / Producto | Parámetro Analizado | Resolución |
            | :--- | :--- | :--- | :--- |
            | **NASA SMAP** | `L2_SM_A/P` (SPL2SMAP) | Humedad volumétrica superficial (0-5 cm) | 9 km / 33 km |
            | **NASA SMAP** | `L4_SM` (SPL4SMGP) | Humedad volumétrica en zona radicular (0-100 cm) y temperatura del suelo capa 1 | 9 km EASE-Grid |
            | **NASA GPM** | `GPM DPR Monthly` (3DPR / IMERG) | Lluvia mensual calibrada por radar Ka/Ku y factor de erosividad pluvial ($R$) | 0.1° (~10 km) |
            | **NASA ECOSTRESS / VIIRS** | `ECO_L4T_ESI` & `ECO2LSTE` | Índice de Estrés Evaporativo ($ET/PET$), humedad cuadriculada y temperatura del suelo ($LST$) | 70 metros |
            | **NASA SRTM** | `SRTMGL1` (Global DEM) | Elevación topográfica, pendiente (%) y factor topográfico $LS$ de erosión | 30 metros (1 arc-sec) |
            | **IMN / MAG Costa Rica** | Cartografía CIA-UCR / IMN | Tipo y orden de suelo, potencial de absorción/infiltración e hidrología | Regionalizada CR |
            | **IMN Costa Rica** | Escenarios Regionales 2030/2050 | Proyecciones climáticas (ΔT, ΔP) por cuenca y región | 6 regiones CR |
            | **NASA POWER** | Agroclimatología (`AG`) | Climatología histórica de temperatura del aire, radiación solar y viento | 0.5° global |
            """
        )


if __name__ == "__main__":
    main()
