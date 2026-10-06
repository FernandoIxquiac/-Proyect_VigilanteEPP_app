import plotly.graph_objects as go
import numpy as np
import pandas as pd

def create_spc_control_chart(hours_df: pd.DataFrame, is_dark: bool = True) -> go.Figure:
    """
    Genera un Gráfico de Control Estadístico de Procesos (SPC / Shewhart Run Chart)
    para el monitoreo de infracciones horarias bajo normativa ISO 45001 / OSHA.
    
    Incluye:
    - Línea de tendencia real con marcadores por hora.
    - Línea Central (CL - Media del Proceso).
    - Límite Superior de Control (UCL - Umbral de Alarma Preventiva).
    - Meta Objetivo Cero Accidentes (LCL = 0).
    """
    text_color = "#f8fafc" if is_dark else "#0f172a"
    muted_color = "#94a3b8" if is_dark else "#64748b"
    grid_color = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.08)"
    bg_paper = "rgba(0, 0, 0, 0)"

    if hours_df.empty or "Turno" not in hours_df.columns:
        hours_df = pd.DataFrame({
            "Turno": ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00"],
            "Infracciones": [0, 0, 0, 0, 0, 0]
        })

    x_vals = hours_df["Turno"].tolist()
    y_vals = hours_df["Infracciones"].tolist()
    y_arr = np.array(y_vals, dtype=float)

    # Cálculo estadístico de límites de control
    mean_val = float(np.mean(y_arr)) if len(y_arr) > 0 else 0.0
    std_val = float(np.std(y_arr)) if len(y_arr) > 0 else 0.0
    
    # UCL: Si la desviación es baja, usar un umbral operativo mínimo para dar perspectiva industrial
    ucl_val = max(mean_val + 2.5 * std_val, mean_val + 2.0, 3.0)
    ucl_val = round(ucl_val, 1)

    fig = go.Figure()

    # 1. Área bajo la curva con gradiente semitransparente
    fill_color = "rgba(96, 165, 250, 0.15)" if is_dark else "rgba(37, 99, 235, 0.12)"
    line_color = "#60a5fa" if is_dark else "#2563eb"

    # Marcadores dinámicos: si supera UCL se tiñe de rojo crítico
    marker_colors = []
    marker_sizes = []
    marker_symbols = []
    for v in y_vals:
        if v >= ucl_val and v > 0:
            marker_colors.append("#ef4444")
            marker_sizes.append(10)
            marker_symbols.append("diamond")
        else:
            marker_colors.append(line_color)
            marker_sizes.append(8)
            marker_symbols.append("circle")

    # Trazo de datos reales
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode="lines+markers",
        name="Infracciones Registradas",
        line=dict(color=line_color, width=2.5, shape="spline"),
        marker=dict(
            color=marker_colors,
            size=marker_sizes,
            symbol=marker_symbols,
            line=dict(width=1.5, color="#ffffff" if is_dark else "#0f172a")
        ),
        fill="tozeroy",
        fillcolor=fill_color,
        hovertemplate="<b>Hora: %{x}</b><br>Infracciones: %{y}<extra></extra>"
    ))

    # 2. Línea Superior de Control (UCL - Alarma ISO / OSHA)
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=[ucl_val] * len(x_vals),
        mode="lines",
        name=f"UCL Alarma ({ucl_val})",
        line=dict(color="#ef4444", width=1.8, dash="dash"),
        hoverinfo="skip"
    ))

    # 3. Línea Central (CL - Media del Proceso)
    cl_val = round(mean_val, 1)
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=[cl_val] * len(x_vals),
        mode="lines",
        name=f"Media CL ({cl_val})",
        line=dict(color="#f59e0b", width=1.5, dash="dot"),
        hoverinfo="skip"
    ))

    # 4. Meta Objetivo Cero Accidentes (LCL = 0)
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=[0] * len(x_vals),
        mode="lines",
        name="Meta Cero (0)",
        line=dict(color="#10b981", width=1.2, dash="dashdot"),
        hoverinfo="skip"
    ))

    # Configuración de Layout y Estilo Cockpit Industrial
    y_max = max(max(y_vals, default=0), ucl_val) + 1.2
    fig.update_layout(
        paper_bgcolor=bg_paper,
        plot_bgcolor=bg_paper,
        font=dict(family="Inter, sans-serif", color=text_color, size=11),
        margin=dict(l=15, r=15, t=30, b=25),
        height=280,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=muted_color),
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(
            showgrid=False,
            color=muted_color,
            tickfont=dict(size=10, color=muted_color),
            linecolor=grid_color
        ),
        yaxis=dict(
            range=[0, y_max],
            showgrid=True,
            gridcolor=grid_color,
            color=muted_color,
            tickfont=dict(size=10, color=muted_color),
            zeroline=False
        ),
        hoverlabel=dict(
            bgcolor="#171f33" if is_dark else "#ffffff",
            font_size=11,
            font_family="Inter, sans-serif",
            font_color="#f8fafc" if is_dark else "#0f172a"
        )
    )

    return fig


def create_severity_bar_chart(history_df: pd.DataFrame, is_dark: bool = True) -> go.Figure:
    """
    Genera un Gráfico de Barras Horizontales de Severidad y Frecuencia de EPP.
    
    Ventajas:
    - Orientación horizontal: los títulos largos nunca se truncan ni se solapan.
    - Asignación de colores semafóricos reales (Verde = Cumple, Naranja = Advertencia, Rojo = Peligro).
    - Conteo exacto y porcentaje visualizado directamente al extremo de cada barra.
    """
    text_color = "#f8fafc" if is_dark else "#0f172a"
    muted_color = "#94a3b8" if is_dark else "#64748b"
    grid_color = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.08)"
    bg_paper = "rgba(0, 0, 0, 0)"

    if history_df.empty or "Categoría" not in history_df.columns:
        history_df = pd.DataFrame([
            {"Categoría": "Cumplimiento Total (OK)", "Cantidad de Eventos": 0},
            {"Categoría": "Sin Chaleco", "Cantidad de Eventos": 0},
            {"Categoría": "Sin Casco", "Cantidad de Eventos": 0}
        ])

    df = history_df.copy()
    total_events = df["Cantidad de Eventos"].sum()

    # Mapeo de colores semafóricos según categoría y severidad
    def get_color(cat: str):
        c_lower = str(cat).lower()
        if "ok" in c_lower or "cumplimiento" in c_lower or "completo" in c_lower:
            return "#10b981"  # Verde esmeralda
        elif "chaleco" in c_lower:
            return "#f59e0b"  # Naranja advertencia
        elif "casco" in c_lower or "peligro" in c_lower or "sin epp" in c_lower:
            return "#ef4444"  # Rojo crítico
        else:
            return "#60a5fa"  # Azul default

    colors = [get_color(c) for c in df["Categoría"]]
    
    # Texto de etiquetas con valor y porcentaje
    bar_texts = []
    for val in df["Cantidad de Eventos"]:
        if total_events > 0:
            pct = (val / total_events) * 100
            bar_texts.append(f"  <b>{val}</b> ({pct:.1f}%)")
        else:
            bar_texts.append(f"  <b>{val}</b>")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df["Categoría"],
        x=df["Cantidad de Eventos"],
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(color="rgba(0,0,0,0)", width=0)
        ),
        text=bar_texts,
        textposition="outside",
        textfont=dict(color=text_color, size=11, family="Inter, sans-serif"),
        hovertemplate="<b>%{y}</b><br>Eventos: %{x}<extra></extra>"
    ))

    # Asegurar margen horizontal para las etiquetas exteriores
    max_val = df["Cantidad de Eventos"].max() if len(df) > 0 else 0
    x_limit = max_val * 1.35 if max_val > 0 else 5

    fig.update_layout(
        paper_bgcolor=bg_paper,
        plot_bgcolor=bg_paper,
        font=dict(family="Inter, sans-serif", color=text_color, size=11),
        margin=dict(l=10, r=40, t=20, b=25),
        height=280,
        showlegend=False,
        xaxis=dict(
            range=[0, x_limit],
            showgrid=True,
            gridcolor=grid_color,
            color=muted_color,
            tickfont=dict(size=10, color=muted_color),
            zeroline=False
        ),
        yaxis=dict(
            autorange="reversed",  # Muestra el orden natural de arriba hacia abajo
            showgrid=False,
            color=text_color,
            tickfont=dict(size=11, color=text_color, family="Inter, sans-serif")
        ),
        hoverlabel=dict(
            bgcolor="#171f33" if is_dark else "#ffffff",
            font_size=11,
            font_family="Inter, sans-serif",
            font_color="#f8fafc" if is_dark else "#0f172a"
        )
    )

    return fig
