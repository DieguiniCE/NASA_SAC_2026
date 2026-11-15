"""
Sensitivity Score & Viability Prediction Model.
Directly implements Section 4 and Section 5 of the Project Blueprint (GEMINI.md):
  1. Mathematical Sensitivity Score: S = k / (Max - Min)
  2. Composite Sensitivity Score weighting Temp, Precipitation, Soil Moisture, and Altitude.
  3. Delta Calculation from crop's sweet_spot.
  4. Success Percentage: 100% baseline minus penalty = f(Delta, Sensitivity).
"""

from typing import Dict, Any, List
from src.data.crops_catalog import CROPS_LIST, CROPS_CATALOG


class SensitivityViabilityModel:
    """
    Implements the Costa Rica Crop Viability algorithm specified in GEMINI.md.
    """

    # Normalization constants (k) chosen so that standard sensitivity ranges between 0.5 and 2.5
    K_TEMP = 10.0            # Typical range ~6-12°C -> S_temp ~ 0.8 - 1.7
    K_PRECIP = 1000.0        # Typical range ~800-1500mm -> S_precip ~ 0.7 - 1.3
    K_SM = 0.20              # Typical range ~0.15-0.25 m3/m3 -> S_sm ~ 0.8 - 1.4
    K_ALT = 800.0            # Typical range ~600-1200m -> S_alt ~ 0.7 - 1.4

    # Composite Sensitivity Weights (Temperature, Precipitation, Soil Moisture, Altitude)
    WEIGHT_TEMP = 0.35
    WEIGHT_PRECIP = 0.30
    WEIGHT_SM = 0.20
    WEIGHT_ALT = 0.15

    @classmethod
    def calculate_crop_sensitivity(cls, crop_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculates individual parameter sensitivities and the composite Sensitivity Score.
        Formula: S = k / (Param_max - Param_min)
        """
        # 1. Temperature sensitivity
        t_min = crop_data["ideal_temp_c"]["min"]
        t_max = crop_data["ideal_temp_c"]["max"]
        t_range = max(1.0, float(t_max - t_min))
        s_temp = round(cls.K_TEMP / t_range, 3)

        # 2. Precipitation sensitivity
        p_min = crop_data["precipitation_mm"]["min"]
        p_max = crop_data["precipitation_mm"]["max"]
        p_range = max(50.0, float(p_max - p_min))
        s_precip = round(cls.K_PRECIP / p_range, 3)

        # 3. Soil moisture sensitivity
        sm_min = crop_data["soil_moisture_m3_m3"]["min"]
        sm_max = crop_data["soil_moisture_m3_m3"]["max"]
        sm_range = max(0.04, float(sm_max - sm_min))
        s_sm = round(cls.K_SM / sm_range, 3)

        # 4. Altitude sensitivity
        alt_min = crop_data["altitude_m"]["min"]
        alt_max = crop_data["altitude_m"]["max"]
        alt_range = max(50.0, float(alt_max - alt_min))
        s_alt = round(cls.K_ALT / alt_range, 3)

        # Composite weighted score
        composite_s = round(
            (cls.WEIGHT_TEMP * s_temp) +
            (cls.WEIGHT_PRECIP * s_precip) +
            (cls.WEIGHT_SM * s_sm) +
            (cls.WEIGHT_ALT * s_alt),
            2
        )

        return {
            "composite_sensitivity": composite_s,
            "s_temperature": s_temp,
            "s_precipitation": s_precip,
            "s_soil_moisture": s_sm,
            "s_altitude": s_alt,
        }

    @classmethod
    def calculate_viability(
        cls,
        crop_data: Dict[str, Any],
        actual_temp_c: float,
        actual_precip_mm: float,
        actual_altitude_m: float,
        actual_soil_moisture_m3_m3: float,
        actual_soil_type: str = "Inceptisol"
    ) -> Dict[str, Any]:
        """
        Executes Steps 3 & 4 of the Blueprint:
          - Delta Calculation from sweet_spot
          - Success Percentage subtraction from 100% baseline multiplied by Sensitivity Score
        """
        sensitivity = cls.calculate_crop_sensitivity(crop_data)
        s_composite = sensitivity["composite_sensitivity"]
        s_temp = sensitivity["s_temperature"]
        s_precip = sensitivity["s_precipitation"]
        s_sm = sensitivity["s_soil_moisture"]
        s_alt = sensitivity["s_altitude"]

        # Step 3: Delta Calculation (|Actual - Sweet_Spot|)
        sweet_temp = crop_data["ideal_temp_c"]["sweet_spot"]
        sweet_precip = crop_data["precipitation_mm"]["sweet_spot"]
        sweet_alt = crop_data["altitude_m"]["sweet_spot"]
        sweet_sm = crop_data["soil_moisture_m3_m3"]["sweet_spot"]

        delta_temp = round(abs(actual_temp_c - sweet_temp), 2)
        delta_precip = round(abs(actual_precip_mm - sweet_precip), 1)
        delta_alt = round(abs(actual_altitude_m - sweet_alt), 1)
        delta_sm = round(abs(actual_soil_moisture_m3_m3 - sweet_sm), 3)

        # Check deviations outside ideal range
        t_min, t_max = crop_data["ideal_temp_c"]["min"], crop_data["ideal_temp_c"]["max"]
        p_min, p_max = crop_data["precipitation_mm"]["min"], crop_data["precipitation_mm"]["max"]
        alt_min, alt_max = crop_data["altitude_m"]["min"], crop_data["altitude_m"]["max"]
        sm_min, sm_max = crop_data["soil_moisture_m3_m3"]["min"], crop_data["soil_moisture_m3_m3"]["max"]

        # Step 4: Penalty Calculation
        # Temperature penalty: proportional to deviation, amplified by s_temp
        if t_min <= actual_temp_c <= t_max:
            # Within ideal range: mild deviation penalty from sweet spot
            penalty_temp = (delta_temp / max(1.0, (t_max - t_min) / 2)) * 6.0 * s_temp
        else:
            # Outside ideal range: severe penalty
            outside_deg = (t_min - actual_temp_c) if actual_temp_c < t_min else (actual_temp_c - t_max)
            penalty_temp = (6.0 + outside_deg * 5.0) * s_temp

        # Precipitation penalty
        if p_min <= actual_precip_mm <= p_max:
            penalty_precip = (delta_precip / max(100.0, (p_max - p_min) / 2)) * 6.0 * s_precip
        else:
            outside_mm = (p_min - actual_precip_mm) if actual_precip_mm < p_min else (actual_precip_mm - p_max)
            penalty_precip = (6.0 + (outside_mm / 100.0) * 4.0) * s_precip

        # Soil moisture penalty
        if sm_min <= actual_soil_moisture_m3_m3 <= sm_max:
            penalty_sm = (delta_sm / max(0.02, (sm_max - sm_min) / 2)) * 5.0 * s_sm
        else:
            outside_sm = (sm_min - actual_soil_moisture_m3_m3) if actual_soil_moisture_m3_m3 < sm_min else (actual_soil_moisture_m3_m3 - sm_max)
            penalty_sm = (5.0 + outside_sm * 60.0) * s_sm

        # Altitude penalty
        if alt_min <= actual_altitude_m <= alt_max:
            penalty_alt = (delta_alt / max(100.0, (alt_max - alt_min) / 2)) * 4.0 * s_alt
        else:
            outside_alt = (alt_min - actual_altitude_m) if actual_altitude_m < alt_min else (actual_altitude_m - alt_max)
            penalty_alt = (4.0 + (outside_alt / 150.0) * 6.0) * s_alt

        # Soil type compatibility bonus / penalty
        soil_types_allowed = crop_data.get("soil_type", [])
        if any(actual_soil_type.lower() in s.lower() for s in soil_types_allowed):
            soil_modifier = -3.0  # Favorable soil reduces penalty by 3 points
        else:
            soil_modifier = 6.0   # Non-ideal soil adds penalty

        total_penalty = penalty_temp + penalty_precip + penalty_sm + penalty_alt + soil_modifier
        success_percentage = max(0, min(100, round(100.0 - total_penalty)))

        if success_percentage >= 80:
            status = "Viabilidad Alta (Condiciones Cercanas al Sweet Spot)"
            color = "green"
        elif success_percentage >= 60:
            status = "Viabilidad Moderada (Desviaciones Tolerables)"
            color = "blue"
        elif success_percentage >= 40:
            status = "Viabilidad Marginal (Riesgo Agronómico)"
            color = "orange"
        else:
            status = "No Viable (Desviación Crítica de Rangos)"
            color = "red"

        return {
            "crop": crop_data["crop"],
            "common_name": crop_data.get("common_name_es", crop_data["crop"]),
            "icon": crop_data.get("icon", "🌱"),
            "success_percentage": success_percentage,
            "status": status,
            "badge_color": color,
            "sensitivity": sensitivity,
            "deltas": {
                "temperature_delta_c": delta_temp,
                "precipitation_delta_mm": delta_precip,
                "altitude_delta_m": delta_alt,
                "soil_moisture_delta": delta_sm,
            },
            "actual_values": {
                "temperature_c": actual_temp_c,
                "precipitation_mm": actual_precip_mm,
                "altitude_m": actual_altitude_m,
                "soil_moisture_m3_m3": actual_soil_moisture_m3_m3,
                "soil_type": actual_soil_type,
            },
            "sweet_spots": {
                "temperature_c": sweet_temp,
                "precipitation_mm": sweet_precip,
                "altitude_m": sweet_alt,
                "soil_moisture_m3_m3": sweet_sm,
            },
            "penalties": {
                "temp": round(penalty_temp, 1),
                "precip": round(penalty_precip, 1),
                "soil_moisture": round(penalty_sm, 1),
                "altitude": round(penalty_alt, 1),
                "soil_modifier": round(soil_modifier, 1),
            },
            "watering_needs": crop_data.get("watering_needs", "N/A"),
            "soil_types_recommended": crop_data.get("soil_type", []),
        }

    @classmethod
    def calculate_all_crops(
        cls,
        actual_temp_c: float,
        actual_precip_mm: float,
        actual_altitude_m: float,
        actual_soil_moisture_m3_m3: float,
        actual_soil_type: str = "Inceptisol"
    ) -> List[Dict[str, Any]]:
        """
        Calculates viability and sensitivity score for all 5 crops specified in GEMINI.md:
        Banana, Coffee, Sugar Cane, Pineapple, Avocado.
        """
        results = []
        for crop in CROPS_LIST:
            res = cls.calculate_viability(
                crop_data=crop,
                actual_temp_c=actual_temp_c,
                actual_precip_mm=actual_precip_mm,
                actual_altitude_m=actual_altitude_m,
                actual_soil_moisture_m3_m3=actual_soil_moisture_m3_m3,
                actual_soil_type=actual_soil_type
            )
            results.append(res)
        return results
