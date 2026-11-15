"""Monthly historical screening of drought, water and wind erosion.

Scores are heuristic indices, not event probabilities, storm forecasts or RUSLE
soil-loss estimates. Interannual frequencies refer only to the stated threshold.
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from calendar import monthrange
from statistics import mean
from src.services.nasa_power import MONTH_KEYS, _valid
from src.services.vegetation_index_service import coverage_factor


def seasonal_indices(precip, temperature, wind, slope, cover=0.5):
    # Approximate demand for screening, not FAO-56 reference ET.
    demand = max(40.0, (temperature + 5) * 4.5)
    dryness = max(0.0, min(1.0, 1 - precip / demand))
    drought = round(dryness * 100)
    water = round(min(100, 100 * (precip / 350) * (0.25 + max(0, slope) / 25) * cover))
    aeolian = None if wind is None else round(min(100, 100 * (wind / 5) ** 2 * dryness * cover))
    return drought, water, aeolian, demand


def level(score):
    return "Sin datos" if score is None else "Alto" if score >= 65 else "Moderado" if score >= 35 else "Bajo"


def build_seasonal_alerts(env, months=6, today=None, delta_temp_c=0, delta_precip_pct=0):
    if not 1 <= months <= 12:
        raise ValueError("months must be between 1 and 12")
    if delta_precip_pct < -100:
        raise ValueError("Invalid precipitation scenario")
    today = today or datetime.now(ZoneInfo("America/Costa_Rica")).date()
    power = env["raw_services"]["nasa_power"]
    params = power.get("parameters", {})
    history = env.get("climate_history", {"records": []})
    slope = env["topography_and_erosion"]["slope_percent"]
    vegetation = env.get("vegetation", {}).get("ndvi", {})
    records_ndvi = vegetation.get("records", [])
    rows = []
    for offset in range(1, months + 1):
        idx = today.year * 12 + today.month - 1 + offset
        year, month0 = divmod(idx, 12)
        month = month0 + 1
        key = MONTH_KEYS[month0]
        samples = [r for r in history.get("records", []) if r["month"] == month]
        p = mean(r["precipitation_mm"] for r in samples) if samples else params.get("PRECTOT_MONTHLY", {}).get(key)
        temp = mean(r["temperature_c"] for r in samples) if samples else params.get("T2M", {}).get(key)
        winds = [r["wind_m_s"] for r in samples if r.get("wind_m_s") is not None]
        wind = mean(winds) if winds else params.get("WS2M", {}).get(key)
        ndvi_samples = [r["ndvi"] for r in records_ndvi if int(r["date"][5:7]) == month]
        ndvi = mean(ndvi_samples) if ndvi_samples else None
        cover = coverage_factor(ndvi)
        cover_assumed = cover is None
        cover = 0.5 if cover_assumed else cover
        valid = _valid(p, 0, 10000) and _valid(temp, -60, 65)
        if valid:
            p *= 1 + delta_precip_pct / 100
            temp += delta_temp_c
            drought, water, aeolian, demand = seasonal_indices(p, temp, wind if _valid(wind, 0, 100) else None, slope, cover)
        else:
            drought = water = aeolian = demand = None
        frequencies = {}
        for hazard, position in (("drought", 0), ("water_erosion", 1), ("wind_erosion", 2)):
            scores = [seasonal_indices(r["precipitation_mm"], r["temperature_c"], r.get("wind_m_s"), slope, cover)[position]
                      for r in samples]
            scores = [s for s in scores if s is not None]
            frequencies[hazard] = round(sum(s >= 65 for s in scores) / len(scores) * 100) if len(scores) >= 3 else None
        actions = []
        if drought is not None and drought >= 35:
            actions.append("Conservar rastrojo y revisar reservas de agua y programación de riego.")
        if water is not None and water >= 35:
            actions.append("Mantener cobertura, drenajes y barreras en curvas de nivel.")
        if aeolian is not None and aeolian >= 35:
            actions.append("Evitar suelo desnudo y revisar cortinas rompevientos.")
        rows.append({
            "month": f"{year}-{month:02d}", "month_num": month, "precipitation_mm": round(p, 1) if valid else None,
            "temperature_c": round(temp, 1) if valid else None, "wind_m_s": wind,
            "drought_score": drought, "water_erosion_score": water, "wind_erosion_score": aeolian,
            "drought_level": level(drought), "water_erosion_level": level(water), "wind_erosion_level": level(aeolian),
            "historical_years": len(samples), "historical_high_risk_frequency_pct": frequencies,
            "ndvi": ndvi, "cover_factor": cover, "cover_assumed": cover_assumed,
            "water_demand_proxy_mm": demand, "actions": actions,
            "source": history.get("source") if samples else power.get("source"),
            "period": history.get("period") if samples else power.get("period"),
            "is_simulated": not samples and power.get("is_simulated", True),
        })
    return {"months": rows, "basis": "Patrón histórico estacional; no pronóstico meteorológico.",
            "scenario": {"delta_temp_c": delta_temp_c, "delta_precip_pct": delta_precip_pct},
            "note": "Índices de cribado 0–100. Frecuencia histórica: años con índice >=65; no probabilidad futura. "
                    "Cobertura desconocida usa C=0.5; la pendiente actual es estimada. Validar en finca."}
