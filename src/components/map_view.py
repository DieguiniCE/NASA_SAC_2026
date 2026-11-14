"""Folium map component for Costa Rica interactive selection."""

import folium
from streamlit_folium import st_folium
import streamlit as st
from typing import Tuple, Optional, Dict, Any

from src.config import COSTA_RICA_CENTER, DEFAULT_ZOOM, CR_LAT_MIN, CR_LAT_MAX, CR_LON_MIN, CR_LON_MAX
from src.data.costa_rica_locations import get_all_locations, find_closest_location


def render_costa_rica_map(
    selected_lat: float,
    selected_lon: float,
    location_name: str = "Punto Seleccionado",
    elevation_m: Optional[int] = None,
    show_reference_zones: bool = True,
    map_height: int = 500
) -> Optional[Tuple[float, float]]:
    """
    Renders an interactive Folium map centered on Costa Rica.
    Captures click / touch events and returns (lat, lon) if a click occurred.
    """
    # Create Folium Map
    m = folium.Map(
        location=[selected_lat, selected_lon] if (CR_LAT_MIN <= selected_lat <= CR_LAT_MAX) else COSTA_RICA_CENTER,
        zoom_start=DEFAULT_ZOOM,
        tiles="CartoDB positron",
        control_scale=True,
    )

    # Add alternative Tile Layers
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Satélite (Esri)",
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

    # Add Selected Point Marker with a distinctive pulsing/red pin
    elev_text = f"{elevation_m} msnm" if elevation_m is not None else "Calculando..."
    popup_html = f"""
    <div style="font-family: Arial, sans-serif; min-width: 170px;">
        <h4 style="margin: 0 0 5px 0; color: #1B5E20;">📍 {location_name}</h4>
        <p style="margin: 2px 0;"><b>Lat:</b> {selected_lat:.4f}°</p>
        <p style="margin: 2px 0;"><b>Lon:</b> {selected_lon:.4f}°</p>
        <p style="margin: 2px 0;"><b>Elevación:</b> {elev_text}</p>
        <p style="margin: 4px 0 0 0; color: #555; font-size: 11px;">Coordenadas activas para datos NASA POWER</p>
    </div>
    """
    folium.Marker(
        location=[selected_lat, selected_lon],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"Punto activo: {location_name} ({selected_lat:.3f}, {selected_lon:.3f})",
        icon=folium.Icon(color="red", icon="leaf", prefix="fa"),
    ).add_to(m)

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
