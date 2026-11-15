"""Folium map component for Costa Rica interactive selection with terrestrial boundary validation."""

import folium
from streamlit_folium import st_folium
import streamlit as st
from typing import Tuple, Optional, Dict, Any

from src.config import COSTA_RICA_CENTER, DEFAULT_ZOOM, CR_LAT_MIN, CR_LAT_MAX, CR_LON_MIN, CR_LON_MAX
from src.data.costa_rica_locations import get_all_locations, find_closest_location
from src.services.land_verification import CR_MAINLAND_POLYGON, validate_terrestrial_location


def render_costa_rica_map(
    selected_lat: float,
    selected_lon: float,
    location_name: str = "Punto Seleccionado",
    elevation_m: Optional[int] = None,
    show_reference_zones: bool = True,
    rejected_coord: Optional[Tuple[float, float, str]] = None,
    map_height: int = 500
) -> Optional[Tuple[float, float]]:
    """
    Renders an interactive Folium map centered on Costa Rica.
    Draws the official terrestrial agricultural boundary of Costa Rica.
    Captures click / touch events and returns (lat, lon) if a click occurred.
    """
    # Create Folium Map
    m = folium.Map(
        location=[selected_lat, selected_lon] if (CR_LAT_MIN <= selected_lat <= CR_LAT_MAX) else COSTA_RICA_CENTER,
        zoom_start=DEFAULT_ZOOM,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    # Add alternative Tile Layers
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Satélite (Esri)",
    ).add_to(m)

    # Add official Terrestrial Agricultural Boundary of Costa Rica
    folium.Polygon(
        locations=CR_MAINLAND_POLYGON,
        color="#2E7D32",
        weight=2.5,
        dash_array="4, 4",
        fill=True,
        fill_color="#4CAF50",
        fill_opacity=0.08,
        tooltip="Zona Continental Agrícola de Costa Rica (Área Apta para Análisis)",
        name="Límite Continental Terrestre (CR)",
    ).add_to(m)

    # Optional: Display agricultural reference zones with tooltips
    if show_reference_zones:
        all_locs = get_all_locations()
        for loc in all_locs:
            crops_str = ", ".join(loc.get("primary_crops", [])[:2])
            tooltip_html = f"<b>{loc['name']}</b><br>Cultivos: {crops_str}<br>Elevación: {loc['elevation_m']} msnm"
            folium.CircleMarker(
                location=[loc["lat"], loc["lon"]],
                radius=5,
                color="#2E7D32",
                fill=True,
                fill_color="#4CAF50",
                fill_opacity=0.7,
                tooltip=folium.Tooltip(tooltip_html),
            ).add_to(m)

    # If an ocean / non-terrestrial point was recently clicked, display a warning marker
    if rejected_coord:
        r_lat, r_lon, r_label = rejected_coord
        popup_ocean = f"""
        <div style="font-family: Arial, sans-serif; min-width: 170px;">
            <h4 style="margin: 0 0 4px 0; color: #D32F2F;">⚠️ {r_label}</h4>
            <p style="margin: 2px 0; font-size: 11px;"><b>Lat:</b> {r_lat:.4f}° · <b>Lon:</b> {r_lon:.4f}°</p>
            <p style="margin: 4px 0 0 0; color: #721C24; font-size: 11px;">
                <b>Zona marítima no apta para cultivo.</b><br>
                Haga clic sobre tierra firme dentro del polígono verde.
            </p>
        </div>
        """
        folium.Marker(
            location=[r_lat, r_lon],
            popup=folium.Popup(popup_ocean, max_width=240),
            tooltip=f"⚠️ {r_label}: Zona marina no analizable",
            icon=folium.Icon(color="blue", icon="water", prefix="fa"),
        ).add_to(m)

    # Add Selected Point Marker with a distinctive pulsing/green-red pin
    elev_text = f"{elevation_m} msnm" if elevation_m is not None else "Calculando..."
    popup_html = f"""
    <div style="font-family: Arial, sans-serif; min-width: 170px;">
        <h4 style="margin: 0 0 5px 0; color: #1B5E20;">📍 {location_name}</h4>
        <p style="margin: 2px 0;"><b>Lat:</b> {selected_lat:.4f}°</p>
        <p style="margin: 2px 0;"><b>Lon:</b> {selected_lon:.4f}°</p>
        <p style="margin: 2px 0;"><b>Elevación:</b> {elev_text}</p>
        <p style="margin: 4px 0 0 0; color: #2E7D32; font-size: 11px; font-weight: bold;">
            Punto terrestre seleccionado; aptitud por evaluar
        </p>
    </div>
    """
    folium.Marker(
        location=[selected_lat, selected_lon],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"Punto activo: {location_name} ({selected_lat:.3f}, {selected_lon:.3f})",
        icon=folium.Icon(color="red", icon="leaf", prefix="fa"),
    ).add_to(m)

    from src.services.thematic_layers import add_thematic_layers
    add_thematic_layers(m)
    st.caption('Capas de suelos y riesgos: estimaciones regionales; activar en el control del mapa. Verde: bajo, amarillo: medio, rojo: alto. No representan mediciones prediales.')

    folium.LayerControl(position="topright").add_to(m)

    # Render with streamlit-folium
    map_data = st_folium(
        m,
        height=map_height,
        use_container_width=True,
        returned_objects=["last_clicked"],
    )

    # Check for click interaction
    if map_data and map_data.get("last_clicked"):
        click_lat = map_data["last_clicked"]["lat"]
        click_lon = map_data["last_clicked"]["lng"]
        return round(click_lat, 4), round(click_lon, 4)

    return None
