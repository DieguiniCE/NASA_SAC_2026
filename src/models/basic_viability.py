"""
Basic Crop Viability Model (Baseline / Placeholder Engine).
NOTE: This is a modular baseline heuristic model designed to be modified and expanded
with machine learning or advanced crop simulation models (e.g., DSSAT, APSIM, MaxEnt)
in subsequent project phases.
"""

from typing import Dict, Any, List
from src.data.crops_catalog import CROPS_CATALOG


# Soil order affinity matrix for standard Costa Rican crops
CROP_SOIL_AFFINITY: Dict[str, Dict[str, float]] = {
    "cafe": {"Andisol": 100.0, "Inceptisol": 90.0, "Ultisol": 65.0, "Alfisol": 70.0, "Vertisol": 20.0, "Entisol": 50.0},
    "cacao": {"Inceptisol": 95.0, "Ultisol": 85.0, "Entisol": 90.0, "Andisol": 75.0, "Alfisol": 60.0, "Vertisol": 30.0},
    "pina": {"Ultisol": 95.0, "Inceptisol": 90.0, "Andisol": 80.0, "Alfisol": 70.0, "Vertisol": 25.0, "Entisol": 60.0},
    "banano_platano": {"Inceptisol": 100.0, "Entisol": 95.0, "Ultisol": 75.0, "Andisol": 80.0, "Alfisol": 70.0, "Vertisol": 35.0},
    "cana_azucar": {"Alfisol": 100.0, "Inceptisol": 90.0, "Vertisol": 85.0, "Andisol": 75.0, "Ultisol": 60.0, "Entisol": 70.0},
    "arroz": {"Vertisol": 100.0, "Alfisol": 95.0, "Inceptisol": 80.0, "Entisol": 75.0, "Ultisol": 60.0, "Andisol": 40.0},
    "papa": {"Andisol": 100.0, "Inceptisol": 70.0, "Ultisol": 30.0, "Alfisol": 20.0, "Vertisol": 10.0, "Entisol": 30.0},
    "yuca": {"Inceptisol": 95.0, "Ultisol": 90.0, "Entisol": 85.0, "Alfisol": 75.0, "Andisol": 80.0, "Vertisol": 30.0},
    "frijol": {"Inceptisol": 95.0, "Alfisol": 90.0, "Andisol": 85.0, "Ultisol": 65.0, "Vertisol": 40.0, "Entisol": 70.0},
}


def calculate_basic_viability(crop_id: str, env_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes a basic multi-criteria viability index (0-100%) for a crop
    using the unified multi-database environmental profile.
    """
    crop = CROPS_CATALOG.get(crop_id)
    if not crop:
        return {"error": "Cultivo no encontrado"}

    limiting_factors: List[str] = []
    positive_factors: List[str] = []

    # 1. Thermal Score (25% weight) - Air & Ground Temp
    air_t = env_profile["temperatures"]["air_temperature_mean_c"]
    ground_t = env_profile["temperatures"]["ground_surface_temperature_c"]
    t_opt_min, t_opt_max = crop["temp_opt"]
    t_tol_min, t_tol_max = crop["temp_tol"]

    if t_opt_min <= air_t <= t_opt_max:
        thermal_score = 100.0
        positive_factors.append(f"Temperatura del aire óptima ({air_t:.1f}°C, ideal: {t_opt_min}-{t_opt_max}°C).")
    elif t_tol_min <= air_t <= t_tol_max:
        thermal_score = 65.0
        limiting_factors.append(f"Temperatura del aire subóptima pero tolerable ({air_t:.1f}°C).")
    else:
        thermal_score = 25.0
        limiting_factors.append(f"Estrés térmico severo ({air_t:.1f}°C fuera del rango {t_tol_min}-{t_tol_max}°C).")

    # Ground temperature check (if ground heats above 34°C, penalty for sensitive roots)
    if ground_t > 33.0 and crop_id in ["papa", "cafe"]:
        thermal_score = max(10.0, thermal_score - 20.0)
        limiting_factors.append(f"Temperatura del suelo elevada ({ground_t:.1f}°C) desfavorece el sistema radicular.")

    # 2. Hydric & Moisture Score (25% weight) - GPM rain + SMAP root moisture + Absorption
    rain_mm = env_profile["precipitation"]["gpm_annual_total_mm"]
    root_sm = env_profile["humidity_and_moisture"]["smap_root_zone_moisture_m3_m3"]
    p_opt_min, p_opt_max = crop["precip_opt"]
    p_tol_min, p_tol_max = crop["precip_tol"]

    if p_opt_min <= rain_mm <= p_opt_max:
        hydric_score = 100.0
        positive_factors.append(f"Precipitación pluvial adecuada ({rain_mm:.0f} mm/año).")
    elif p_tol_min <= rain_mm <= p_tol_max:
        hydric_score = 65.0
        limiting_factors.append(f"Precipitación en límites de tolerancia ({rain_mm:.0f} mm/año).")
    else:
        hydric_score = 25.0
        limiting_factors.append(f"Régimen pluviométrico inadecuado ({rain_mm:.0f} mm/año).")

    # Root zone soil moisture modifier from SMAP L4
    if root_sm < 0.20 and crop_id in ["banano_platano", "cacao"]:
        hydric_score = max(15.0, hydric_score - 20.0)
        limiting_factors.append(f"Déficit en humedad radicular SMAP L4 ({root_sm:.2f} m³/m³).")
    elif root_sm > 0.44 and crop_id in ["yuca", "papa"]:
        hydric_score = max(15.0, hydric_score - 25.0)
        limiting_factors.append(f"Exceso de humedad en raíces SMAP L4 ({root_sm:.2f} m³/m³), riesgo de asfixia o pudrición.")

    # 3. Soil Suitability Score (20% weight) - IMN Soil Order & Absorption
    soil_order = env_profile["soil"]["order"]
    affinities = CROP_SOIL_AFFINITY.get(crop_id, {})
    soil_score = affinities.get(soil_order, 70.0)

    if soil_score >= 90.0:
        positive_factors.append(f"Suelo {soil_order} altamente afín al cultivo.")
    elif soil_score <= 40.0:
        limiting_factors.append(f"Suelo {soil_order} restrictivo para este cultivo.")

    # 4. Topography & Erosion Safety Score (15% weight) - SRTM elevation & slope
    elevation = env_profile["topography_and_erosion"]["elevation_msnm"]
    slope_pct = env_profile["topography_and_erosion"]["slope_percent"]
    e_opt_min, e_opt_max = crop["elevation_opt"]

    topo_score = 100.0
    if not (e_opt_min <= elevation <= e_opt_max):
        diff = min(abs(elevation - e_opt_min), abs(elevation - e_opt_max))
        topo_penalty = min(60.0, (diff / 300.0) * 20.0)
        topo_score -= topo_penalty
        limiting_factors.append(f"Altitud ({elevation} msnm) fuera del piso óptimo ({e_opt_min}-{e_opt_max} msnm).")
    else:
        positive_factors.append(f"Elevación ideal ({elevation} msnm).")

    # Slope & Erosion Risk penalty
    if slope_pct > 30.0:
        topo_score = max(10.0, topo_score - 25.0)
        limiting_factors.append(f"Pendiente pronunciada ({slope_pct:.1f}%), riesgo de erosión acelerada.")

    # 5. Climate Change Resilience Score (15% weight) - IMN Projections
    proj = env_profile["precipitation"]["imn_projections"]
    temp_proj = proj["temp_change_2050"]
    precip_proj = proj["precip_change_2050"]
    cc_score = 75.0  # baseline

    if "-" in precip_proj and crop_id in ["cacao", "banano_platano"]:
        cc_score -= 20.0
        limiting_factors.append(f"Vulnerable a reducción proyectada de lluvias al 2050 ({precip_proj}).")
    elif "+" in temp_proj and crop_id in ["cafe", "papa"]:
        cc_score -= 25.0
        limiting_factors.append(f"Vulnerable al calentamiento regional proyectado al 2050 ({temp_proj}).")
    else:
        positive_factors.append("Resiliencia moderada a alta frente al escenario de cambio climático.")

    # Weighted Overall Score
    overall_score = round(
        (thermal_score * 0.25) +
        (hydric_score * 0.25) +
        (soil_score * 0.20) +
        (topo_score * 0.15) +
        (cc_score * 0.15)
    )

    if overall_score >= 82:
        verdict = "Altamente Viable (Aptitud Óptima)"
        badge_color = "green"
    elif overall_score >= 64:
        verdict = "Viable con Manejo Agronómico"
        badge_color = "blue"
    elif overall_score >= 45:
        verdict = "Viabilidad Marginal / Riesgo Elevado"
        badge_color = "orange"
    else:
        verdict = "No Recomendado (Incompatible)"
        badge_color = "red"

    return {
        "crop_id": crop_id,
        "crop_name": crop["name"],
        "crop_icon": crop["icon"],
        "overall_score": overall_score,
        "verdict": verdict,
        "badge_color": badge_color,
        "score_breakdown": {
            "Térmico (Aire y Suelo)": round(thermal_score),
            "Hídrico (Lluvia y Raíces)": round(hydric_score),
            "Edafológico (Suelo y Absorción)": round(soil_score),
            "Topográfico y Erosión": round(topo_score),
            "Resiliencia Climática (2050)": round(cc_score),
        },
        "positive_factors": positive_factors,
        "limiting_factors": limiting_factors,
        "model_version": "v0.1-super-basic-heuristic",
    }
