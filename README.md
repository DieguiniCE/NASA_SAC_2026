# 🛰️ AgroClima Costa Rica | NASA Space Apps Challenge 2026

**AgroClima CR** es una aplicación interactiva desarrollada en **Python** y **Streamlit** diseñada para evaluar la aptitud agroclimática de suelos y microclimas en Costa Rica, permitiendo determinar si el cultivo de especies agrícolas específicas (Café, Cacao, Piña, Banano, Caña de Azúcar, Arroz, Papa, Yuca, Frijol, etc.) es viable o representa un riesgo frente a las características naturales del lugar y el cambio climático.

La aplicación integra la **API de Agroclimatología (AG) de NASA POWER** (*Prediction of Worldwide Energy Resources*), extrayendo métricas satelitales globales de temperatura, precipitación corregida, humedad relativa y radiación solar.

---

## 🚀 Características Principales (Fase 1: Barebones UI y Mapa Interactivo)

1. **🗺️ Mapa Interactivo de Costa Rica**:
   - Desarrollado con **Folium** y **Leaflet**.
   - **Selección Táctil / Clic Directo:** Toque o haga clic sobre cualquier cantón, valle, ladera o llanura del territorio nacional para reubicar el marcador de análisis.
   - **Capas Múltiples:** Vista cartográfica clara, OpenStreetMap y vista Satelital de alta resolución (Esri).
   - **Regiones Agrícolas de Referencia:** Muestra marcadores de distritos agrícolas y cuencas productivas clave en las 7 provincias.

2. **✍️ Selección de Ubicación Multi-Modal**:
   - **Por Clic Táctil:** Captura inmediata de latitud y longitud al tocar el mapa.
   - **Por Lista Predefinida:** Selector por Provincia (San José, Alajuela, Cartago, Heredia, Guanacaste, Puntarenas, Limón) y sus principales cantones y cuencas agrícolas.
   - **Por Texto Libre / Búsqueda:** Escriba el nombre del cantón o región agrícola (ej. *Tarrazú, San Carlos, Pococí, Liberia*).
   - **Por Coordenadas Manuales:** Ingrese valores exactos de Latitud Norte y Longitud Oeste dentro de los límites geográficos de Costa Rica.

3. **🛰️ Integración con NASA POWER API**:
   - Conexión al endpoint de climatología de la comunidad de **Agroclimatología (`AG`)**:
     `https://power.larc.nasa.gov/api/temporal/climatology/point`
   - Parámetros analizados:
     - `T2M`: Temperatura media a 2 metros (°C)
     - `T2M_MAX` / `T2M_MIN`: Temperaturas máximas y mínimas (°C)
     - `PRECTOTCORR`: Precipitación corregida (mm/día y total mensual/anual)
     - `RH2M`: Humedad relativa (%)
     - `ALLSKY_SFC_SW_DWN`: Radiación solar global descendente (MJ/m²/día)
     - `WS2M`: Velocidad del viento (m/s)
   - Resiliencia local: Cuenta con un modelo microclimático calibrado para Costa Rica (gradiente altitudinal de Holdridge y vertientes Caribe/Pacífico) como respaldo en caso de desconexión.

4. **📊 Visualizaciones Agroecológicas**:
   - **Walter-Lieth Climadiagrama:** Gráfico interactivo en Plotly con barras de lluvia mensual superpuestas a la curva de temperatura para identificar períodos de déficit hídrico y floración.
   - **Perfil de Radiación Solar y Humedad Relativa:** Comparativa anual mensual.
   - **Tabla Detallada con Exportación CSV:** Descarga directa de datos agrometeorológicos para análisis agronómico.

5. **🌱 Motor Barebones de Evaluación de Cultivos**:
   - Catálogo agroclimático de cultivos tropicales con rangos óptimos y tolerables.
   - Diagnóstico automatizado con puntuación porcentual (0 - 100%), veredicto agronómico y notas sobre vulnerabilidad climática (ej. roya del café por calor nocturno, acame por vientos en banano).
   - Matriz comparativa simultánea de todos los cultivos para la ubicación seleccionada.

6. **📈 Módulo Barebones de Cambio Climático**:
   - Sensibilidad a eventos ENOS (El Niño / La Niña) por vertiente.
   - Medidas recomendadas de adaptación y agricultura climáticamente inteligente (Sistemas Agroforestales, cosecha de agua, coberturas vivas).

---

## 📂 Estructura del Proyecto

```
NASA_SAC_2026/
├── app.py                     # Punto de entrada de la aplicación Streamlit
├── requirements.txt           # Dependencias de Python fijadas
├── README.md                  # Documentación del proyecto
└── src/
    ├── __init__.py
    ├── config.py              # Constantes, límites geográficos y parámetros NASA
    ├── services/
    │   ├── __init__.py
    │   └── nasa_power.py      # Cliente de la API de NASA POWER y modelo de respaldo
    ├── components/
    │   ├── __init__.py
    │   ├── map_view.py        # Mapa interactivo de Costa Rica con Folium
    │   ├── sidebar.py         # Menús de navegación y controles de búsqueda
    │   ├── metrics_display.py # Tarjetas de métricas e indicadores anuales
    │   └── charts.py          # Gráficos agroclimáticos interactivos en Plotly
    └── data/
        ├── __init__.py
        ├── costa_rica_locations.py # Directorio de provincias, cantones y cultivos típicos
        └── crops_catalog.py   # Reglas bioclimáticas y motor de evaluación de idoneidad
```

---

## 🛠️ Instalación y Ejecución

### 1. Activar el Entorno Virtual

En Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

*(Si no existe el entorno virtual, créelo e instale los requisitos):*
```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

### 2. Iniciar la Aplicación

Ejecute Streamlit en el puerto local predeterminado:
```powershell
.\.venv\Scripts\streamlit run app.py
```

La aplicación abrirá automáticamente su navegador en `http://localhost:8501`.

---

## 🌐 API de NASA POWER

Documentación oficial: [NASA POWER API Docs](https://power.larc.nasa.gov/api/pages/)
- Comunidad: `AG` (Agroclimatology)
- Formato: JSON
- Requiere API Key: **No** (Acceso público y libre provisto por la NASA).
