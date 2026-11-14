"""Plotly interactive charts for Agro-climatic profiles and Walter-Lieth diagram."""

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

    # Precipitation Bars (Primary Y-axis)
    fig.add_trace(
        go.Bar(
            x=MONTH_NAMES,
            y=precip_series,
            name="Precipitación Total (mm)",
            marker_color="rgba(33, 150, 243, 0.75)",
            marker_line=dict(color="#1976D2", width=1.5),
            hovertemplate="<b>%{x}</b><br>Lluvia: %{y:.1f} mm<extra></extra>",
        ),
        secondary_y=False,
    )

    # Temperature Min/Max Range Fill
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

    # Mean Temperature Line (Secondary Y-axis)
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
        title="<b>Perfil Agroclimático Mensual (NASA POWER)</b>",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=30),
        plot_bgcolor="#F9FBF9",
        paper_bgcolor="#FFFFFF",
        height=380,
    )

    fig.update_yaxes(
        title_text="<b>Precipitación (mm / mes)</b>",
        secondary_y=False,
        showgrid=True,
        gridcolor="#E0E0E0",
    )
    fig.update_yaxes(
        title_text="<b>Temperatura (°C)</b>",
        secondary_y=True,
        showgrid=False,
    )

    return fig


def create_humidity_solar_chart(clima_data: Dict[str, Any]) -> go.Figure:
    """
    Creates chart for Relative Humidity (%) and Solar Irradiance.
    """
    month_keys = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    params = clima_data.get("parameters", {})

    rh_series = [params.get("RH2M", {}).get(m, 75.0) for m in month_keys]
    solar_series = [params.get("ALLSKY_SFC_SW_DWN", {}).get(m, 16.0) for m in month_keys]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=MONTH_NAMES,
            y=rh_series,
            mode="lines+markers",
            name="Humedad Relativa (%)",
            line=dict(color="#00897B", width=2.5),
            marker=dict(size=6),
            hovertemplate="Humedad: %{y:.1f}%<extra></extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=MONTH_NAMES,
            y=solar_series,
            mode="lines+markers",
            name="Radiación Solar (MJ/m²/día)",
            line=dict(color="#FB8C00", width=2.5, dash="dash"),
            marker=dict(size=6),
            hovertemplate="Radiación: %{y:.1f} MJ/m²/día<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="<b>Humedad Relativa y Radiación Solar Anual</b>",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=30),
        plot_bgcolor="#F9FBF9",
        paper_bgcolor="#FFFFFF",
        height=320,
    )

    fig.update_yaxes(title_text="<b>Humedad Relativa (%)</b>", secondary_y=False, showgrid=True, gridcolor="#E0E0E0")
    fig.update_yaxes(title_text="<b>Radiación Solar</b>", secondary_y=True, showgrid=False)

    return fig
