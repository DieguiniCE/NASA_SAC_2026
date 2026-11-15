"""Indicative national layers, with an optional official soil GeoJSON override.

The built-in coarse cells are model outputs, not IMN/MAG survey polygons.
"""
from functools import lru_cache
from pathlib import Path
import json
from src.services.land_verification import is_point_on_land_cr
from src.services.nasa_power import _generate_synthetic_cr_climatology
from src.services.srtm_service import SRTMService
from src.services.imn_cr_service import IMNCostaRicaService
from src.services.gpm_service import GPMService
from src.services.seasonal_risk_service import seasonal_indices

SOIL_COLORS = {"Andisol": "#795548", "Ultisol": "#b71c1c", "Inceptisol": "#fbc02d",
               "Alfisol": "#ef6c00", "Vertisol": "#6a1b9a", "Entisol": "#26a69a"}


@lru_cache(maxsize=1)
def build_thematic_layers():
    soils, erosion, deficit = [], [], []
    # Interior cells only; coastal gaps intentional at this approximate resolution.
    step = 0.15
    for iy in range(22):
        lat = 8 + iy * step
        for ix in range(24):
            lon = -86 + ix * step
            corners = [(lat, lon), (lat + step, lon), (lat + step, lon + step), (lat, lon + step)]
            if not all(is_point_on_land_cr(a, b) for a, b in corners):
                continue
            center_lat, center_lon = lat + step / 2, lon + step / 2
            climate = _generate_synthetic_cr_climatology(center_lat, center_lon)
            topo = SRTMService.get_topography_profile(center_lat, center_lon, climate["elevation_m"])
            precip = GPMService.get_precipitation_profile(center_lat, center_lon,
                monthly_distribution=climate["parameters"]["PRECTOT_MONTHLY"])
            soil = IMNCostaRicaService.get_soil_and_climate_projections(center_lat, center_lon,
                topo["elevation_msnm"], precip["rainfall_erosivity_R"], topo["topographic_ls_factor"])
            points = [[b, a] for a, b in corners] + [[corners[0][1], corners[0][0]]]
            soils.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [points]},
                          "properties": {"soil_order": soil["soil_order_classified"],
                                         "source": "Modelo regional orientativo; no cartografía oficial"}})
            indices = [seasonal_indices(p, climate["annual_summary"]["mean_temp_c"], None, topo["slope_percent"])
                       for p in climate["parameters"]["PRECTOT_MONTHLY"].values()]
            erosion.append([center_lat, center_lon, max(s[1] for s in indices) / 100])
            deficit.append([center_lat, center_lon, max(s[0] for s in indices) / 100])
    return {"soils": {"type": "FeatureCollection", "features": soils},
            "erosion": erosion, "deficit": deficit}


def add_thematic_layers(map_object):
    import folium
    from folium.plugins import HeatMap
    layers = build_thematic_layers()
    path = Path(__file__).parents[1] / "data" / "layers" / "soils.geojson"
    soil_data = layers["soils"]
    name = "Suelos: estimación regional (celdas ~17 km)"
    if path.is_file():
        try:
            supplied = json.loads(path.read_text(encoding="utf-8"))
            if supplied.get("type") == "FeatureCollection" and all(
                f.get("properties", {}).get("soil_order") in SOIL_COLORS
                and f.get("properties", {}).get("source") for f in supplied.get("features", [])):
                soil_data = supplied
                name = "Suelos: cartografía local suministrada"
        except (OSError, ValueError):
            pass
    folium.GeoJson(soil_data, name=name, show=False,
        style_function=lambda feature: {
            "fillColor": SOIL_COLORS.get(feature["properties"].get("soil_order"), "#888888"),
            "color": "#555555", "weight": 0.3, "fillOpacity": 0.40},
        tooltip=folium.GeoJsonTooltip(fields=["soil_order", "source"], aliases=["Suelo", "Fuente"])).add_to(map_object)
    for name, data in (("Erosión hídrica potencial: modelo regional", layers["erosion"]),
                       ("Déficit hídrico estacional: modelo regional", layers["deficit"])):
        group = folium.FeatureGroup(name=name, show=False)
        HeatMap(data, radius=25, blur=18, min_opacity=0.15,
                gradient={0.2: "#388e3c", 0.5: "#fbc02d", 0.8: "#f57c00", 1.0: "#b71c1c"}).add_to(group)
        group.add_to(map_object)
