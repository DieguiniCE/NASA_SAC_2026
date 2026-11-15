"""Plotly interactive charts with Dark/Light mode support and bilingual labels."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List
from src.config import MONTH_NAMES
from src.i18n import t


def get_chart_theme(dark_mode: bool = False) -> Dict[str, str]:
    """Returns color theme dictionary according to dark/light mode."""
    if dark_mode:
        return {
            "paper_bg": "#1A1F26",
            "plot_bg": "#12161C",
            "text_color": "#FFFFFF",
            "grid_color": "#2D3748",
            "font_family": "Inter, sans-serif",
            "subtext_color": "#FFFFFF",
            "border_color": "#374151",
            "gauge_bg": "#212730",
        }
    return {
        "paper_bg": "#FFFFFF",
        "plot_bg": "#FAFAFA",
        "text_color": "#000000",
        "grid_color": "#E5E7EB",
        "font_family": "Inter, sans-serif",
        "subtext_color": "#000000",
        "border_color": "#D1D5DB",
        "gauge_bg": "#F3F4F6",
    }


def create_viability_gauge(score: int, crop_name: str, icon: str = "🌱", dark_mode: bool = False) -> go.Figure:
    """Creates a Plotly gauge chart for a single crop viability score."""
    theme = get_chart_theme(dark_mode)

    if score >= 80:
        bar_color = "#2E7D32" if not dark_mode else "#4CAF50"
    elif score >= 60:
        bar_color = "#1565C0" if not dark_mode else "#42A5F5"
    elif score >= 40:
        bar_color = "#E65100" if not dark_mode else "#FFA726"
    else:
        bar_color = "#B71C1C" if not dark_mode else "#EF5350"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 26, "color": bar_color, "family": theme["font_family"]}},
        title={
            "text": f"<b>{icon} {crop_name}</b>",
            "font": {"size": 13, "color": theme["text_color"], "family": theme["font_family"]}
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": theme["subtext_color"],
                "tickfont": {"size": 10, "color": theme["subtext_color"]},
                "dtick": 25,
            },
            "bar": {"color": bar_color, "thickness": 0.75},
            "bgcolor": theme["gauge_bg"],
            "borderwidth": 1,
            "bordercolor": theme["border_color"],
            "steps": [
                {"range": [0, 40],   "color": "rgba(239, 83, 80, 0.25)"},
                {"range": [40, 60],  "color": "rgba(255, 167, 38, 0.25)"},
                {"range": [60, 80],  "color": "rgba(66, 165, 245, 0.25)"},
                {"range": [80, 100], "color": "rgba(76, 175, 80, 0.25)"},
            ],
            "threshold": {
                "line": {"color": bar_color, "width": 3},
                "thickness": 0.85,
                "value": score,
            },
        }
    ))

    fig.update_layout(
        paper_bgcolor=theme["paper_bg"],
        font={"color": theme["text_color"], "family": theme["font_family"]},
        margin=dict(l=20, r=20, t=50, b=10),
        height=200,
    )
    return fig


def create_viability_bar_chart(all_results: List[Dict[str, Any]], dark_mode: bool = False, lang: str = "es") -> go.Figure:
    """Creates a horizontal bar chart comparing viability scores for all 5 crops."""
    theme = get_chart_theme(dark_mode)

    crops = [f"{r['icon']} {r['crop']}" for r in all_results]
    scores = [r["success_percentage"] for r in all_results]
    colors = []
    for s in scores:
        if s >= 80:
            colors.append("#2E7D32" if not dark_mode else "#4CAF50")
        elif s >= 60:
            colors.append("#1565C0" if not dark_mode else "#42A5F5")
        elif s >= 40:
            colors.append("#E65100" if not dark_mode else "#FFA726")
        else:
            colors.append("#B71C1C" if not dark_mode else "#EF5350")

    fig = go.Figure(go.Bar(
        x=scores,
        y=crops,
        orientation="h",
        marker_color=colors,
        text=[f"{s}%" for s in scores],
        textposition="outside",
        textfont=dict(size=13, color=theme["text_color"]),
        hovertemplate="<b>%{y}</b><br>" + t("chart_viab_x") + ": %{x}%<extra></extra>",
    ))

    high_label = "Alta" if lang == "es" else "High"
    mod_label = "Mod." if lang == "es" else "Mod."

    fig.add_vline(x=80, line_dash="dot", line_color="#4CAF50", line_width=1.5,
                  annotation_text=high_label, annotation_font_color="#4CAF50", annotation_font_size=11)
    fig.add_vline(x=60, line_dash="dot", line_color="#42A5F5", line_width=1,
                  annotation_text=mod_label, annotation_font_color="#42A5F5", annotation_font_size=11)

    fig.update_layout(
        title=f"<b>{t('chart_viab_title')}</b>",
        title_font={"color": theme["text_color"], "size": 14},
        font={"color": theme["text_color"], "family": theme["font_family"]},
        xaxis=dict(
            range=[0, 115],
            title=dict(text=t("chart_viab_x"), font=dict(color=theme["text_color"])),
            showgrid=True,
            gridcolor=theme["grid_color"],
            color=theme["text_color"],
            tickfont=dict(color=theme["text_color"]),
        ),
        yaxis=dict(title="", color=theme["text_color"], tickfont=dict(color=theme["text_color"])),
        margin=dict(l=10, r=60, t=50, b=30),
        paper_bgcolor=theme["paper_bg"],
        plot_bgcolor=theme["plot_bg"],
        height=280,
    )
    return fig


def create_climadiagram(clima_data: Dict[str, Any], dark_mode: bool = False, lang: str = "es") -> go.Figure:
    """Combined Walter-Lieth style Agroclimatic diagram with Dark/Light mode."""
    theme = get_chart_theme(dark_mode)

    month_keys = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    params = clima_data.get("parameters", {})

    temp_series = [params.get("T2M", {}).get(m, 22.0) for m in month_keys]
    temp_max_series = [params.get("T2M_MAX", {}).get(m, 27.0) for m in month_keys]
    temp_min_series = [params.get("T2M_MIN", {}).get(m, 17.0) for m in month_keys]
    precip_series = [params.get("PRECTOT_MONTHLY", {}).get(m, 150.0) for m in month_keys]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    rain_name = t("chart_rain")
    range_name = t("chart_temp_range")
    mean_name = t("chart_temp_mean")

    bar_color = "rgba(33, 150, 243, 0.75)" if not dark_mode else "rgba(66, 165, 245, 0.65)"
    line_border = "#1976D2" if not dark_mode else "#90CAF9"

    fig.add_trace(
        go.Bar(
            x=MONTH_NAMES,
            y=precip_series,
            name=rain_name,
            marker_color=bar_color,
            marker_line=dict(color=line_border, width=1.5),
            hovertemplate="<b>%{x}</b><br>" + rain_name + ": %{y:.1f} mm<extra></extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=MONTH_NAMES,
            y=temp_max_series,
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        ),
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(
            x=MONTH_NAMES,
            y=temp_min_series,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(255, 152, 0, 0.22)" if not dark_mode else "rgba(255, 167, 38, 0.20)",
            name=range_name,
            hoverinfo="skip",
        ),
        secondary_y=True,
    )

    mean_line_color = "#E65100" if not dark_mode else "#FFA726"
    mean_marker_color = "#BF360C" if not dark_mode else "#FF7043"

    fig.add_trace(
        go.Scatter(
            x=MONTH_NAMES,
            y=temp_series,
            mode="lines+markers",
            name=mean_name,
            line=dict(color=mean_line_color, width=3),
            marker=dict(size=7, color=mean_marker_color),
            hovertemplate="<b>%{x}</b><br>" + mean_name + ": %{y:.1f} °C<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title=f"<b>{t('chart_clima_title')}</b>",
        title_font={"color": theme["text_color"], "size": 14},
        font={"color": theme["text_color"], "family": theme["font_family"]},
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font={"color": theme["text_color"], "size": 11}
        ),
        margin=dict(l=40, r=40, t=60, b=30),
        plot_bgcolor=theme["plot_bg"],
        paper_bgcolor=theme["paper_bg"],
        height=360,
    )

    fig.update_yaxes(
        title_text=f"<b>{t('chart_precip_y')}</b>",
        title_font=dict(color=theme["text_color"]),
        secondary_y=False,
        showgrid=True,
        gridcolor=theme["grid_color"],
        color=theme["text_color"],
        tickfont=dict(color=theme["text_color"]),
    )
    fig.update_yaxes(
        title_text=f"<b>{t('chart_temp_y')}</b>",
        title_font=dict(color=theme["text_color"]),
        secondary_y=True,
        showgrid=False,
        color=theme["text_color"],
        tickfont=dict(color=theme["text_color"]),
    )
    fig.update_xaxes(
        showgrid=False,
        color=theme["text_color"],
        tickfont=dict(color=theme["text_color"]),
    )

    return fig


def create_moisture_comparison_chart(surface_sm: float, root_sm: float, esi_val: float, dark_mode: bool = False, lang: str = "es") -> go.Figure:
    """Comparative bar gauges for SMAP L2 Surface vs L4 Root moisture."""
    theme = get_chart_theme(dark_mode)

    x1 = t("chart_smap_x1")
    x2 = t("chart_smap_x2")

    colors = ["#42A5F5", "#1E88E5"] if not dark_mode else ["#64B5F6", "#2196F3"]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name=t("chart_smap_y"),
        x=[x1, x2],
        y=[surface_sm, root_sm],
        text=[f"{surface_sm:.3f} m³/m³", f"{root_sm:.3f} m³/m³"],
        textposition="auto",
        marker_color=colors,
        textfont=dict(color="#FFFFFF", size=12),
    ))

    fig.update_layout(
        title=f"<b>{t('chart_smap_title')}</b>",
        title_font={"color": theme["text_color"], "size": 13},
        font={"color": theme["text_color"], "family": theme["font_family"]},
        yaxis=dict(
            title=dict(text=t("chart_smap_y"), font=dict(color=theme["text_color"])),
            range=[0, 0.55],
            showgrid=True,
            gridcolor=theme["grid_color"],
            color=theme["text_color"],
            tickfont=dict(color=theme["text_color"]),
        ),
        xaxis=dict(color=theme["text_color"], tickfont=dict(color=theme["text_color"])),
        margin=dict(l=40, r=40, t=50, b=40),
        plot_bgcolor=theme["plot_bg"],
        paper_bgcolor=theme["paper_bg"],
        height=320,
    )
    return fig


def create_temperature_breakdown_chart(air_t: float, ground_t: float, max_t: float, min_t: float, dark_mode: bool = False, lang: str = "es") -> go.Figure:
    """Bar chart comparing Air Temperature and Ground/Surface Temperature (ECOSTRESS / SMAP)."""
    theme = get_chart_theme(dark_mode)

    labels = [
        t("chart_t_min"),
        t("chart_t_mean"),
        t("chart_t_ground"),
        t("chart_t_max"),
    ]
    vals = [min_t, air_t, ground_t, max_t]
    colors = ["#29B6F6", "#FFA726", "#EF5350", "#D32F2F"] if not dark_mode else ["#4FC3F7", "#FFB74D", "#E57373", "#F44336"]

    fig = go.Figure(go.Bar(
        x=labels,
        y=vals,
        text=[f"{v:.1f} °C" for v in vals],
        textposition="auto",
        marker_color=colors,
        textfont=dict(color="#FFFFFF", size=12),
    ))

    fig.update_layout(
        title=f"<b>{t('chart_thermo_title')}</b>",
        title_font={"color": theme["text_color"], "size": 13},
        font={"color": theme["text_color"], "family": theme["font_family"]},
        yaxis=dict(
            title=dict(text=t("chart_temp_y"), font=dict(color=theme["text_color"])),
            range=[0, max(38.0, max_t + 5)],
            showgrid=True,
            gridcolor=theme["grid_color"],
            color=theme["text_color"],
            tickfont=dict(color=theme["text_color"]),
        ),
        xaxis=dict(color=theme["text_color"], tickfont=dict(color=theme["text_color"])),
        margin=dict(l=30, r=30, t=50, b=30),
        height=300,
        paper_bgcolor=theme["paper_bg"],
        plot_bgcolor=theme["plot_bg"],
    )
    return fig


def create_delta_comparison_chart(crop_res: Dict[str, Any], dark_mode: bool = False, lang: str = "es") -> go.Figure:
    """Horizontal bar chart showing actual vs. sweet-spot values for a single crop."""
    theme = get_chart_theme(dark_mode)

    if lang == "es":
        params = ["Temperatura (°C)", "Precipitación (÷10 mm)", "Altitud (÷10 m)", "Humedad Suelo (×100 m³/m³)"]
    else:
        params = ["Temperature (°C)", "Precipitation (÷10 mm)", "Altitude (÷10 m)", "Soil Moisture (×100 m³/m³)"]

    actual = crop_res["actual_values"]
    sweet = crop_res["sweet_spots"]

    actual_vals = [
        actual["temperature_c"],
        actual["precipitation_mm"] / 10,
        actual["altitude_m"] / 10,
        actual["soil_moisture_m3_m3"] * 100,
    ]
    sweet_vals = [
        sweet["temperature_c"],
        sweet["precipitation_mm"] / 10,
        sweet["altitude_m"] / 10,
        sweet["soil_moisture_m3_m3"] * 100,
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name=t("chart_sweet_label"),
        x=params,
        y=sweet_vals,
        marker_color="rgba(46, 125, 50, 0.7)" if not dark_mode else "rgba(76, 175, 80, 0.75)",
        marker_line=dict(color="#1B5E20" if not dark_mode else "#81C784", width=1.5),
    ))
    fig.add_trace(go.Bar(
        name=t("chart_actual_label"),
        x=params,
        y=actual_vals,
        marker_color="rgba(230, 81, 0, 0.75)" if not dark_mode else "rgba(255, 152, 0, 0.8)",
        marker_line=dict(color="#BF360C" if not dark_mode else "#FFB74D", width=1.5),
    ))

    fig.update_layout(
        barmode="group",
        title=f"<b>{t('chart_delta_title')} — {crop_res['icon']} {crop_res['crop']}</b>",
        title_font={"color": theme["text_color"], "size": 13},
        font={"color": theme["text_color"], "family": theme["font_family"]},
        yaxis=dict(
            title=dict(text=t("chart_delta_y"), font=dict(color=theme["text_color"])),
            showgrid=True,
            gridcolor=theme["grid_color"],
            color=theme["text_color"],
            tickfont=dict(color=theme["text_color"]),
        ),
        xaxis=dict(color=theme["text_color"], tickfont=dict(color=theme["text_color"])),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font={"color": theme["text_color"], "size": 11}
        ),
        margin=dict(l=30, r=30, t=60, b=40),
        paper_bgcolor=theme["paper_bg"],
        plot_bgcolor=theme["plot_bg"],
        height=320,
    )
    return fig


def create_rotation_radar_chart(comparison_data: Dict[str, Any], primary_crop: str, dark_mode: bool = False, lang: str = "es") -> go.Figure:
    """Radar chart comparing Monoculture vs Rotation across 5 agronomic dimensions."""
    theme = get_chart_theme(dark_mode)

    dims = comparison_data["dimensions_es"] if lang == "es" else comparison_data["dimensions_en"]
    mono_scores = comparison_data["monoculture_scores"]
    rot_scores = comparison_data["rotation_scores"]

    # Close the loops
    dims_closed = dims + [dims[0]]
    mono_closed = mono_scores + [mono_scores[0]]
    rot_closed = rot_scores + [rot_scores[0]]

    fig = go.Figure()

    # Monoculture trace (red/orange fill)
    fig.add_trace(go.Scatterpolar(
        r=mono_closed,
        theta=dims_closed,
        fill="toself",
        fillcolor="rgba(239, 83, 80, 0.20)" if not dark_mode else "rgba(239, 83, 80, 0.30)",
        line=dict(color="#E53935" if not dark_mode else "#EF5350", width=2, dash="dash"),
        name="Monocultivo Continuo" if lang == "es" else "Continuous Monoculture",
        hovertemplate="<b>%{theta}</b>: %{r}%<extra></extra>",
    ))

    # Rotation trace (green vibrant fill)
    fig.add_trace(go.Scatterpolar(
        r=rot_closed,
        theta=dims_closed,
        fill="toself",
        fillcolor="rgba(46, 125, 50, 0.35)" if not dark_mode else "rgba(76, 175, 80, 0.40)",
        line=dict(color="#2E7D32" if not dark_mode else "#4CAF50", width=3),
        name="Esquema con Rotación" if lang == "es" else "Rotation Scheme",
        hovertemplate="<b>%{theta}</b>: %{r}%<extra></extra>",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=True,
                ticksuffix="%",
                gridcolor=theme["grid_color"],
                color=theme["text_color"],
                tickfont=dict(color=theme["text_color"]),
            ),
            angularaxis=dict(gridcolor=theme["grid_color"], color=theme["text_color"], tickfont=dict(color=theme["text_color"])),
            bgcolor=theme["plot_bg"],
        ),
        title=dict(
            text=f"<b>{t('chart_mono_vs_rot')} — {primary_crop}</b>",
            font=dict(color=theme["text_color"], size=14),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="center",
            x=0.5,
            font=dict(color=theme["text_color"], size=12)
        ),
        margin=dict(l=40, r=40, t=65, b=30),
        paper_bgcolor=theme["paper_bg"],
        height=380,
    )
    return fig


def create_rotation_gauge(score: int, primary_crop: str, dark_mode: bool = False, lang: str = "es") -> go.Figure:
    """Gauge showing the composite viability of the rotational system."""
    theme = get_chart_theme(dark_mode)

    if score >= 80:
        bar_color = "#2E7D32" if not dark_mode else "#4CAF50"
    elif score >= 60:
        bar_color = "#1565C0" if not dark_mode else "#42A5F5"
    else:
        bar_color = "#E65100" if not dark_mode else "#FFA726"

    title_text = "Viabilidad del Sistema Rotacional" if lang == "es" else "Rotation System Viability"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 28, "color": bar_color, "family": theme["font_family"]}},
        title={
            "text": f"<b>{title_text}</b><br><span style='font-size:11px; color:{theme['text_color']};'>{primary_crop}</span>",
            "font": {"size": 13, "color": theme["text_color"], "family": theme["font_family"]}
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": theme["subtext_color"],
                "tickfont": {"size": 10, "color": theme["subtext_color"]},
                "dtick": 25,
            },
            "bar": {"color": bar_color, "thickness": 0.75},
            "bgcolor": theme["gauge_bg"],
            "borderwidth": 1,
            "bordercolor": theme["border_color"],
            "steps": [
                {"range": [0, 50],   "color": "rgba(239, 83, 80, 0.20)"},
                {"range": [50, 75],  "color": "rgba(255, 167, 38, 0.20)"},
                {"range": [75, 100], "color": "rgba(76, 175, 80, 0.25)"},
            ],
            "threshold": {
                "line": {"color": bar_color, "width": 3},
                "thickness": 0.85,
                "value": score,
            },
        }
    ))

    fig.update_layout(
        paper_bgcolor=theme["paper_bg"],
        font={"color": theme["text_color"], "family": theme["font_family"]},
        margin=dict(l=20, r=20, t=55, b=10),
        height=220,
    )
    return fig
