"""
Bilingual translation system (Spanish / English) for AgroClima CR.
Usage:
    from src.i18n import t
    st.markdown(t("page_analyze"))
"""

import streamlit as st

TRANSLATIONS = {
    # ── App-wide ─────────────────────────────────────────────────────────────
    "app_title":        {"es": "AgroClima CR | NASA Space Apps",
                         "en": "AgroClima CR | NASA Space Apps"},
    "app_subtitle":     {"es": "Explorador de Viabilidad Agroclimática · Costa Rica",
                         "en": "Agro-Climatic Crop Suitability Explorer · Costa Rica"},
    "data_fusion_notice": {
        "es": "Los satélites de la NASA brindan cobertura continua; las estaciones del IMN aportan precisión local. "
              "La fusión de ambas fuentes produce el perfil ambiental más exacto para cada coordenada de Costa Rica.",
        "en": "NASA satellites provide continuous coverage; IMN ground stations add local precision. "
              "Fusing both sources produces the most accurate environmental profile for each Costa Rica coordinate."},
    "tooltip_hint":     {"es": "(Pase el cursor sobre el texto subrayado para ver la ficha explicativa flotante).",
                         "en": "(Hover over the underlined text to see the floating info card)."},

    # ── Sidebar ───────────────────────────────────────────────────────────────
    "nav_label":        {"es": "Navegación", "en": "Navigation"},
    "location_label":   {"es": "Ubicación",  "en": "Location"},
    "method_label":     {"es": "Método:",    "en": "Method:"},
    "map_click":        {"es": "🗺️ Clic en el mapa",        "en": "🗺️ Click on map"},
    "canton_select":    {"es": "🏙️ Seleccionar Cantón",     "en": "🏙️ Select Canton"},
    "text_search":      {"es": "✍️ Buscar localidad",        "en": "✍️ Search location"},
    "manual_coords":    {"es": "📐 Coordenadas manuales",    "en": "📐 Manual coordinates"},
    "set_location_btn": {"es": "📍 Fijar Ubicación",         "en": "📍 Set Location"},
    "search_placeholder":{"es":"Tarrazú, Guápiles, Turrialba...",
                          "en":"Tarrazú, Guápiles, Turrialba..."},
    "no_results":       {"es": "Sin resultados. Use coordenadas manuales.",
                         "en": "No results. Try manual coordinates."},
    "lat_label":        {"es": "Latitud (8.0°–11.3°):",      "en": "Latitude (8.0°–11.3°):"},
    "lon_label":        {"es": "Longitud (-86.0°–-82.5°):",  "en": "Longitude (-86.0°–-82.5°):"},
    "update_coords":    {"es": "Actualizar",                  "en": "Update"},
    "click_hint":       {"es": "💡 Haga clic en cualquier punto del mapa para seleccionarlo.",
                         "en": "💡 Click anywhere on the map to select it."},
    "show_zones":       {"es": "Mostrar regiones de referencia",
                         "en": "Show reference regions"},
    "active_location":  {"es": "📍 Ubicación Activa",    "en": "📍 Active Location"},
    "databases_label":  {"es": "Bases de Datos Integradas", "en": "Integrated Databases"},
    "language_toggle":  {"es": "🌐 Idioma / Language",    "en": "🌐 Idioma / Language"},
    "dark_mode_toggle": {"es": "🌙 Modo Oscuro",          "en": "🌙 Dark Mode"},

    # ── Page names ────────────────────────────────────────────────────────────
    "page_analyze":     {"es": "🗺️ Analizar Ubicación",       "en": "🗺️ Analyze Location"},
    "page_crops":       {"es": "🌾 Fichas de Cultivo",         "en": "🌾 Crop Profiles"},
    "page_rotation":    {"es": "🔄 Rotación de Cultivos",      "en": "🔄 Crop Rotation"},
    "page_science":     {"es": "🔬 Datos Científicos",         "en": "🔬 Scientific Data"},

    # ── Page 1: Analyze ───────────────────────────────────────────────────────
    "map_title":        {"es": "🗺️ Mapa Interactivo de Costa Rica",
                         "en": "🗺️ Interactive Map of Costa Rica"},
    "map_caption":      {"es": "Toque o haga clic en cualquier punto para colocar el pin y recalcular la viabilidad.",
                         "en": "Tap or click any point to place a pin and recalculate viability."},
    "cards_title":      {"es": "🌾 Viabilidad de los 5 Cultivos",
                         "en": "🌾 Viability of the 5 Crops"},
    "soil_label":       {"es": "Suelo",    "en": "Soil"},
    "params_title":     {"es": "📊 Parámetros Físicos del Punto",
                         "en": "📊 Physical Parameters at Point"},

    # ── Page 2: Crop Profiles ─────────────────────────────────────────────────
    "how_it_works":     {"es": "📐 ¿Cómo funciona el modelo? — Fórmula del Sensitivity Score",
                         "en": "📐 How does the model work? — Sensitivity Score Formula"},
    "select_crop":      {"es": "Seleccione el cultivo:",    "en": "Select crop:"},
    "viability_pct":    {"es": "Porcentaje de Viabilidad",  "en": "Viability Percentage"},
    "composite_s":      {"es": "Composite S",               "en": "Composite S"},
    "sensitivity_title":{"es": "Sensitivity Sub-Scores (S = k / rango)",
                         "en": "Sensitivity Sub-Scores (S = k / range)"},
    "agro_req_title":   {"es": "Requerimientos Agronómicos", "en": "Agronomic Requirements"},
    "watering_label":   {"es": "💧 Necesidades de Riego",   "en": "💧 Watering Needs"},
    "soil_rec_label":   {"es": "🪨 Suelos Recomendados",    "en": "🪨 Recommended Soils"},
    "tolerable_t_label":{"es": "🌡️ Rango Tolerable T°",    "en": "🌡️ Tolerable T° Range"},
    "deltas_title":     {"es": "📊 Deltas y Penalizaciones", "en": "📊 Deltas & Penalties"},
    "param_col":        {"es": "Parámetro",   "en": "Parameter"},
    "actual_col":       {"es": "Actual",      "en": "Actual"},
    "sweet_col":        {"es": "Sweet Spot",  "en": "Sweet Spot"},
    "delta_col":        {"es": "Δ",           "en": "Δ"},
    "points_col":       {"es": "−Puntos",     "en": "−Points"},
    "matrix_title":     {"es": "📋 Matriz Comparativa — Todos los Cultivos",
                         "en": "📋 Comparative Matrix — All Crops"},
    "viability_col":    {"es": "Viabilidad",  "en": "Viability"},
    "diagnosis_col":    {"es": "Diagnóstico", "en": "Diagnosis"},

    # ── Status strings ────────────────────────────────────────────────────────
    "status_high":      {"es": "Viabilidad Alta",     "en": "High Viability"},
    "status_moderate":  {"es": "Viabilidad Moderada", "en": "Moderate Viability"},
    "status_marginal":  {"es": "Viabilidad Marginal", "en": "Marginal Viability"},
    "status_none":      {"es": "No Viable",           "en": "Not Viable"},

    # ── Page 3: Rotation ──────────────────────────────────────────────────────
    "rotation_title":   {"es": "🔄 Exploración de Rotación de Cultivos — Decisión Agroecológica",
                         "en": "🔄 Crop Rotation Strategy Explorer — Agroecological Decision Tool"},
    "rotation_intro":   {
        "es": "Esta herramienta combina observaciones de la NASA (SMAP, ECOSTRESS, GPM, SRTM, Landsat) y del IMN "
              "para comparar al menos tres estrategias rotacionales frente al monocultivo continuo, evaluando la "
              "regeneración del suelo, el corte biológico de plagas, la retención hídrica y las prioridades del productor.",
        "en": "This tool synthesizes NASA Earth observations (SMAP, ECOSTRESS, GPM, SRTM, Landsat) and IMN data "
              "to compare at least three rotation strategies against continuous monoculture, assessing soil health, "
              "pest disruption, water retention, and farmer priorities."},
    "rotation_disclaimer": {
        "es": "ℹ️ <b>Herramienta de Apoyo a la Decisión:</b> Esta plataforma está diseñada para identificar patrones "
              "y oportunidades agroecológicas, <u>no para reemplazar</u> el criterio tradicional del productor, sus observaciones "
              "de campo o la asesoría de extensionistas agrícolas locales (MAG / INTA / ICAFE / CORBANA / LAICA).",
        "en": "ℹ️ <b>Decision-Support Tool:</b> This platform is designed to identify agroecological patterns "
              "and possibilities, <u>not to replace</u> farmer judgment, local field knowledge, or in-situ agronomic "
              "extension services (MAG / INTA / ICAFE / CORBANA / LAICA)."},
    "rotation_select_primary": {"es": "Seleccione el Cultivo Principal para la Rotación:",
                                "en": "Select Primary Crop for Rotation Analysis:"},
    "rotation_priority_title": {"es": "🎯 Prioridad Principal del Productor:",
                                "en": "🎯 Farmer Primary Goal & Priorities:"},
    "priority_balanced": {"es": "⚖️ Enfoque Equilibrado (Sostenibilidad Global)", "en": "⚖️ Balanced Holistic Approach"},
    "priority_soil":     {"es": "🌱 Regenerar Suelo & Fijar Nitrógeno",          "en": "🌱 Soil Health & Nitrogen Fixation"},
    "priority_water":    {"es": "💧 Ahorro Hídrico & Resiliencia a Sequía",       "en": "💧 Water Conservation & Drought Resilience"},
    "priority_income":   {"es": "💰 Ingresos Suplementarios & Mercado",           "en": "💰 Supplemental Income & Cash Flow"},
    "priority_pest":     {"es": "🛡️ Control Biológico de Plagas & Nemátodos",    "en": "🛡️ Biological Pest & Nematode Disruption"},
    "priority_erosion":  {"es": "⛰️ Protección Antierosión en Laderas",           "en": "⛰️ Slope Erosion Mitigation"},
    "concept_title":       {"es": "📖 ¿En qué consiste esta Estrategia?",
                            "en": "📖 What does this Strategy Consist Of?"},
    "why_suggested_title": {"es": "💡 Por qué se sugiere esta Estrategia",
                            "en": "💡 Why this Strategy was Suggested"},
    "evidence_title":      {"es": "🛰️ Evidencia Satelital & Terrestre (NASA + IMN)",
                            "en": "🛰️ Earth Observation Evidence (NASA + IMN)"},
    "benefits_title":      {"es": "🌟 Beneficios Agronómicos & Ambientales",
                            "en": "🌟 Agronomic & Environmental Benefits"},
    "gaps_title":          {"es": "🔍 Vacíos de Información & Incertidumbre",
                            "en": "🔍 Information Gaps & Uncertainty"},
    "farmer_review_title": {"es": "⚠️ Aspectos Críticos para Revisión del Productor",
                            "en": "⚠️ Critical Points for Local Farmer Review"},
    "simulation_title":    {"es": "🧪 Simulador de Escenarios Climáticos (What-If)",
                            "en": "🧪 Climate Scenario Simulator (What-If Analysis)"},
    "timeline_title":      {"es": "📅 Calendario Agroclimático & Transiciones de Suelo Desnudo (12 Meses)",
                            "en": "📅 12-Month Agro-Climatic Calendar & Bare-Soil Transitions"},
    "strategy_comparison_title": {"es": "📊 Comparativa de las Estrategias para este Cultivo",
                                  "en": "📊 Strategy Comparison for this Crop"},
    "top_recommended_badge": {"es": "🏆 ESTRATEGIA ÓPTIMA RECOMENDADA", "en": "🏆 TOP RECOMMENDED STRATEGY"},
    "baseline_badge":        {"es": "📊 LÍNEA BASE (MONOCULTIVO)",       "en": "📊 BASELINE (MONOCULTURE)"},
    "rotation_schedule_title": {"es": "📅 Secuencia y Prácticas del Esquema",
                                "en": "📅 Sequence and Agronomic Practices"},
    "rotation_partner_title":  {"es": "🌱 Especies Rotacionales & Coberturas Utilizadas",
                                "en": "🌱 Rotational Crops & Cover Species Used"},
    "rotation_viability_title":{"es": "Viabilidad del Sistema",
                                "en": "System Viability"},
    "year_label":       {"es": "Período / Fase", "en": "Period / Phase"},
    "crop_label":       {"es": "Cultivo", "en": "Crop"},
    "benefit_label":    {"es": "Beneficio Principal", "en": "Main Benefit"},

    # ── Page 4: Science tabs ──────────────────────────────────────────────────
    "tab_satellites":   {"es": "🛰️ Sensores Satelitales", "en": "🛰️ Satellite Sensors"},
    "tab_soil":         {"es": "🪨 Suelos & Erosión",      "en": "🪨 Soil & Erosion"},
    "tab_climate":      {"es": "📈 Proyecciones Climáticas","en": "📈 Climate Projections"},
    "tab_glossary":     {"es": "📖 Glosario Científico",   "en": "📖 Scientific Glossary"},
    "sat_title":        {"es": "🛰️ Parámetros Satelitales", "en": "🛰️ Satellite Parameters"},
    "smap_title":       {"es": "🛰️ NASA SMAP — Humedad del Suelo",
                         "en": "🛰️ NASA SMAP — Soil Moisture"},
    "eco_title":        {"es": "🌿 NASA ECOSTRESS / VIIRS — Estrés Evaporativo & Temperatura",
                         "en": "🌿 NASA ECOSTRESS / VIIRS — Evaporative Stress & Temperature"},
    "gpm_title":        {"es": "🌧️ NASA GPM DPR Monthly — Precipitación por Radar",
                         "en": "🌧️ NASA GPM DPR Monthly — Radar Precipitation"},
    "srtm_title":       {"es": "⛰️ NASA SRTM 30m Global — Topografía Digital",
                         "en": "⛰️ NASA SRTM 30m Global — Digital Topography"},
    "soil_tab_title":   {"es": "🪨 Suelos de Costa Rica — IMN / MAG / CIA-UCR",
                         "en": "🪨 Costa Rica Soils — IMN / MAG / CIA-UCR"},
    "erosion_title":    {"es": "🛡️ Riesgo de Erosión Hídrica — Modelo RUSLE",
                         "en": "🛡️ Water Erosion Risk — RUSLE Model"},
    "erosion_level_label":{"es": "Nivel de Riesgo",    "en": "Risk Level"},
    "soil_loss_label":  {"es": "Pérdida de Suelo Estimada", "en": "Estimated Soil Loss"},
    "recommendation_label":{"es": "Recomendación",     "en": "Recommendation"},
    "topo_title":       {"es": "Factores Topográficos", "en": "Topographic Factors"},
    "climate_tab_title":{"es": "📈 Proyecciones de Cambio Climático — IMN Costa Rica",
                         "en": "📈 Climate Change Projections — IMN Costa Rica"},
    "met_region_label": {"es": "Región Meteorológica", "en": "Meteorological Region"},
    "scenario_2030":    {"es": "📅 Escenario 2030",    "en": "📅 Scenario 2030"},
    "scenario_2050":    {"es": "📅 Escenario 2050",    "en": "📅 Scenario 2050"},
    "short_term":       {"es": "Corto Plazo",          "en": "Short Term"},
    "medium_term":      {"es": "Mediano Plazo",         "en": "Medium Term"},
    "delta_t_label":    {"es": "Aumento de Temperatura (ΔT)", "en": "Temperature Increase (ΔT)"},
    "delta_p_label":    {"es": "Variación Precipitación (ΔP)","en": "Precipitation Change (ΔP)"},
    "regional_challenges":{"es": "⚠️ Desafíos Climáticos Regionales",
                           "en": "⚠️ Regional Climate Challenges"},
    "dry_season_label": {"es": "☀️ Impacto Estación Seca","en": "☀️ Dry Season Impact"},
    "extreme_rain_label":{"es": "🌧️ Lluvias Extremas",   "en": "🌧️ Extreme Rainfall"},
    "missions_title":   {"es": "🛰️ Resumen de Misiones y Productos",
                         "en": "🛰️ Missions & Products Summary"},
    "mission_col":      {"es": "Misión / Base de Datos", "en": "Mission / Database"},
    "product_col":      {"es": "Producto",   "en": "Product"},
    "param_model_col":  {"es": "Parámetro en el Modelo", "en": "Model Parameter"},

    # ── Chart labels ──────────────────────────────────────────────────────────
    "chart_rain":       {"es": "Lluvia GPM / POWER (mm)",   "en": "GPM / POWER Rainfall (mm)"},
    "chart_temp_range": {"es": "Rango T° Mín-Máx",          "en": "Min-Max T° Range"},
    "chart_temp_mean":  {"es": "Temperatura Media (°C)",     "en": "Mean Temperature (°C)"},
    "chart_precip_y":   {"es": "Precipitación (mm / mes)",   "en": "Precipitation (mm / month)"},
    "chart_temp_y":     {"es": "Temperatura (°C)",           "en": "Temperature (°C)"},
    "chart_clima_title":{"es": "Perfil Agrometeorológico Mensual (NASA POWER & GPM DPR)",
                         "en": "Monthly Agrometeorological Profile (NASA POWER & GPM DPR)"},
    "chart_smap_title": {"es": "Humedad del Suelo: Superficie vs. Zona Radicular (NASA SMAP)",
                         "en": "Soil Moisture: Surface vs. Root Zone (NASA SMAP)"},
    "chart_smap_x1":    {"es": "SMAP L2 Superficie (0-5cm)", "en": "SMAP L2 Surface (0-5cm)"},
    "chart_smap_x2":    {"es": "SMAP L4 Zona Radicular (0-100cm)", "en": "SMAP L4 Root Zone (0-100cm)"},
    "chart_smap_y":     {"es": "Contenido Volumétrico de Agua (m³/m³)",
                         "en": "Volumetric Water Content (m³/m³)"},
    "chart_thermo_title":{"es": "Termometría: Temperatura del Aire vs. Suelo",
                          "en": "Thermometry: Air vs. Ground Temperature"},
    "chart_t_min":      {"es": "T° Mínima Aire",             "en": "Min Air T°"},
    "chart_t_mean":     {"es": "T° Media Aire (POWER)",      "en": "Mean Air T° (POWER)"},
    "chart_t_ground":   {"es": "T° Suelo / LST (ECOSTRESS)", "en": "Ground T° / LST (ECOSTRESS)"},
    "chart_t_max":      {"es": "T° Máxima Aire",             "en": "Max Air T°"},
    "chart_viab_title": {"es": "Comparativa de Viabilidad — 5 Cultivos",
                         "en": "Viability Comparison — 5 Crops"},
    "chart_viab_x":     {"es": "Porcentaje de Viabilidad (%)", "en": "Viability Percentage (%)"},
    "chart_delta_title":{"es": "Actual vs. Sweet Spot",      "en": "Actual vs. Sweet Spot"},
    "chart_sweet_label":{"es": "Sweet Spot (Ideal)",         "en": "Sweet Spot (Ideal)"},
    "chart_actual_label":{"es":"Valor Actual",               "en": "Actual Value"},
    "chart_delta_y":    {"es": "Valor (escala normalizada)", "en": "Value (normalized scale)"},
    "chart_rotation_title":{"es": "Viabilidad de Rotación de Cultivos",
                            "en": "Crop Rotation Viability"},
    "chart_rotation_x": {"es": "Cultivo Rotacional",         "en": "Rotation Crop"},
    "chart_rotation_y": {"es": "Viabilidad de la Rotación (%)", "en": "Rotation Viability (%)"},
    "chart_mono_vs_rot":{"es": "Rotación vs. Monocultivo",  "en": "Rotation vs. Monoculture"},

    # ── Metric labels ─────────────────────────────────────────────────────────
    "metric_air_t":     {"es": "🌡️ Temperatura del Aire",      "en": "🌡️ Air Temperature"},
    "metric_ground_t":  {"es": "🌱 Temp. del Suelo (LST / SMAP)","en": "🌱 Ground Temp. (LST / SMAP)"},
    "metric_elevation": {"es": "⛰️ Elevación (SRTM 30m)",       "en": "⛰️ Elevation (SRTM 30m)"},
    "metric_rain":      {"es": "🌧️ Precipitación (GPM Radar)",  "en": "🌧️ Precipitation (GPM Radar)"},
    "metric_rh":        {"es": "💧 Humedad Aire (RH2M)",         "en": "💧 Air Humidity (RH2M)"},
    "metric_root_sm":   {"es": "🌿 Humedad Raíces (SMAP L4)",   "en": "🌿 Root Moisture (SMAP L4)"},
    "metric_soil_type": {"es": "🪨 Tipo de Suelo (IMN / MAG)",  "en": "🪨 Soil Type (IMN / MAG)"},
    "metric_erosion":   {"es": "🛡️ Riesgo de Erosión (RUSLE)", "en": "🛡️ Erosion Risk (RUSLE)"},
    "metric_slope":     {"es": "Pendiente",  "en": "Slope"},
    "metric_peak":      {"es": "Pico",       "en": "Peak"},
    "metric_absorption":{"es": "Absorción",  "en": "Absorption"},
}


def t(key: str) -> str:
    """Return the translated string for the current language in session state."""
    lang = st.session_state.get("lang", "es")
    entry = TRANSLATIONS.get(key, {})
    return entry.get(lang, entry.get("es", key))


def lang() -> str:
    """Return current language code ('es' or 'en')."""
    return st.session_state.get("lang", "es")
