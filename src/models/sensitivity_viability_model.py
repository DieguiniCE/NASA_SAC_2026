"""Transparent agronomic suitability index; not a calibrated yield probability.

Ideal ranges have a plateau. Outside ranges, continuous bounded responses use
tolerable temperature limits and explicit extrapolation scales for other factors.
Weights are applied once; elevation is a weak proxy to avoid counting heat twice.
"""
import math
from typing import Dict, Any, List
from src.data.crops_catalog import CROPS_LIST


class SensitivityViabilityModel:
    K_TEMP, K_PRECIP, K_SM, K_ALT = 10.0, 1000.0, 0.20, 800.0
    WEIGHT_TEMP, WEIGHT_PRECIP, WEIGHT_SM, WEIGHT_ALT = 0.45, 0.30, 0.20, 0.05
    WEIGHTS = {"temp": WEIGHT_TEMP, "precip": WEIGHT_PRECIP,
               "soil_moisture": WEIGHT_SM, "altitude": WEIGHT_ALT}
    MODEL_VERSION = "2.0"
    VALIDATIONS = [
        "Análisis de laboratorio de suelo: pH, nutrientes y toxicidad por aluminio.",
        "Comprobar drenaje, compactación, profundidad efectiva y humedad de raíces.",
        "Verificar variedad, pendiente y calendario local con asistencia agronómica.",
    ]

    @classmethod
    def calculate_crop_sensitivity(cls, crop_data):
        specs = [("temperature", "ideal_temp_c", cls.K_TEMP, 1.0),
                 ("precipitation", "precipitation_mm", cls.K_PRECIP, 50.0),
                 ("soil_moisture", "soil_moisture_m3_m3", cls.K_SM, 0.04),
                 ("altitude", "altitude_m", cls.K_ALT, 50.0)]
        values = {f"s_{name}": round(k / max(floor, crop_data[key]["max"] - crop_data[key]["min"]), 3)
                  for name, key, k, floor in specs}
        values["composite_sensitivity"] = round(sum(
            values[f"s_{name}"] * weight for name, weight in
            zip(("temperature", "precipitation", "soil_moisture", "altitude"),
                cls.WEIGHTS.values())), 2)
        return values

    @staticmethod
    def factor_suitability(value, bounds, lower_scale, upper_scale=None):
        """100 throughout ideal interval; 50 at one scale outside. No hard jumps."""
        low, high = float(bounds["min"]), float(bounds["max"])
        if low > high or lower_scale <= 0 or (upper_scale is not None and upper_scale <= 0):
            raise ValueError("Invalid crop response range")
        distance = low - value if value < low else value - high if value > high else 0.0
        scale = lower_scale if value < low else (upper_scale or lower_scale)
        return 100.0 * math.exp(-math.log(2) * min(1e6, (distance / scale) ** 2))

    @classmethod
    def calculate_viability(cls, crop_data: Dict[str, Any], actual_temp_c: float,
                            actual_precip_mm: float, actual_altitude_m: float,
                            actual_soil_moisture_m3_m3: float,
                            actual_soil_type: str = "Inceptisol",
                            delta_temp_c: float = 0.0, delta_precip_pct: float = 0.0,
                            irrigation: bool = False, shade: bool = False,
                            data_quality: str = "estimated", include_uncertainty: bool = True):
        vals = (actual_temp_c, actual_precip_mm, actual_altitude_m,
                actual_soil_moisture_m3_m3, delta_temp_c, delta_precip_pct)
        if any(v is None or not math.isfinite(float(v)) for v in vals):
            raise ValueError("Environmental inputs must be finite, complete numbers")
        if not -60 <= actual_temp_c <= 65 or actual_precip_mm < 0 or not 0 <= actual_soil_moisture_m3_m3 <= 1 or not -100 <= actual_altitude_m <= 9000:
            raise ValueError("Environmental input outside physical bounds")
        if delta_precip_pct < -100:
            raise ValueError("Precipitation change cannot be below -100%")
        temp = actual_temp_c + delta_temp_c
        precip = actual_precip_mm * (1 + delta_precip_pct / 100)
        moisture = max(0.0, min(1.0, actual_soil_moisture_m3_m3 *
                              (1 + delta_precip_pct / 200 - delta_temp_c * 0.02)))
        # Shade response is an explicit coffee microclimate scenario, never a universal bonus.
        if shade and crop_data["crop"] == "Coffee" and temp > crop_data["ideal_temp_c"]["max"]:
            temp = max(crop_data["ideal_temp_c"]["max"], temp - 1.5)
        t, p, sm, alt = (crop_data[k] for k in
                         ("ideal_temp_c", "precipitation_mm", "soil_moisture_m3_m3", "altitude_m"))
        tol = crop_data.get("tolerable_temp_c", {"min": t["min"] - 4, "max": t["max"] + 4})
        p_tol = crop_data.get("tolerable_precipitation_mm", {})
        p_lower_scale = max(100, p["min"] - p_tol["min"]) if "min" in p_tol else max(400, p["min"] * 0.60)
        p_upper_scale = max(100, p_tol["max"] - p["max"]) if "max" in p_tol else max(800, p["max"] * 0.60)
        factors = {
            "temp": cls.factor_suitability(temp, t, max(2, t["min"] - tol["min"]) / math.sqrt(2),
                                           max(2, tol["max"] - t["max"]) / math.sqrt(2)),
            "precip": cls.factor_suitability(precip, p, p_lower_scale, p_upper_scale),
            "soil_moisture": cls.factor_suitability(moisture, sm, 0.12, 0.15),
            "altitude": cls.factor_suitability(actual_altitude_m, alt, 1000, 1000),
        }
        # Supplemental irrigation mitigates only a deficit, never excess water.
        if irrigation:
            if precip < p["min"]:
                factors["precip"] += (100 - factors["precip"]) * 0.70
            if moisture < sm["min"]:
                factors["soil_moisture"] += (100 - factors["soil_moisture"]) * 0.70
        soil_match = any(actual_soil_type.strip().casefold() == s.casefold()
                         for s in crop_data.get("soil_type", []))
        soil_penalty = 0.0 if soil_match or not actual_soil_type.strip() else 3.0
        penalties = {key: (100 - value) * cls.WEIGHTS[key] for key, value in factors.items()}
        # A severe limiting factor cannot be hidden by excellent unrelated factors.
        weighted_score = 100 - sum(penalties.values()) - soil_penalty
        critical_fit = min(factors["temp"], factors["precip"], factors["soil_moisture"])
        limiting_cap = 100 * math.sqrt(critical_fit / 100)
        score = round(max(0, min(100, weighted_score, limiting_cap)))
        if score >= 80:
            status, color = "Viabilidad Alta", "green"
        elif score >= 60:
            status, color = "Viabilidad Moderada", "blue"
        elif score >= 40:
            status, color = "Viabilidad Marginal", "orange"
        else:
            status, color = "No Viable en las condiciones evaluadas", "red"
        result = {
            "crop": crop_data["crop"], "common_name": crop_data.get("common_name_es", crop_data["crop"]),
            "icon": crop_data.get("icon", "🌱"), "success_percentage": score,
            "status": status, "badge_color": color, "model_version": cls.MODEL_VERSION,
            "score_interpretation": "Índice de aptitud 0–100; no probabilidad de cosecha ni rentabilidad.",
            "sensitivity": cls.calculate_crop_sensitivity(crop_data),
            "factor_scores": {k: round(v, 1) for k, v in factors.items()}, "weights": dict(cls.WEIGHTS),
            "limiting_factor": min(factors, key=factors.get),
            "limiting_cap": round(limiting_cap, 1),
            "limiting_penalty": round(max(0, weighted_score - limiting_cap), 1),
            "deltas": {"temperature_delta_c": round(temp - t["sweet_spot"], 2),
                       "precipitation_delta_mm": round(precip - p["sweet_spot"], 1),
                       "altitude_delta_m": round(actual_altitude_m - alt["sweet_spot"], 1),
                       "soil_moisture_delta": round(moisture - sm["sweet_spot"], 3)},
            "actual_values": {"temperature_c": temp, "precipitation_mm": precip,
                              "altitude_m": actual_altitude_m, "soil_moisture_m3_m3": moisture,
                              "soil_type": actual_soil_type},
            "sweet_spots": {"temperature_c": t["sweet_spot"], "precipitation_mm": p["sweet_spot"],
                            "altitude_m": alt["sweet_spot"], "soil_moisture_m3_m3": sm["sweet_spot"]},
            "penalties": {**{k: round(v, 1) for k, v in penalties.items()}, "soil_modifier": soil_penalty},
            "watering_needs": crop_data.get("watering_needs", "N/A"),
            "soil_types_recommended": crop_data.get("soil_type", []),
            "mandatory_field_validations": cls.VALIDATIONS,
            "management": {"irrigation": irrigation, "shade": shade},
        }
        if include_uncertainty:
            # Deterministic sensitivity envelope, NOT an empirical confidence interval.
            dt, dp, dsm = (1.0, 0.10, 0.04) if data_quality == "observed" else (2.0, 0.20, 0.08)
            samples = [score]
            for sign_t in (-1, 1):
                for sign_p in (-1, 1):
                    for sign_sm in (-1, 1):
                        samples.append(cls.calculate_viability(
                            crop_data, actual_temp_c + sign_t * dt,
                            max(0, actual_precip_mm * (1 + sign_p * dp)), actual_altitude_m,
                            max(0, min(1, actual_soil_moisture_m3_m3 + sign_sm * dsm)),
                            actual_soil_type, delta_temp_c, delta_precip_pct, irrigation, shade,
                            data_quality, False)["success_percentage"])
            result["uncertainty"] = {
                "lower": min(samples), "upper": max(samples),
                "margin_points": max(score - min(samples), max(samples) - score),
                "confidence": "Media" if data_quality == "observed" else "Baja",
                "kind": "Rango de sensibilidad; no intervalo de confianza estadístico",
                "assumptions": {"temperature_c": dt, "rainfall_fraction": dp, "moisture_m3_m3": dsm},
            }
        return result

    @classmethod
    def calculate_all_crops(cls, actual_temp_c, actual_precip_mm, actual_altitude_m,
                            actual_soil_moisture_m3_m3, actual_soil_type="Inceptisol", **options):
        return [cls.calculate_viability(crop, actual_temp_c, actual_precip_mm, actual_altitude_m,
                                       actual_soil_moisture_m3_m3, actual_soil_type, **options)
                for crop in CROPS_LIST]
