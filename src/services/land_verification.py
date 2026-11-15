"""
Terrestrial Land Verification and Geographic Boundary Service for Costa Rica.
Ensures that analyzed coordinates correspond to terrestrial agricultural terrain,
preventing selection or evaluation of marine / oceanic zones (Pacific Ocean, Caribbean Sea,
interior marine waters of Golfo de Nicoya / Golfo Dulce) or areas outside national borders.
"""

from typing import Tuple, Dict, Any, List, Optional
import math
from src.data.costa_rica_locations import find_closest_location


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two points in kilometers."""
    r_earth = 6371.0  # Earth mean radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2) + (
        math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return round(r_earth * c, 2)


# High-precision mainland boundary polygon of Costa Rica (clockwise perimeter)
# Points: (latitude, longitude)
CR_MAINLAND_POLYGON: List[Tuple[float, float]] = [
    # ── Northern Border with Nicaragua (West to East) ──
    (11.218, -85.715),  # Bahía Salinas (Pacific NW corner)
    (11.230, -85.630),  # Peñas Blancas border crossing
    (11.180, -85.400),  # North of Guanacaste Volcanic Range
    (11.090, -85.120),  # North of Upala
    (11.050, -84.750),  # North of Los Chiles / Río Frío
    (10.920, -84.350),  # Río San Juan border (Boca San Carlos)
    (10.750, -84.000),  # Río San Juan (Sarapiquí confluence)
    (10.770, -83.750),  # Río San Juan near Delta
    (10.793, -83.615),  # Barra del Colorado (Caribbean mouth of San Juan)

    # ── Caribbean Coast (North to South-East) ──
    (10.550, -83.510),  # Tortuguero coastline
    (10.300, -83.360),  # Parismina mouth
    (10.150, -83.200),  # Matina coastline
    (9.995, -83.030),   # Puerto Limón
    (9.780, -82.870),   # Cahuita Point
    (9.650, -82.740),   # Puerto Viejo de Talamanca
    (9.620, -82.660),   # Manzanillo / Gandoca
    (9.570, -82.600),   # Boca del Río Sixaola (Panama Border Caribbean)

    # ── Southern Border with Panama (Caribbean to Pacific) ──
    (9.500, -82.610),   # Sixaola river valley
    (9.450, -82.750),   # Bribri / Talamanca border ridge
    (9.200, -82.950),   # Cordillera de Talamanca continental divide
    (8.920, -82.850),   # Border near Paso Canoas / Coto Brus
    (8.530, -82.830),   # Paso Canoas / Corredores border
    (8.270, -82.870),   # Burica Peninsula border
    (8.040, -82.880),   # Punta Burica tip (Southernmost tip of Costa Rica)

    # ── Pacific Coast: Golfo Dulce & Osa Peninsula ──
    (8.200, -82.980),   # Pavones coast
    (8.380, -83.130),   # Golfito approach
    (8.530, -83.180),   # Inner Golfito bay
    (8.650, -83.300),   # Inner Golfo Dulce / Rincón
    (8.540, -83.470),   # Puerto Jiménez / Golfo Dulce west
    (8.360, -83.500),   # Cabo Matapalo (Osa Peninsula south tip)
    (8.400, -83.680),   # Corcovado Pacific coast
    (8.700, -83.720),   # Drake Bay / Punta Llorona
    (8.850, -83.600),   # Sierpe river mouth / Térraba-Sierpe wetlands
    (9.000, -83.660),   # Coronado / Palmar coast
    (9.160, -83.740),   # Dominical coast

    # ── Central Pacific Coast ──
    (9.420, -84.160),   # Quepos / Manuel Antonio
    (9.520, -84.360),   # Parrita
    (9.610, -84.630),   # Jacó / Playa Hermosa
    (9.720, -84.660),   # Punta Leona
    (9.800, -84.750),   # Tárcoles / Caldera

    # ── Golfo de Nicoya & Nicoya Peninsula ──
    (9.970, -84.830),   # Puntarenas city / port
    (10.050, -84.950),  # Inner Gulf (Chomes)
    (10.200, -85.150),  # Río Tempisque delta (mouth)
    (10.050, -85.180),  # Nicoya eastern coast
    (9.820, -84.900),   # Paquera peninsula
    (9.700, -84.950),   # Tambor / Bahía Ballena
    (9.570, -85.080),   # Cabo Blanco (Nicoya Peninsula south tip)
    (9.600, -85.180),   # Malpaís / Santa Teresa
    (9.720, -85.320),   # Coyote coast
    (9.870, -85.550),   # Sámara / Carrillo
    (9.980, -85.690),   # Nosara
    (10.150, -85.820),  # Ostional / San Juanillo
    (10.300, -85.850),  # Tamarindo / Cabo Velas
    (10.570, -85.700),  # Playa Hermosa / Playas del Coco
    (10.750, -85.730),  # Bahía Culebra / Papagayo
    (10.880, -85.950),  # Península de Santa Elena tip
    (11.000, -85.800),  # Cuajiniquil / Junquillal
    (11.218, -85.715),  # Return to Bahía Salinas
]

# Major inhabited / agricultural islands in Golfo de Nicoya
AGRICULTURAL_ISLANDS: List[Dict[str, Any]] = [
    {
        "name": "Isla Chira (Golfo de Nicoya)",
        "lat": 10.095,
        "lon": -85.150,
        "radius_km": 5.5,
    },
    {
        "name": "Isla Venado (Golfo de Nicoya)",
        "lat": 9.985,
        "lon": -85.060,
        "radius_km": 3.0,
    },
]


def is_point_in_polygon(lat: float, lon: float, polygon: List[Tuple[float, float]]) -> bool:
    """
    Standard Ray-Casting algorithm to test point inclusion in a 2D polygon.
    Returns True if (lat, lon) is strictly inside or on edge of the polygon.
    """
    n = len(polygon)
    inside = False
    p1_lat, p1_lon = polygon[0]

    for i in range(1, n + 1):
        p2_lat, p2_lon = polygon[i % n]
        if min(p1_lon, p2_lon) < lon <= max(p1_lon, p2_lon):
            if p1_lon != p2_lon:
                lat_inters = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                if lat <= lat_inters:
                    inside = not inside
        p1_lat, p1_lon = p2_lat, p2_lon

    return inside


def is_point_on_land_cr(lat: float, lon: float) -> bool:
    """
    Checks if given coordinates correspond to terrestrial land of Costa Rica.
    Evaluates mainland boundary and major agricultural islands.
    """
    # 1. Test mainland polygon
    if is_point_in_polygon(lat, lon, CR_MAINLAND_POLYGON):
        return True

    # 2. Test agricultural islands in Gulf of Nicoya
    for island in AGRICULTURAL_ISLANDS:
        dist = haversine_distance_km(lat, lon, island["lat"], island["lon"])
        if dist <= island["radius_km"]:
            return True

    return False


def classify_location_type(lat: float, lon: float) -> Tuple[str, str, str]:
    """
    Classifies a non-terrestrial or foreign coordinate.
    Returns:
        (category_code, name_es, name_en)
    """
    if lat > 11.23 or (lat > 11.05 and lon < -85.60):
        return ("FOREIGN_NORTH", "Nicaragua / Territorio Extranjero", "Nicaragua / Foreign Territory")

    if lon > -82.55 or (lon > -82.85 and lat < 8.80):
        return ("FOREIGN_SOUTH", "Panamá / Territorio Extranjero", "Panama / Foreign Territory")

    # Interior gulf marine waters
    if 9.70 <= lat <= 10.15 and -85.15 <= lon <= -84.78:
        return ("MARINE_GULF_NICOYA", "Golfo de Nicoya (Aguas Marinas)", "Gulf of Nicoya (Marine Waters)")

    if 8.30 <= lat <= 8.68 and -83.50 <= lon <= -83.15:
        return ("MARINE_GULF_DULCE", "Golfo Dulce (Aguas Marinas)", "Golfo Dulce (Marine Waters)")

    # Caribbean Sea
    if lon > -83.55 and lat >= 9.55:
        return ("MARINE_CARIBBEAN", "Mar Caribe (Zona Marina)", "Caribbean Sea (Marine Zone)")

    # Pacific Ocean
    return ("MARINE_PACIFIC", "Océano Pacífico (Zona Marina)", "Pacific Ocean (Marine Zone)")


def validate_terrestrial_location(lat: float, lon: float) -> Dict[str, Any]:
    """
    Performs comprehensive terrestrial verification for agricultural suitability.
    Returns validation dictionary with status, classifications, and closest land point.
    """
    is_land = is_point_on_land_cr(lat, lon)
    closest_land = find_closest_location(lat, lon)
    dist_to_land = haversine_distance_km(lat, lon, closest_land["lat"], closest_land["lon"])

    if is_land:
        return {
            "is_valid": True,
            "is_land": True,
            "classification_code": "TERRESTRIAL_LAND",
            "classification_es": "Terreno Agrícola Continental (Costa Rica)",
            "classification_en": "Continental Agricultural Land (Costa Rica)",
            "message_es": "Ubicación terrestre válida dentro de Costa Rica.",
            "message_en": "Valid terrestrial location within Costa Rica.",
            "closest_land_location": closest_land,
            "distance_to_land_km": 0.0,
        }

    code, cat_es, cat_en = classify_location_type(lat, lon)
    msg_es = (
        f"La coordenada ({lat:.4f}, {lon:.4f}) se ubica en {cat_es}. "
        "AgroClima analiza únicamente terrenos agrícolas terrestres de Costa Rica. "
        f"El punto continental más cercano es {closest_land['name']} ({dist_to_land:.1f} km)."
    )
    msg_en = (
        f"The coordinate ({lat:.4f}, {lon:.4f}) is located in {cat_en}. "
        "AgroClima only analyzes terrestrial agricultural land in Costa Rica. "
        f"The closest mainland point is {closest_land['name']} ({dist_to_land:.1f} km away)."
    )

    return {
        "is_valid": False,
        "is_land": False,
        "classification_code": code,
        "classification_es": cat_es,
        "classification_en": cat_en,
        "message_es": msg_es,
        "message_en": msg_en,
        "closest_land_location": closest_land,
        "distance_to_land_km": dist_to_land,
    }


def get_cr_boundary_geojson() -> Dict[str, Any]:
    """Returns a GeoJSON Feature representing the Costa Rica terrestrial analysis polygon."""
    # GeoJSON expects coordinates as [longitude, latitude]
    coords = [[lon, lat] for lat, lon in CR_MAINLAND_POLYGON]
    return {
        "type": "Feature",
        "properties": {
            "name": "Zona Terrestre Agrícola de Costa Rica",
            "country": "Costa Rica",
            "source": "AgroClima CR Spatial Boundary Engine",
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [coords],
        },
    }
