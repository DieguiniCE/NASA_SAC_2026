"""NASA POWER API Client for Agroclimatological Data."""

import requests
import json
from typing import Dict, Any, Optional
import math
from src.config import (
    NASA_POWER_BASE_URL,
    NASA_POWER_COMMUNITY,
    NASA_PARAMETERS,
    MONTH_NAMES,
    MONTH_DAYS
)
from src.data.costa_rica_locations import find_closest_location


def _generate_synthetic_cr_climatology(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fallback agroclimate generator calibrated for Costa Rica's microclimates
    (Pacific dry, Central Valley, Caribbean moist, and Montane zones)
    when network access to NASA servers is blocked or unavailable.
    """
    closest = find_closest_location(lat, lon)
    elev = closest.get("elevation_m", 1000)

    # Base temperature determined by elevation lapse rate (~6.5°C per 1000m)
    # Sea-level base temp ~27.5°C
    sea_level_temp = 27.5
    base_t2m = max(10.0, sea_level_temp - (elev * 0.0062))

    # Rainfall pattern:
    # Pacific / Guanacaste (lon < -85.0): Distinct dry season Dec-Apr, total ~1600mm
    # Caribbean: Wet year-round, total ~3200mm
    # Central Valley / Pacific Montane (Tarrazú, Cartago, San José): ~1800-2200mm, dry Dec-Apr
    is_guanacaste = (lon < -85.0) and (lat > 9.8)
    is_caribbean = (lat >= 10.0 and lon >= -84.2) or (lat < 10.0 and lon >= -83.6)

    monthly_t2m = {}
    monthly_t2m_max = {}
    monthly_t2m_min = {}
    monthly_precip_daily = {}  # mm/day
    monthly_precip_total = {}  # mm/month
    monthly_rh = {}
    monthly_solar = {}
    monthly_wind = {}

    annual_precip_sum = 0.0

    for i, month in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]):
        days = MONTH_DAYS[i]
        # Slight seasonal variation in temperature (March-April warmest in CR)
        temp_offset = math.sin((i - 1) / 12 * 2 * math.pi) * 1.2
        t_mean = round(base_t2m + temp_offset, 2)
        t_max = round(t_mean + 4.5, 2)
        t_min = round(t_mean - 4.5, 2)

        # Precipitation pattern
        if is_guanacaste:
            # Harsh dry season Jan-Apr (<20mm/month)
            if i in [0, 1, 2, 3]:  # Jan-Apr
                p_day = 0.3 + 0.1 * i
                rh = 62.0 - i * 2.0
            else:
                p_day = 6.5 + math.sin((i - 4) / 7 * math.pi) * 3.5
                rh = 82.0 + math.sin((i - 4) / 7 * math.pi) * 4.0
        elif is_caribbean:
            # Wet year-round with slight dry period in Sep-Oct
            if i in [8, 9]:  # Sep-Oct veranillo
                p_day = 5.0
                rh = 83.0
            else:
                p_day = 9.0 + math.sin(i / 12 * 2 * math.pi) * 2.5
                rh = 88.0
        else:
            # Valle Central / General: dry Dec-Apr, wet May-Nov
            if i in [0, 1, 2]:
                p_day = 0.8
                rh = 68.0
            elif i == 3:
                p_day = 2.5
                rh = 72.0
            elif i in [8, 9]:  # Sep-Oct peak rain
                p_day = 11.5
                rh = 88.0
            else:
                p_day = 7.0
                rh = 82.0

        p_total = round(p_day * days, 1)
        annual_precip_sum += p_total

        monthly_t2m[month] = t_mean
        monthly_t2m_max[month] = t_max
        monthly_t2m_min[month] = t_min
        monthly_precip_daily[month] = round(p_day, 2)
        monthly_precip_total[month] = p_total
        monthly_rh[month] = round(rh, 1)
        monthly_solar[month] = round(16.5 + math.cos(i / 12 * 2 * math.pi) * 2.5, 2)
        monthly_wind[month] = round(2.8 + (1.5 if i in [0, 1, 2] else 0.0), 2)

    # Annual averages
    monthly_t2m["ANN"] = round(sum(monthly_t2m[m] for m in ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]) / 12, 2)
    monthly_t2m_max["ANN"] = round(sum(monthly_t2m_max[m] for m in ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]) / 12, 2)
    monthly_t2m_min["ANN"] = round(sum(monthly_t2m_min[m] for m in ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]) / 12, 2)
    monthly_rh["ANN"] = round(sum(monthly_rh[m] for m in ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]) / 12, 1)
    monthly_precip_daily["ANN"] = round(annual_precip_sum / 365, 2)

    return {
        "is_simulated": True,
        "source": "Modelo Agroclimático Costa Rica (Calibración Holdridge / Local)",
        "elevation_m": elev,
        "closest_known_place": closest["name"],
        "parameters": {
            "T2M": monthly_t2m,
            "T2M_MAX": monthly_t2m_max,
            "T2M_MIN": monthly_t2m_min,
            "PRECTOTCORR": monthly_precip_daily,
            "PRECTOT_MONTHLY": monthly_precip_total,
            "RH2M": monthly_rh,
            "ALLSKY_SFC_SW_DWN": monthly_solar,
            "WS2M": monthly_wind,
        },
        "annual_summary": {
            "mean_temp_c": monthly_t2m["ANN"],
            "max_temp_c": monthly_t2m_max["ANN"],
            "min_temp_c": monthly_t2m_min["ANN"],
            "annual_precipitation_mm": round(annual_precip_sum, 1),
            "mean_relative_humidity": monthly_rh["ANN"],
            "dry_months_count": sum(1 for m, p in monthly_precip_total.items() if p < 60.0),
        }
    }




MONTH_KEYS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN",
              "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")


def _valid(value, low, high):
    return isinstance(value, (int, float)) and math.isfinite(value) and low <= value <= high


def _normalize_months(values):
    """Accept POWER named months and numeric month representations."""
    return {month: values.get(month, values.get(str(i), values.get(f"{i:02d}")))
            for i, month in enumerate(MONTH_KEYS, 1)}


def parse_power_climatology(raw_data, lat, lon):
    raw = raw_data.get("properties", {}).get("parameter", {})
    ranges = {"T2M": (-60, 65), "T2M_MAX": (-60, 65), "T2M_MIN": (-60, 65),
              "PRECTOTCORR": (0, 2000), "RH2M": (0, 100), "WS2M": (0, 100)}
    parameters = {}
    for key, limits in ranges.items():
        monthly = _normalize_months(raw.get(key, {}))
        if any(not _valid(value, *limits) for value in monthly.values()):
            raise ValueError(f"Incomplete or invalid POWER parameter: {key}")
        monthly["ANN"] = sum(monthly[m] * MONTH_DAYS[i] for i, m in enumerate(MONTH_KEYS)) / 365
        parameters[key] = monthly
    units = raw_data.get("parameters", {}).get("PRECTOTCORR", {}).get("units", "mm/day").lower()
    multiplier = {"mm/day": 1, "mm/hour": 24, "mm/hr": 24}.get(units)
    if multiplier is None:
        raise ValueError(f"Unsupported precipitation units: {units}")
    daily = {k: v * multiplier for k, v in parameters["PRECTOTCORR"].items()}
    parameters["PRECTOTCORR"] = daily
    parameters["PRECTOT_MONTHLY"] = {m: round(daily[m] * MONTH_DAYS[i], 1)
                                    for i, m in enumerate(MONTH_KEYS)}
    parameters["ALLSKY_SFC_SW_DWN"] = raw.get("ALLSKY_SFC_SW_DWN", {})
    coordinates = raw_data.get("geometry", {}).get("coordinates", [])
    elevation = coordinates[2] if len(coordinates) > 2 and _valid(coordinates[2], -100, 9000) else None
    return {
        "is_simulated": False, "source": "NASA POWER / MERRA-2 climatología",
        "period": raw_data.get("header", {}).get("range", "Climatología NASA POWER"),
        "elevation_m": elevation, "closest_known_place": find_closest_location(lat, lon)["name"],
        "parameters": parameters,
        "annual_summary": {
            "mean_temp_c": round(parameters["T2M"]["ANN"], 1),
            "max_temp_c": round(parameters["T2M_MAX"]["ANN"], 1),
            "min_temp_c": round(parameters["T2M_MIN"]["ANN"], 1),
            "annual_precipitation_mm": round(sum(parameters["PRECTOT_MONTHLY"].values()), 1),
            "mean_relative_humidity": round(parameters["RH2M"]["ANN"], 1),
            "dry_months_count": sum(v < 60 for v in parameters["PRECTOT_MONTHLY"].values()),
        },
    }


def fetch_nasa_power_climatology(lat: float, lon: float, timeout_sec: int = 8) -> Dict[str, Any]:
    reason = None
    try:
        response = requests.get(NASA_POWER_BASE_URL, params={
            "parameters": ",".join(NASA_PARAMETERS), "community": NASA_POWER_COMMUNITY,
            "longitude": round(lon, 4), "latitude": round(lat, 4), "format": "JSON",
        }, timeout=timeout_sec)
        response.raise_for_status()
        return parse_power_climatology(response.json(), lat, lon)
    except (requests.RequestException, ValueError, TypeError, KeyError) as exc:
        reason = type(exc).__name__
    fallback = _generate_synthetic_cr_climatology(lat, lon)
    fallback["fallback_reason"] = reason
    fallback["period"] = "Modelo regional sin observaciones históricas verificadas"
    return fallback


def fetch_power_monthly_history(lat, lon, years=5, today=None, timeout_sec=8):
    """Five complete historical years; no future or partial annual totals."""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from calendar import monthrange
    today = today or datetime.now(ZoneInfo("America/Costa_Rica")).date()
    end = today.year - 1
    start = end - years + 1
    try:
        response = requests.get("https://power.larc.nasa.gov/api/temporal/monthly/point",
            params={"parameters": "T2M,T2M_MIN,PRECTOTCORR,WS2M", "community": "AG",
                    "latitude": round(lat, 4), "longitude": round(lon, 4),
                    "start": start, "end": end, "format": "JSON"}, timeout=timeout_sec)
        response.raise_for_status()
        raw = response.json()
        data = raw["properties"]["parameter"]
        units = raw.get("parameters", {}).get("PRECTOTCORR", {}).get("units", "mm/day").lower()
        factor = {"mm/day": 1, "mm/hour": 24, "mm/hr": 24}.get(units)
        if factor is None:
            raise ValueError("Unknown rainfall units")
        records = []
        for year in range(start, end + 1):
            for month in range(1, 13):
                key = f"{year}{month:02d}"
                p, temp, wind, tmin = (data.get(k, {}).get(key) for k in
                                      ("PRECTOTCORR", "T2M", "WS2M", "T2M_MIN"))
                if not (_valid(p, 0, 2000) and _valid(temp, -60, 65)):
                    continue
                records.append({"year": year, "month": month,
                    "precipitation_mm": round(p * factor * monthrange(year, month)[1], 1),
                    "temperature_c": temp, "wind_m_s": wind if _valid(wind, 0, 100) else None,
                    "min_temperature_c": tmin if _valid(tmin, -60, 65) else None})
        return {"source": "NASA POWER / MERRA-2 mensual", "is_simulated": False,
                "period": f"{start}–{end}", "records": records, "expected_months": years * 12}
    except (requests.RequestException, ValueError, KeyError, TypeError):
        return {"source": "Sin serie interanual disponible", "is_simulated": False,
                "period": f"{start}–{end}", "records": [], "expected_months": years * 12}
