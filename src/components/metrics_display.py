"""Metrics display cards for Multi-Satellite and IMN Agroclimatic parameters with i18n."""

import streamlit as st
from typing import Dict, Any
from src.i18n import t, lang


def render_climate_metrics(clima_data: Dict[str, Any]):
    """
    Renders multi-parameter summary metrics cards for the unified environmental profile.
    """
    if "temperatures" in clima_data:
        # Unified environmental profile
        t_air = clima_data["temperatures"]["air_temperature_mean_c"]
        t_ground = clima_data["temperatures"]["ground_surface_temperature_c"]
        t_max = clima_data["temperatures"]["air_temperature_max_c"]
        t_min = clima_data["temperatures"]["air_temperature_min_c"]

        rain_mm = clima_data["precipitation"]["gpm_annual_total_mm"]
        rh_air = clima_data["humidity_and_moisture"]["air_relative_humidity_pct"]
        root_sm = clima_data["humidity_and_moisture"]["smap_root_zone_moisture_m3_m3"]
        soil_abs = clima_data["humidity_and_moisture"]["soil_absorption_potential"]

        elev = clima_data["topography_and_erosion"]["elevation_msnm"]
        slope_pct = clima_data["topography_and_erosion"]["slope_percent"]
        erosion_risk = clima_data["topography_and_erosion"]["erosion_risk_level"].split("(")[0].strip()
        erosion_loss = clima_data["topography_and_erosion"]["soil_loss_estimated_ton_ha_yr"]

        soil_order = clima_data["soil"]["order"]

        is_es = lang() == "es"
        min_label = "Mín" if is_es else "Min"
        max_label = "Máx" if is_es else "Max"
        delta_label = "ΔSuelo-Aire" if is_es else "ΔGround-Air"
        slope_label = t("metric_slope")
        peak_label = t("metric_peak")
        sat_label = "NASA POWER Satelital" if is_es else "NASA POWER Satellite"
        abs_label = t("metric_absorption")
        yr_label = "ton/ha/año" if is_es else "ton/ha/yr"

        # Row 1: Temperatures & Topography
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric(
                label=t("metric_air_t"),
                value=f"{t_air:.1f} °C",
                delta=f"{min_label}: {t_min:.1f}° / {max_label}: {t_max:.1f}°",
                delta_color="off"
            )
        with c2:
            st.metric(
                label=t("metric_ground_t"),
                value=f"{t_ground:.1f} °C",
                delta=f"{delta_label}: {t_ground - t_air:+.1f} °C",
                delta_color="normal" if abs(t_ground - t_air) < 3.0 else "inverse"
            )
        with c3:
            st.metric(
                label=t("metric_elevation"),
                value=f"{elev} msnm",
                delta=f"{slope_label}: {slope_pct:.1f}%",
                delta_color="off"
            )
        with c4:
            st.metric(
                label=t("metric_rain"),
                value=f"{rain_mm:,.0f} mm",
                delta=f"{peak_label}: {clima_data['precipitation']['gpm_peak_month']}",
                delta_color="off"
            )

        # Row 2: Moisture, Soil Type & Erosion Risk
        c5, c6, c7, c8 = st.columns(4)
        with c5:
            st.metric(
                label=t("metric_rh"),
                value=f"{rh_air:.1f} %",
                delta=sat_label,
                delta_color="off"
            )
        with c6:
            st.metric(
                label=t("metric_root_sm"),
                value=f"{root_sm:.3f} m³/m³",
                delta=clima_data["humidity_and_moisture"]["smap_root_status"][:22] + "...",
                delta_color="off"
            )
        with c7:
            st.metric(
                label=t("metric_soil_type"),
                value=soil_order,
                delta=f"{abs_label}: {soil_abs}",
                delta_color="off"
            )
        with c8:
            st.metric(
                label=t("metric_erosion"),
                value=erosion_risk,
                delta=f"{erosion_loss:.1f} {yr_label}",
                delta_color="inverse" if "Alto" in erosion_risk or "Crítico" in erosion_risk or "High" in erosion_risk or "Critical" in erosion_risk else "normal"
            )

    else:
        # Fallback for old dictionary
        summary = clima_data.get("annual_summary", {})
        elev = clima_data.get("elevation_m", 1000)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric(t("metric_air_t"), f"{summary.get('mean_temp_c', 22.0):.1f} °C")
        with c2:
            st.metric(t("metric_rain"), f"{summary.get('annual_precipitation_mm', 2000.0):,.0f} mm")
        with c3:
            st.metric(t("metric_rh"), f"{summary.get('mean_relative_humidity', 78.0):.1f} %")
        with c4:
            st.metric(t("metric_elevation"), f"{elev} msnm")
