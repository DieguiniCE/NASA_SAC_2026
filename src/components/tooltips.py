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
        "category_en": "Water Balance",
        "definition": "The sum of evaporation from the land surface plus transpiration from plants. It shows how much water is actually leaving the soil.",
        "definition_es": "La suma de la evaporación del suelo más la transpiración vegetal de los cultivos. Indica cuánta agua real está perdiendo el suelo hacia la atmósfera.",
        "sensor": "NASA ECOSTRESS (PT-JPL) & VIIRS"
    },
    "Soil Moisture Anomalies": {
        "term_es": "Anomalías de Humedad del Suelo",
        "category": "Hidrología Satelital",
        "category_en": "Satellite Hydrology",
        "definition": "Deviations from the normal amount of water in the soil for a given time of year. Indicates unexpected droughts or floods.",
        "definition_es": "Desviaciones respecto a la cantidad histórica normal de agua en el suelo para una época del año. Indica sequías repentinas o riesgo de anegamiento.",
        "sensor": "NASA SMAP (L2_SM_A/P & L4_SM)"
    },
    "Water-Balance Indicators": {
        "term_es": "Indicadores de Balance Hídrico",
        "category": "Agroclimatología",
        "category_en": "Agroclimatology",
        "definition": "Metrics comparing the water entering the system (rainfall) versus water leaving (evaporation/runoff) to determine if a crop will face water stress.",
        "definition_es": "Métricas que comparan el agua que ingresa al agroecosistema (lluvia) versus el agua que egresa (evaporación/escorrentía) para anticipar estrés hídrico.",
        "sensor": "NASA GPM DPR + ECOSTRESS ESI"
    },
    "Satellite vs. Ground Data": {
        "term_es": "Datos Satelitales vs. Estaciones de Tierra",
        "category": "Fusión Multifuente",
        "category_en": "Multi-Source Fusion",
        "definition": "Satellites scan massive areas from space to find broader climate trends, while ground stations measure exact local weather. Combining them gives us the most accurate picture!",
        "definition_es": "Los satélites de la NASA escanean áreas continuas para captar patrones climáticos amplios, mientras las estaciones del IMN miden el clima local exacto. ¡Combinarlos interpola las condiciones más precisas!",
        "sensor": "Fusión NASA Earthdata + IMN Costa Rica"
    },
    "NDVI": {
        "term_es": "Índice de Vegetación (NDVI)",
        "category": "Teledetección Óptica",
        "category_en": "Optical Remote Sensing",
        "definition": "Normalized Difference Vegetation Index: measures canopy greenness, density, and photosynthetic vigor by comparing red and near-infrared reflectance.",
        "definition_es": "Índice de Vegetación de Diferencia Normalizada: mide el verdor, densidad foliar y vigor fotosintético comparando la reflectancia en el rojo y el infrarrojo cercano.",
        "sensor": "NASA Landsat 8/9 OLI & MODIS / VIIRS"
    },
    "Frost Risk": {
        "term_es": "Riesgo de Heladas",
        "category": "Agrometeorología Extrema",
        "category_en": "Extreme Agrometeorology",
        "definition": "The probability of land surface temperature dropping below 0-3°C, critical in high-elevation cordilleras (Cerro de la Muerte, Tarrazú, Irazú) damaging coffee or fruit blossoms.",
        "definition_es": "Probabilidad de que la temperatura caiga por debajo de 0-3°C en zonas altas de cordillera (Cerro de la Muerte, Tarrazú, Irazú), congelando tejidos tiernos de café o frutales.",
        "sensor": "NASA ECOSTRESS LST & IMN Red de Altura"
    },
    "Biological Nitrogen Fixation": {
        "term_es": "Fijación Biológica de Nitrógeno",
        "category": "Salud del Suelo & Microbioma",
        "category_en": "Soil Health & Microbiome",
        "definition": "The biological process where leguminous plants symbiotically host Rhizobium bacteria in root nodules, converting atmospheric N2 into plant-available ammonium without synthetic fertilizer.",
        "definition_es": "Proceso biológico donde leguminosas (Canavalia, Frijol, Crotalaria) alojan bacterias Rhizobium en nódulos radiculares, convirtiendo el nitrógeno atmosférico en abono natural.",
        "sensor": "Agroecología Tropical & Modelado de Biomasa GEDI"
    },
    "Harmonized Resolution Grid": {
        "term_es": "Cuadrícula de Análisis Multirresolución",
        "category": "Fusión de Datos Espaciales",
        "category_en": "Spatial Data Fusion",
        "definition": "Resampling and harmonizing satellite datasets with diverse spatial grids (SMAP 9km, GPM 10km, ECOSTRESS 70m, SRTM 30m) into a unified agricultural decision layer.",
        "definition_es": "Remuestreo y armonización de múltiples satélites con resoluciones dispares (SMAP 9km, GPM 10km, ECOSTRESS 70m, SRTM 30m) en una cuadrícula analítica coherente para Costa Rica.",
        "sensor": "NASA Earthdata GIS Fusion Engine"
    }
}


def get_tooltip_css(dark_mode: bool = False) -> str:
    """
    CSS for hardware-monitor style tooltips (MSI Afterburner / HWiNFO aesthetic).
    Strict black font for light mode, white font for dark mode.
    """
    term_color = "#FFFFFF" if dark_mode else "#000000"
    hover_color = "#FFA726" if dark_mode else "#E65100"
    hover_bg = "rgba(255, 179, 0, 0.20)" if dark_mode else "rgba(255, 179, 0, 0.15)"

    return f"""
    <style>
    /* Tooltip container */
    .scientific-term {{
        position: relative;
        display: inline-block;
        border-bottom: 2px dotted #FFB300;
        cursor: help;
        font-weight: 700;
        color: {term_color} !important;
        transition: color 0.2s ease;
    }}
    .scientific-term:hover {{
        color: {hover_color} !important;
        background-color: {hover_bg};
        border-radius: 3px;
    }}

    /* Tooltip popup box (MSI Afterburner / HWiNFO style) */
    .scientific-term .tooltip-box {{
        visibility: hidden;
        opacity: 0;
        width: 320px;
        background: #12161A;
        color: #FFFFFF !important;
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
    }}

    /* Tooltip arrow */
    .scientific-term .tooltip-box::after {{
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -6px;
        border-width: 6px;
        border-style: solid;
        border-color: #12161A transparent transparent transparent;
    }}

    /* Hover trigger */
    .scientific-term:hover .tooltip-box {{
        visibility: visible;
        opacity: 1;
        transform: translateY(0);
    }}

    .tooltip-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #333;
        padding-bottom: 5px;
        margin-bottom: 6px;
    }}
    .tooltip-title {{
        color: #00E676;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .tooltip-badge {{
        background: #FFB300;
        color: #000;
        font-size: 10px;
        font-weight: 800;
        padding: 1px 5px;
        border-radius: 3px;
        text-transform: uppercase;
    }}
    .tooltip-body {{
        margin: 0;
        color: #FFFFFF !important;
    }}
    .tooltip-sensor {{
        margin-top: 6px;
        padding-top: 5px;
        border-top: 1px dashed #263238;
        font-size: 11px;
        color: #B0BEC5 !important;
    }}
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
            <p class="tooltip-body" style="margin-top: 4px; color: #ECEFF1;"><b>ES:</b> {info['definition_es']}</p>
            <div class="tooltip-sensor">📡 <i>Fuente: {info['sensor']}</i></div>
        </div>
    </span>
    """
    return html.strip()


def render_glossary_panel(lang: str = "es"):
    """Renders the full educational dictionary panel."""
    is_es = lang == "es"
    title = "### 📖 Diccionario Científico y Glosario Educativo" if is_es else "### 📖 Scientific Dictionary & Educational Glossary"
    subtitle = (
        "Pase el cursor sobre los términos subrayados para desplegar la explicación interactiva "
        "(sistema inspirado en herramientas de diagnóstico de precisión como *MSI Afterburner* y *HWiNFO*)."
        if is_es else
        "Hover over the underlined terms to reveal the interactive explanation card "
        "(inspired by diagnostic tools like *MSI Afterburner* and *HWiNFO*)."
    )
    st.markdown(title)
    st.markdown(subtitle)

    for term, data in SCIENTIFIC_DICTIONARY.items():
        cat = data["category"] if is_es else data.get("category_en", data["category"])
        expander_title = f"🔬 {term} ({data['term_es']}) — [{cat}]"
        with st.expander(expander_title, expanded=True):
            st.markdown(f"**{'Definición oficial' if is_es else 'Official Definition'}:** {data['definition']}")
            st.markdown(f"**{'Explicación en español' if is_es else 'Spanish Explanation'}:** {data['definition_es']}")
            st.caption(f"🛰️ {'Misión / Fuente' if is_es else 'Mission / Source'}: {data['sensor']}")
