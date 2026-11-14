"""Metrics display cards for Agroclimatic conditions."""

import streamlit as st
from typing import Dict, Any


def render_climate_metrics(clima_data: Dict[str, Any]):
    """
    Renders high-level summary cards for the selected location's natural characteristics.
    """
    summary = clima_data.get("annual_summary", {})
    elev = clima_data.get("elevation_m")
    elev_str = f"{elev} msnm" if elev is not None else "N/D"

    temp = summary.get("mean_temp_c", 22.0)
    temp_max = summary.get("max_temp_c", 27.0)
    temp_min = summary.get("min_temp_c", 17.0)
    precip = summary.get("annual_precipitation_mm", 2000.0)
    humidity = summary.get("mean_relative_humidity", 78.0)
    dry_months = summary.get("dry_months_count", 3)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            label="🌡️ Temperatura Media",
            value=f"{temp:.1f} °C",
            delta=f"Mín: {temp_min:.1f}° / Máx: {temp_max:.1f}°",
            delta_color="off"
        )

    with c2:
        st.metric(
            label="🌧️ Precipitación Anual",
            value=f"{precip:,.0f} mm",
            delta=f"{dry_months} meses secos (<60mm)",
            delta_color="normal" if dry_months > 0 else "off"
        )

    with c3:
        st.metric(
            label="💧 Humedad Relativa",
            value=f"{humidity:.1f} %",
            delta="Humedad Media Anual",
            delta_color="off"
        )

    with c4:
        st.metric(
            label="⛰️ Elevación Estimada",
            value=elev_str,
            delta="Piso Altitudinal",
            delta_color="off"
        )
