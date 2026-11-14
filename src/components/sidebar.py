"""Sidebar navigation, menus, and location input controls."""

import streamlit as st
from typing import Tuple, Dict, Any, Optional
from src.config import CR_LAT_MIN, CR_LAT_MAX, CR_LON_MIN, CR_LON_MAX
from src.data.costa_rica_locations import COSTA_RICA_LOCATIONS, get_all_locations, find_closest_location


def render_sidebar() -> Tuple[str, float, float, str, bool]:
    """
    Renders the sidebar navigation and location input controls.
    Returns:
        (active_page, latitude, longitude, location_label, show_zones_toggle)
    """
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; padding: 5px 0 15px 0;">
                <span style="font-size: 42px;">🌱</span>
                <h2 style="margin: 0; color: #1B5E20; font-weight: 700;">AgroClima CR</h2>
                <span style="font-size: 12px; color: #555; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                    NASA Space Apps Challenge
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 🧭 Menú de Navegación")
        page_options = [
            "📍 Explorador & Mapa Agroclimático",
            "🌱 Evaluación de Cultivos (Preview)",
            "📈 Tendencias y Cambio Climático (Preview)",
            "ℹ️ Metodología y API NASA POWER",
        ]
        active_page = st.radio(
            "Seleccione una sección:",
            page_options,
            index=0,
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("### 🗺️ Selección de Ubicación")
        st.caption("Elija cómo desea indicar la ubicación en Costa Rica:")

        input_mode = st.radio(
            "Método de selección:",
            [
                "🗺️ Clic directo en el mapa",
                "🏙️ Seleccionar por Cantón / Región",
                "✍️ Escribir nombre de localidad",
                "📐 Coordenadas manuales (Lat/Lon)",
            ],
            index=0,
        )

        # Initialize session state coordinates if not present
        if "selected_lat" not in st.session_state:
            st.session_state["selected_lat"] = 9.9281  # San José Centro
            st.session_state["selected_lon"] = -84.0907
            st.session_state["location_name"] = "San José Centro (Valle Central)"

        lat = st.session_state["selected_lat"]
        lon = st.session_state["selected_lon"]
        loc_name = st.session_state["location_name"]

        all_locations = get_all_locations()

        if input_mode == "🏙️ Seleccionar por Cantón / Región":
            provinces = list(COSTA_RICA_LOCATIONS.keys())
            # Find current province if possible
            default_prov_idx = 0
            for i, p in enumerate(provinces):
                if any(l["name"] == loc_name for l in COSTA_RICA_LOCATIONS[p]):
                    default_prov_idx = i
                    break

            selected_prov = st.selectbox("Provincia:", provinces, index=default_prov_idx)
            canton_list = COSTA_RICA_LOCATIONS[selected_prov]
            canton_names = [c["name"] for c in canton_list]

            default_canton_idx = 0
            for i, c in enumerate(canton_list):
                if c["name"] == loc_name:
                    default_canton_idx = i
                    break

            selected_canton_name = st.selectbox("Cantón / Región Agrícola:", canton_names, index=default_canton_idx)
            chosen_loc = next(c for c in canton_list if c["name"] == selected_canton_name)

            if st.button("📍 Fijar esta Ubicación", use_container_width=True, type="primary"):
                st.session_state["selected_lat"] = chosen_loc["lat"]
                st.session_state["selected_lon"] = chosen_loc["lon"]
                st.session_state["location_name"] = chosen_loc["name"]
                st.rerun()

        elif input_mode == "✍️ Escribir nombre de localidad":
            st.write("Escriba el nombre de una ciudad, cantón o zona agrícola:")
            search_query = st.text_input(
                "Buscar:",
                placeholder="Ej. Tarrazú, Guápiles, San Carlos, Liberia...",
                label_visibility="collapsed"
            )

            if search_query:
                q_clean = search_query.strip().lower()
                matches = [
                    l for l in all_locations
                    if q_clean in l["name"].lower()
                    or q_clean in l["canton"].lower()
                    or q_clean in l["province"].lower()
                    or any(q_clean in c.lower() for c in l.get("primary_crops", []))
                ]
                if matches:
                    st.success(f"Encontrados {len(matches)} resultado(s):")
                    for m in matches[:4]:
                        if st.button(f"👉 {m['name']} ({m['province']})", key=f"btn_search_{m['name']}"):
                            st.session_state["selected_lat"] = m["lat"]
                            st.session_state["selected_lon"] = m["lon"]
                            st.session_state["location_name"] = m["name"]
                            st.rerun()
                else:
                    st.warning("No se encontró una coincidencia directa en el catálogo predefinido. Puede ingresar coordenadas exactas.")

        elif input_mode == "📐 Coordenadas manuales (Lat/Lon)":
            with st.form("manual_coords_form"):
                new_lat = st.number_input(
                    "Latitud Norte (8.0° a 11.3°):",
                    min_value=CR_LAT_MIN,
                    max_value=CR_LAT_MAX,
                    value=float(st.session_state["selected_lat"]),
                    format="%.4f",
                    step=0.01,
                )
                new_lon = st.number_input(
                    "Longitud Oeste (-86.0° a -82.5°):",
                    min_value=CR_LON_MIN,
                    max_value=CR_LON_MAX,
                    value=float(st.session_state["selected_lon"]),
                    format="%.4f",
                    step=0.01,
                )
                submitted = st.form_submit_button("Actualizar Mapa y Clima", use_container_width=True)
                if submitted:
                    closest = find_closest_location(new_lat, new_lon)
                    st.session_state["selected_lat"] = new_lat
                    st.session_state["selected_lon"] = new_lon
                    st.session_state["location_name"] = f"Punto ({new_lat:.3f}, {new_lon:.3f}) próx. a {closest['canton']}"
                    st.rerun()

        else:
            st.info("💡 **Instrucción**: Toque o haga clic directamente en cualquier punto del mapa para seleccionarlo.")

        st.markdown("---")
        st.markdown("### ⚙️ Opciones del Mapa")
        show_zones = st.toggle("Mostrar regiones agrícolas de referencia", value=True)

        st.markdown("---")
        # Current active point summary in sidebar
        cur_lat = st.session_state["selected_lat"]
        cur_lon = st.session_state["selected_lon"]
        cur_name = st.session_state["location_name"]

        st.markdown(
            f"""
            <div style="background-color: #E8F5E9; border-left: 4px solid #2E7D32; padding: 10px; border-radius: 4px;">
                <p style="margin: 0; font-size: 11px; color: #2E7D32; font-weight: bold; text-transform: uppercase;">Punto Activo</p>
                <p style="margin: 3px 0 0 0; font-size: 13px; font-weight: 600; color: #1B5E20;">{cur_name}</p>
                <p style="margin: 2px 0 0 0; font-size: 12px; color: #333;">Lat: <code>{cur_lat:.4f}</code> | Lon: <code>{cur_lon:.4f}</code></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption("📡 Datos climatológicos provistos por NASA POWER Agroclimatology (AG).")

        return active_page, cur_lat, cur_lon, cur_name, show_zones
