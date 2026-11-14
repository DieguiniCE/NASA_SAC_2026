"""
AgroClima Costa Rica - NASA Space Apps Challenge 2026
Main Application Entrypoint
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
from src.data.costa_rica_locations import find_closest_location, get_all_locations
from src.data.crops_catalog import CROPS_CATALOG, evaluate_crop_suitability
from src.services.nasa_power import fetch_nasa_power_climatology
from src.components.sidebar import render_sidebar
from src.components.map_view import render_costa_rica_map
from src.components.metrics_display import render_climate_metrics
from src.components.charts import create_climadiagram, create_humidity_solar_chart


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
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%);
        color: white;
        padding: 18px 24px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
    }
    .main-header h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: white !important;
    }
    .main-header p {
        margin: 4px 0 0 0;
        font-size: 14px;
        opacity: 0.92;
        color: #E8F5E9 !important;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-top: 6px;
    }
    .status-live {
        background-color: #C8E6C9;
        color: #1B5E20;
        border: 1px solid #81C784;
    }
    .status-sim {
        background-color: #FFF3E0;
        color: #E65100;
        border: 1px solid #FFB74D;
    }
    .card-box {
        background: white;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=3600, show_spinner=False)
def load_agroclima(lat: float, lon: float) -> Dict[str, Any]:
    """Cached wrapper around NASA POWER agroclimatology fetcher."""
    return fetch_nasa_power_climatology(lat, lon)


def main():
    # Render sidebar and retrieve user selections
    active_page, lat, lon, loc_name, show_zones = render_sidebar()

    # Query NASA POWER Agroclimatology data
    with st.spinner("Conectando con la API de NASA POWER..."):
        clima_data = load_agroclima(lat, lon)

    # Detect closest reference location for contextual information
    closest_loc = find_closest_location(lat, lon)
    elev = clima_data.get("elevation_m") or closest_loc.get("elevation_m", 1000)

    # Application Header
    status_class = "status-live" if not clima_data.get("is_simulated") else "status-sim"
    status_icon = "🛰️" if not clima_data.get("is_simulated") else "⚡"
    status_text = clima_data.get("source", "NASA POWER")

    st.markdown(
        f"""
        <div class="main-header">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h1>🌱 {APP_TITLE}</h1>
                    <p>{APP_SUBTITLE} — Evaluación Agroclimática de Cultivos y Cambio Climático</p>
                </div>
                <div>
                    <span class="status-badge {status_class}">
                        {status_icon} {status_text}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # PAGE 1: EXPLORADOR Y MAPA AGROCLIMÁTICO (Página Principal)
    # =========================================================================
    if active_page == "📍 Explorador & Mapa Agroclimático":
        col_map, col_info = st.columns([1.6, 1.0], gap="medium")

        with col_map:
            st.markdown("### 🗺️ Mapa Interactivo de Costa Rica")
            st.caption(
                "💡 **Interacción táctil**: Haga clic o toque cualquier punto del mapa nacional para cambiar la ubicación analizada."
            )

            # Render Folium Map
            clicked_coords = render_costa_rica_map(
                selected_lat=lat,
                selected_lon=lon,
                location_name=loc_name,
                elevation_m=elev,
                show_reference_zones=show_zones,
                map_height=490,
            )

            # If user clicked on the map, update state and trigger rerun
            if clicked_coords:
                c_lat, c_lon = clicked_coords
                # Check if click is a new coordinate (with slight tolerance to prevent loops)
                if abs(c_lat - lat) > 0.005 or abs(c_lon - lon) > 0.005:
                    if CR_LAT_MIN <= c_lat <= CR_LAT_MAX and CR_LON_MIN <= c_lon <= CR_LON_MAX:
                        nearest = find_closest_location(c_lat, c_lon)
                        st.session_state["selected_lat"] = c_lat
                        st.session_state["selected_lon"] = c_lon
                        st.session_state["location_name"] = f"Punto ({c_lat:.3f}, {c_lon:.3f}) próx. a {nearest['canton']}"
                        st.rerun()

        with col_info:
            st.markdown("### 📍 Detalles de la Ubicación")

            st.markdown(
                f"""
                <div class="card-box">
                    <h4 style="margin: 0 0 10px 0; color: #1B5E20;">{loc_name}</h4>
                    <p style="margin: 4px 0;"><b>Coordenadas:</b> Latitud <code>{lat:.4f}° N</code>, Longitud <code>{lon:.4f}° W</code></p>
                    <p style="margin: 4px 0;"><b>Región / Cantón más cercano:</b> {closest_loc['canton']} ({closest_loc['province']})</p>
                    <p style="margin: 4px 0;"><b>Piso Altitudinal Estimado:</b> ~{elev} msnm</p>
                    <p style="margin: 4px 0;"><b>Zona Bioclimática:</b> {closest_loc.get('climate_type', 'Tropical')}</p>
                    <div style="margin-top: 10px;">
                        <span style="font-size: 12px; font-weight: bold; color: #555;">Cultivos Tradicionales en la Zona:</span><br>
                        {''.join(f'<span style="display:inline-block; background:#E8F5E9; color:#2E7D32; padding:2px 8px; border-radius:10px; font-size:11px; margin:2px;">{crop}</span>' for crop in closest_loc.get('primary_crops', []))}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Quick suitability teaser card
            annual_sum = clima_data.get("annual_summary", {})
            t_mean = annual_sum.get("mean_temp_c", 22.0)
            p_ann = annual_sum.get("annual_precipitation_mm", 2000.0)
            rh_mean = annual_sum.get("mean_relative_humidity", 78.0)

            st.markdown("#### ⚡ Diagnóstico Agroclimático Rápido")
            if t_mean < 18.0:
                st.info("❄️ **Zona Fría / Montano**: Ideal para cultivos de altura (Papa, cebolla, café de especialidad, frutales de hoja caduca).")
            elif t_mean <= 24.0:
                st.success("🌤️ **Zona Templada / Valle**: Clima altamente versátil (Café, caña, hortalizas, frutales diversos).")
            else:
                st.warning("🔥 **Zona Cálida / Bajura**: Favorable para cultivos tropicales intensivos (Cacao, banano, piña, caña, palma, arroz).")

            if p_ann < 1500:
                st.markdown("⚠️ **Régimen Hídrico**: Déficit estacional marcado. Requiere considerar disponibilidad de agua o riego.")
            elif p_ann > 3200:
                st.markdown("🌧️ **Régimen Hídrico**: Alta pluviosidad perenne. Vital asegurar drenaje para evitar hongos y anegamiento.")
            else:
                st.markdown("💧 **Régimen Hídrico**: Pluviosidad moderada y bien balanceada para agricultura tropical.")

        # Full-width Metrics Section
        st.markdown("---")
        st.markdown("### 📊 Variables Naturales y Agrometeorológicas (Anuales)")
        render_climate_metrics(clima_data)

        # Interactive Charts Section
        st.markdown("---")
        st.markdown("### 📈 Perfil Climático a lo largo del Año")

        tab_clima, tab_solar, tab_table = st.tabs([
            "🌧️ Walter-Lieth Climadiagrama (Lluvia vs Temperatura)",
            "☀️ Radiación Solar y Humedad Relativa",
            "📋 Tabla de Datos Mensuales"
        ])

        with tab_clima:
            st.plotly_chart(create_climadiagram(clima_data), use_container_width=True)
            st.caption(
                "📌 *El climadiagrama combina la precipitación mensual (barras azules) con la curva de temperatura media (línea naranja). "
                "Permite identificar con precisión los meses secos y los períodos de mayor humedad agropecuaria.*"
            )

        with tab_solar:
            st.plotly_chart(create_humidity_solar_chart(clima_data), use_container_width=True)
            st.caption(
                "📌 *Datos de insolación diaria (ALLSKY_SFC_SW_DWN) y humedad a 2 metros (RH2M) provistos por satélites de NASA.*"
            )

        with tab_table:
            params = clima_data.get("parameters", {})
            month_keys = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
            df_table = pd.DataFrame({
                "Mes": MONTH_NAMES,
                "T° Media (°C)": [params.get("T2M", {}).get(m) for m in month_keys],
                "T° Máxima (°C)": [params.get("T2M_MAX", {}).get(m) for m in month_keys],
                "T° Mínima (°C)": [params.get("T2M_MIN", {}).get(m) for m in month_keys],
                "Lluvia (mm/mes)": [params.get("PRECTOT_MONTHLY", {}).get(m) for m in month_keys],
                "Humedad Rel. (%)": [params.get("RH2M", {}).get(m) for m in month_keys],
                "Radiación (MJ/m²/día)": [params.get("ALLSKY_SFC_SW_DWN", {}).get(m) for m in month_keys],
                "Viento (m/s)": [params.get("WS2M", {}).get(m) for m in month_keys],
            })
            st.dataframe(df_table, use_container_width=True)

            csv_data = df_table.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Serie Climatológica (CSV)",
                data=csv_data,
                file_name=f"nasa_power_cr_{lat:.3f}_{lon:.3f}.csv",
                mime="text/csv",
            )

    # =========================================================================
    # PAGE 2: EVALUACIÓN DE CULTIVOS (BAREBONES / PREVIEW)
    # =========================================================================
    elif active_page == "🌱 Evaluación de Cultivos (Preview)":
        st.markdown("### 🌱 Motor de Evaluación de Idoneidad de Cultivos")
        st.markdown(
            f"Analizando la aptitud para el punto seleccionado: **{loc_name}** "
            f"(Lat: `{lat:.4f}`, Lon: `{lon:.4f}`, Elevación: ~`{elev}` msnm)."
        )

        annual_sum = clima_data.get("annual_summary", {})
        t_mean = annual_sum.get("mean_temp_c", 22.0)
        p_ann = annual_sum.get("annual_precipitation_mm", 2000.0)
        rh_mean = annual_sum.get("mean_relative_humidity", 78.0)

        crop_ids = list(CROPS_CATALOG.keys())
        crop_names = [f"{CROPS_CATALOG[cid]['icon']} {CROPS_CATALOG[cid]['name']}" for cid in crop_ids]

        selected_crop_idx = st.selectbox(
            "Seleccione el cultivo para evaluar en este punto:",
            range(len(crop_ids)),
            format_func=lambda i: crop_names[i],
        )
        selected_crop_id = crop_ids[selected_crop_idx]
        eval_result = evaluate_crop_suitability(selected_crop_id, t_mean, p_ann, rh_mean)
        crop_info = eval_result["crop"]

        c_eval1, c_eval2 = st.columns([1.2, 1.0])

        with c_eval1:
            st.markdown(f"#### Diagnóstico para {crop_info['icon']} **{crop_info['name']}**")

            # Score and Verdict
            badge_color = eval_result["badge_color"]
            st.markdown(
                f"""
                <div style="background-color: #FAFAFA; border: 2px solid {'#4CAF50' if badge_color=='green' else '#2196F3' if badge_color=='blue' else '#FF9800' if badge_color=='orange' else '#F44336'}; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 22px; font-weight: bold; color: #333;">{eval_result['verdict']}</span>
                        <span style="font-size: 26px; font-weight: 800; color: {'#2E7D32' if badge_color=='green' else '#1565C0' if badge_color=='blue' else '#E65100' if badge_color=='orange' else '#C62828'};">{eval_result['score']} / 100</span>
                    </div>
                    <div style="margin-top: 10px;">
                        <div style="background-color: #E0E0E0; border-radius: 6px; height: 12px; width: 100%;">
                            <div style="background-color: {'#4CAF50' if badge_color=='green' else '#2196F3' if badge_color=='blue' else '#FF9800' if badge_color=='orange' else '#F44336'}; height: 12px; border-radius: 6px; width: {eval_result['score']}%;"></div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("##### 🔍 Factores Evaluados:")
            for note in eval_result["notes"]:
                st.write(note)

            st.markdown("##### ⚠️ Vulnerabilidad ante el Cambio Climático:")
            st.warning(crop_info["climate_vulnerability"])

        with c_eval2:
            st.markdown("#### 📋 Ficha Técnica Agroecológica")
            st.markdown(f"**Categoría:** {crop_info['category']}")
            st.write(crop_info["description"])

            st.markdown("##### Rangos Óptimos vs Medidos:")
            t_opt = crop_info["temp_opt"]
            p_opt = crop_info["precip_opt"]
            h_opt = crop_info["humidity_opt"]

            comp_df = pd.DataFrame({
                "Parámetro": ["Temperatura Media", "Precipitación Anual", "Humedad Relativa"],
                "Valor en esta Ubicación": [f"{t_mean:.1f} °C", f"{p_ann:.0f} mm", f"{rh_mean:.1f} %"],
                "Rango Óptimo Cultivo": [f"{t_opt[0]} a {t_opt[1]} °C", f"{p_opt[0]:.0f} a {p_opt[1]:.0f} mm", f"{h_opt[0]:.0f} a {h_opt[1]:.0f} %"],
            })
            st.table(comp_df)

        st.markdown("---")
        st.markdown("### 📊 Matriz Comparativa General de Todos los Cultivos en este Punto")

        all_results = []
        for cid in crop_ids:
            res = evaluate_crop_suitability(cid, t_mean, p_ann, rh_mean)
            c = res["crop"]
            all_results.append({
                "Cultivo": f"{c['icon']} {c['name'].split('(')[0].strip()}",
                "Puntaje de Aptitud": f"{res['score']}%",
                "Veredicto": res["verdict"],
                "T° Óptima (°C)": f"{c['temp_opt'][0]} - {c['temp_opt'][1]}",
                "Lluvia Óptima (mm)": f"{c['precip_opt'][0]:.0f} - {c['precip_opt'][1]:.0f}",
            })

        df_all = pd.DataFrame(all_results)
        st.dataframe(df_all, use_container_width=True)

    # =========================================================================
    # PAGE 3: TENDENCIAS Y CAMBIO CLIMÁTICO (BAREBONES / PREVIEW)
    # =========================================================================
    elif active_page == "📈 Tendencias y Cambio Climático (Preview)":
        st.markdown("### 📈 Tendencias y Vulnerabilidad al Cambio Climático")
        st.info("💡 Este módulo integrará proyecciones a futuro y análisis de anomalías térmicas y de precipitación.")

        c_cc1, c_cc2 = st.columns(2)

        with c_cc1:
            st.markdown("#### 🌡️ Desafíos Climáticos en Costa Rica")
            st.markdown(
                """
                - **Fenómeno ENOS (El Niño / La Niña):**
                  - *El Niño:* Sequía y aumento de temperaturas en la Vertiente del Pacífico (Guanacaste, Valle Central); lluvias intensas en el Caribe.
                  - *La Niña:* Inundaciones y exceso de precipitaciones en el Pacífico y Zona Sur; sequías relativas en el Caribe.
                - **Aumento de Temperaturas Mínimas Nocturnas:**
                  - Afecta la calidad de taza del café arábica al acelerar la maduración del grano y favorecer la esporulación de hongos como la roya (*Hemileia vastatrix*).
                - **Desplazamiento Altitudinal de Zonas de Vida:**
                  - Los pisos térmicos óptimos se desplazan entre 100 y 250 metros hacia arriba, forzando a los productores a adaptar variedades o tecnologías.
                """
            )

        with c_cc2:
            st.markdown("#### 🛡️ Medidas de Adaptación Recomendadas")
            st.markdown(
                """
                1. **Sistemas Agroforestales (SAF):**
                   - Uso de árboles de sombra (Guaba, Plátano, Madero Negro) para amortiguar hasta 3-4°C de temperatura en el dosel.
                2. **Manejo de Suelos y Coberturas Vivas:**
                   - Siembra en curvas de nivel y cobertura de rastrojo para reducir la evaporación del suelo en épocas secas.
                3. **Cosecha de Agua y Riego Eficiente:**
                   - Reservorios en fincas y riego por goteo para mitigar los veranillos prolongados.
                4. **Variedades Resilientes:**
                   - Híbridos F1 de café tolerantes a la roya y con resistencia a sequía.
                """
            )

    # =========================================================================
    # PAGE 4: METODOLOGÍA Y API NASA POWER
    # =========================================================================
    elif active_page == "ℹ️ Metodología y API NASA POWER":
        st.markdown("### ℹ️ Acerca de AgroClima CR y la API de NASA POWER")

        st.markdown(
            """
            Esta aplicación aprovecha los conjuntos de datos abiertos de observación de la Tierra de **NASA POWER**
            *(Prediction of Worldwide Energy Resources)*, diseñados específicamente para apoyar la investigación agrícola,
            la energía solar y la modelación agroclimática global.

            #### 🛰️ Parámetros de Agroclimatología (Comunidad `AG`) utilizados:
            - **`T2M` (Temperature at 2 Meters):** Temperatura media diaria del aire a 2 metros sobre la superficie terrestre (°C).
            - **`T2M_MAX` / `T2M_MIN`:** Temperaturas máximas y mínimas registradas para la evaluación de estrés térmico vegetal.
            - **`PRECTOTCORR` (Precipitation Corrected):** Tasa de precipitación corregida (mm/día) derivada de modelos asimilados de la NASA (MERRA-2 / GEOS).
            - **`RH2M` (Relative Humidity at 2 Meters):** Humedad relativa del aire a 2 metros (%).
            - **`ALLSKY_SFC_SW_DWN`:** Radiación solar global descendente sobre la superficie para estimación de fotosíntesis y evapotranspiración.
            - **`WS2M`:** Velocidad del viento a 2 metros de altura (m/s).

            #### 🔗 Enlace Oficial a la Documentación:
            Consulte la documentación de la API en: [NASA POWER API Documentation](https://power.larc.nasa.gov/api/pages/)

            ---
            *Desarrollado para el NASA Space Apps Challenge 2026. Proyecto enfocado en la resiliencia agroalimentaria de Costa Rica.*
            """
        )


if __name__ == "__main__":
    main()
