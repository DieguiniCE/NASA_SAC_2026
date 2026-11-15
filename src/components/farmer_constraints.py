"""Shared farm and scenario controls across all pages."""
import streamlit as st


def render_farmer_constraints():
    with st.expander("Manejo de finca / Farm management"):
        st.checkbox("Riego suplementario disponible / Supplemental irrigation", key="farm_irrigation")
        st.selectbox("Sombra / Shade", ["Sin sombra", "SAF confirmado", "Automática (GEDI orientativo)"],
                     key="farm_shade_mode")
        st.selectbox("Mecanización / Mechanization", ["Manual", "Ligera", "Tractor"], key="farm_mechanization")
        st.caption("Riego: amortiguación supuesta de hasta 70% del déficit. "
                   "Sombra en café: hasta −1.5 °C en el escenario cálido; validar disponibilidad real.")


def render_scenario_controls():
    with st.expander("Simulación climática / Climate what-if"):
        st.slider("Δ Temperatura (°C)", -2.0, 4.0, 0.0, 0.5, key="scenario_temp")
        st.slider("Δ Lluvia (%)", -40, 40, 0, 5, key="scenario_precip")
        st.caption("Se aplica a cultivos, rotaciones y alertas; los datos originales se conservan.")
