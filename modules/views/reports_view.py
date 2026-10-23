"""Vista de reportes periciales, bitacora forense y exportacion formal (ISO 45001 / OSHA)."""

import os
import datetime
import pandas as pd
import streamlit as st

from styles import get_svg_icon
from modules.database import (
    get_all_sessions_list,
    close_active_session,
    get_detailed_events_dataframe,
    get_history_dataframe,
)
from modules.report_generator import compute_audit_kpis, generate_html_report


def render_reports_view(is_dark: bool):
    """Renderiza el dictamen pericial, bitacora forense, galeria y exportacion oficial."""
    st.markdown("### Reportes y Exportación")
    st.caption("Dictamen pericial automatizado con trazabilidad por operario, peritaje fotográfico y exportación oficial (ISO 45001 / OSHA).")

    sessions = get_all_sessions_list()
    session_options = {"Histórico Global Consolidado": None}
    session_status_map = {None: "closed"}
    for s in sessions:
        is_active_sess = (s.get("status") == "active")
        status_tag = "(En Curso - Preliminar)" if is_active_sess else "(Cerrada)"
        label = f"Sesión #{s['id']} {status_tag} ({s.get('start_time', '')}) - {s.get('total_events', 0)} eventos"
        session_options[label] = s['id']
        session_status_map[s['id']] = s.get("status", "closed")

    col_rep_sess, col_rep_auditor = st.columns([1.5, 1.5])
    with col_rep_sess:
        selected_label = st.selectbox("Seleccionar Sesión para Reporte:", list(session_options.keys()))
        selected_session = session_options[selected_label]
        is_active_selected = (session_status_map.get(selected_session) == "active")
    with col_rep_auditor:
        auditor_name = st.text_input("Nombre del Auditor / Perito:", value="Supervisor SST")

    if is_active_selected:
        col_alert_act, col_close_act = st.columns([2.3, 1.3])
        with col_alert_act:
            st.warning("**Turno en Operación Continua:** Esta sesión continúa acumulando eventos en tiempo real. Puedes generar dictámenes preliminares sin pausar la supervisión.")
        with col_close_act:
            if st.button("Cerrar Turno Actual y Sellar Dictamen", type="primary", use_container_width=True, help="Concluye la sesión activa actual, fijando los totales definitivos"):
                close_active_session(session_id=selected_session)
                st.success("Turno concluido formalmente. El dictamen ahora es definitivo.")
                st.rerun()

    detailed_df = get_detailed_events_dataframe(session_id=selected_session)

    if detailed_df.empty:
        st.info("No hay datos registrados. Usa la sección Análisis en Vivo para comenzar.")
        return

    audit_kpis = compute_audit_kpis(detailed_df)

    v_color = "#10b981" if audit_kpis["risk_badge"] == "safe" else ("#ef4444" if audit_kpis["risk_badge"] == "danger" else "#f59e0b")
    diag_icon_name = "shield-check" if audit_kpis["risk_badge"] == "safe" else ("shield-x" if audit_kpis["risk_badge"] == "danger" else "alert-triangle")
    diag_icon_svg = get_svg_icon(diag_icon_name, size=16, color=v_color, stroke_width=2.2)

    st.markdown(f"""
    <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-left: 6px solid {v_color}; border-radius: 8px; padding: 14px 18px; margin-bottom: 16px; box-shadow: var(--shadow-card);">
        <div style="display:flex; align-items:center; gap:6px; font-size:0.75rem; font-weight:700; color:{v_color}; text-transform:uppercase; letter-spacing:0.04em;">
            {diag_icon_svg} DIAGNÓSTICO PERICIAL DE AUDITORÍA
        </div>
        <div style="font-size:1.1rem; font-weight:800; color:var(--text-primary); margin: 4px 0;">{audit_kpis['risk_verdict']}</div>
        <div style="font-size:0.82rem; color:var(--text-secondary);">Infracción predominante: <strong style="color:var(--text-primary);">{audit_kpis['top_infraction']}</strong> &bull; Total de verificaciones: <strong style="color:var(--text-primary);">{audit_kpis['total_inspections']}</strong> &bull; Apego a la norma: <strong style="color:{v_color};">{audit_kpis['compliance_pct']}%</strong></div>
    </div>
    """, unsafe_allow_html=True)

    col_f1, col_f2 = st.columns([1.5, 1.5])
    with col_f1:
        filter_severity = st.selectbox(
            "Filtrar por nivel de riesgo:",
            ["Todos los registros", "Solo Infracciones (Crítico / Advertencia)", "Solo Cumplimientos (Seguro)"]
        )
    with col_f2:
        all_workers = ["Todos los operarios"]
        if not detailed_df.empty and "ID_Operario" in detailed_df.columns:
            unique_w = [w for w in detailed_df["ID_Operario"].dropna().unique().tolist() if w != "N/A"]
            unique_w.sort()
            all_workers.extend(unique_w)
        filter_worker = st.selectbox("Filtrar por operario rastreado:", all_workers)

    filtered_df = detailed_df.copy()
    if "Solo Infracciones" in filter_severity:
        filtered_df = filtered_df[filtered_df["Nivel_Riesgo"].isin(["danger", "warning"])]
    elif "Solo Cumplimientos" in filter_severity:
        filtered_df = filtered_df[filtered_df["Nivel_Riesgo"] == "safe"]

    if filter_worker != "Todos los operarios":
        filtered_df = filtered_df[filtered_df["ID_Operario"] == filter_worker]

    if not filtered_df.empty:
        col_vm1, col_vm2 = st.columns([1.6, 1.4])
        with col_vm1:
            st.markdown(f"**Registros coincidentes:** `{len(filtered_df)} eventos periciales`")
        with col_vm2:
            view_mode = st.radio(
                "Modalidad de visualización:",
                ["Tabla Ejecutiva (ISO 45001)", "Tarjetas Periciales (Feed)"],
                horizontal=True,
                label_visibility="collapsed"
            )

        if "Tabla" in view_mode:
            display_df = filtered_df.copy()
            risk_map = {
                "safe": "CONFORME",
                "warning": "ADVERTENCIA",
                "danger": "CRÍTICO"
            }
            display_df["Nivel_Riesgo"] = display_df["Nivel_Riesgo"].map(lambda x: risk_map.get(str(x).lower(), str(x)))
            if "ID_Evento" in display_df.columns:
                display_df["ID_Evento"] = display_df["ID_Evento"].apply(lambda x: f"#EV-{int(x):04d}" if pd.notna(x) else "")
            if "Certeza_Pct" in display_df.columns:
                display_df["Certeza_Pct"] = display_df["Certeza_Pct"].apply(lambda x: f"{float(x):.1f}%" if pd.notna(x) else "95.0%")

            cols_to_show = [c for c in ["ID_Evento", "Sesion", "ID_Operario", "Fecha_Hora", "Categoria", "Detalle_Auditoria", "Nivel_Riesgo", "Certeza_Pct"] if c in display_df.columns]

            st.dataframe(
                display_df[cols_to_show],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID_Evento": st.column_config.TextColumn("Código", width="small"),
                    "Sesion": st.column_config.TextColumn("Turno / Sesión", width="medium"),
                    "ID_Operario": st.column_config.TextColumn("Operario", width="small"),
                    "Fecha_Hora": st.column_config.DatetimeColumn("Fecha y Hora", format="DD/MM/YYYY HH:mm:ss", width="medium"),
                    "Categoria": st.column_config.TextColumn("Categoría EPP", width="medium"),
                    "Detalle_Auditoria": st.column_config.TextColumn("Dictamen Pericial", width="large"),
                    "Nivel_Riesgo": st.column_config.TextColumn("Nivel de Riesgo", width="small"),
                    "Certeza_Pct": st.column_config.TextColumn("Certeza IA", width="small")
                }
            )
        else:
            card_cols = st.columns(2)
            bg_card_hex = "#171f33" if is_dark else "#ffffff"
            text_main = "#f8fafc" if is_dark else "#0f172a"
            text_sub = "#94a3b8" if is_dark else "#64748b"
            border_dark = "#424754" if is_dark else "#cbd5e1"

            for idx, (_, row) in enumerate(filtered_df.iterrows()):
                col = card_cols[idx % 2]
                r_status = str(row.get("Nivel_Riesgo", "safe")).lower()
                b_color = "#10b981" if r_status == "safe" else ("#ef4444" if r_status == "danger" else "#f59e0b")
                b_bg = "rgba(16, 185, 129, 0.15)" if r_status == "safe" else ("rgba(239, 68, 68, 0.15)" if r_status == "danger" else "rgba(245, 158, 11, 0.15)")
                b_text = "CONFORME" if r_status == "safe" else ("CRÍTICO" if r_status == "danger" else "ADVERTENCIA")
                card_icon_name = "shield-check" if r_status == "safe" else ("shield-x" if r_status == "danger" else "alert-triangle")
                card_icon_svg = get_svg_icon(card_icon_name, size=11, color=b_color, stroke_width=2.0)

                img_path = str(row.get("Ruta_Evidencia", "") or "")
                has_img = os.path.exists(img_path) if img_path else False

                with col:
                    st.markdown(f"""
                    <div style="background:{bg_card_hex}; border:1px solid {border_dark}; border-left:5px solid {b_color}; border-radius:8px; padding:12px 14px; margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <span style="font-size:0.75rem; font-family:monospace; font-weight:700; color:{text_sub};">#EV-{int(row.get('ID_Evento', 0)):04d} &bull; {row.get('Fecha_Hora', '')}</span>
                            <span style="display:inline-flex; align-items:center; gap:4px; background:{b_bg}; color:{b_color}; border:1px solid {b_color}; font-size:0.68rem; font-weight:800; padding:2px 8px; border-radius:4px;">{card_icon_svg} {b_text}</span>
                        </div>
                        <div style="font-size:0.94rem; font-weight:800; color:{text_main}; margin-bottom:4px;">
                            {row.get('ID_Operario', 'Operario')} &bull; {row.get('Categoria', '')}
                        </div>
                        <div style="font-size:0.80rem; color:{text_sub}; line-height:1.3;">
                            {row.get('Detalle_Auditoria', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if has_img:
                        with st.expander(f"Ver Evidencia Fotográfica ({row.get('ID_Operario', 'Operario')})", expanded=False):
                            st.image(img_path, use_container_width=True)
    else:
        st.info("No se encontraron registros que coincidan con los filtros seleccionados.")

    st.markdown("---")
    st.markdown("#### Galería de Evidencias Fotográficas de Infracciones")
    st.caption("Registro visual pericial de capturas fotográficas asociadas a infracciones detectadas por cámara.")

    with st.expander("Desplegar / Ocultar Galería de Evidencias Fotográficas", expanded=True):
        if "Ruta_Evidencia" in detailed_df.columns:
            evidence_rows = detailed_df[detailed_df["Ruta_Evidencia"].notna() & (detailed_df["Ruta_Evidencia"] != "")]
            if not evidence_rows.empty:
                evidence_cols = st.columns(3)
                for idx, (_, ev_row) in enumerate(evidence_rows.head(6).iterrows()):
                    col = evidence_cols[idx % 3]
                    img_path = ev_row["Ruta_Evidencia"]
                    if os.path.exists(img_path):
                        caption_text = f"{ev_row.get('ID_Operario', 'Operario')} - {ev_row.get('Categoria', '')}\n{ev_row.get('Fecha_Hora', '')}"
                        col.image(img_path, caption=caption_text, use_container_width=True)
            else:
                st.info("No hay evidencias fotográficas registradas en este periodo.")
        else:
            st.info("No hay evidencias fotográficas registradas aún.")

    st.markdown("---")
    st.markdown("#### Exportación Oficial de Informes y Certificados")

    col_exp1, col_exp2, col_exp3 = st.columns(3)
    with col_exp1:
        session_display = f"Sesión #{selected_session}" if selected_session else "Histórico Global Consolidado"
        html_report = generate_html_report(
            filtered_df,
            session_name=session_display,
            auditor_name=auditor_name,
            is_preliminary=is_active_selected
        )
        html_filename = f"informe_auditoria_epp_{datetime.date.today()}.html"
        pdf_icon = get_svg_icon("file-download", size=15, color="var(--brand-primary)", extra_style="margin-right:6px;")
        rep_banner_title = "DICTAMEN PRELIMINAR (HTML / PDF)" if is_active_selected else "INFORME FORMAL (HTML / PDF)"
        rep_btn_label = "Descargar Dictamen Preliminar (PDF)" if is_active_selected else "Descargar Informe Oficial (PDF)"
        st.markdown(f"<div style='display:flex; align-items:center; font-size:0.76rem; font-weight:700; color:var(--text-secondary); margin-bottom:6px;'>{pdf_icon} {rep_banner_title}</div>", unsafe_allow_html=True)
        st.download_button(
            label=rep_btn_label,
            data=html_report.encode("utf-8"),
            file_name=html_filename,
            mime="text/html",
            use_container_width=True,
            help="Descarga el informe oficial en formato HTML con membrete, listo para guardar en PDF con Ctrl+P"
        )
    with col_exp2:
        forensic_csv = filtered_df.to_csv(index=False).encode('utf-8')
        csv_name = f"vigilante_epp_sesion_{selected_session}_{datetime.date.today()}.csv" if selected_session else f"vigilante_epp_historico_{datetime.date.today()}.csv"
        csv_icon = get_svg_icon("file-spreadsheet", size=15, color="var(--brand-primary)", extra_style="margin-right:6px;")
        st.markdown(f"<div style='display:flex; align-items:center; font-size:0.76rem; font-weight:700; color:var(--text-secondary); margin-bottom:6px;'>{csv_icon} BITÁCORA FORENSE (CSV)</div>", unsafe_allow_html=True)
        st.download_button(
            label="Descargar Bitácora Forense (.CSV)",
            data=forensic_csv,
            file_name=csv_name,
            mime="text/csv",
            use_container_width=True
        )
    with col_exp3:
        chart_df = get_history_dataframe(session_id=selected_session)
        summary_csv = chart_df.to_csv(index=False).encode('utf-8')
        summary_icon = get_svg_icon("file-spreadsheet", size=15, color="var(--brand-primary)", extra_style="margin-right:6px;")
        st.markdown(f"<div style='display:flex; align-items:center; font-size:0.76rem; font-weight:700; color:var(--text-secondary); margin-bottom:6px;'>{summary_icon} RESUMEN CONSOLIDADO (CSV)</div>", unsafe_allow_html=True)
        st.download_button(
            label="Descargar Resumen Consolidado (.CSV)",
            data=summary_csv,
            file_name=f"vigilante_epp_resumen_kpis_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
