# AgroClima Costa Rica

Aplicación Streamlit y API FastAPI para comparar aptitud de cultivos, asociaciones
y rotaciones, con escenarios climáticos y alertas estacionales.

## Ejecutar

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
# API opcional:
.\.venv\Scripts\python.exe -m uvicorn src.api:app --reload
```

## Modelo de aptitud v2

- Temperatura **45%**, lluvia anual **30%**, humedad radicular **20%**, altitud **5%**.
- Cada factor tiene aptitud 100 dentro del rango ideal y descenso continuo fuera.
  La distancia al punto óptimo se muestra como referencia, sin penalizar condiciones
  que siguen dentro del rango ideal. Los rangos originales del catálogo se conservan.
- Temperatura usa los límites tolerables del catálogo: en esos límites el factor
  térmico vale aproximadamente 25/100. Los demás anchos de respuesta son supuestos
  explícitos: lluvia 60% del límite (mínimos 400/800 mm), humedad 0.12/0.15 m³/m³,
  altitud 1000 m. La piña usa límites de desarrollo de lluvia de 600–4000 mm
  reportados en [Agronomía Mesoamericana](https://archivo.revistas.ucr.ac.cr/index.php/agromeso/article/download/48171/50585?inline=1),
  diferenciados del óptimo y condicionados al drenaje. Deben calibrarse con rendimientos y variedades locales.
- Puntaje ponderado = 100 menos las penalizaciones de los factores y hasta 3 puntos
  por suelo no compatible. Un factor crítico impone un límite adicional:
  `100 * sqrt(min(temperatura, lluvia, humedad) / 100)`.
  Así, buenas condiciones secundarias no ocultan un déficit o estrés térmico extremo.
- La altitud tiene poco peso porque también influye sobre la temperatura. El índice
  descriptivo `S=k/rango` ya no multiplica nuevamente las penalizaciones.
- Alta >=80, moderada >=60, marginal >=40, insuficiente <40.
- **Es un índice heurístico de aptitud, no una probabilidad de cosecha, un rendimiento
  ni una predicción de rentabilidad.** No está validado con una muestra de cosechas.

El rango de incertidumbre explora ocho combinaciones de perturbaciones de
temperatura, lluvia y humedad; incluye el puntaje central. Para entradas estimadas
usa ±2 °C, ±20% de lluvia y ±0.08 m³/m³; para datos observados, ±1 °C, ±10% y ±0.04.
Se muestra como **rango de sensibilidad**, no como intervalo estadístico de confianza.
No se inventa un margen fijo de ±5%. La mezcla actual de fuentes mantiene confianza baja.

## Funcionalidades

1. Controles globales ΔT de −2 a +4 °C y ΔP de −40 a +40%; comparación actual/escenario
   en tarjetas, con el mismo escenario en rotaciones y alertas.
2. Riego suplementario: reduce hasta 70% de las penalizaciones por déficit, nunca por
   exceso. Sombra de café: escenario de hasta −1.5 °C si está por encima del ideal.
   Aviso de tractor cuando la pendiente estimada supera 15%.
3. Vigilancia de frío con mínimas climatológicas: >8 °C bajo; (4,8] vigilancia;
   <=4 alerta alta. **No confirma heladas ni inversiones nocturnas.**
   El gradiente 0.006 °C/m solo se usa si se indica una elevación de referencia distinta.
4. Rotaciones ordenadas por objetivo: agua, suelo/N, plagas, ingresos y erosión.
   Viabilidad y alineación se mantienen separadas. El orden combina 70% aptitud y
   30% meta, con filtro de viabilidad. Sin mínimos forzados ni elección obligatoria
   de una rotación: también puede ganar la línea base o no haber opción recomendable.
   Ventaja neta = diferencia respecto a la línea base **en puntos porcentuales**.
   Café, banano y aguacate se tratan como asociaciones entre calles, no rotación anual.
5. Panel de validaciones obligatorias: laboratorio de suelo, drenaje, compactación,
   humedad, variedad y pendiente.
6. Serie mensual NDVI MODIS con filtro de calidad. NDVI <0.25 dispara vigilancia
   de suelo expuesto y eleva el factor C de cobertura de la aproximación RUSLE.
   NDVI negativo puede indicar agua; no confirma suelo desnudo.
7. Capas Folium activables: suelos, erosión hídrica y déficit hídrico.
   Las capas incluidas son **estimaciones regionales**, no cartografía oficial.
8. Conector GEDI RH98/AGBD con filtros de calidad y estado sin cobertura.
   La detección de dosel puede activar el escenario de sombra de café si el usuario
   elige el modo automático. Un dosel cercano no demuestra sombra sobre el cultivo.

Las alertas cubren los **seis meses siguientes**, con fechas de Costa Rica. Usan
los últimos cinco años completos de NASA POWER y, si faltan, su climatología mensual.
Incluyen sequía, erosión hídrica y eólica, acciones sugeridas, período y número de años.
Los índices son de cribado; no pronostican tormentas, pérdidas de suelo ni probabilidades.
La frecuencia histórica solo se calcula con al menos tres años válidos por mes.
Si falta viento, el riesgo eólico es desconocido. Si falta NDVI se informa el supuesto C=0.5.

## Procedencia real

NASA POWER consulta climatología y series mensuales MERRA-2. Se validan valores
faltantes, límites físicos, unidades de precipitación y años bisiestos.
Una respuesta incompleta activa un modelo regional explícitamente identificado;
los faltantes no se convierten en cero lluvia.

Los servicios heredados llamados SMAP, GPM, ECOSTRESS, SRTM e IMN **no descargan
actualmente todos esos productos**: humedad, temperatura de suelo, pendiente,
clasificación edáfica y escenarios regionales usan estimaciones o tablas locales.
La lluvia del perfil se deriva de POWER. La elevación de localidad cercana no es
un DEM predial. La interfaz y API incluyen procedencia para evitar confundirlas
con mediciones. Las pérdidas RUSLE heredadas son aproximaciones no calibradas.

## Activar MODIS / GEDI

Requiere una cuenta/proyecto de Google Earth Engine habilitado y autenticación:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-earthengine.txt
.\.venv\Scripts\earthengine.exe authenticate
$env:EARTHENGINE_PROJECT = "mi-proyecto-habilitado"
.\.venv\Scripts\python.exe -m streamlit run app.py
```

La aplicación no solicita credenciales ni inicia sesiones interactivas durante una consulta.
Sin configuración, fallo remoto o ausencia de huellas válidas, informa indisponibilidad
y no fabrica NDVI, biomasa ni sombreado. La consulta GEDI usa un compuesto histórico
en 100 m alrededor del punto; no representa toda la finca ni fecha actual.
La integración remota requiere verificación con un proyecto habilitado.

Productos y documentación:
- [NASA POWER climatología](https://power.larc.nasa.gov/docs/services/api/temporal/climatology/)
- [NASA POWER mensual](https://power.larc.nasa.gov/docs/services/api/temporal/monthly/)
- [MOD13Q1 v061: NDVI, escala y calidad](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13Q1)
- [GEDI L2A: RH98](https://developers.google.com/earth-engine/datasets/catalog/LARSE_GEDI_GEDI02_A_002_MONTHLY)
- [GEDI L4A: AGBD](https://developers.google.com/earth-engine/datasets/catalog/LARSE_GEDI_GEDI04_A_002_MONTHLY)
- [FAO: fundamentos físicos de heladas](https://www.fao.org/4/y7223e/y7223e09.htm)

### Cartografía de suelos suministrada

Guardar `src/data/layers/soils.geojson` para reemplazar la capa aproximada.
Debe ser un FeatureCollection WGS84 con geometrías válidas y propiedades
`soil_order` (Andisol, Ultisol, Inceptisol, Alfisol, Vertisol o Entisol) y
`source` (procedencia/licencia) por cada polígono. No se incluye un archivo
inventado de IMN/MAG.

## API

`GET /api/viability?lat=9.9281&lon=-84.0907&delta_temp_c=2&delta_precip_pct=-30&irrigation=true&shade=false`

Devuelve cinco cultivos, pesos, contribuciones, límite crítico, rango de sensibilidad,
escenario, procedencia, alertas, frío y disponibilidad de vegetación.
Las coordenadas y escenarios se validan. Se conservan los campos anteriores de resultados.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Incluye casos de aptitud ideal/extrema, sequía/riego/anegamiento, ausencia de datos,
unidades, año bisiesto, rotaciones sin mínimos artificiales, separación de metas,
calendario regional, cambio de año, NDVI/GEDI, API y navegación Streamlit.
Las pruebas usan fixtures y no requieren NASA, credenciales ni acceso de red.
