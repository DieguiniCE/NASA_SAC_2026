"""
Instituto Meteorológico Nacional de Costa Rica (IMN) & MAG/CIA-UCR Service.
Implements:
  - Soil Orders in Costa Rica (Andisoles, Ultisoles, Inceptisoles, Alfisoles, Vertisoles, Entisoles)
  - Soil Absorption Potential & Infiltration Rates (mm/h, AWC)
  - Water Erosion Risk Engine (RUSLE model approximation: R * K * LS)
  - IMN Climate Change Projections (Escenarios Regionalizados 2030 y 2050 para CR)
"""

from typing import Dict, Any, List
import math
from src.data.costa_rica_locations import find_closest_location


# Soil Orders in Costa Rica and their agronomic/hydraulic properties
# Based on MAG / Centro de Investigaciones Agronómicas (CIA-UCR) / IMN cartography
SOIL_ORDERS_DATA: Dict[str, Dict[str, Any]] = {
    "Andisol": {
        "order": "Andisol (Suelo de ceniza volcánica)",
        "coverage_cr_pct": 14.5,
        "texture": "Franco a franco-limoso con alofana",
        "ph_range": (5.2, 6.5),
        "organic_matter": "Muy Alta (>8%)",
        "erodibility_K": 0.12,  # Resilient to detachment due to stable aggregates
        "absorption_potential": "Muy Alto",
        "infiltration_rate_mm_h": 45.0,  # Fast, highly porous
        "available_water_capacity_mm_m": 180.0,
        "drainage": "Excelente a moderado",
        "description": "Suelos volcánicos de alta fertilidad física, esponjosos, gran retención de humedad sin anegamiento. Predominan en el Valle Central y faldas de las cordilleras volcánicas (Irazú, Poás, Barva, Turrialba).",
        "agronomic_recommendation": "Ideal para hortalizas de altura, café de especialidad, fresa y papa. Se debe vigilar la fijación de fósforo por la alofana.",
    },
    "Ultisol": {
        "order": "Ultisol (Suelo rojo tropical meteorizado)",
        "coverage_cr_pct": 21.0,
        "texture": "Arcillosa con acumulación de óxidos de hierro y aluminio",
        "ph_range": (4.2, 5.2),
        "organic_matter": "Media a baja (<3.5%)",
        "erodibility_K": 0.24,  # Moderate to high erodibility when bare
        "absorption_potential": "Moderado a Lento",
        "infiltration_rate_mm_h": 14.0,
        "available_water_capacity_mm_m": 120.0,
        "drainage": "Moderado a imperfecto en subsuelo",
        "description": "Suelos rojos muy antiguos, fuertemente lavados y ácidos. Predominan en el Caribe, llanuras de San Carlos, Sarapiquí y el Pacífico Sur (Buenos Aires, Golfito).",
        "agronomic_recommendation": "Requiere encalado regular para corregir acidez y toxicidad de aluminio. Apto para piña, palma aceitera, banano y pastos tolerantes a la acidez.",
    },
    "Inceptisol": {
        "order": "Inceptisol (Suelo de desarrollo incipiente)",
        "coverage_cr_pct": 38.0,
        "texture": "Franco-arcillo-limosa",
        "ph_range": (5.0, 6.2),
        "organic_matter": "Moderada (3 - 5%)",
        "erodibility_K": 0.28,  # Moderate erodibility on hillsides
        "absorption_potential": "Moderadamente Alto",
        "infiltration_rate_mm_h": 24.0,
        "available_water_capacity_mm_m": 145.0,
        "drainage": "Bueno",
        "description": "El orden más extendido en Costa Rica. Suelos jóvenes en laderas y terrazas aluviales con buena capacidad de retención y fertilidad química moderada.",
        "agronomic_recommendation": "Gran versatilidad agrícola (café, frutales, maíz, frijol). En laderas requiere estrictas obras de conservación para mitigar la erosión.",
    },
    "Alfisol": {
        "order": "Alfisol (Suelo fértil con saturación de bases)",
        "coverage_cr_pct": 9.5,
        "texture": "Franco-arcillosa rica en nutrientes básicos",
        "ph_range": (5.8, 7.0),
        "organic_matter": "Media (2.5 - 4%)",
        "erodibility_K": 0.32,  # Susceptible to crusting during dry-wet transitions
        "absorption_potential": "Moderado",
        "infiltration_rate_mm_h": 18.0,
        "available_water_capacity_mm_m": 135.0,
        "drainage": "Bueno a moderado",
        "description": "Suelos fértiles propios de regiones con estación seca bien definida. Abundantes en la provincia de Guanacaste y el Pacífico Central.",
        "agronomic_recommendation": "Altamente productivos para caña de azúcar, arroz bajo riego, melón, mango y ganadería intensiva.",
    },
    "Vertisol": {
        "order": "Vertisol (Arcillas expansivas 2:1 / Sonzocuites)",
        "coverage_cr_pct": 3.0,
        "texture": "Arcillosa pesada (>50% arcillas montmorilloníticas)",
        "ph_range": (6.5, 7.8),
        "organic_matter": "Media (2 - 3%)",
        "erodibility_K": 0.22,
        "absorption_potential": "Muy Lento a Nulo cuando saturado (se expande y sella)",
        "infiltration_rate_mm_h": 2.5,  # Almost impermeable when wet
        "available_water_capacity_mm_m": 190.0,
        "drainage": "Muy deficiente / encharcamiento prolongado",
        "description": "Suelos negros pesados de las bajuras del Río Tempisque (Cañas, Bagaces, Filadelfia). Se agrietan profundamente en verano y se sellan impermeables en invierno.",
        "agronomic_recommendation": "Idóneo para arroz inundado y caña de azúcar. Inadecuado para árboles frutales o café por asfixia radicular.",
    },
    "Entisol": {
        "order": "Entisol (Suelo aluvial reciente / poco evolucionado)",
        "coverage_cr_pct": 6.5,
        "texture": "Arenosa a franco-arenosa estratificada",
        "ph_range": (5.5, 6.8),
        "organic_matter": "Baja (<2%)",
        "erodibility_K": 0.35,  # High erodibility / easily washed by river floods
        "absorption_potential": "Muy Rápido (alta percolación)",
        "infiltration_rate_mm_h": 60.0,
        "available_water_capacity_mm_m": 90.0,
        "drainage": "Excesivo a imperfecto por nivel freático alto",
        "description": "Suelos muy jóvenes ubicados en vegas de ríos, deltas costeros y planicies de inundación reciente (ríos Térraba, Reventazón, Sixaola).",
        "agronomic_recommendation": "Apto para plátano, banano y cultivos de ciclo corto con riesgo de inundación estacional.",
    }
}


# Regional Climate Change Scenarios for Costa Rica (IMN 2030 / 2050)
IMN_REGIONAL_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "Central": {
        "region_name": "Región Central (Valle Central y Macizo)",
        "temp_change_2030": "+1.1 °C",
        "temp_change_2050": "+2.1 °C",
        "precip_change_2030": "-8 %",
        "precip_change_2050": "-18 %",
        "dry_season_impact": "Estación seca se extiende 15-20 días adicionales; veranillos de julio más prolongados.",
        "extreme_rain_impact": "Eventos de lluvia torrencial concentrada aumentan un 22% (riesgo de escorrentía en laderas).",
    },
    "Chorotega": {
        "region_name": "Región Chorotega (Pacífico Norte / Guanacaste)",
        "temp_change_2030": "+1.4 °C",
        "temp_change_2050": "+2.6 °C",
        "precip_change_2030": "-14 %",
        "precip_change_2050": "-26 %",
        "dry_season_impact": "Sequías extremas más severas en el corredor seco; estrés térmico para cultivos sin riego.",
        "extreme_rain_impact": "Ciclones tropicales indirectos generan crecidas súbitas en cuenca del Tempisque.",
    },
    "Huetar Norte": {
        "region_name": "Región Huetar Norte (San Carlos, Upala, Los Chiles)",
        "temp_change_2030": "+1.2 °C",
        "temp_change_2050": "+2.2 °C",
        "precip_change_2030": "+5 %",
        "precip_change_2050": "+12 %",
        "dry_season_impact": "Disminución de períodos secos continuos; mayor humedad ambiental constante.",
        "extreme_rain_impact": "Anegamiento recurrente en llanuras bajas; proliferación de hongos fitopatógenos.",
    },
    "Huetar Caribe": {
        "region_name": "Región Huetar Caribe (Limón, Pococí, Talamanca)",
        "temp_change_2030": "+1.0 °C",
        "temp_change_2050": "+2.0 °C",
        "precip_change_2030": "+8 %",
        "precip_change_2050": "+16 %",
        "dry_season_impact": "Régimen perhúmedo; aumento del nivel del mar compromete acuíferos costeros.",
        "extreme_rain_impact": "Frentes fríos invernales provocan inundaciones severas y desbordamientos en plantaciones bananeras.",
    },
    "Brunca": {
        "region_name": "Región Brunca (Pacífico Sur / Pérez Zeledón, Coto Brus, Osa)",
        "temp_change_2030": "+1.2 °C",
        "temp_change_2050": "+2.3 °C",
        "precip_change_2030": "-4 %",
        "precip_change_2050": "-10 %",
        "dry_season_impact": "Variabilidad marcada entre laderas altas y llanura costera del Golfo Dulce.",
        "extreme_rain_impact": "Deslizamientos frecuentes en la Fila Brunqueña por lluvias de gran intensidad.",
    },
    "Pacífico Central": {
        "region_name": "Región Pacífico Central (Puntarenas, Esparza, Quepos, Parrita)",
        "temp_change_2030": "+1.3 °C",
        "temp_change_2050": "+2.4 °C",
        "precip_change_2030": "-9 %",
        "precip_change_2050": "-19 %",
        "dry_season_impact": "Mayor evapotranspiración en costa; salinización incipiente en suelos de bajura.",
        "extreme_rain_impact": "Oleajes y marejadas combinadas con descargas fluviales en la desembocadura de los ríos.",
    }
}


class IMNCostaRicaService:
    """Service connector for Instituto Meteorológico Nacional de Costa Rica soil and climate projection data."""

    @classmethod
    def get_soil_and_climate_projections(
        cls,
        lat: float,
        lon: float,
        elevation_m: int = 1000,
        r_erosivity: float = 4200.0,
        ls_topographic: float = 2.5
    ) -> Dict[str, Any]:
        """
        Determines the dominant soil order, soil absorption potential,
        calculates water erosion risk via RUSLE approximation, and attaches
        IMN 2030/2050 climate change projection scenarios.
        """
        # Determine IMN Climate Region
        if lon < -85.0 and lat > 9.8:
            region_key = "Chorotega"
        elif (lat >= 10.0 and lon >= -84.2) or (lat < 10.0 and lon >= -83.6 and lat > 9.4):
            region_key = "Huetar Caribe"
        elif lat > 10.3 and lon < -84.2:
            region_key = "Huetar Norte"
        elif lat < 9.4 and lon < -83.1:
            region_key = "Brunca"
        elif lon < -84.5 and lat <= 10.0:
            region_key = "Pacífico Central"
        else:
            region_key = "Central"

        imn_projection = IMN_REGIONAL_SCENARIOS[region_key]

        # Determine Dominant Soil Order in Costa Rica based on geography and elevation:
        # Andisoles: Volcanic mountain regions & central valley (elev > 900 in central parts)
        # Vertisoles: Tempisque lowlands (lon < -85.0, elev < 80)
        # Alfisoles: Guanacaste / Pacific Dry low-to-mid lands
        # Ultisoles: Humid Caribbean & South Pacific weathered lowlands
        # Inceptisoles: General hillsides, Premontane valleys
        # Entisoles: River floodplains and coastal strips (elev < 15 near river basins)
        if lon < -85.0 and elevation_m < 80:
            soil_key = "Vertisol"
        elif lon < -85.0:
            soil_key = "Alfisol"
        elif (9.7 <= lat <= 10.4) and (-84.5 <= lon <= -83.6) and elevation_m >= 850:
            soil_key = "Andisol"
        elif (lon >= -84.2 and lat >= 10.0) or (lat <= 9.3 and lon <= -83.3):
            soil_key = "Ultisol"
        elif elevation_m < 15:
            soil_key = "Entisol"
        else:
            soil_key = "Inceptisol"

        soil_data = SOIL_ORDERS_DATA[soil_key]
        k_factor = soil_data["erodibility_K"]

        # Water Erosion Risk Calculation (RUSLE: A = R * K * LS * C * P)
        # Using typical baseline vegetation cover factor C ~ 0.20 (mixed agricultural / pasture)
        # and support practice factor P ~ 0.85
        c_factor = 0.20
        p_factor = 0.85
        estimated_soil_loss_t_ha_yr = round(r_erosivity * k_factor * ls_topographic * c_factor * p_factor * 0.01, 1)

        if estimated_soil_loss_t_ha_yr < 12.0:
            erosion_risk = "Bajo (Pérdida de suelo < 12 ton/ha/año)"
            risk_color = "green"
            erosion_advice = "Suelo protegido con tasa de regeneración natural estable."
        elif estimated_soil_loss_t_ha_yr < 30.0:
            erosion_risk = "Moderado (12 - 30 ton/ha/año)"
            risk_color = "blue"
            erosion_advice = "Requiere laboreo en contorno y mantenimiento de coberturas de rastrojo."
        elif estimated_soil_loss_t_ha_yr < 65.0:
            erosion_risk = "Alto (30 - 65 ton/ha/año)"
            risk_color = "orange"
            erosion_advice = "Peligro de pérdida de horizonte fértil. Imprescindible siembra en curvas de nivel, terrazas y barreras vivas (Zacate Vetiver)."
        else:
            erosion_risk = "Crítico / Extremo (> 65 ton/ha/año)"
            risk_color = "red"
            erosion_advice = "Riesgo inminente de cárcavas y deslaves. No apto para labranza limpia; requiere reforestación o SAF denso."

        return {
            "source": "Instituto Meteorológico Nacional de Costa Rica (IMN) / MAG / CIA-UCR",
            "imn_climate_region": imn_projection["region_name"],
            "climate_change_projections": imn_projection,
            "soil_order_classified": soil_key,
            "soil_details": soil_data,
            "soil_absorption_potential": soil_data["absorption_potential"],
            "infiltration_rate_mm_h": soil_data["infiltration_rate_mm_h"],
            "available_water_capacity_mm_m": soil_data["available_water_capacity_mm_m"],
            "erosion_risk_analysis": {
                "rusle_factors": {
                    "R_rainfall_erosivity": r_erosivity,
                    "K_soil_erodibility": k_factor,
                    "LS_topographic": ls_topographic,
                    "C_cover_factor": c_factor,
                    "P_conservation_factor": p_factor,
                },
                "estimated_loss_ton_ha_yr": estimated_soil_loss_t_ha_yr,
                "risk_level": erosion_risk,
                "risk_color": risk_color,
                "conservation_advice": erosion_advice,
            }
        }
