"""Seasonal alerts, provenance, MODIS/GEDI and field validation UI."""
import pandas as pd
import streamlit as st
from src.services.seasonal_risk_service import build_seasonal_alerts
from src.models.sensitivity_viability_model import SensitivityViabilityModel


def render_risk_panel(env, delta_temp=0, delta_precip=0):
    report = build_seasonal_alerts(env, delta_temp_c=delta_temp, delta_precip_pct=delta_precip)
    high = [row for row in report["months"] if any(
        row[key] is not None and row[key] >= 65 for key in
        ("drought_score", "water_erosion_score", "wind_erosion_score"))]
    if high:
        names = {"drought_score": "sequía", "water_erosion_score": "erosión hídrica", "wind_erosion_score": "erosión eólica"}
        summary = ["{}: {}".format(row["month"], ", ".join(name for key, name in names.items()
                    if row[key] is not None and row[key] >= 65)) for row in high]
        st.warning("Riesgo estacional alto en meses siguientes · " + " · ".join(summary))
    with st.expander("Alertas de los próximos 6 meses / Seasonal alerts", expanded=bool(high)):
        st.caption(report["basis"])
        st.dataframe(pd.DataFrame([{
            "Mes": r["month"], "Lluvia (mm)": r["precipitation_mm"],
            "Sequía": r["drought_level"], "Erosión hídrica": r["water_erosion_level"],
            "Erosión eólica": r["wind_erosion_level"], "Años históricos": r["historical_years"],
            "Cobertura": "Supuesto C=0.5" if r["cover_assumed"] else "NDVI histórico",
        } for r in report["months"]]), hide_index=True, use_container_width=True)
        st.caption(report["note"])
        for row in report["months"]:
            if row["actions"]:
                st.write(f"**{row['month']}:** " + " ".join(row["actions"]))
        st.caption("Fuente: " + str(report["months"][0]["source"]) + " · " + str(report["months"][0]["period"]))
        if any(row["is_simulated"] for row in report["months"]):
            st.warning("Parte del panel usa climatología regional simulada por falta de datos históricos.")
        st.download_button("Descargar alertas (CSV)", pd.DataFrame(report["months"]).to_csv(index=False),
                           "alertas_estacionales.csv", "text/csv")
    with st.expander("Heladas, vegetación y validaciones en finca"):
        frost = env["frost_risk"]
        st.write(f"**Frío / heladas:** {frost['level']} · mínima climatológica {frost['adjusted_min_c']} °C")
        st.caption(frost["note"])
        vegetation = env["vegetation"]
        ndvi = vegetation["ndvi"]
        if ndvi["records"]:
            frame = pd.DataFrame(ndvi["records"]).set_index("date")
            st.line_chart(frame[["ndvi"]])
            exposed = [r["date"] for r in ndvi["records"] if r["exposed_soil_risk"]]
            if exposed:
                st.warning("NDVI < 0.25: posible suelo expuesto en " + ", ".join(exposed))
            st.caption(ndvi["note"] + " Último mes observado: " + ndvi["latest_date"])
        else:
            st.info("NDVI no disponible. No se infiere suelo desnudo sin observaciones.")
        canopy = vegetation["canopy"]
        if canopy["status"] == "available":
            st.write(f"**GEDI:** altura RH98 {canopy['rh98_m']:.1f} m · biomasa {canopy['agbd_mg_ha']:.1f} Mg/ha.")
            st.caption(str(canopy["observation_date"]) + " · " + canopy["note"])
        else:
            st.info("GEDI no disponible: no se aplica sombreado automático.")
        st.write("**Validaciones obligatorias en finca**")
        for item in SensitivityViabilityModel.VALIDATIONS:
            st.write("• " + item)
