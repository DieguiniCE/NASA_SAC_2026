"""Plotly interactive charts for Agro-climatic profiles, satellite gauges, and viability radar."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List
from src.config import MONTH_NAMES


def create_viability_gauge(score: int, crop_name: str, icon: str = "🌱") -> go.Figure:
    """
    Creates a Plotly gauge chart for a single crop viability score.
    Color: red < 40, orange < 60, blue < 80, green >= 80.
    """
    if score >= 80:
        bar_color = "#2E7D32"
        bg_color = "#E8F5E9"
    elif score >= 60:
        bar_color = "#1565C0"
        bg_color = "#E3F2FD"
    elif score >= 40:
        bar_color = "#E65100"
        bg_color = "#FFF3E0"
    else:
        bar_color = "#B71C1C"
        bg_color = "#FFEBEE"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 26, "color": bar_color, "family": "Inter, sans-serif"}},
        title={
            "text": f"<b>{icon} {crop_name}</b>",
            "font": {"size": 13, "color": "#333", "family": "Inter, sans-serif"}
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#BDBDBD",
                "tickfont": {"size": 10},
                "dtick": 25,
            },
            "bar": {"color": bar_color, "thickness": 0.75},
            "bgcolor": "#F5F5F5",
            "borderwidth": 1,
            "bordercolor": "#E0E0E0",
            "steps": [
                {"range": [0, 40],   "color": "#FFCDD2"},
                {"range": [40, 60],  "color": "#FFE0B2"},
                {"range": [60, 80],  "color": "#BBDEFB"},
                {"range": [80, 100], "color": "#C8E6C9"},
            ],
            "threshold": {
                "line": {"color": bar_color, "width": 3},
                "thickness": 0.85,
                "value": score,
            },
        }
    ))

    fig.update_layout(
        paper_bgcolor=bg_color,
        margin=dict(l=20, r=20, t=50, b=10),
        height=200,
    )
    return fig


def create_viability_bar_chart(all_results: List[Dict[str, Any]]) -> go.Figure:
    """
    Creates a horizontal bar chart comparing viability scores for all 5 crops.
    """
    crops = [f"{r['icon']} {r['crop']}" for r in all_results]
    scores = [r["success_percentage"] for r in all_results]
    colors = []
    for s in scores:
        if s >= 80:
            colors.append("#2E7D32")
        elif s >= 60:
            colors.append("#1565C0")
        elif s >= 40:
            colors.append("#E65100")
        else:
            colors.append("#B71C1C")

    fig = go.Figure(go.Bar(
        x=scores,
        y=crops,
        orientation="h",
        marker_color=colors,
        text=[f"{s}%" for s in scores],
        textposition="outside",
        textfont=dict(size=13, color="#333"),
        hovertemplate="<b>%{y}</b><br>Viabilidad: %{x}%<extra></extra>",
    ))

    fig.add_vline(x=80, line_dash="dot", line_color="#2E7D32", line_width=1.5,
                  annotation_text="Alta", annotation_font_color="#2E7D32", annotation_font_size=11)
    fig.add_vline(x=60, line_dash="dot", line_color="#1565C0", line_width=1,
                  annotation_text="Mod.", annotation_font_color="#1565C0", annotation_font_size=11)

    fig.update_layout(
        title="<b>Comparativa de Viabilidad — 5 Cultivos</b>",
        xaxis=dict(range=[0, 115], title="Porcentaje de Viabilidad (%)", showgrid=True, gridcolor="#EEEEEE"),
        yaxis=dict(title=""),
        margin=dict(l=10, r=60, t=50, b=30),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FAFAFA",
        height=280,
    )
    return fig


def create_climadiagram(clima_data: Dict[str, Any]) -> go.Figure:
    """
    Creates a combined Walter-Lieth style Agroclimatic diagram:
    Precipitation (bars, mm/month) and Mean Temperature (line, °C) over 12 months.
    """
    month_keys = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    params = clima_data.get("parameters", {})

    temp_series = [params.get("T2M", {}).get(m, 22.0) for m in month_keys]
    temp_max_series = [params.get("T2M_MAX", {}).get(m, 27.0) for m in month_keys]
    temp_min_series = [params.get("T2M_MIN", {}).get(m, 17.0) for m in month_keys]
    precip_series = [params.get("PRECTOT_MONTHLY", {}).get(m, 150.0) for m in month_keys]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=MONTH_NAMES,
            y=precip_series,
            name="Lluvia GPM / POWER (mm)",
            marker_color="rgba(33, 150, 243, 0.75)",
            marker_line=dict(color="#1976D2", width=1.5),
            hovertemplate="<b>%{x}</b><br>Lluvia: %{y:.1f} mm<extra></extra>",
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
            fillcolor="rgba(255, 152, 0, 0.18)",
            name="Rango T° Mín-Máx",
            hoverinfo="skip",
        ),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(
            x=MONTH_NAMES,
            y=temp_series,
            mode="lines+markers",
            name="Temperatura Media (°C)",
            line=dict(color="#E65100", width=3),
            marker=dict(size=7, color="#BF360C"),
            hovertemplate="<b>%{x}</b><br>T° Media: %{y:.1f} °C<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="<b>Perfil Agrometeorológico Mensual (NASA POWER & GPM DPR)</b>",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=30),
        plot_bgcolor="#F9FBF9",
        paper_bgcolor="#FFFFFF",
        height=360,
    )

    fig.update_yaxes(title_text="<b>Precipitación (mm / mes)</b>", secondary_y=False, showgrid=True, gridcolor="#E0E0E0")
    fig.update_yaxes(title_text="<b>Temperatura (°C)</b>", secondary_y=True, showgrid=False)

    return fig


def create_moisture_comparison_chart(surface_sm: float, root_sm: float, esi_val: float) -> go.Figure:
    """
    Creates comparative bar gauges for SMAP L2 Surface vs L4 Root moisture and ECOSTRESS ESI.
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Humedad Volumétrica (m³/m³)",
        x=["SMAP L2 Superficie (0-5cm)", "SMAP L4 Zona Radicular (0-100cm)"],
        y=[surface_sm, root_sm],
        text=[f"{surface_sm:.3f} m³/m³", f"{root_sm:.3f} m³/m³"],
        textposition="auto",
        marker_color=["#42A5F5", "#1E88E5"],
    ))

    fig.update_layout(
        title="<b>Humedad del Suelo: Superficie vs. Zona Radicular (NASA SMAP)</b>",
        yaxis=dict(title="Contenido Volumétrico de Agua (m³/m³)", range=[0, 0.55], showgrid=True),
        margin=dict(l=40, r=40, t=50, b=40),
        plot_bgcolor="#FAFAFA",
        paper_bgcolor="#FFFFFF",
        height=320,
    )
    return fig


def create_viability_radar_chart(breakdown: Dict[str, float], crop_name: str, overall_score: int) -> go.Figure:
    """
    Creates a radar / polar chart for the multi-factor viability model.
    """
    categories = list(breakdown.keys())
    values = list(breakdown.values())

    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(76, 175, 80, 0.25)",
        line=dict(color="#2E7D32", width=2.5),
        name=crop_name,
        hovertemplate="<b>%{theta}</b>: %{r}%<extra></extra>",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=True,
                ticksuffix="%",
                gridcolor="#E0E0E0",
            ),
            angularaxis=dict(gridcolor="#E0E0E0")
        ),
        title=f"<b>Aptitud Agroclimática: {crop_name} ({overall_score}/100)</b>",
        margin=dict(l=40, r=40, t=60, b=30),
        paper_bgcolor="#FFFFFF",
        height=360,
    )
    return fig


def create_temperature_breakdown_chart(air_t: float, ground_t: float, max_t: float, min_t: float) -> go.Figure:
    """
    Bar chart comparing Air Temperature and Ground/Surface Temperature (ECOSTRESS / SMAP).
    """
    labels = ["T° Mínima Aire", "T° Media Aire (POWER)", "T° Suelo / LST (ECOSTRESS)", "T° Máxima Aire"]
    vals = [min_t, air_t, ground_t, max_t]
    colors = ["#29B6F6", "#FFA726", "#EF5350", "#D32F2F"]

    fig = go.Figure(go.Bar(
        x=labels,
        y=vals,
        text=[f"{v:.1f} °C" for v in vals],
        textposition="auto",
        marker_color=colors
    ))

    fig.update_layout(
        title="<b>Termometría: Temperatura del Aire vs. Temperatura del Suelo</b>",
        yaxis=dict(title="Temperatura (°C)", range=[0, max(38.0, max_t + 5)]),
        margin=dict(l=30, r=30, t=50, b=30),
        height=300,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FAFAFA",
    )
    return fig


def create_delta_comparison_chart(crop_res: Dict[str, Any]) -> go.Figure:
    """
    Horizontal bar chart showing actual vs. sweet-spot values for a single crop.
    Shows delta as distance from ideal.
    """
    params = ["Temperatura (°C)", "Precipitación (÷10 mm)", "Altitud (÷10 m)", "Humedad Suelo (×100 m³/m³)"]
    actual = crop_res["actual_values"]
    sweet = crop_res["sweet_spots"]

    # Normalize to comparable scale
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
        name="Sweet Spot (Ideal)",
        x=params,
        y=sweet_vals,
        marker_color="rgba(46, 125, 50, 0.6)",
        marker_line=dict(color="#1B5E20", width=1.5),
    ))
    fig.add_trace(go.Bar(
        name="Valor Actual",
        x=params,
        y=actual_vals,
        marker_color="rgba(230, 81, 0, 0.75)",
        marker_line=dict(color="#BF360C", width=1.5),
    ))

    fig.update_layout(
        barmode="group",
        title=f"<b>Actual vs. Sweet Spot — {crop_res['icon']} {crop_res['crop']}</b>",
        yaxis=dict(title="Valor (escala normalizada)", showgrid=True, gridcolor="#EEEEEE"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=30, r=30, t=60, b=40),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FAFAFA",
        height=320,
    )
    return fig
