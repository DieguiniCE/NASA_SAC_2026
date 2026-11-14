"""Geographical dataset of Costa Rica provinces, cantons, and agricultural regions."""

from typing import List, Dict, Any
import math

COSTA_RICA_LOCATIONS: Dict[str, List[Dict[str, Any]]] = {
    "San José": [
        {
            "name": "San José Centro (Valle Central)",
            "canton": "San José",
            "lat": 9.9281,
            "lon": -84.0907,
            "elevation_m": 1172,
            "primary_crops": ["Hortalizas", "Café periurbano", "Frutales"],
            "climate_type": "Premontano Húmedo / Valle Central",
        },
        {
            "name": "Tarrazú / San Marcos (Zona de Los Santos)",
            "canton": "Tarrazú",
            "lat": 9.6608,
            "lon": -84.0289,
            "elevation_m": 1429,
            "primary_crops": ["Café Especial de Altura (Strictly Hard Bean)", "Aguacate", "Manzana"],
            "climate_type": "Montano Bajo / Altura",
        },
        {
            "name": "Pérez Zeledón (San Isidro de El General)",
            "canton": "Pérez Zeledón",
            "lat": 9.3739,
            "lon": -83.7039,
            "elevation_m": 702,
            "primary_crops": ["Café", "Caña de Azúcar", "Ganadería Doble Propósito", "Granos Básicos"],
            "climate_type": "Premontano Muy Húmedo / Valle del General",
        },
        {
            "name": "Puriscal (Santiago)",
            "canton": "Puriscal",
            "lat": 9.8486,
            "lon": -84.3142,
            "elevation_m": 1105,
            "primary_crops": ["Café", "Tabaco", "Granos Básicos", "Cítricos"],
            "climate_type": "Premontano Húmedo de Transición",
        },
        {
            "name": "Dota (Santa María de Dota)",
            "canton": "Dota",
            "lat": 9.6542,
            "lon": -83.9711,
            "elevation_m": 1548,
            "primary_crops": ["Café Gourmet de Altura", "Manzana", "Mora", "Ciruela"],
            "climate_type": "Montano Bajo Lluvioso",
        },
    ],
    "Alajuela": [
        {
            "name": "Alajuela Centro",
            "canton": "Alajuela",
            "lat": 10.0163,
            "lon": -84.2116,
            "elevation_m": 952,
            "primary_crops": ["Café", "Caña de Azúcar", "Frutales tropicales"],
            "climate_type": "Premontano Tropical Húmedo",
        },
        {
            "name": "San Carlos (Ciudad Quesada)",
            "canton": "San Carlos",
            "lat": 10.3238,
            "lon": -84.4287,
            "elevation_m": 656,
            "primary_crops": ["Ganadería de Leche y Carne", "Piña", "Raíces y Tubérculos (Yuca, Ñame)", "Cítricos"],
            "climate_type": "Bosque Muy Húmedo Tropical / Llanuras del Norte",
        },
        {
            "name": "San Ramón",
            "canton": "San Ramón",
            "lat": 10.0883,
            "lon": -84.4700,
            "elevation_m": 1057,
            "primary_crops": ["Café", "Caña de Azúcar", "Hortalizas", "Frutas"],
            "climate_type": "Premontano Húmedo",
        },
        {
            "name": "Naranjo",
            "canton": "Naranjo",
            "lat": 10.0989,
            "lon": -84.3878,
            "elevation_m": 1043,
            "primary_crops": ["Café de Origen Calidad Alta", "Cítricos"],
            "climate_type": "Premontano Húmedo",
        },
        {
            "name": "Grecia",
            "canton": "Grecia",
            "lat": 10.0739,
            "lon": -84.3122,
            "elevation_m": 999,
            "primary_crops": ["Caña de Azúcar (Ingenios)", "Café", "Fresa"],
            "climate_type": "Premontano Húmedo",
        },
        {
            "name": "Upala (Llanuras del Norte / Frontera)",
            "canton": "Upala",
            "lat": 10.8986,
            "lon": -85.0164,
            "elevation_m": 48,
            "primary_crops": ["Frijol", "Cacao", "Piña", "Raíces y Tubérculos"],
            "climate_type": "Tropical Húmedo / Llanuras",
        },
        {
            "name": "Los Chiles",
            "canton": "Los Chiles",
            "lat": 11.0333,
            "lon": -84.7167,
            "elevation_m": 43,
            "primary_crops": ["Naranja / Cítricos", "Piña", "Frijol", "Ganadería Extensiva"],
            "climate_type": "Tropical Húmedo Cálido",
        },
    ],
    "Cartago": [
        {
            "name": "Cartago Centro / Valle de El Guarco",
            "canton": "Cartago",
            "lat": 9.8644,
            "lon": -83.9194,
            "elevation_m": 1435,
            "primary_crops": ["Papa", "Cebolla", "Zanahoria", "Repollo", "Hortalizas"],
            "climate_type": "Montano Bajo Subtropical",
        },
        {
            "name": "Turrialba",
            "canton": "Turrialba",
            "lat": 9.9047,
            "lon": -83.6836,
            "elevation_m": 646,
            "primary_crops": ["Café", "Caña de Azúcar", "Queso Turrialba / Leche", "Macadamia", "Banano"],
            "climate_type": "Premontano Muy Húmedo Vertiente Caribe",
        },
        {
            "name": "Oreamuno / Potrero Cerrado (Faldas del Volcán Irazú)",
            "canton": "Oreamuno",
            "lat": 9.9167,
            "lon": -83.8833,
            "elevation_m": 2180,
            "primary_crops": ["Papa de Altura", "Cebolla", "Flores", "Lechería Especializada"],
            "climate_type": "Montano Alto Frío",
        },
        {
            "name": "Paraíso / Orosi / Cachí",
            "canton": "Paraíso",
            "lat": 9.8383,
            "lon": -83.8678,
            "elevation_m": 1325,
            "primary_crops": ["Café de Sombra", "Chayote (Exportación)", "Hortalizas"],
            "climate_type": "Premontano Húmedo",
        },
    ],
    "Heredia": [
        {
            "name": "Heredia Centro",
            "canton": "Heredia",
            "lat": 9.9989,
            "lon": -84.1169,
            "elevation_m": 1150,
            "primary_crops": ["Café", "Frutales"],
            "climate_type": "Premontano Húmedo",
        },
        {
            "name": "Barva",
            "canton": "Barva",
            "lat": 10.0219,
            "lon": -84.1239,
            "elevation_m": 1176,
            "primary_crops": ["Café de Altura", "Hortalizas"],
            "climate_type": "Premontano Húmedo Fértil Volcánico",
        },
        {
            "name": "Sarapiquí (Puerto Viejo)",
            "canton": "Sarapiquí",
            "lat": 10.4578,
            "lon": -84.0089,
            "elevation_m": 37,
            "primary_crops": ["Banano", "Piña", "Palmito", "Pimienta", "Yuca"],
            "climate_type": "Bosque Tropical Muy Húmedo / Caribe",
        },
    ],
    "Guanacaste": [
        {
            "name": "Liberia (Pampa Guanacasteca)",
            "canton": "Liberia",
            "lat": 10.6346,
            "lon": -85.4407,
            "elevation_m": 144,
            "primary_crops": ["Arroz bajo riego", "Caña de Azúcar", "Ganadería Bovina", "Melón"],
            "climate_type": "Bosque Tropical Seco (Pacífico Norte)",
        },
        {
            "name": "Nicoya (Península de Nicoya / Zona Azul)",
            "canton": "Nicoya",
            "lat": 10.1444,
            "lon": -85.4528,
            "elevation_m": 123,
            "primary_crops": ["Maíz", "Frijol", "Melón", "Sandía", "Ganadería"],
            "climate_type": "Bosque Tropical Seco / Sabana",
        },
        {
            "name": "Santa Cruz",
            "canton": "Santa Cruz",
            "lat": 10.2625,
            "lon": -85.5853,
            "elevation_m": 54,
            "primary_crops": ["Caña", "Arroz", "Melón para exportación", "Ganado"],
            "climate_type": "Bosque Tropical Seco",
        },
        {
            "name": "Cañas (Distrito de Riego Arenal-Tempisque)",
            "canton": "Cañas",
            "lat": 10.4311,
            "lon": -85.0931,
            "elevation_m": 86,
            "primary_crops": ["Arroz intensivo", "Caña de Azúcar", "Tilapia / Acuicultura"],
            "climate_type": "Bosque Tropical Seco con Riego",
        },
        {
            "name": "Tilarán",
            "canton": "Tilarán",
            "lat": 10.4722,
            "lon": -84.9686,
            "elevation_m": 564,
            "primary_crops": ["Café", "Ganado de Leche", "Macadamia"],
            "climate_type": "Premontano Húmedo con Vientos Fuertes",
        },
    ],
    "Puntarenas": [
        {
            "name": "Puntarenas Centro / Esparza",
            "canton": "Puntarenas",
            "lat": 9.9763,
            "lon": -84.8384,
            "elevation_m": 5,
            "primary_crops": ["Mango", "Aguacate criollo", "Melón", "Pesca y Acuicultura"],
            "climate_type": "Tropical Seco / Litoral Pacífico",
        },
        {
            "name": "Buenos Aires (Valle del Diquís)",
            "canton": "Buenos Aires",
            "lat": 9.1714,
            "lon": -83.3342,
            "elevation_m": 361,
            "primary_crops": ["Piña (Gran Escala)", "Café en zonas altas", "Ganado"],
            "climate_type": "Tropical Húmedo Pacífico Sur",
        },
        {
            "name": "Coto Brus (San Vito / Sabalito)",
            "canton": "Coto Brus",
            "lat": 8.8878,
            "lon": -82.9739,
            "elevation_m": 996,
            "primary_crops": ["Café de Especialidad", "Plátano", "Frijol", "Hortalizas"],
            "climate_type": "Premontano Muy Húmedo / Frontera Sur",
        },
        {
            "name": "Osa / Palmar Sur",
            "canton": "Osa",
            "lat": 8.9592,
            "lon": -83.4542,
            "elevation_m": 16,
            "primary_crops": ["Palma Aceitera (Africana)", "Arroz", "Banano"],
            "climate_type": "Bosque Muy Húmedo Tropical Pacífico Sur",
        },
        {
            "name": "Quepos / Parrita",
            "canton": "Quepos",
            "lat": 9.4319,
            "lon": -84.1619,
            "elevation_m": 8,
            "primary_crops": ["Palma Africana", "Arroz", "Papaya"],
            "climate_type": "Tropical Húmedo Costero",
        },
    ],
    "Limón": [
        {
            "name": "Limón Centro",
            "canton": "Limón",
            "lat": 9.9907,
            "lon": -83.0360,
            "elevation_m": 10,
            "primary_crops": ["Banano", "Plátano", "Cacao", "Coco"],
            "climate_type": "Bosque Muy Húmedo Tropical Caribe",
        },
        {
            "name": "Pococí (Guápiles)",
            "canton": "Pococí",
            "lat": 10.2167,
            "lon": -83.7833,
            "elevation_m": 262,
            "primary_crops": ["Piña", "Banano de Exportación", "Palmito", "Ganadería"],
            "climate_type": "Tropical Muy Húmedo Perenne",
        },
        {
            "name": "Siquirres",
            "canton": "Siquirres",
            "lat": 10.0975,
            "lon": -83.5067,
            "elevation_m": 62,
            "primary_crops": ["Banano", "Piña", "Cacao", "Yuca"],
            "climate_type": "Tropical Muy Húmedo Caribe",
        },
        {
            "name": "Talamanca (Bribri / Puerto Viejo de Talamanca)",
            "canton": "Talamanca",
            "lat": 9.6200,
            "lon": -82.8400,
            "elevation_m": 32,
            "primary_crops": ["Cacao Fino y de Aroma (Orgánico)", "Banano criollo", "Plátano", "Sistemas Agroforestales"],
            "climate_type": "Bosque Húmedo Tropical / Reserva Indígena y Caribe Sur",
        },
    ],
}


def get_all_locations() -> List[Dict[str, Any]]:
    """Return a flat list of all preset locations in Costa Rica."""
    all_locs = []
    for province, loc_list in COSTA_RICA_LOCATIONS.items():
        for item in loc_list:
            loc = item.copy()
            loc["province"] = province
            all_locs.append(loc)
    return all_locs


def find_closest_location(lat: float, lon: float) -> Dict[str, Any]:
    """Find the closest preset location using Euclidean distance."""
    all_locs = get_all_locations()
    best_loc = all_locs[0]
    min_dist = float("inf")
    for loc in all_locs:
        dist = math.hypot(loc["lat"] - lat, loc["lon"] - lon)
        if dist < min_dist:
            min_dist = dist
            best_loc = loc
    return best_loc
