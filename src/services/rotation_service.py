"""
Crop Rotation & Agroecological Diversification Service.
Analyzes viability and benefits of crop rotations for Costa Rican agricultural zones.
Evaluates rotation sequences against monoculture based on soil health, pest disruption,
water-balance resilience, and erosion mitigation.
"""

from typing import Dict, Any, List


# Secondary rotation partners and cover crops widely used in Costa Rica
ROTATION_PARTNERS = {
    "beans_legumes": {
        "name_es": "Frijol / Leguminosas de Cobertura (Phaseolus / Canavalia)",
        "name_en": "Beans / Cover Legumes (Phaseolus / Canavalia)",
        "icon": "🫘",
        "category": "Fijación Biológica de Nitrógeno",
        "category_en": "Biological Nitrogen Fixation",
        "water_needs": "Bajo a moderado (300-500 mm/ciclo)",
        "water_needs_en": "Low to moderate (300-500 mm/cycle)",
        "soil_benefit": "+30-50 kg N/ha fijado biológicamente; incrementa materia orgánica.",
        "soil_benefit_en": "+30-50 kg N/ha biologically fixed; increases organic matter.",
        "pest_break": "Rompe ciclo de nemátodos y hongos del suelo en monocultivos.",
        "pest_break_en": "Disrupts nematode and soil-borne fungal cycles in monoculture.",
        "optimal_elev": (0, 1600),
        "ideal_temp": (18, 28),
    },
    "maize_cereal": {
        "name_es": "Maíz / Sorgo (Zea mays / Sorghum)",
        "name_en": "Maize / Sorghum (Zea mays / Sorghum)",
        "icon": "🌽",
        "category": "Biomasa & Micorrizas",
        "category_en": "Biomass & Mycorrhizae",
        "water_needs": "Moderado (500-750 mm/ciclo)",
        "water_needs_en": "Moderate (500-750 mm/cycle)",
        "soil_benefit": "Aporte masivo de rastrojo superficial (mulch), previene erosión por impacto pluvial.",
        "soil_benefit_en": "Massive surface mulch contribution, prevents rainfall splash erosion.",
        "pest_break": "No comparte plagas mayores con café o banano.",
        "pest_break_en": "Does not share major pests with coffee or banana.",
        "optimal_elev": (0, 1400),
        "ideal_temp": (20, 30),
    },
    "cassava_roots": {
        "name_es": "Yuca / Camote (Manihot esculenta / Ipomoea)",
        "name_en": "Cassava / Sweet Potato (Manihot esculenta / Ipomoea)",
        "icon": "🍠",
        "category": "Descompactación Radicular",
        "category_en": "Root Decompaction",
        "water_needs": "Tolerante a sequía estacional (600-1200 mm)",
        "water_needs_en": "Drought tolerant (600-1200 mm)",
        "soil_benefit": "Raíces profundas que rompen piso de arado en suelos compactados.",
        "soil_benefit_en": "Deep roots that penetrate hardpan in compacted soils.",
        "pest_break": "Excelente rotación posterior a piña o caña.",
        "pest_break_en": "Excellent rotation following pineapple or sugarcane.",
        "optimal_elev": (0, 1000),
        "ideal_temp": (22, 32),
    },
    "green_manure": {
        "name_es": "Abono Verde / Crotalaria (Crotalaria juncea / Mucuna)",
        "name_en": "Green Manure / Crotalaria (Crotalaria juncea / Mucuna)",
        "icon": "🌿",
        "category": "Biofumigación & Nemátodos",
        "category_en": "Biofumigation & Nematodes",
        "water_needs": "Bajo (rápido establecimiento en 60-90 días)",
        "water_needs_en": "Low (rapid establishment in 60-90 days)",
        "soil_benefit": "Control natural de nemátodos agalladores (Meloidogyne spp.); fija N.",
        "soil_benefit_en": "Natural control of root-knot nematodes (Meloidogyne spp.); fixes N.",
        "pest_break": "Efecto biofumigante comprobado contra patógenos del suelo.",
        "pest_break_en": "Proven biofumigation effect against soil-borne pathogens.",
        "optimal_elev": (0, 1800),
        "ideal_temp": (17, 30),
    },
}


# Rotation plans for the 5 target crops in GEMINI.md
CROP_ROTATION_PLANS = {
    "Coffee": {
        "rotation_type": "Agroforestal & Cobertura Viva (Agroforestry & Living Mulch)",
        "schedule": [
            {"year": "Año 1", "year_en": "Year 1", "phase": "☕ Café Productivo + Poda y Deshije", "phase_en": "Productive Coffee + Pruning", "role": "Cultivo Principal / Cash Crop"},
            {"year": "Año 2", "year_en": "Year 2", "phase": "🫘 Intercalado con Frijol Tapado / Canavalia", "phase_en": "Intercropped with Beans / Canavalia", "role": "Fijación de Nitrógeno y control de malezas"},
            {"year": "Año 3", "year_en": "Year 3", "phase": "🌿 Abono Verde (Crotalaria) en calles de café", "phase_en": "Green Manure (Crotalaria) in alleys", "role": "Control biológico de nemátodos y mulch orgánico"},
            {"year": "Año 4", "year_en": "Year 4", "phase": "☕ Renovación de tejido / Cosecha plena", "phase_en": "Tissue renewal / Full harvest", "role": "Pico de productividad con suelo regenerado"},
        ],
        "primary_partner": "beans_legumes",
        "secondary_partner": "green_manure",
        "benefits_es": [
            "Ahorro de hasta un 30% en fertilización nitrogenada sintética mediante simbiosis Rhizobium.",
            "Supresión natural de nemátodos agalladores y de lesiones en raíces de cafeto.",
            "Protección contra erosión laminar en laderas pronunciadas comunes en zonas cafetaleras (Tarrazú, Naranjo, Turrialba).",
            "Mantenimiento de humedad en época seca (Veranillo de San Juan).",
        ],
        "benefits_en": [
            "Saves up to 30% in synthetic nitrogen fertilizer through Rhizobium symbiosis.",
            "Natural suppression of root-knot and lesion nematodes in coffee roots.",
            "Protection against sheet erosion on steep slopes typical of coffee areas (Tarrazú, Naranjo, Turrialba).",
            "Moisture retention during dry spells (Midsummer drought / Veranillo).",
        ],
        "risks_es": [
            "Evitar especies trepadoras agresivas que puedan asfixiar las ramas productivas de café.",
            "Monitorear humedad excesiva que propicie Ojo de Gallo (Mycena citricolor) en altitudes > 1200 m.",
        ],
        "risks_en": [
            "Avoid aggressive climbing vines that could smother productive coffee branches.",
            "Monitor excess humidity that could trigger American Leaf Spot (Mycena citricolor) above 1200 m.",
        ],
    },
    "Banana": {
        "rotation_type": "Rotación Post-Ciclo & Barbecho Mejorado (Fallow & Root Regeneration)",
        "schedule": [
            {"year": "Año 1-2", "year_en": "Year 1-2", "phase": "🍌 Banano Ciclo 1 & Retoños (Ratoon)", "phase_en": "Banana Cycle 1 & Ratoons", "role": "Extracción y producción alta"},
            {"year": "Año 3", "year_en": "Year 3", "phase": "🌽 Maíz de Cobertura / Crotalaria", "phase_en": "Cover Maize / Crotalaria", "role": "Corte de ciclo biológico de Sigatoka y nemátodos"},
            {"year": "Año 4", "year_en": "Year 4", "phase": "🫘 Leguminosa rastrera (Mucuna pruriens)", "phase_en": "Trailing legume (Mucuna pruriens)", "role": "Restitución de potasio y estructura de suelo aluvial"},
        ],
        "primary_partner": "green_manure",
        "secondary_partner": "maize_cereal",
        "benefits_es": [
            "Disrupción del inóculo de hongos del suelo (Fusarium oxysporum / Mal de Panamá y Radopholus similis).",
            "Reestructuración de horizontes compactados por maquinaria pesada y tránsito continuo de cosecha.",
            "Aporte masivo de biomasa vegetal que amortigua el exceso hídrico en el Caribe (Limón / Sarapiquí).",
        ],
        "benefits_en": [
            "Disruption of soil fungal inoculum (Fusarium oxysporum / Panama Disease and Radopholus similis).",
            "Restructuring of horizons compacted by heavy machinery and continuous harvest traffic.",
            "Massive plant biomass contribution buffering excess rainfall in the Caribbean (Limón / Sarapiquí).",
        ],
        "risks_es": [
            "Drenaje deficiente puede causar pudrición de rizomas de cultivos rotacionales en llanuras aluviales.",
        ],
        "risks_en": [
            "Poor drainage may cause root rot in rotational crops on alluvial floodplains.",
        ],
    },
    "Sugar Cane": {
        "rotation_type": "Rotación Entre Socas & Leguminosa Estacional (Inter-Ratoon Rotation)",
        "schedule": [
            {"year": "Año 1-4", "year_en": "Year 1-4", "phase": "🌾 Caña de Azúcar (Plantilla y 3 Socas)", "phase_en": "Sugar Cane (Plant cane and 3 ratoons)", "role": "Cosecha comercial sucesiva"},
            {"year": "Año 5 (Entrezafra)", "year_en": "Year 5 (Inter-season)", "phase": "🫘 Soya o Frijol Caupí de ciclo corto (90 días)", "phase_en": "Short-cycle Soy or Cowpea (90 days)", "role": "Recuperación de fertilidad y descanso del suelo"},
            {"year": "Año 5 (Siembra)", "year_en": "Year 5 (Planting)", "phase": "🌾 Nueva Plantilla de Caña", "phase_en": "New Cane Planting", "role": "Reinicio de ciclo con vigor incrementado"},
        ],
        "primary_partner": "beans_legumes",
        "secondary_partner": "green_manure",
        "benefits_es": [
            "Rompe la fatiga del suelo tras múltiples socas y reduce infestación de malezas gramíneas.",
            "Aporta hasta 60 kg N/ha disponible para la nueva plantilla de caña.",
            "Disminuye la incidencia del taladrador del tallo (Diatraea spp.).",
        ],
        "benefits_en": [
            "Breaks soil fatigue after multiple ratoon cycles and reduces grass weed infestation.",
            "Provides up to 60 kg N/ha available for the new cane planting.",
            "Decreases incidence of sugarcane borer (Diatraea spp.).",
        ],
        "risks_es": [
            "Ventana corta entre zafra y lluvias requiere variedades de leguminosas de maduración temprana.",
        ],
        "risks_en": [
            "Short window between harvest and rainy season requires early-maturing legume varieties.",
        ],
    },
    "Pineapple": {
        "rotation_type": "Biofumigación Post-Rastrojo & Desintoxicación (Biofumigation & Detox)",
        "schedule": [
            {"year": "Año 1-2", "year_en": "Year 1-2", "phase": "🍍 Piña (Cosecha principal y cosecha inducida)", "phase_en": "Pineapple (Main crop and ratoon harvest)", "role": "Extracción intensiva de nutrientes"},
            {"year": "Año 3 (Fase 1)", "year_en": "Year 3 (Phase 1)", "phase": "🌿 Incorporación de rastrojo + Crotalaria juncea", "phase_en": "Stubble incorporation + Crotalaria juncea", "role": "Biofumigación y control de Symphylidos"},
            {"year": "Año 3 (Fase 2)", "year_en": "Year 3 (Phase 2)", "phase": "🍠 Yuca / Camote o Pasto Brachiaria", "phase_en": "Cassava / Sweet Potato or Brachiaria grass", "role": "Descompactación y lavado biológico de agroquímicos"},
            {"year": "Año 4", "year_en": "Year 4", "phase": "🍍 Nueva siembra de Piña", "phase_en": "New Pineapple planting", "role": "Suelo regenerado sin acumulamiento de nemátodos"},
        ],
        "primary_partner": "green_manure",
        "secondary_partner": "cassava_roots",
        "benefits_es": [
            "Solución biológica al grave problema de sinfilidos (Scutigerella) y nemátodos en piñeras.",
            "Mejora la permeabilidad en suelos Ultisoles arcillosos de la Zona Norte y Huetar Norte.",
            "Reduce la acidez residual y la fitotoxicidad de herbicidas aplicados en ciclos anteriores.",
        ],
        "benefits_en": [
            "Biological solution to the severe symphylid (Scutigerella) and nematode issue in pineapple fields.",
            "Improves permeability in acidic Ultisol clays of Northern Costa Rica (San Carlos / Upala).",
            "Reduces residual acidity and phytotoxicity from herbicides applied in previous cycles.",
        ],
        "risks_es": [
            "El rastrojo de piña genera gran volumen de acidez; requiere adecuada aireación al incorporar.",
        ],
        "risks_en": [
            "Pineapple stubble generates large acidic volume; requires adequate aeration during tillage.",
        ],
    },
    "Avocado": {
        "rotation_type": "Agrosilvicultura & Cobertura Viva Anti-Phytophthora (Agroforestry Living Cover)",
        "schedule": [
            {"year": "Permanente", "year_en": "Permanent", "phase": "🥑 Aguacate Hass / Antillano", "phase_en": "Avocado Hass / West Indian", "role": "Cultivo perenne frutal"},
            {"year": "Estacional", "year_en": "Seasonal", "phase": "🫘 Cobertura viva de Maní Forrajero (Arachis pintoi)", "phase_en": "Living cover of Forage Peanut (Arachis pintoi)", "role": "Protección contra pudrición radicular"},
            {"year": "Intermitente", "year_en": "Intermittent", "phase": "🌽 Siembra en calles anchas de Maíz criollo", "phase_en": "Wide-alley cropping with native Maize", "role": "Ingreso extra en etapa juvenil del huerto"},
        ],
        "primary_partner": "beans_legumes",
        "secondary_partner": "maize_cereal",
        "benefits_es": [
            "La cobertura viva compite contra el patógeno Phytophthora cinnamomi (tristeza del aguacate).",
            "Evita el salpicado de lluvia sobre los troncos que propaga antracnosis y hongos vasculares.",
            "Disminuye la temperatura del suelo en verano en 2-4°C, protegiendo las raíces superficiales.",
        ],
        "benefits_en": [
            "Living cover actively competes against Phytophthora cinnamomi root rot.",
            "Prevents rain-splash on tree trunks that spreads anthracnose and vascular fungi.",
            "Lowers summer soil surface temperatures by 2-4°C, protecting feeder roots.",
        ],
        "risks_es": [
            "No debe competir por luz ni trepar al tronco del árbol de aguacate.",
            "Asegurar drenaje excepcional en época de tormentas tropicales.",
        ],
        "risks_en": [
            "Must not compete for light or climb the avocado tree trunk.",
            "Ensure exceptional drainage during tropical storm events.",
        ],
    },
}


class RotationAnalysisService:
    """Calculates viability scores and agronomic performance for crop rotation vs monoculture."""

    @classmethod
    def evaluate_rotation(
        cls,
        primary_crop: str,
        primary_viability: int,
        actual_temp_c: float,
        actual_precip_mm: float,
        actual_altitude_m: float,
        actual_soil_moisture_m3_m3: float,
        actual_soil_type: str = "Inceptisol",
    ) -> Dict[str, Any]:
        """
        Calculates rotation viability index and compares rotation vs monoculture across 5 dimensions:
          1. Salud del Suelo / Soil Health
          2. Disrupción de Plagas / Pest Disruption
          3. Eficiencia Hídrica / Water Efficiency
          4. Resiliencia Económica / Economic Resilience
          5. Mitigación de Erosión / Erosion Mitigation
        """
        plan = CROP_ROTATION_PLANS.get(primary_crop, CROP_ROTATION_PLANS["Coffee"])
        partner_1_key = plan["primary_partner"]
        partner_2_key = plan["secondary_partner"]
        p1 = ROTATION_PARTNERS[partner_1_key]
        p2 = ROTATION_PARTNERS[partner_2_key]

        # Environmental suitability for the rotational partners
        # Check partner 1
        p1_elev_min, p1_elev_max = p1["optimal_elev"]
        p1_t_min, p1_t_max = p1["ideal_temp"]
        p1_fit = 100
        if not (p1_elev_min <= actual_altitude_m <= p1_elev_max):
            p1_fit -= min(40, abs(actual_altitude_m - p1_elev_min if actual_altitude_m < p1_elev_min else actual_altitude_m - p1_elev_max) / 20)
        if not (p1_t_min <= actual_temp_c <= p1_t_max):
            p1_fit -= min(40, abs(actual_temp_c - p1_t_min if actual_temp_c < p1_t_min else actual_temp_c - p1_t_max) * 4)
        p1_fit = max(35, round(p1_fit))

        # Check partner 2
        p2_elev_min, p2_elev_max = p2["optimal_elev"]
        p2_t_min, p2_t_max = p2["ideal_temp"]
        p2_fit = 100
        if not (p2_elev_min <= actual_altitude_m <= p2_elev_max):
            p2_fit -= min(40, abs(actual_altitude_m - p2_elev_min if actual_altitude_m < p2_elev_min else actual_altitude_m - p2_elev_max) / 20)
        if not (p2_t_min <= actual_temp_c <= p2_t_max):
            p2_fit -= min(40, abs(actual_temp_c - p2_t_min if actual_temp_c < p2_t_min else actual_temp_c - p2_t_max) * 4)
        p2_fit = max(35, round(p2_fit))

        # Rotation composite score
        # Rotation boosts long-term viability by +8% to +18% over raw monoculture by regenerating soil
        regeneration_bonus = 12 if "Andisol" in actual_soil_type or "Inceptisol" in actual_soil_type else 8
        combined_viability = min(98, max(25, round(
            (primary_viability * 0.55) + (p1_fit * 0.25) + (p2_fit * 0.20) + regeneration_bonus
        )))

        # Monoculture vs Rotation radar scores (0 to 100)
        # Monoculture degrades soil and increases pest risk over time
        mono_soil_health = max(30, round(primary_viability * 0.65))
        rot_soil_health = min(96, round(primary_viability * 0.70 + 26))

        mono_pest_control = max(25, round(primary_viability * 0.55))
        rot_pest_control = min(94, round(primary_viability * 0.60 + 30))

        mono_water_eff = max(35, round(primary_viability * 0.70))
        rot_water_eff = min(92, round(primary_viability * 0.75 + 18))

        mono_econ_resilience = max(30, round(primary_viability * 0.60))
        rot_econ_resilience = min(95, round(primary_viability * 0.65 + 28))

        mono_erosion_control = max(25, round(primary_viability * 0.60 - (10 if actual_altitude_m > 800 else 0)))
        rot_erosion_control = min(98, round(primary_viability * 0.70 + 25))

        dimensions_es = [
            "Salud del Suelo (N & M.O.)",
            "Control de Plagas & Nemátodos",
            "Eficiencia y Retención Hídrica",
            "Resiliencia Económica",
            "Protección contra Erosión",
        ]
        dimensions_en = [
            "Soil Health (N & O.M.)",
            "Pest & Nematode Control",
            "Water Efficiency & Retention",
            "Economic Resilience",
            "Erosion Protection",
        ]

        mono_values = [
            mono_soil_health,
            mono_pest_control,
            mono_water_eff,
            mono_econ_resilience,
            mono_erosion_control,
        ]
        rot_values = [
            rot_soil_health,
            rot_pest_control,
            rot_water_eff,
            rot_econ_resilience,
            rot_erosion_control,
        ]

        # Is rotation a better alternative?
        net_advantage_pct = round(sum(rot_values) / len(rot_values) - sum(mono_values) / len(mono_values))
        is_recommended = net_advantage_pct > 8

        return {
            "primary_crop": primary_crop,
            "primary_viability": primary_viability,
            "rotation_type": plan["rotation_type"],
            "schedule": plan["schedule"],
            "partner_1": p1,
            "partner_1_fit": p1_fit,
            "partner_2": p2,
            "partner_2_fit": p2_fit,
            "combined_viability": combined_viability,
            "net_advantage_pct": net_advantage_pct,
            "is_recommended": is_recommended,
            "benefits_es": plan["benefits_es"],
            "benefits_en": plan["benefits_en"],
            "risks_es": plan["risks_es"],
            "risks_en": plan["risks_en"],
            "comparison": {
                "dimensions_es": dimensions_es,
                "dimensions_en": dimensions_en,
                "monoculture_scores": mono_values,
                "rotation_scores": rot_values,
            },
        }
