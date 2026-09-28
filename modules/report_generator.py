import os
import base64
import datetime
import pandas as pd

def compute_audit_kpis(detailed_df: pd.DataFrame) -> dict:
    """Calcula métricas analíticas e índices de riesgo pericial para el informe."""
    if detailed_df.empty:
        return {
            "total_inspections": 0,
            "compliance_pct": 100.0,
            "infractions_count": 0,
            "risk_verdict": "SIN DATOS SUFICIENTES",
            "risk_badge": "info",
            "top_infraction": "Ninguna",
            "top_workers_infractions": []
        }
        
    total = len(detailed_df)
    safe_events = len(detailed_df[detailed_df["Nivel_Riesgo"] == "safe"])
    infractions = len(detailed_df[detailed_df["Nivel_Riesgo"].isin(["danger", "warning"])])
    
    compliance_pct = round((safe_events / total * 100), 1) if total > 0 else 100.0
    
    if compliance_pct >= 90.0:
        verdict = "BAJO RIESGO (Condición Segura • Planta Apta)"
        badge = "safe"
    elif compliance_pct >= 75.0:
        verdict = "RIESGO MODERADO (Bajo Observación • Reforzar Supervisión)"
        badge = "warning"
    else:
        verdict = "RIESGO CRÍTICO (Alerta Alta • Probabilidad Inminente de Incidente)"
        badge = "danger"
        
    # Infracción predominante
    infr_df = detailed_df[detailed_df["Nivel_Riesgo"].isin(["danger", "warning"])]
    if not infr_df.empty:
        top_infraction = infr_df["Categoria"].mode().iloc[0]
        # Conteo por operario
        worker_counts = infr_df["ID_Operario"].value_counts().head(3).to_dict()
        top_workers = [{"worker": k, "count": v} for k, v in worker_counts.items() if k != "N/A"]
    else:
        top_infraction = "Cero infracciones detectadas"
        top_workers = []
        
    return {
        "total_inspections": total,
        "compliance_pct": compliance_pct,
        "infractions_count": infractions,
        "safe_count": safe_events,
        "risk_verdict": verdict,
        "risk_badge": badge,
        "top_infraction": top_infraction,
        "top_workers_infractions": top_workers
    }

def image_to_base64(image_path: str) -> str:
    """Convierte una imagen de disco a formato Base64 para incrustarla en el informe HTML."""
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        return None

def generate_html_report(detailed_df: pd.DataFrame, session_name: str = "Histórico Global", auditor_name: str = "Supervisor de Seguridad y Salud en el Trabajo") -> str:
    """
    Genera un informe oficial de auditoría en formato HTML corporativo auto-contenido.
    Listo para guardar como PDF (Ctrl+P) con membrete, métricas, evidencias y casillas de firma.
    """
    kpis = compute_audit_kpis(detailed_df)
    now = datetime.datetime.now()
    report_code = f"AUD-EPP-{now.strftime('%Y%m%d')}-{now.strftime('%H%M')}"
    
    # Preparar filas de tabla
    table_rows = ""
    evidence_cards = ""
    embedded_photos = 0
    
    for _, row in detailed_df.head(50).iterrows():
        status = row.get("Nivel_Riesgo", "safe")
        if status == "safe":
            badge_class = "badge-safe"
            badge_text = "CONFORME (OK)"
        elif status == "danger":
            badge_class = "badge-danger"
            badge_text = "CRÍTICO"
        else:
            badge_class = "badge-warning"
            badge_text = "ADVERTENCIA"
            
        evidence_link = "—"
        ev_path = row.get("Ruta_Evidencia")
        if ev_path and os.path.exists(ev_path):
            evidence_link = "📸 Evidencia Adjunta"
            if embedded_photos < 6:
                b64_img = image_to_base64(ev_path)
                if b64_img:
                    evidence_cards += f"""
                    <div class="evidence-box">
                        <img src="{b64_img}" alt="Evidencia Fotográfica" class="evidence-img" />
                        <div class="evidence-caption">
                            <strong>{row.get('ID_Operario', 'N/A')}</strong> | {row.get('Categoria', '')}<br/>
                            <small>{row.get('Fecha_Hora', '')}</small>
                        </div>
                    </div>
                    """
                    embedded_photos += 1

        table_rows += f"""
        <tr>
            <td style="font-weight:700;">#{row.get('ID_Evento', '')}</td>
            <td>{row.get('Fecha_Hora', '')}</td>
            <td><strong>{row.get('ID_Operario', 'N/A')}</strong></td>
            <td>{row.get('Categoria', '')}</td>
            <td>{row.get('Detalle_Auditoria', '')}</td>
            <td><span class="badge {badge_class}">{badge_text}</span></td>
            <td>{row.get('Certeza_Pct', 0)}%</td>
            <td>{evidence_link}</td>
        </tr>
        """
        
    verdict_color = "#10b981" if kpis["risk_badge"] == "safe" else ("#ef4444" if kpis["risk_badge"] == "danger" else "#f59e0b")
    
    reincidence_html = ""
    if kpis["top_workers_infractions"]:
        items = "".join([f"<li><strong>{w['worker']}:</strong> {w['count']} infracciones registradas</li>" for w in kpis["top_workers_infractions"]])
        reincidence_html = f"<ul>{items}</ul>"
    else:
        reincidence_html = "<p style='color:#10b981; font-weight:600;'>No se detectaron reincidencias en el periodo auditado.</p>"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Informe Oficial de Auditoría EPP - {report_code}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }}
        
        body {{
            background-color: #f8fafc;
            color: #0f172a;
            padding: 30px 20px;
        }}
        
        .report-sheet {{
            background: #ffffff;
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
        }}
        
        /* Encabezado */
        .report-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        
        .header-title h1 {{
            font-size: 1.5rem;
            font-weight: 800;
            color: #1e3a8a;
            letter-spacing: -0.02em;
        }}
        
        .header-title p {{
            font-size: 0.85rem;
            color: #64748b;
            margin-top: 4px;
        }}
        
        .meta-box {{
            text-align: right;
            font-size: 0.8rem;
            color: #475569;
            line-height: 1.5;
        }}
        
        /* Dictamen Banner */
        .verdict-banner {{
            background-color: #f1f5f9;
            border-left: 6px solid {verdict_color};
            padding: 16px 20px;
            border-radius: 6px;
            margin-bottom: 25px;
        }}
        
        .verdict-banner h3 {{
            font-size: 1rem;
            font-weight: 700;
            color: {verdict_color};
            margin-bottom: 4px;
        }}
        
        .verdict-banner p {{
            font-size: 0.85rem;
            color: #334155;
        }}
        
        /* Grid de KPIs */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }}
        
        .kpi-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 14px;
            text-align: center;
        }}
        
        .kpi-card .value {{
            font-size: 1.4rem;
            font-weight: 800;
            color: #0f172a;
            margin-top: 4px;
        }}
        
        .kpi-card .label {{
            font-size: 0.72rem;
            text-transform: uppercase;
            font-weight: 700;
            color: #64748b;
            letter-spacing: 0.05em;
        }}
        
        /* Tablas */
        h2.section-title {{
            font-size: 1.05rem;
            font-weight: 800;
            color: #1e293b;
            border-bottom: 1px solid #cbd5e1;
            padding-bottom: 8px;
            margin-bottom: 14px;
            margin-top: 25px;
        }}
        
        table.report-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.82rem;
            margin-bottom: 25px;
        }}
        
        table.report-table th {{
            background-color: #f1f5f9;
            color: #334155;
            font-weight: 700;
            text-align: left;
            padding: 10px;
            border-bottom: 2px solid #cbd5e1;
        }}
        
        table.report-table td {{
            padding: 9px 10px;
            border-bottom: 1px solid #f1f5f9;
            color: #1e293b;
        }}
        
        .badge {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 700;
        }}
        
        .badge-safe {{ background: #dcfce7; color: #15803d; }}
        .badge-danger {{ background: #fee2e2; color: #b91c1c; }}
        .badge-warning {{ background: #fef3c7; color: #b45309; }}
        
        /* Galería de Evidencias */
        .evidence-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 35px;
        }}
        
        .evidence-box {{
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            overflow: hidden;
            background: #ffffff;
        }}
        
        .evidence-img {{
            width: 100%;
            height: 140px;
            object-fit: cover;
            display: block;
        }}
        
        .evidence-caption {{
            padding: 8px 10px;
            font-size: 0.72rem;
            color: #475569;
            background: #f8fafc;
            border-top: 1px solid #e2e8f0;
        }}
        
        /* Firmas de Autorización */
        .signatures {{
            display: flex;
            justify-content: space-between;
            margin-top: 50px;
            padding-top: 20px;
        }}
        
        .sig-box {{
            width: 42%;
            text-align: center;
            border-top: 1px solid #64748b;
            padding-top: 8px;
            font-size: 0.8rem;
            color: #475569;
        }}
        
        .sig-box strong {{
            display: block;
            color: #0f172a;
            font-size: 0.88rem;
            margin-bottom: 2px;
        }}

        /* Print Media Styles */
        @media print {{
            body {{
                background: #ffffff;
                padding: 0;
            }}
            .report-sheet {{
                box-shadow: none;
                border: none;
                max-width: 100%;
                padding: 10px;
            }}
            .no-print {{
                display: none;
            }}
        }}
    </style>
</head>
<body>

<div class="report-sheet">
    <div class="report-header">
        <div class="header-title">
            <h1>🛡️ VIGILANTE EPP 4.0</h1>
            <p>Informe Técnico de Auditoría Forense y Prevención de Riesgos Laborales</p>
            <p style="font-size:0.75rem; color:#94a3b8;">Cumplimiento Normativo ISO 45001 / OSHA 1910 • Visión Artificial</p>
        </div>
        <div class="meta-box">
            <div><strong>Código:</strong> {report_code}</div>
            <div><strong>Fecha de Emisión:</strong> {now.strftime('%d/%m/%Y %H:%M')}</div>
            <div><strong>Ámbito Auditado:</strong> {session_name}</div>
            <div><strong>Sistema Auditor:</strong> SafeGuard AI v4.0</div>
        </div>
    </div>
    
    <div class="verdict-banner">
        <h3>DIAGNÓSTICO PERICIAL: {kpis['risk_verdict']}</h3>
        <p>Se auditaron un total de <strong>{kpis['total_inspections']} verificaciones automatizadas</strong>. La tasa global de apego a la norma es de <strong>{kpis['compliance_pct']}%</strong> con <strong>{kpis['infractions_count']} incidentes</strong> registrados.</p>
    </div>
    
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="label">Total Auditorías</div>
            <div class="value">{kpis['total_inspections']:,}</div>
        </div>
        <div class="kpi-card">
            <div class="label">Cumplimiento</div>
            <div class="value" style="color:{verdict_color};">{kpis['compliance_pct']}%</div>
        </div>
        <div class="kpi-card">
            <div class="label">Infracciones Totales</div>
            <div class="value" style="color:#ef4444;">{kpis['infractions_count']}</div>
        </div>
        <div class="kpi-card">
            <div class="label">Falta Predominante</div>
            <div class="value" style="font-size:0.95rem; line-height:1.4; color:#d97706;">{kpis['top_infraction']}</div>
        </div>
    </div>
    
    <h2 class="section-title">1. Resumen de Reincidencias por Trabajador Rastreado</h2>
    <div style="font-size:0.85rem; margin-bottom:20px; line-height:1.6;">
        {reincidence_html}
    </div>
    
    {"<h2 class='section-title'>2. Evidencia Fotográfica Forense de Infracciones Recientes</h2><div class='evidence-grid'>" + evidence_cards + "</div>" if evidence_cards else ""}
    
    <h2 class="section-title">3. Bitácora Cronológica de Auditoría (Últimos Registros)</h2>
    <table class="report-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Fecha y Hora</th>
                <th>ID Operario</th>
                <th>Categoría</th>
                <th>Detalle del Hallazgo</th>
                <th>Estado</th>
                <th>Certeza</th>
                <th>Evidencia</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    
    <div class="signatures">
        <div class="sig-box">
            <strong>{auditor_name}</strong>
            Especialista en Seguridad y Salud en el Trabajo (SST)
        </div>
        <div class="sig-box">
            <strong>Gerencia de Operaciones / Planta</strong>
            Revisado y Aprobado para Archivo Oficial
        </div>
    </div>
</div>

</body>
</html>
"""
    return html
