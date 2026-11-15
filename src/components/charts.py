"""Plotly interactive charts for Agro-climatic profiles, satellite gauges, and viability radar."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any
from src.config import MONTH_NAMES


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

    # Close the radar loop
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
        title=f"<b>Aptitud Agroclimática Multivariable: {crop_name} ({overall_score}/100)</b>",
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
