"""
Unified Environmental Data Lake and Satellite Fusion Engine.
Harmonizes and synthesizes data across:
  1. NASA SMAP (L2_SM_A/P surface moisture, L4_SM root moisture, ground temperature)
  2. NASA GPM (DPR Monthly precipitation radar, erosivity R)
  3. NASA ECOSTRESS / VIIRS (70m Tiled Evaporative Stress Index, LST ground temp)
  4. NASA SRTM (30m Global DEM, topographic slope, relief, drainage)
  5. IMN Costa Rica (Soil orders, soil absorption potential, erosion risk, 2030/2050 projections)
  6. NASA POWER (Agroclimatology climatological baseline, air temp, solar radiation)
"""

from typing import Dict, Any
from src.services.nasa_power import fetch_nasa_power_climatology
from src.services.smap_service import SMAPService
from src.services.gpm_service import GPMService
from src.services.ecostress_service import ECOSTRESSService
from src.services.srtm_service import SRTMService
from src.services.imn_cr_service import IMNCostaRicaService
from src.data.costa_rica_locations import find_closest_location


def get_unified_environmental_profile(lat: float, lon: float) -> Dict[str, Any]:
    """
    Synthesizes multi-mission satellite and local institutional databases into
    a single comprehensive environmental profile for a location in Costa Rica.
    """
    # 1. Base Climatology from NASA POWER
    nasa_power_data = fetch_nasa_power_climatology(lat, lon)
    annual_sum = nasa_power_data.get("annual_summary", {})
    air_temp_c = annual_sum.get("mean_temp_c", 22.0)
    annual_precip_mm = annual_sum.get("annual_precipitation_mm", 2200.0)
    air_humidity_pct = annual_sum.get("mean_relative_humidity", 78.0)
    closest_loc = find_closest_location(lat, lon)
    elev_init = nasa_power_data.get("elevation_m") or closest_loc.get("elevation_m", 1000)

    # 2. NASA SRTM 30m Global Topography
    srtm_data = SRTMService.get_topography_profile(lat, lon, known_elevation_m=elev_init)
    true_elevation = srtm_data["elevation_msnm"]
    slope_deg = srtm_data["slope_degrees"]
    ls_factor = srtm_data["topographic_ls_factor"]

    # 3. NASA GPM DPR Monthly Precipitation & Radar Climatology
    gpm_data = GPMService.get_precipitation_profile(
        lat, lon,
        base_annual_mm=annual_precip_mm,
        monthly_distribution=nasa_power_data.get("parameters", {}).get("PRECTOT_MONTHLY")
    )
    r_erosivity = gpm_data["rainfall_erosivity_R"]

    # 4. NASA SMAP L2 Surface & L4 Root-Zone Moisture
    smap_data = SMAPService.get_soil_moisture_profile(
        lat=lat,
        lon=lon,
        recent_rain_mm=gpm_data["peak_monthly_mm"] * 0.4,
        annual_rain_mm=gpm_data["annual_precipitation_mm"],
        air_temp_c=air_temp_c,
        elevation_m=true_elevation
    )
    root_moisture = smap_data["summary"]["root_zone_moisture_m3_m3"]
    ground_temp_smap = smap_data["summary"]["ground_temp_c"]

    # 5. NASA ECOSTRESS / VIIRS Tiled ESI & Land Surface Temperature
    ecostress_data = ECOSTRESSService.get_tiled_moisture_and_lst(
        lat=lat,
        lon=lon,
        air_temp_c=air_temp_c,
        elevation_m=true_elevation,
        root_moisture_m3_m3=root_moisture
    )
    ground_temp_lst = ecostress_data["land_surface_temp_c"]

    # Average Ground Temperature from ECOSTRESS thermal LST and SMAP L4 layer 1
    blended_ground_temp_c = round((ground_temp_lst * 0.6) + (ground_temp_smap * 0.4), 1)

    # 6. Instituto Meteorológico Nacional (IMN) Soil & Climate Projections
    imn_data = IMNCostaRicaService.get_soil_and_climate_projections(
        lat=lat,
        lon=lon,
        elevation_m=true_elevation,
        r_erosivity=r_erosivity,
        ls_topographic=ls_factor
    )

    return {
        "location": {
            "lat": lat,
            "lon": lon,
            "closest_locality": closest_loc["name"],
            "canton": closest_loc["canton"],
            "province": closest_loc["province"],
            "imn_region": imn_data["imn_climate_region"],
        },
        "temperatures": {
            "air_temperature_mean_c": air_temp_c,
            "air_temperature_max_c": annual_sum.get("max_temp_c", 27.0),
            "air_temperature_min_c": annual_sum.get("min_temp_c", 17.0),
            "ground_surface_temperature_c": blended_ground_temp_c,
            "ground_temp_ecostress_lst_c": ground_temp_lst,
            "ground_temp_smap_layer1_c": ground_temp_smap,
            "source_air": "NASA POWER / IMN",
            "source_ground": "NASA ECOSTRESS (ECO2LSTE) & SMAP (L4_SM soil_temp_layer1)",
        },
        "humidity_and_moisture": {
            "air_relative_humidity_pct": air_humidity_pct,
            "smap_surface_soil_moisture_m3_m3": smap_data["summary"]["surface_soil_moisture_m3_m3"],
            "smap_root_zone_moisture_m3_m3": root_moisture,
            "smap_root_status": smap_data["summary"]["root_status"],
            "ecostress_evaporative_stress_index": ecostress_data["evaporative_stress_index"],
            "ecostress_stress_evaluation": ecostress_data["stress_evaluation"],
            "soil_absorption_potential": imn_data["soil_absorption_potential"],
            "soil_infiltration_rate_mm_h": imn_data["infiltration_rate_mm_h"],
            "soil_water_retention_capacity_mm_m": imn_data["available_water_capacity_mm_m"],
        },
        "precipitation": {
            "gpm_annual_total_mm": gpm_data["annual_precipitation_mm"],
            "gpm_monthly_series": gpm_data["monthly_precipitation_mm"],
            "gpm_peak_month": gpm_data["peak_rainfall_month"],
            "gpm_peak_monthly_mm": gpm_data["peak_monthly_mm"],
            "rainfall_erosivity_R": r_erosivity,
            "historical_source": "NASA GPM DPR Monthly & IMERG Radar Climatology",
            "imn_projections": imn_data["climate_change_projections"],
        },
        "topography_and_erosion": {
            "elevation_msnm": true_elevation,
            "slope_degrees": slope_deg,
            "slope_percent": srtm_data["slope_percent"],
            "landform_classification": srtm_data["landform_classification"],
            "mechanization_capacity": srtm_data["mechanization_capacity"],
            "drainage_hazard": srtm_data["drainage_hazard"],
            "topographic_ls_factor": ls_factor,
            "erosion_risk_level": imn_data["erosion_risk_analysis"]["risk_level"],
            "erosion_risk_color": imn_data["erosion_risk_analysis"]["risk_color"],
            "soil_loss_estimated_ton_ha_yr": imn_data["erosion_risk_analysis"]["estimated_loss_ton_ha_yr"],
            "conservation_advice": imn_data["erosion_risk_analysis"]["conservation_advice"],
            "elevation_source": "NASA SRTMGL1 (30m Global DEM)",
        },
        "soil": {
            "order": imn_data["soil_order_classified"],
            "details": imn_data["soil_details"],
            "texture": imn_data["soil_details"]["texture"],
            "ph_range": imn_data["soil_details"]["ph_range"],
            "organic_matter": imn_data["soil_details"]["organic_matter"],
            "drainage": imn_data["soil_details"]["drainage"],
            "source": "Instituto Meteorológico Nacional (IMN) / MAG / CIA-UCR",
        },
        "raw_services": {
            "smap": smap_data,
            "gpm": gpm_data,
            "ecostress": ecostress_data,
            "srtm": srtm_data,
            "imn": imn_data,
            "nasa_power": nasa_power_data,
        }
    }
