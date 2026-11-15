# 🛰️ AgroClima Costa Rica | NASA Space Apps Challenge 2026

**AgroClima CR** es una plataforma agroambiental y bioclimática desarrollada en **Python** y **Streamlit** diseñada para analizar la viabilidad del cultivo en cualquier punto geográfico de Costa Rica, integrando datos satelitales globales de observación de la Tierra provistos por la **NASA** e información climática y edafológica del **Instituto Meteorológico Nacional (IMN)** y el **Ministerio de Agricultura y Ganadería (MAG)**.

---

## 🛰️ Bases de Datos y Misiones Satelitales Integradas

La aplicación conecta e implementa las siguientes fuentes de datos para evaluar las variables requeridas:

| Base de Datos / Misión | Producto / Instrucción | Variable Agroambiental Extraída | Resolución |
| :--- | :--- | :--- | :--- |
| **NASA SMAP** *(Soil Moisture Active Passive)* | **`L2_SM_A/P`** (`SPL2SMAP` / `SPL2SMP`) | **Humedad del Suelo Superficial** (0–5 cm, $m^3/m^3$) | 9 km / 33 km |
| **NASA SMAP** | **`L4_SM`** (`SPL4SMGP`) | **Humedad en Zona Radicular** (0–100 cm, $m^3/m^3$) y **Temperatura del Suelo** (`soil_temp_layer1` a 5 cm) | 9 km EASE-Grid |
| **NASA GPM** *(Global Precipitation Measurement)* | **`GPM DPR Monthly`** (`3DPR` / IMERG Monthly) | **Precipitación Mensual por Radar** (Bandas Ka/Ku), picos de tormenta y factor de erosividad pluvial ($R$) | 0.1° (~10 km) |
| **NASA ECOSTRESS / VIIRS** | **`ECO_L4T_ESI`** & **`ECO2LSTE`** | **Índice de Estrés Evaporativo (ESI)** ($ET/PET$), humedad cuadriculada a 70m y **Temperatura Superficial Terrestre (LST / Ground Temp)** | 70 metros |
| **NASA SRTM** *(Shuttle Radar Topography Mission)* | **`SRTMGL1`** (Global DEM) | **Elevación Topográfica Exacta** ($msnm$), **Pendiente del Terreno** (% y grados) y factor topográfico $LS$ | 30 metros (1 arc-sec) |
| **IMN / MAG Costa Rica** | Cartografía CIA-UCR / IMN | **Órdenes de Suelo** (Andisol, Ultisol, Inceptisol, Alfisol, Vertisol, Entisol), textura, pH y **Potencial de Absorción e Infiltración** ($mm/h$) | Regionalizada CR |
| **IMN Costa Rica** | Escenarios Regionalizados 2030 / 2050 | **Proyecciones de Cambio Climático** ($\Delta T$, $\Delta P$, variación estacional) para las 6 regiones del país | 6 subregiones CR |
| **NASA POWER** | Agroclimatología (`community=AG`) | **Temperatura del Aire** (Media, Mín, Máx), Humedad Relativa (`RH2M`), Radiación Solar (`ALLSKY_SFC_SW_DWN`) y Viento | 0.5° global |

---

## 📊 Parámetros Clave Analizados

1. **🌡️ Temperatura del Aire y del Suelo:**
   - Temperatura del aire a 2 metros (`T2M`, Mín, Máx) provista por NASA POWER / IMN.
   - Temperatura de la superficie del suelo provista por **NASA ECOSTRESS (LST)** y **NASA SMAP (L4_SM `soil_temp_layer1`)**.
2. **🛡️ Riesgo de Erosión Hídrica:**
   - Calculado mediante el modelo paramétrico **RUSLE** ($A = R \times K \times LS \times C \times P$), combinando la erosividad de lluvia $R$ de **GPM DPR**, la erodabilidad $K$ del suelo **IMN**, y la longitud/gradiente de pendiente $LS$ de **SRTM 30m**.
3. **🪨 Tipo y Orden de Suelo:**
   - Clasificación de órdenes según *Soil Taxonomy* en Costa Rica (Andisoles, Ultisoles, Inceptisoles, Alfisoles, Vertisoles, Entisoles) con sus propiedades físicas, químicas y de drenaje.
4. **⛰️ Elevación Topográfica:**
   - Elevación y relieve provistos por **NASA SRTM 30m**, junto con clasificación de aptitud para mecanización agrícola.
5. **🌧️ Precipitación (Histórica y Proyecciones):**
   - Serie histórica mensual de radar **GPM DPR** y NASA POWER.
   - Escenarios regionalizados de cambio climático del **IMN para 2030 y 2050** ($\Delta T$, $\Delta P$).
6. **💧 Humedad (Aire y Potencial de Absorción del Suelo):**
   - Humedad relativa atmosférica (`RH2M`).
   - Humedad superficial (0–5 cm) con **SMAP L2_SM_A/P**.
   - Humedad radicular activa (0–100 cm) con **SMAP L4_SM**.
   - **Potencial de absorción e infiltración hidráulica** ($mm/h$) y capacidad de retención de agua ($AWC$, $mm/m$) según el orden de suelo del IMN/MAG.

---

## 🌱 Modelo Básico de Viabilidad (Baseline Engine)

Como se solicitó, se implementó un **modelo básico inicial** multivariable para evaluar la viabilidad de siembra sin entrar aún en el entrenamiento de redes neuronales o simulaciones complejas:
- **Componente Térmico (25%):** Concordancia de T° de aire y suelo con el rango óptimo del cultivo.
- **Componente Hídrico (25%):** Régimen pluvial (GPM) y disponibilidad hídrica en raíces (SMAP L4).
- **Componente Edafológico (20%):** Afinidad con el orden de suelo (IMN) y drenaje/absorción.
- **Componente Topográfico (15%):** Piso altitudinal (SRTM) y penalización por riesgo de erosión en pendiente.
- **Componente de Resiliencia Climática (15%):** Vulnerabilidad ante el escenario IMN 2050.

> [!NOTE]
> Este modelo es un baseline modular diseñado para ser ajustado, calibrado o reemplazado por modelos de Machine Learning (ej. Random Forest, XGBoost) o modelos agroecológicos (DSSAT, APSIM) en etapas posteriores.

---

## 📂 Arquitectura de Archivos

```
NASA_SAC_2026/
├── app.py                           # Punto de entrada Streamlit (Vistas multibase y menús)
├── requirements.txt                 # Dependencias fijadas (Streamlit, Folium, Plotly, etc.)
├── README.md                        # Documentación del sistema
└── src/
    ├── config.py                    # Constantes, límites geográficos y parámetros NASA
    ├── services/
    │   ├── data_lake.py             # Agregador y motor de fusión satelital + IMN
    │   ├── smap_service.py          # NASA SMAP (L2_SM_A/P y L4_SM)
    │   ├── gpm_service.py           # NASA GPM DPR Monthly & Erosividad R
    │   ├── ecostress_service.py     # NASA ECOSTRESS / VIIRS (ESI & LST)
    │   ├── srtm_service.py          # NASA SRTM 30m DEM & Pendiente
    │   ├── imn_cr_service.py        # IMN Suelos, Absorción, Erosión RUSLE y Proyecciones 2050
    │   └── nasa_power.py            # NASA POWER Agroclimatology (AG)
    ├── models/
    │   └── basic_viability.py       # Modelo básico de aptitud de cultivo multivariable
    ├── components/
    │   ├── map_view.py              # Mapa interactivo de Costa Rica (Folium)
    │   ├── sidebar.py               # Menús de navegación y selector de ubicación
    │   ├── metrics_display.py       # Tarjetas de indicadores ambientales
    │   └── charts.py                # Gráficos Walter-Lieth, radar de aptitud y termometría
    └── data/
        ├── costa_rica_locations.py  # Directorio de cantones y zonas agropecuarias de CR
        └── crops_catalog.py         # Requerimientos biofísicos de cultivos tropicales
```

---

## 🔄 Motor de Rotación de Cultivos & Diversificación Agroecológica

Cumpliendo con los **Objetivos del NASA Space Apps Challenge 2026**, la plataforma incorpora un módulo avanzado de exploración y comparación de estrategias rotacionales para los 5 cultivos clave de Costa Rica (Café, Banano, Caña de Azúcar, Piña y Aguacate):

1. **Comparación de al menos tres estrategias rotacionales:**
   - **Estrategia 0 (Línea Base / Monocultivo Tradicional):** Práctica continua convencional.
   - **Estrategia 1 (Agroecológica & Fijación de Nitrógeno):** Regeneración biológica con leguminosas (*Canavalia*, *Mucuna*, *Phaseolus*) y biofumigación con *Crotalaria juncea*.
   - **Estrategia 2 (Diversificación Comercial & Renta Extra):** Intercalado y rotación con cultivos de mercado y seguridad alimentaria (*Maíz criollo*, *Yuca de exportación*, *Camote*).
   - **Estrategia 3 (Resiliencia Climática & Conservación Hídrica):** Manto vivo perenne (*Arachis pintoi* - Maní forrajero), barreras vivas de *Vetiver* y pastos profundos (*Brachiaria*).

2. **Los 5 Pilares de Análisis Requeridos por NASA:**
   - 💡 **Por qué se sugiere / Rationale:** Justificación agroecológica según el clima y suelo local.
   - 🛰️ **Evidencia Satelital & Terrestre:** Indicadores concretos de **NASA SMAP** (humedad radicular), **ECOSTRESS** (índice de estrés evaporativo ESI y temperatura superficial LST), **GPM DPR** (precipitación y erosividad), **SRTM** (pendiente topográfica) y suelos **IMN**.
   - 🌟 **Beneficios Ofrecidos:** Fijación de nitrógeno (+40 a +70 kg N/ha), reducción de erosión (>80%), corte de nemátodos y hongos fitopatógenos, e ingresos complementarios.
   - 🔍 **Vacíos de Información & Incertidumbre:** Transparencia científica sobre nubosidad óptica, variabilidad microclimática y acceso local a semillas.
   - ⚠️ **Riesgos y Revisión del Productor:** Aspectos agronómicos que requieren el criterio in-situ del agricultor (mano de obra, deshierbe, drenaje).

3. **Alineación con Prioridades del Productor:**
   - Filtros de prioridad interactivos: *Enfoque Equilibrado*, *Regenerar Suelo & N*, *Ahorro Hídrico*, *Ingresos Extra*, *Control de Plagas*, *Control de Erosión*.

4. **Calendario Agroclimático de 12 Meses & Transiciones de Suelo Desnudo:**
   - Visualización mes a mes de las precipitaciones GPM, el índice de estrés climático, los períodos críticos de suelo descubierto (bare soil) en monocultivo y la protección continua de la cobertura viva rotacional.

5. **Simulador de Escenarios Climáticos (What-If Analysis):**
   - Sliders de variación de temperatura ($\Delta T$) y lluvia ($\Delta P$) que demuestran en tiempo real la estabilidad y resiliencia de los sistemas rotacionales frente a sequías (El Niño) o temporales extremos.

6. **Herramienta de Apoyo Centrada en el Agricultor:**
   - Recordatorio ético de que el sistema apoya y empodera el conocimiento tradicional y la toma de decisiones, sin reemplazar el juicio del agricultor ni la asesoría de extensionistas locales (MAG/INTA/ICAFE/CORBANA/LAICA).

---

## 🚀 Instrucciones de Ejecución

1. **Activar el entorno virtual**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Lanzar la aplicación**:
   ```powershell
   .\.venv\Scripts\streamlit run app.py
   ```

3. **Abrir en el navegador**:
   ```
   http://localhost:8501
   ```
