"""Vista de estadisticas ejecutivas y control de procesos (SPC/ROI)."""

import streamlit as st

from modules.database import (
    get_all_sessions_list,
    get_compliance_stats,
    get_history_dataframe,
    get_hourly_risk_distribution,
)
from modules.metrics import calculate_roi
from modules.charts import create_spc_control_chart, create_severity_bar_chart


def render_stats_view(is_dark: bool):
    """Renderiza el panel de control estadistico, metricas de proceso y estimacion de ROI."""
    st.markdown("### Estadísticas y Control de Procesos")
    st.caption("Métricas del análisis en vivo. Refleja las auditorías del turno activo y registros históricos en tiempo real.")

    sessions = get_all_sessions_list()
    session_options = {"Histórico Global Consolidado": None}
    for s in sessions:
        status_tag = "(En Curso - Preliminar)" if s.get("status") == "active" else "(Cerrada)"
        label = f"Sesión #{s['id']} {status_tag} ({s.get('start_time', '')}) - {s.get('total_events', 0)} eventos"
        session_options[label] = s['id']

    selected_label = st.selectbox(
        "Seleccionar Sesión / Turno para Análisis:",
        list(session_options.keys()),
        key="stats_session_select"
    )
    selected_session = session_options[selected_label]

    @st.fragment(run_every="2s")
    def render_live_stats_charts(target_session):
        total_inspections, _, compliance_rate, total_infractions = get_compliance_stats(session_id=target_session)
        roi_default = calculate_roi(120, 2500)

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi_label = f"Auditorías (Sesión #{target_session})" if target_session else "Total Auditorías Históricas"
        infraction_pct = round((total_infractions / total_inspections * 100), 1) if total_inspections > 0 else 0

        kpi1.metric(label=kpi_label, value=f"{total_inspections:,}", delta=f"{infraction_pct}% infracciones")
        kpi2.metric(label="% Cumplimiento", value=f"{compliance_rate}%", delta=f"{compliance_rate - 75:.1f}% vs media industrial")
        kpi3.metric(label="Total Infracciones", value=f"{total_infractions}", delta=f"{infraction_pct}% tasa crítica")
        kpi4.metric(label="ROI Estimado Anual", value=f"${roi_default['total_saved']:,.0f} USD", delta=f"ROI +{roi_default['roi_percent']:.0f}%")

        st.markdown("---")

        col_chart1, col_chart2 = st.columns([1.1, 1.3])

        with col_chart1:
            st.markdown("#### Distribución de Severidad y Cumplimiento EPP")
            chart_df = get_history_dataframe(session_id=target_session)
            fig_bars = create_severity_bar_chart(chart_df, is_dark=is_dark)
            st.plotly_chart(fig_bars, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Desglose semafórico y frecuencia de eventos por categoría.*")

        with col_chart2:
            st.markdown("#### Gráfico de Control Estadístico Horario (SPC)")
            hours_data = get_hourly_risk_distribution(session_id=target_session)
            fig_spc = create_spc_control_chart(hours_data, is_dark=is_dark)
            st.plotly_chart(fig_spc, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Límites de control estadístico (UCL/CL) y picos de riesgo (ISO 45001 / OSHA).*")

    render_live_stats_charts(selected_session)

    st.markdown("---")

    st.markdown("#### Calculadora Interactiva de Retorno de Inversión (ROI)")
    st.write("Ajusta las variables operativas de la planta para estimar el ahorro anual con **Vigilante EPP**.")

    col_inputs, col_results = st.columns([1.1, 1.2])

    with col_inputs:
        num_workers = st.slider("Trabajadores en Planta / Turno:", min_value=1, max_value=200, value=50, step=5)
        avg_fine = st.slider("Costo promedio por multa o incidente laboral (USD):", min_value=500, max_value=10000, value=2500, step=250)
        roi = calculate_roi(num_workers, avg_fine)

    with col_results:
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.metric(
                label="Accidentes Evitados / Año",
                value=f"{roi['saved_incidents']}",
                delta="85% tasa de reducción"
            )
        with res_col2:
            st.metric(
                label="Ahorro Anual Estimado",
                value=f"${roi['total_saved']:,.0f} USD",
                delta=f"ROI Neto: +{roi['roi_percent']:.0f}%"
            )

        st.markdown(f"""
        > **Resumen Ejecutivo:** Con una dotación de **{num_workers} operarios**, Vigilante EPP proyecta evitar **~{roi['saved_incidents']} incidentes anuales**, generando un ahorro estimado de **${roi['total_saved']:,.2f} USD** en multas laborales y primas de seguro.
        """)
