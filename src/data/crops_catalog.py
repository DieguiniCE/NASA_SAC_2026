"""Crops Catalog and Agro-Climatic Suitability Rules for Costa Rica."""

from typing import Dict, Any, List


CROPS_CATALOG: Dict[str, Dict[str, Any]] = {
    "cafe": {
        "id": "cafe",
        "name": "Café Arábica (Coffea arabica)",
        "icon": "☕",
        "category": "Cultivo de Exportación / Altura",
        "temp_opt": (18.0, 24.0),
        "temp_tol": (15.0, 28.0),
        "precip_opt": (1400.0, 2200.0),  # mm/year
        "precip_tol": (1100.0, 2800.0),
        "humidity_opt": (65.0, 85.0),
        "elevation_opt": (900, 1900),
        "dry_season_months_opt": (2, 4),
        "description": "El café de Costa Rica se caracteriza por ser 100% Arábica. Requiere una estación seca definida para inducir una floración uniforme y buena maduración de la cereza.",
        "climate_vulnerability": "Muy vulnerable al aumento de temperaturas nocturnas (favorece la roya del café Hemileia vastatrix) y a lluvias atípicas durante la cosecha.",
        "best_known_regions": ["Tarrazú / Los Santos", "Naranjo / Valle Occidental", "Coto Brus", "Turrialba", "Tres Ríos"]
    },
    "cacao": {
        "id": "cacao",
        "name": "Cacao Fino y de Aroma (Theobroma cacao)",
        "icon": "🍫",
        "category": "Agroforestería / Tradicional",
        "temp_opt": (23.0, 30.0),
        "temp_tol": (20.0, 34.0),
        "precip_opt": (1600.0, 2800.0),
        "precip_tol": (1200.0, 3500.0),
        "humidity_opt": (75.0, 90.0),
        "elevation_opt": (0, 800),
        "dry_season_months_opt": (0, 3),
        "description": "Cultivo tropical perenne que prospera bajo sombra en sistemas agroforestales. Clave para la biodiversidad y la economía campesina e indígena en el Caribe y Norte.",
        "climate_vulnerability": "Sensible a sequías severas prolongadas y a humedades excesivas estancadas que propagan la Monilia (Moniliophthora roreri).",
        "best_known_regions": ["Talamanca", "Upala", "Guatuso", "Siquirres", "Sarapiquí"]
    },
    "pina": {
        "id": "pina",
        "name": "Piña Golden MD2 (Ananas comosus)",
        "icon": "🍍",
        "category": "Cultivo de Gran Escala de Exportación",
        "temp_opt": (22.0, 31.0),
        "temp_tol": (18.0, 35.0),
        "precip_opt": (1500.0, 2800.0),
        "precip_tol": (1000.0, 3600.0),
        "humidity_opt": (70.0, 88.0),
        "elevation_opt": (0, 600),
        "dry_season_months_opt": (1, 3),
        "description": "Costa Rica es uno de los mayores exportadores mundiales de piña fresca. Requiere suelos bien drenados, alta radiación solar y temperaturas cálidas constantes.",
        "climate_vulnerability": "Exceso de encharcamiento causa pudrición de raíz (Phytophthora); las olas de calor extremo pueden provocar quemaduras de sol en la fruta.",
        "best_known_regions": ["San Carlos", "Pococí / Guápiles", "Buenos Aires", "Sarapiquí", "Upala"]
    },
    "banano_platano": {
        "id": "banano_platano",
        "name": "Banano y Plátano (Musa spp.)",
        "icon": "🍌",
        "category": "Exportación y Seguridad Alimentaria",
        "temp_opt": (24.0, 32.0),
        "temp_tol": (20.0, 36.0),
        "precip_opt": (2000.0, 3500.0),
        "precip_tol": (1500.0, 4200.0),
        "humidity_opt": (75.0, 95.0),
        "elevation_opt": (0, 700),
        "dry_season_months_opt": (0, 2),
        "description": "Columna vertebral histórica de las exportaciones del litoral Caribe costarricense. Exige abundante humedad, calor constante y suelos fértiles aluviales.",
        "climate_vulnerability": "Vientos fuertes causan acame y derribo de plantas; temperaturas y humedad muy elevadas aceleran el ciclo de la Sigatoka Negra (Pseudocercospora fijiensis).",
        "best_known_regions": ["Limón", "Pococí", "Siquirres", "Matina", "Talamanca", "Golfito", "Corredores"]
    },
    "cana_azucar": {
        "id": "cana_azucar",
        "name": "Caña de Azúcar (Saccharum officinarum)",
        "icon": "🌾",
        "category": "Agroindustria / Azúcar y Biocombustible",
        "temp_opt": (22.0, 32.0),
        "temp_tol": (18.0, 36.0),
        "precip_opt": (1300.0, 2200.0),
        "precip_tol": (1000.0, 2800.0),
        "humidity_opt": (60.0, 80.0),
        "elevation_opt": (0, 1100),
        "dry_season_months_opt": (3, 5),
        "description": "Cultivo agroindustrial que necesita alta radiación solar para el crecimiento vegetativo y un período seco marcado para la maduración y concentración de sacarosa (zafra).",
        "climate_vulnerability": "Lluvias tardías durante la época de zafra reducen los grados Brix (rendimiento azucarero) y dificultan el paso de maquinaria pesada.",
        "best_known_regions": ["Guanacaste (Cañas, Carrillo, Liberia)", "Grecia", "San Ramón", "Turrialba", "Pérez Zeledón"]
    },
    "arroz": {
        "id": "arroz",
        "name": "Arroz (Oryza sativa)",
        "icon": "🍚",
        "category": "Grano Básico de Consumo Nacional",
        "temp_opt": (24.0, 33.0),
        "temp_tol": (20.0, 37.0),
        "precip_opt": (1600.0, 2500.0),
        "precip_tol": (1200.0, 3200.0),
        "humidity_opt": (65.0, 85.0),
        "elevation_opt": (0, 400),
        "dry_season_months_opt": (2, 4),
        "description": "Base de la dieta costarricense. Se produce tanto en secano (favorecido por lluvias regulares) como bajo sistemas de riego tecnificado (Distrito Arenal-Tempisque).",
        "climate_vulnerability": "Esterilidad del grano si las temperaturas sobrepasan 35°C durante la floración/antesis; vulnerable a sequías agudas inducidas por El Niño (ENOS).",
        "best_known_regions": ["Guanacaste (Distrito de Riego Arenal-Tempisque)", "Parrita", "Osa", "Upala"]
    },
    "papa": {
        "id": "papa",
        "name": "Papa (Solanum tuberosum)",
        "icon": "🥔",
        "category": "Hortícola de Clima Frío / Valle Central",
        "temp_opt": (12.0, 18.0),
        "temp_tol": (9.0, 22.0),
        "precip_opt": (1000.0, 1800.0),
        "precip_tol": (800.0, 2400.0),
        "humidity_opt": (70.0, 90.0),
        "elevation_opt": (1600, 3100),
        "dry_season_months_opt": (2, 4),
        "description": "Cultivo de altura fundamental en la provincia de Cartago y las faldas del Volcán Irazú. Requiere clima fresco para la adecuada tuberización.",
        "climate_vulnerability": "Temperaturas cálidas inhiben la formación de tubérculos; exceso de humedad desata tizón tardío (Phytophthora infestans).",
        "best_known_regions": ["Cartago (Oreamuno, Potrero Cerrado, Llano Grande, Alvarado)", "Zarcero"]
    },
    "yuca": {
        "id": "yuca",
        "name": "Yuca Parafinada y Fresca (Manihot esculenta)",
        "icon": "🍠",
        "category": "Raíz Tropical de Exportación",
        "temp_opt": (22.0, 30.0),
        "temp_tol": (18.0, 35.0),
        "precip_opt": (1200.0, 2500.0),
        "precip_tol": (800.0, 3500.0),
        "humidity_opt": (65.0, 85.0),
        "elevation_opt": (0, 900),
        "dry_season_months_opt": (1, 4),
        "description": "Cultivo sumamente rústico y tolerante a condiciones edáficas complejas. Costa Rica es líder en exportación de yuca fresca parafinada a Norteamérica y Europa.",
        "climate_vulnerability": "Tolerante a la sequía gracias a su sistema radicular profundo, pero vulnerable a pudriciones bacterianas con saturación freática.",
        "best_known_regions": ["San Carlos", "Pococí", "Upala", "Siquirres", "Pérez Zeledón"]
    },
    "frijol": {
        "id": "frijol",
        "name": "Frijol Negro y Rojo (Phaseolus vulgaris)",
        "icon": "🫘",
        "category": "Grano Básico de Seguridad Alimentaria",
        "temp_opt": (18.0, 26.0),
        "temp_tol": (15.0, 30.0),
        "precip_opt": (1000.0, 1800.0),
        "precip_tol": (700.0, 2400.0),
        "humidity_opt": (60.0, 80.0),
        "elevation_opt": (200, 1400),
        "dry_season_months_opt": (2, 4),
        "description": "Alimento básico nacional. En Costa Rica se cultiva bajo el sistema de frijol tapado y en siembras tecnificadas en la zona norte y sur.",
        "climate_vulnerability": "Muy sensible a lluvias intensas en la fase de madurez y cosecha (provoca germinación en vaina y antracnosis) y al estrés por calor prolongado.",
        "best_known_regions": ["Upala", "Los Chiles", "Pérez Zeledón", "Coto Brus", "Buenos Aires"]
    }
}


def evaluate_crop_suitability(crop_id: str, annual_temp: float, annual_precip: float, annual_humidity: float) -> Dict[str, Any]:
    """
    Evaluates suitability score (0-100) and details for a crop based on climatic parameters.
    """
    crop = CROPS_CATALOG.get(crop_id)
    if not crop:
        return {"error": "Crop not found"}

    temp_score = 100.0
    precip_score = 100.0
    hum_score = 100.0
    notes = []

    # 1. Temperature evaluation
    t_min_opt, t_max_opt = crop["temp_opt"]
    t_min_tol, t_max_tol = crop["temp_tol"]

    if t_min_opt <= annual_temp <= t_max_opt:
        notes.append(f"✅ Temperatura ideal ({annual_temp:.1f}°C, óptimo: {t_min_opt}-{t_max_opt}°C).")
    elif t_min_tol <= annual_temp <= t_max_tol:
        temp_score = 65.0
        if annual_temp < t_min_opt:
            notes.append(f"⚠️ Temperatura algo fresca ({annual_temp:.1f}°C), tolerable pero fuera del óptimo.")
        else:
            notes.append(f"⚠️ Temperatura algo elevada ({annual_temp:.1f}°C), tolerable pero fuera del óptimo.")
    else:
        temp_score = 20.0
        if annual_temp < t_min_tol:
            notes.append(f"❌ Clima demasiado frío ({annual_temp:.1f}°C, mín tolerable: {t_min_tol}°C).")
        else:
            notes.append(f"❌ Clima excesivamente caluroso ({annual_temp:.1f}°C, máx tolerable: {t_max_tol}°C).")

    # 2. Precipitation evaluation
    p_min_opt, p_max_opt = crop["precip_opt"]
    p_min_tol, p_max_tol = crop["precip_tol"]

    if p_min_opt <= annual_precip <= p_max_opt:
        notes.append(f"✅ Precipitación adecuada ({annual_precip:.0f} mm/año, rango óptimo: {p_min_opt:.0f}-{p_max_opt:.0f} mm).")
    elif p_min_tol <= annual_precip <= p_max_tol:
        precip_score = 65.0
        if annual_precip < p_min_opt:
            notes.append(f"⚠️ Precipitación baja ({annual_precip:.0f} mm/año), requerirá riego de apoyo.")
        else:
            notes.append(f"⚠️ Precipitación alta ({annual_precip:.0f} mm/año), requerirá drenajes eficientes.")
    else:
        precip_score = 20.0
        if annual_precip < p_min_tol:
            notes.append(f"❌ Déficit hídrico severo ({annual_precip:.0f} mm/año, mínimo: {p_min_tol:.0f} mm).")
        else:
            notes.append(f"❌ Lluvia excesiva destructiva ({annual_precip:.0f} mm/año, máximo: {p_max_tol:.0f} mm).")

    # 3. Humidity evaluation
    h_min_opt, h_max_opt = crop["humidity_opt"]
    if h_min_opt <= annual_humidity <= h_max_opt:
        notes.append(f"✅ Humedad relativa favorable ({annual_humidity:.1f}%, óptimo: {h_min_opt:.0f}-{h_max_opt:.0f}%).")
    elif (h_min_opt - 12.0) <= annual_humidity <= (h_max_opt + 10.0):
        hum_score = 70.0
        notes.append(f"⚠️ Humedad relativa aceptable ({annual_humidity:.1f}%).")
    else:
        hum_score = 35.0
        notes.append(f"❌ Humedad relativa desfavorecedora ({annual_humidity:.1f}%).")

    # Overall weighted score
    overall_score = round(0.40 * temp_score + 0.40 * precip_score + 0.20 * hum_score)

    if overall_score >= 85:
        verdict = "Altamente Recomendado (Condiciones Óptimas)"
        badge_color = "green"
    elif overall_score >= 65:
        verdict = "Recomendado con Manejo Agronómico"
        badge_color = "blue"
    elif overall_score >= 45:
        verdict = "Marginal / Alto Riesgo Climático"
        badge_color = "orange"
    else:
        verdict = "No Recomendado (Clima Incompatible)"
        badge_color = "red"

    return {
        "crop": crop,
        "score": overall_score,
        "verdict": verdict,
        "badge_color": badge_color,
        "notes": notes,
        "scores_breakdown": {
            "temperature": round(temp_score),
            "precipitation": round(precip_score),
            "humidity": round(hum_score)
        }
    }
