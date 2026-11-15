"""
Scientific Term Tooltips System (similar to MSI Afterburner / HWiNFO).
Implements Section 6 of the Project Blueprint (GEMINI.md).
"""

import streamlit as st
from typing import Dict

# Dictionary specified in GEMINI.md
SCIENTIFIC_DICTIONARY: Dict[str, Dict[str, str]] = {
    "Evapotranspiration": {
        "term_es": "Evapotranspiración",
        "category": "Balance Hídrico",
        "definition": "The sum of evaporation from the land surface plus transpiration from plants. It shows how much water is actually leaving the soil.",
        "definition_es": "La suma de la evaporación del suelo más la transpiración vegetal de los cultivos. Indica cuánta agua real está perdiendo el suelo hacia la atmósfera.",
        "sensor": "NASA ECOSTRESS (PT-JPL) & VIIRS"
    },
    "Soil Moisture Anomalies": {
        "term_es": "Anomalías de Humedad del Suelo",
        "category": "Hidrología Satelital",
        "definition": "Deviations from the normal amount of water in the soil for a given time of year. Indicates unexpected droughts or floods.",
        "definition_es": "Desviaciones respecto a la cantidad histórica normal de agua en el suelo para una época del año. Indica sequías repentinas o riesgo de anegamiento.",
        "sensor": "NASA SMAP (L2_SM_A/P & L4_SM)"
    },
    "Water-Balance Indicators": {
        "term_es": "Indicadores de Balance Hídrico",
        "category": "Agroclimatología",
        "definition": "Metrics comparing the water entering the system (rainfall) versus water leaving (evaporation/runoff) to determine if a crop will face water stress.",
        "definition_es": "Métricas que comparan el agua que ingresa al agroecosistema (lluvia) versus el agua que egresa (evaporación/escorrentía) para anticipar estrés hídrico.",
        "sensor": "NASA GPM DPR + ECOSTRESS ESI"
    },
    "Satellite vs. Ground Data": {
        "term_es": "Datos Satelitales vs. Estaciones de Tierra",
        "category": "Fusión Multifuente",
        "definition": "Satellites scan massive areas from space to find broader climate trends, while ground stations measure exact local weather. Combining them gives us the most accurate picture!",
        "definition_es": "Los satélites de la NASA escanean áreas continuas para captar patrones climáticos amplios, mientras las estaciones del IMN miden el clima local exacto. ¡Combinarlos interpola las condiciones más precisas!",
        "sensor": "Fusión NASA Earthdata + IMN Costa Rica"
    }
}


def get_tooltip_css() -> str:
    """
    CSS for hardware-monitor style tooltips (MSI Afterburner / HWiNFO aesthetic).
    """
    return """
    <style>
    /* Tooltip container */
    .scientific-term {
        position: relative;
        display: inline-block;
        border-bottom: 1.5px dotted #FFB300;
        cursor: help;
        font-weight: 600;
        color: #1B5E20;
        transition: color 0.2s ease;
    }
    .scientific-term:hover {
        color: #E65100;
        background-color: rgba(255, 179, 0, 0.12);
        border-radius: 3px;
    }

    /* Tooltip popup box (MSI Afterburner / HWiNFO style) */
    .scientific-term .tooltip-box {
        visibility: hidden;
        opacity: 0;
        width: 320px;
        background: #12161A;
        color: #E0E0E0;
        text-align: left;
        border-radius: 6px;
        padding: 12px 14px;
        position: absolute;
        z-index: 9999;
        bottom: 125%;
        left: 50%;
        margin-left: -160px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45), 0 0 0 1px #2E7D32;
        transition: opacity 0.25s cubic-bezier(0.4, 0, 0.2, 1), transform 0.25s ease;
        transform: translateY(6px);
        pointer-events: none;
        font-size: 12px;
        line-height: 1.45;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
    }

    /* Tooltip arrow */
    .scientific-term .tooltip-box::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -6px;
        border-width: 6px;
        border-style: solid;
        border-color: #12161A transparent transparent transparent;
    }

    /* Hover trigger */
    .scientific-term:hover .tooltip-box {
        visibility: visible;
        opacity: 1;
        transform: translateY(0);
    }

    .tooltip-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #333;
        padding-bottom: 5px;
        margin-bottom: 6px;
    }
    .tooltip-title {
        color: #00E676;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .tooltip-badge {
        background: #FFB300;
        color: #000;
        font-size: 10px;
        font-weight: 800;
        padding: 1px 5px;
        border-radius: 3px;
        text-transform: uppercase;
    }
    .tooltip-body {
        margin: 0;
        color: #ECEFF1;
    }
    .tooltip-sensor {
        margin-top: 6px;
        padding-top: 5px;
        border-top: 1px dashed #263238;
        font-size: 11px;
        color: #90A4AE;
    }
    </style>
    """


def render_term(term_key: str, display_text: str = None) -> str:
    """
    Returns an HTML string that renders the term with hover popup.
    """
    info = SCIENTIFIC_DICTIONARY.get(term_key)
    if not info:
        return display_text or term_key

    text = display_text or term_key
    html = f"""
    <span class="scientific-term">
        {text}
        <div class="tooltip-box">
            <div class="tooltip-header">
                <span class="tooltip-title">🔬 {term_key}</span>
                <span class="tooltip-badge">{info['category']}</span>
            </div>
            <p class="tooltip-body"><b>EN:</b> {info['definition']}</p>
            <p class="tooltip-body" style="margin-top: 4px; color: #CFD8DC;"><b>ES:</b> {info['definition_es']}</p>
            <div class="tooltip-sensor">📡 <i>Fuente: {info['sensor']}</i></div>
        </div>
    </span>
    """
    return html.strip()


def render_glossary_panel():
    """Renders the full educational dictionary panel."""
    st.markdown("### 📖 Diccionario Científico y Glosario Educativo")
    st.markdown(
        "Pase el cursor sobre los términos subrayados para desplegar la explicación interactiva "
        "(sistema inspirado en herramientas de diagnóstico de precisión como *MSI Afterburner* y *HWiNFO*)."
    )

    for term, data in SCIENTIFIC_DICTIONARY.items():
        with st.expander(f"🔬 {term} ({data['term_es']}) — [{data['category']}]", expanded=True):
            st.markdown(f"**Definición oficial:** {data['definition']}")
            st.markdown(f"**Explicación en español:** {data['definition_es']}")
            st.caption(f"🛰️ Misión / Fuente: {data['sensor']}")
