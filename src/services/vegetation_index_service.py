"""Quality-filtered optional MODIS and GEDI retrieval using Earth Engine.

No credentials or no valid footprints => unavailable, never synthetic satellite data.
Install requirements-earthengine.txt and configure EARTHENGINE_PROJECT to enable.
"""
import os
import math
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def _number(value, low, high):
    return isinstance(value, (int, float)) and math.isfinite(value) and low <= value <= high


def coverage_factor(ndvi):
    """Screening RUSLE C proxy; local calibration required. Unknown != bare soil."""
    if not _number(ndvi, -0.2, 1):
        return None
    if ndvi < 0.25:
        return 0.85
    return round(max(0.02, min(0.85, math.exp(-2 * ndvi / max(0.01, 1 - ndvi)))), 3)


def summarize_ndvi(records):
    valid = [r for r in records if _number(r.get("ndvi"), -0.2, 1)
             and r.get("quality_ok", False) and r.get("date")]
    valid.sort(key=lambda r: r["date"])
    for record in valid:
        record["exposed_soil_risk"] = record["ndvi"] < 0.25
        record["cover_factor"] = coverage_factor(record["ndvi"])
    return {"status": "available" if valid else "unavailable", "source": "MODIS MOD13Q1 v061",
            "resolution_m": 250, "records": valid,
            "latest_ndvi": valid[-1]["ndvi"] if valid else None,
            "latest_date": valid[-1]["date"] if valid else None,
            "note": "NDVI bajo sugiere suelo expuesto; verificar agua, cosecha y nubes en campo."}


def summarize_canopy(height, biomass, quality_ok=True, observation_date=None):
    available = quality_ok and _number(height, 0, 120) and _number(biomass, 0, 1500)
    return {"status": "available" if available else "unavailable",
            "source": "GEDI L2A RH98 / L4A AGBD", "rh98_m": height if available else None,
            "agbd_mg_ha": biomass if available else None, "observation_date": observation_date,
            "canopy_detected": bool(available and height >= 5 and biomass >= 20),
            "note": "Muestreo discontinuo de 25 m; dosel cercano no confirma sombra sobre el cultivo."}


def get_vegetation_profile(lat, lon):
    result = {"ndvi": summarize_ndvi([]), "canopy": summarize_canopy(None, None),
              "status": "not_configured"}
    project = os.environ.get("EARTHENGINE_PROJECT")
    if not project:
        return result
    try:
        import ee
        # Authentication is provisioned outside the app; never prompt from a request.
        ee.Initialize(project=project)
        ee.data.setDeadline(20000)
        point = ee.Geometry.Point([lon, lat])
        today = datetime.now(ZoneInfo("America/Costa_Rica")).date()
        end = today.replace(day=1)
        start = (end - timedelta(days=730)).replace(day=1)
        collection = (ee.ImageCollection("MODIS/061/MOD13Q1").filterBounds(point)
                      .filterDate(start.isoformat(), end.isoformat()))
        def ndvi_feature(image):
            value = image.select("NDVI").multiply(0.0001).updateMask(image.select("SummaryQA").eq(0))
            mean = value.reduceRegion(ee.Reducer.mean(), point.buffer(125), 250).get("NDVI")
            return ee.Feature(None, {"date": image.date().format("YYYY-MM-dd"), "ndvi": mean})
        features = ee.FeatureCollection(collection.toList(collection.size()).map(lambda img: ndvi_feature(ee.Image(img)))).getInfo()["features"]
        # Monthly average from accepted 16-day composites, preserving observation dates.
        buckets = {}
        for feature in features:
            props = feature["properties"]
            if _number(props.get("ndvi"), -0.2, 1):
                buckets.setdefault(props["date"][:7], []).append(props["ndvi"])
        result["ndvi"] = summarize_ndvi([
            {"date": month + "-01", "ndvi": round(sum(values) / len(values), 4),
             "quality_ok": True, "samples": len(values)} for month, values in buckets.items()])
        result["status"] = "connected"
        try:
            roi = point.buffer(100)
            def mask_height(image):
                return image.updateMask(image.select("quality_flag").eq(1)).updateMask(
                    image.select("degrade_flag").eq(0)).select("rh98")
            def mask_biomass(image):
                return image.updateMask(image.select("l4_quality_flag").eq(1)).updateMask(
                    image.select("degrade_flag").eq(0)).select("agbd")
            height = (ee.ImageCollection("LARSE/GEDI/GEDI02_A_002_MONTHLY").filterBounds(roi)
                      .filterDate("2019-01-01", end.isoformat()).map(mask_height).median()
                      .reduceRegion(ee.Reducer.mean(), roi, 25).get("rh98").getInfo())
            biomass = (ee.ImageCollection("LARSE/GEDI/GEDI04_A_002_MONTHLY").filterBounds(roi)
                       .filterDate("2019-01-01", end.isoformat()).map(mask_biomass).median()
                       .reduceRegion(ee.Reducer.mean(), roi, 25).get("agbd").getInfo())
            result["canopy"] = summarize_canopy(height, biomass, observation_date=f"2019–{end.year} (compuesto)")
        except Exception:
            result["canopy"]["note"] = "GEDI sin cobertura válida o consulta no disponible."
    except Exception as exc:
        result["status"] = "unavailable"
        result["error_type"] = type(exc).__name__
    return result
