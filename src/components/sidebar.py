"""Sidebar navigation, menus, and location input controls."""

import streamlit as st
from typing import Tuple
from src.config import CR_LAT_MIN, CR_LAT_MAX, CR_LON_MIN, CR_LON_MAX
from src.data.costa_rica_locations import COSTA_RICA_LOCATIONS, get_all_locations, find_closest_location


# Streamlined 3-page navigation aligned with GEMINI.md
PAGE_ANALYZE   = "🗺️ Analizar Ubicación"
PAGE_CROPS     = "🌾 Fichas de Cultivo"
PAGE_SCIENCE   = "🔬 Datos Científicos"

PAGE_OPTIONS = [PAGE_ANALYZE, PAGE_CROPS, PAGE_SCIENCE]


def render_sidebar() -> Tuple[str, float, float, str, bool]:
    """
    Renders the sidebar navigation and location input controls.
    Returns:
        (active_page, latitude, longitude, location_label, show_zones_toggle)
    """
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; padding: 8px 0 18px 0;">
                <span style="font-size: 44px;">🛰️🌱</span>
                <h2 style="margin: 4px 0 2px 0; color: #1B5E20; font-weight: 800; font-size: 20px; letter-spacing: -0.3px;">AgroClima CR</h2>
                <span style="font-size: 11px; color: #666; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                    NASA Satellites · IMN Costa Rica
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Navigation
        st.markdown(
            "<p style='font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:#888; margin-bottom:4px;'>Navegación</p>",
            unsafe_allow_html=True,
        )
        active_page = st.radio(
            "Página:",
            PAGE_OPTIONS,
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Location Input
        st.markdown(
            "<p style='font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:#888; margin-bottom:4px;'>Ubicación</p>",
            unsafe_allow_html=True,
        )

        input_mode = st.radio(
            "Método:",
            [
                "🗺️ Clic en el mapa",
                "🏙️ Seleccionar Cantón",
                "✍️ Buscar localidad",
                "📐 Coordenadas manuales",
            ],
            index=0,
            label_visibility="collapsed",
        )

        # Initialize session state
        if "selected_lat" not in st.session_state:
            st.session_state["selected_lat"] = 9.9281
            st.session_state["selected_lon"] = -84.0907
            st.session_state["location_name"] = "San José Centro (Valle Central)"

        all_locations = get_all_locations()

        if input_mode == "🏙️ Seleccionar Cantón":
            provinces = list(COSTA_RICA_LOCATIONS.keys())
            selected_prov = st.selectbox("Provincia:", provinces, index=0)
            canton_list = COSTA_RICA_LOCATIONS[selected_prov]
            canton_names = [c["name"] for c in canton_list]
            selected_canton_name = st.selectbox("Cantón:", canton_names, index=0)
            chosen_loc = next(c for c in canton_list if c["name"] == selected_canton_name)

            if st.button("📍 Fijar Ubicación", use_container_width=True, type="primary"):
                st.session_state["selected_lat"] = chosen_loc["lat"]
                st.session_state["selected_lon"] = chosen_loc["lon"]
                st.session_state["location_name"] = chosen_loc["name"]
                st.rerun()

        elif input_mode == "✍️ Buscar localidad":
            search_query = st.text_input(
                "Buscar:",
                placeholder="Tarrazú, Guápiles, Turrialba...",
                label_visibility="collapsed",
            )
            if search_query:
                q = search_query.strip().lower()
                matches = [
                    l for l in all_locations
                    if q in l["name"].lower()
                    or q in l["canton"].lower()
                    or q in l["province"].lower()
                    or any(q in c.lower() for c in l.get("primary_crops", []))
                ]
                if matches:
                    for m in matches[:4]:
                        if st.button(f"→ {m['name']} ({m['province']})", key=f"sb_{m['name']}"):
                            st.session_state["selected_lat"] = m["lat"]
                            st.session_state["selected_lon"] = m["lon"]
                            st.session_state["location_name"] = m["name"]
                            st.rerun()
                else:
                    st.caption("Sin resultados. Use coordenadas manuales.")

        elif input_mode == "📐 Coordenadas manuales":
            with st.form("manual_coords"):
                new_lat = st.number_input("Latitud (8.0°–11.3°):", min_value=CR_LAT_MIN, max_value=CR_LAT_MAX,
                                          value=float(st.session_state["selected_lat"]), format="%.4f", step=0.01)
                new_lon = st.number_input("Longitud (-86.0°–-82.5°):", min_value=CR_LON_MIN, max_value=CR_LON_MAX,
                                          value=float(st.session_state["selected_lon"]), format="%.4f", step=0.01)
                if st.form_submit_button("Actualizar", use_container_width=True):
                    closest = find_closest_location(new_lat, new_lon)
                    st.session_state["selected_lat"] = new_lat
                    st.session_state["selected_lon"] = new_lon
                    st.session_state["location_name"] = f"({new_lat:.3f}, {new_lon:.3f}) · {closest['canton']}"
                    st.rerun()

        else:
            st.caption("💡 Haga clic en cualquier punto del mapa para seleccionarlo.")

        st.markdown("---")

        # Map layers toggle
        show_zones = st.toggle("Mostrar regiones de referencia", value=True)

        st.markdown("---")

        # Active location display
        cur_lat = st.session_state["selected_lat"]
        cur_lon = st.session_state["selected_lon"]
        cur_name = st.session_state["location_name"]

        st.markdown(
            f"""
            <div style="background:#E8F5E9; border-left:4px solid #2E7D32; padding:10px 12px; border-radius:5px;">
                <p style="margin:0; font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; color:#2E7D32;">📍 Ubicación Activa</p>
                <p style="margin:4px 0 2px 0; font-size:13px; font-weight:700; color:#1B5E20; line-height:1.3;">{cur_name}</p>
                <p style="margin:0; font-size:11px; color:#555;">Lat <code>{cur_lat:.4f}</code> · Lon <code>{cur_lon:.4f}</code></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="margin-top:12px; font-size:10px; color:#888; line-height:1.7;">
                <b style="color:#555;">Bases de Datos Integradas</b><br>
                🛰️ NASA SMAP L2_SM_A/P · L4_SM<br>
                🛰️ NASA GPM DPR Monthly<br>
                🛰️ NASA ECOSTRESS / VIIRS<br>
                🛰️ NASA SRTM Global 30m<br>
                🇨🇷 IMN / MAG Costa Rica
            </div>
            """,
            unsafe_allow_html=True,
        )

        return active_page, cur_lat, cur_lon, cur_name, show_zones
