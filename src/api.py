"""
FastAPI REST Service for Crop Viability in Costa Rica.
Implements Phase 4 of GEMINI.md:
  Endpoint: GET /api/viability?lat={lat}&lon={lon}
  Returns the viability success percentage and sensitivity metrics for all 5 crops.
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

from src.services.data_lake import get_unified_environmental_profile
from src.services.land_verification import validate_terrestrial_location
from src.models.sensitivity_viability_model import SensitivityViabilityModel
from src.data.crops_catalog import CROPS_LIST
from src.config import CR_LAT_MIN, CR_LAT_MAX, CR_LON_MIN, CR_LON_MAX

app = FastAPI(
    title="Costa Rica Crop Viability & Agricultural API",
    description="NASA Space Apps 2026 - Environmental Data Lake & Crop Viability Model for Costa Rica",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "project": "Costa Rica Crop Viability & Agricultural App",
        "blueprint": "GEMINI.md",
        "status": "online",
        "endpoints": {
            "viability": "/api/viability?lat={lat}&lon={lon}",
            "crops": "/api/crops",
            "health": "/api/health"
        }
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "AgroClima Costa Rica Engine"}


@app.get("/api/crops")
def list_crops():
    """Returns the plant profiles for all 5 target crops."""
    return {"count": len(CROPS_LIST), "crops": CROPS_LIST}


@app.get("/api/viability")
def calculate_viability(
    lat: float = Query(..., description="Latitude (North)", ge=CR_LAT_MIN, le=CR_LAT_MAX),
    lon: float = Query(..., description="Longitude (West)", ge=CR_LON_MIN, le=CR_LON_MAX)
) -> Dict[str, Any]:
    """
    Core REST endpoint specified in GEMINI.md:
    Triggers multi-satellite data fetch (SMAP, GPM, ECOSTRESS, SRTM, IMN)
    and executes the Sensitivity Score & Success Percentage algorithm for all 5 crops.
    Validates that coordinates correspond to terrestrial land (excludes marine / ocean zones).
    """
    # Step 1: Terrestrial Land Verification
    val = validate_terrestrial_location(lat, lon)
    if not val["is_valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "NON_TERRESTRIAL_LOCATION",
                "message": val["message_es"],
                "message_en": val["message_en"],
                "classification": val["classification_es"],
                "closest_land_location": val["closest_land_location"]["name"],
                "distance_to_land_km": val["distance_to_land_km"],
            }
        )

    try:
        # Step 2: Data Fetch
        env_profile = get_unified_environmental_profile(lat, lon)

        actual_t = env_profile["temperatures"]["air_temperature_mean_c"]
        actual_p = env_profile["precipitation"]["gpm_annual_total_mm"]
        actual_alt = env_profile["topography_and_erosion"]["elevation_msnm"]
        actual_sm = env_profile["humidity_and_moisture"]["smap_root_zone_moisture_m3_m3"]
        actual_soil = env_profile["soil"]["order"]

        # Step 3 & 4: Delta calculation & Success percentage for all 5 crops
        viability_results = SensitivityViabilityModel.calculate_all_crops(
            actual_temp_c=actual_t,
            actual_precip_mm=actual_p,
            actual_altitude_m=actual_alt,
            actual_soil_moisture_m3_m3=actual_sm,
            actual_soil_type=actual_soil
        )

        return {
            "status": "success",
            "coordinates": {"latitude": lat, "longitude": lon},
            "location_details": env_profile["location"],
            "environmental_parameters": {
                "air_temperature_c": actual_t,
                "ground_temperature_c": env_profile["temperatures"]["ground_surface_temperature_c"],
                "annual_precipitation_mm": actual_p,
                "altitude_msnm": actual_alt,
                "soil_moisture_m3_m3": actual_sm,
                "soil_type_imn": actual_soil,
                "soil_absorption_potential": env_profile["humidity_and_moisture"]["soil_absorption_potential"],
                "erosion_risk_level": env_profile["topography_and_erosion"]["erosion_risk_level"],
            },
            "satellite_sources": {
                "soil_moisture": "NASA SMAP (L2_SM_A/P & L4_SM)",
                "precipitation": "NASA GPM (DPR Monthly)",
                "topography": "NASA SRTM (30m Global DEM)",
                "vegetation_stress": "NASA ECOSTRESS (ESI) & VIIRS",
                "local_climate_soil": "IMN Costa Rica"
            },
            "crops_viability": viability_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
