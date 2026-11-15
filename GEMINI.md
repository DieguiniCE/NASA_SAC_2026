# Project Blueprint: Costa Rica Crop Viability & Agricultural App

## 1. Project Overview
This application is an agricultural decision-support tool tailored for farmers in Costa Rica. It analyzes historical and current climate, soil, and topographical data to calculate the viability of specific crops at a user-selected location. The app features an interactive map, dynamic plant profiles, a "Sensitivity Score" algorithm, and educational tooltips to help farmers understand complex scientific concepts.

## 2. Architecture & Tech Stack Recommendations
*   **Frontend**: React.js or Vue.js (for reactive UI and state management).
*   **Map Integration**: NASA Worldview/Earthdata API or Google Maps API (Google Maps is recommended for geocoding user text input to coordinates; NASA layers can be overlaid).
*   **Backend**: Python (FastAPI or Django) is highly recommended for handling geospatial data, scientific calculations, and NASA API integrations.
*   **Data Aggregation Engine**: Google Earth Engine (GEE) Python API. GEE is the most efficient way to query SMAP, GPM, SRTM, and VIIRS data simultaneously based on a specific coordinate point.

## 3. Data Sources & API Integrations
The backend must implement data pipelines to fetch parameters based on user-provided coordinates (Latitude, Longitude).

### A. NASA / Global Satellite Databases
Use NASA's Earthdata Search API, AppEEARS, or Google Earth Engine to query the following:
1.  **SMAP (Soil Moisture Active Passive)**:
    *   `L2_SM_A/P`: Fetch surface soil moisture data.
    *   `L4_SM`: Fetch root-zone soil moisture data.
2.  **GPM (Global Precipitation Measurement)**:
    *   `DPR Monthly`: Fetch historical precipitation averages and anomalies.
3.  **ECOSTRESS / VIIRS**:
    *   Fetch tiled vegetation temperature and vegetation stress indices (Evaporative Stress Index).
4.  **SRTM (Shuttle Radar Topography Mission)**:
    *   Fetch high-resolution global elevation/topography data to determine altitude.

### B. Local Costa Rican Databases
1.  **Instituto Meteorológico Nacional (IMN)**:
    *   *Data to scrape/query*: Ground/Air temperature, specific local erosion risks, localized soil types, and historical/projected rainfall.
    *   *Implementation*: If IMN lacks a public REST API, developers should request historic CSV/GeoJSON datasets to host locally in a PostGIS database.

*Note on Combining Data*: The app must clarify that satellite observations (NASA) provide broad, continuous coverage but can suffer from resolution limits, whereas ground-based measurements (IMN) offer high local accuracy. Combining them interpolates the precise local conditions.

## 4. Plant Profiles & The "Sensitivity Score"
The app will feature a database of crop information cards (Banana, Coffee, Sugar Cane, Pineapple, Avocado).

### Plant Profile Data Structure
Each crop requires a JSON object detailing its parameters:
```json
{
  "crop": "Coffee",
  "ideal_temp_c": {"min": 18, "max": 24, "sweet_spot": 21},
  "precipitation_mm": {"min": 1500, "max": 2500},
  "altitude_m": {"min": 800, "max": 1400},
  "soil_type": ["Andisol", "Loam"],
  "watering_needs": "Moderate, well-drained"
}
```

### Calculating the Sensitivity Score
The Sensitivity Score represents how vulnerable a plant is to deviations from its ideal conditions. 
*   **Concept**: A narrow survival range = High Sensitivity. A wide survival range = Low Sensitivity.
*   **Mathematical Approach**: 
    Let $T_{max}$ be the maximum tolerable temperature and $T_{min}$ be the minimum. The temperature sensitivity $S_{temp}$ can be modeled inversely to the range:
    $$S_{temp} = \frac{k}{T_{max} - T_{min}}$$
    *(Where $k$ is a normalization constant).* 
    The developer should calculate a composite Sensitivity Score weighting Temperature, Precipitation, and Soil Moisture.

## 5. The Viability Prediction Model
When a user selects a location, the algorithm executes the following steps:
1.  **Geocoding**: Convert place name to Lat/Lon (or accept map click).
2.  **Data Fetch**: Query NASA and IMN databases for the exact Lat/Lon to get current/historical averages for: Temp, Precipitation, Altitude, Soil Moisture, etc.
3.  **Delta Calculation**: Calculate the difference between the location's actual data and the crop's `sweet_spot`.
4.  **Success Percentage**: Subtract points from a baseline of 100% based on how far the local data deviates from the ideal range, multiplied by the crop's Sensitivity Score. 
    *   *Example*: If Coffee is highly sensitive to heat ($S_{temp}$ is high), and the location is $4^\circ\text{C}$ above the ideal, the success percentage drops significantly.

## 6. UI/UX Features & Requirements
### Interactive Map
*   Full-screen or split-screen map of Costa Rica.
*   Clickable interface that places a pin and triggers the `calculateViability(lat, lon)` function.

### Scientific Term Tooltips (Hover functionality)
Implement a robust tooltip system (similar to MSI Afterburner/HWiNFO). When the user hovers over specific scientific terms, an absolute-positioned `div` appears with an explanation, disappearing `onMouseLeave`.

**Dictionary for Tooltips:**
*   **Evapotranspiration**: The sum of evaporation from the land surface plus transpiration from plants. It shows how much water is actually leaving the soil.
*   **Soil Moisture Anomalies**: Deviations from the normal amount of water in the soil for a given time of year. Indicates unexpected droughts or floods.
*   **Water-Balance Indicators**: Metrics comparing the water entering the system (rainfall) versus water leaving (evaporation/runoff) to determine if a crop will face water stress.
*   **Satellite vs. Ground Data**: Satellites scan massive areas from space to find broader climate trends, while ground stations measure exact local weather. Combining them gives us the most accurate picture!

## 7. Step-by-Step Developer Implementation Plan
1.  **Phase 1: Environment & Database Setup**
    *   Set up a PostgreSQL/PostGIS database.
    *   Import local Costa Rican soil and climate data from IMN.
2.  **Phase 2: NASA API Integration**
    *   Register for NASA Earthdata credentials.
    *   Write Python scripts using libraries like `geopandas` and `xarray` to query SMAP, GPM, SRTM, and ECOSTRESS by coordinate.
3.  **Phase 3: Logic & Algorithms**
    *   Create the Crop JSON files.
    *   Write the Sensitivity Score calculator.
    *   Develop the Viability Success Percentage algorithm.
4.  **Phase 4: API Development**
    *   Build a REST endpoint: `GET /api/viability?lat={lat}&lon={lon}` that triggers the data fetch and model, returning the success score for all 5 crops.
5.  **Phase 5: Frontend Map & UI**
    *   Integrate Google Maps / Leaflet.js.
    *   Build the Plant Information Cards UI.
    *   Implement the custom hover-tooltips for the scientific dictionary.