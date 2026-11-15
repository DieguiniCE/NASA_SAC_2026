"""Sidebar navigation, menus, and location input controls with i18n and Dark Mode support."""

import streamlit as st
from typing import Tuple
from src.config import CR_LAT_MIN, CR_LAT_MAX, CR_LON_MIN, CR_LON_MAX
from src.data.costa_rica_locations import COSTA_RICA_LOCATIONS, get_all_locations, find_closest_location
from src.i18n import t

PAGE_ANALYZE  = "analyze"
PAGE_CROPS    = "crops"
PAGE_ROTATION = "rotation"
PAGE_SCIENCE  = "science"


def render_sidebar() -> Tuple[str, float, float, str, bool, bool, str]:
    """
    Renders sidebar navigation, language/theme settings, and location input controls.
    Returns:
        (active_page_key, latitude, longitude, location_label, show_zones_toggle, dark_mode, current_lang)
    """
    # Initialize session state for lang and dark_mode if missing
    if "lang" not in st.session_state:
        st.session_state["lang"] = "es"
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False

    dark_mode = st.session_state["dark_mode"]
    current_lang = st.session_state["lang"]

    # Strict black font for light mode, white font for dark mode
    txt_color = "#FFFFFF" if dark_mode else "#000000"

    with st.sidebar:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 4px 0 12px 0;">
                <span style="font-size: 40px;">🛰️🌱</span>
                <h2 style="margin: 2px 0 1px 0; color: {txt_color}; font-weight: 800; font-size: 19px; letter-spacing: -0.3px;">AgroClima CR</h2>
                <span style="font-size: 10.5px; color: {txt_color}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px;">
                    NASA Satellites · IMN Costa Rica
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Settings: Language & Dark Mode ────────────────────────────────────
        col_lang, col_theme = st.columns([1, 1], gap="small")
        with col_lang:
            lang_options = ["Español", "English"]
            current_lang_idx = 0 if st.session_state["lang"] == "es" else 1
            chosen_lang = st.radio(
                "🌐",
                lang_options,
                index=current_lang_idx,
                horizontal=True,
                label_visibility="collapsed",
            )
            new_lang_code = "es" if chosen_lang == "Español" else "en"
            if new_lang_code != st.session_state["lang"]:
                st.session_state["lang"] = new_lang_code
                st.rerun()

        with col_theme:
            dark_mode_val = st.toggle(
                "🌙 " + ("Oscuro" if st.session_state["lang"] == "es" else "Dark"),
                value=st.session_state["dark_mode"],
            )
            if dark_mode_val != st.session_state["dark_mode"]:
                st.session_state["dark_mode"] = dark_mode_val
                st.rerun()

        st.markdown("---")

        # ── Navigation (4 pages) ──────────────────────────────────────────────
        st.markdown(
            f"<p style='font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:{txt_color}; margin-bottom:4px;'>{t('nav_label')}</p>",
            unsafe_allow_html=True,
        )

        pages = [
            (PAGE_ANALYZE,  t("page_analyze")),
            (PAGE_CROPS,    t("page_crops")),
            (PAGE_ROTATION, t("page_rotation")),
            (PAGE_SCIENCE,  t("page_science")),
        ]
        page_keys = [p[0] for p in pages]
        page_labels = [p[1] for p in pages]

        selected_label = st.radio(
            "Página:",
            page_labels,
            index=0,
            label_visibility="collapsed",
        )
        active_page = page_keys[page_labels.index(selected_label)]

        st.markdown("---")

        # ── Location Input ────────────────────────────────────────────────────
        st.markdown(
            f"<p style='font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:{txt_color}; margin-bottom:4px;'>{t('location_label')}</p>",
            unsafe_allow_html=True,
        )

        method_labels = [
            t("map_click"),
            t("canton_select"),
            t("text_search"),
            t("manual_coords"),
        ]
        chosen_method = st.radio(
            t("method_label"),
            method_labels,
            index=0,
            label_visibility="collapsed",
        )

        # Initialize coordinates if missing
        if "selected_lat" not in st.session_state:
            st.session_state["selected_lat"] = 9.9281
            st.session_state["selected_lon"] = -84.0907
            st.session_state["location_name"] = "San José Centro (Valle Central)"

        all_locations = get_all_locations()

        if chosen_method == t("canton_select"):
            provinces = list(COSTA_RICA_LOCATIONS.keys())
            selected_prov = st.selectbox("Provincia / Province:", provinces, index=0)
            canton_list = COSTA_RICA_LOCATIONS[selected_prov]
            canton_names = [c["name"] for c in canton_list]
            selected_canton_name = st.selectbox("Cantón / Canton:", canton_names, index=0)
            chosen_loc = next(c for c in canton_list if c["name"] == selected_canton_name)

            if st.button(t("set_location_btn"), use_container_width=True, type="primary"):
                st.session_state["selected_lat"] = chosen_loc["lat"]
                st.session_state["selected_lon"] = chosen_loc["lon"]
                st.session_state["location_name"] = chosen_loc["name"]
                st.rerun()

        elif chosen_method == t("text_search"):
            search_query = st.text_input(
                "Buscar:",
                placeholder=t("search_placeholder"),
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
                    st.caption(t("no_results"))

        elif chosen_method == t("manual_coords"):
            with st.form("manual_coords_form"):
                new_lat = st.number_input(
                    t("lat_label"),
                    min_value=CR_LAT_MIN,
                    max_value=CR_LAT_MAX,
                    value=float(st.session_state["selected_lat"]),
                    format="%.4f",
                    step=0.01,
                )
                new_lon = st.number_input(
                    t("lon_label"),
                    min_value=CR_LON_MIN,
                    max_value=CR_LON_MAX,
                    value=float(st.session_state["selected_lon"]),
                    format="%.4f",
                    step=0.01,
                )
                if st.form_submit_button(t("update_coords"), use_container_width=True):
                    closest = find_closest_location(new_lat, new_lon)
                    st.session_state["selected_lat"] = new_lat
                    st.session_state["selected_lon"] = new_lon
                    st.session_state["location_name"] = f"({new_lat:.3f}, {new_lon:.3f}) · {closest['canton']}"
                    st.rerun()

        else:
            st.caption(t("click_hint"))

        st.markdown("---")

        # Map layers toggle
        show_zones = st.toggle(t("show_zones"), value=True)

        st.markdown("---")

        # Active location display
        cur_lat = st.session_state["selected_lat"]
        cur_lon = st.session_state["selected_lon"]
        cur_name = st.session_state["location_name"]

        bg_card = "#1B2A1E" if dark_mode else "#E8F5E9"
        border_col = "#4CAF50" if dark_mode else "#2E7D32"

        st.markdown(
            f"""
            <div style="background:{bg_card}; border-left:4px solid {border_col}; padding:9px 11px; border-radius:5px;">
                <p style="margin:0; font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; color:{txt_color};">{t('active_location')}</p>
                <p style="margin:4px 0 2px 0; font-size:12.5px; font-weight:700; color:{txt_color}; line-height:1.3;">{cur_name}</p>
                <p style="margin:0; font-size:11px; color:{txt_color};">Lat <code>{cur_lat:.4f}</code> · Lon <code>{cur_lon:.4f}</code></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div style="margin-top:10px; font-size:9.5px; color:{txt_color}; line-height:1.6;">
                <b style="color:{txt_color};">{t('databases_label')}</b><br>
                🛰️ NASA SMAP L2_SM_A/P · L4_SM<br>
                🛰️ NASA GPM DPR Monthly<br>
                🛰️ NASA ECOSTRESS / VIIRS<br>
                🛰️ NASA SRTM Global 30m<br>
                🇨🇷 IMN / MAG Costa Rica
            </div>
            """,
            unsafe_allow_html=True,
        )

        return active_page, cur_lat, cur_lon, cur_name, show_zones, dark_mode, current_lang
