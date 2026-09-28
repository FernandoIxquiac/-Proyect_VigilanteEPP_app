import os
import sqlite3
import datetime
import pandas as pd
import cv2

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "vigilante_epp.db")
CAPTURES_DIR = "captures"

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(CAPTURES_DIR, exist_ok=True)

def get_connection():
    """Retorna una conexión a la base de datos SQLite con claves foráneas activadas."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """
    Inicializa el esquema relacional normalizado:
    - camera_sessions: Tabla maestra de sesiones/turnos de monitoreo.
    - camera_events: Tabla transaccional vinculada con FOREIGN KEY a la sesión.
    - Índices B-Tree para optimización de consultas a escala.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Verificar si la tabla camera_events requiere migración (si falta session_id)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='camera_events'")
        events_exists = cursor.fetchone()
        
        if events_exists:
            cursor.execute("PRAGMA table_info(camera_events)")
            columns = [row[1] for row in cursor.fetchall()]
            if "session_id" not in columns:
                # Esquema anterior no normalizado: recrear con estructura óptima
                cursor.execute("DROP TABLE IF EXISTS camera_events")
                cursor.execute("DROP TABLE IF EXISTS camera_sessions")

        # 2. Tabla Maestra de Sesiones / Turnos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS camera_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                status TEXT DEFAULT 'active',   -- 'active' o 'closed'
                total_events INTEGER DEFAULT 0,
                infractions_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Tabla Transaccional de Eventos de Cámara
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS camera_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                worker_id TEXT DEFAULT 'N/A',
                timestamp DATETIME NOT NULL,
                category TEXT NOT NULL,
                details TEXT,
                status TEXT NOT NULL,          -- 'safe', 'danger', 'warning'
                personnel_count INTEGER DEFAULT 1,
                confidence REAL DEFAULT 0.0,
                evidence_path TEXT,
                FOREIGN KEY (session_id) REFERENCES camera_sessions(id) ON DELETE CASCADE
            )
        """)
        
        # Migración segura si la tabla ya existía sin worker_id
        cursor.execute("PRAGMA table_info(camera_events)")
        existing_cols = [row[1] for row in cursor.fetchall()]
        if "worker_id" not in existing_cols:
            cursor.execute("ALTER TABLE camera_events ADD COLUMN worker_id TEXT DEFAULT 'N/A'")
        
        # 4. Índices para consultas de alta velocidad
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_session ON camera_events(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_worker ON camera_events(worker_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON camera_events(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_status ON camera_events(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_category ON camera_events(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON camera_sessions(status)")
        
        # 5. Inicializar primera sesión limpia si la BD está vacía (sin datos ficticios de demostración)
        cursor.execute("SELECT COUNT(*) FROM camera_sessions")
        sess_count = cursor.fetchone()[0]
        
        if sess_count == 0:
            now = datetime.datetime.now()
            cursor.execute("""
                INSERT INTO camera_sessions (session_name, start_time, status, total_events, infractions_count)
                VALUES (?, ?, 'active', 0, 0)
            """, (f"Sesión #1 ({now.strftime('%d/%m/%Y %H:%M')})", now.strftime("%Y-%m-%d %H:%M:%S")))
            
        conn.commit()

def get_or_create_active_session() -> int:
    """Obtiene el ID de la sesión activa. Si no existe, crea una nueva automáticamente."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM camera_sessions WHERE status = 'active' ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return row[0]
            
        # Si no hay sesión activa, crear una nueva
        now = datetime.datetime.now()
        cursor.execute("SELECT COUNT(*) FROM camera_sessions")
        count = cursor.fetchone()[0] + 1
        cursor.execute("""
            INSERT INTO camera_sessions (session_name, start_time, status)
            VALUES (?, ?, 'active')
        """, (f"Sesión #{count} ({now.strftime('%d/%m/%Y %H:%M')})", now.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return cursor.lastrowid

def create_new_session(session_name: str = None) -> int:
    """
    Cierra la sesión activa actual y crea una nueva sesión limpia.
    NO borra el historial anterior: preserva todos los datos para trazabilidad.
    """
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Cerrar sesión activa previa actualizando totales
        cursor.execute("SELECT id FROM camera_sessions WHERE status = 'active'")
        active_rows = cursor.fetchall()
        for a_row in active_rows:
            sid = a_row[0]
            cursor.execute("SELECT COUNT(*) FROM camera_events WHERE session_id = ?", (sid,))
            t_events = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM camera_events WHERE session_id = ? AND status IN ('danger', 'warning')", (sid,))
            t_infr = cursor.fetchone()[0]
            
            cursor.execute("""
                UPDATE camera_sessions 
                SET end_time = ?, status = 'closed', total_events = ?, infractions_count = ?
                WHERE id = ?
            """, (now_str, t_events, t_infr, sid))
            
        # 2. Crear nueva sesión
        cursor.execute("SELECT COUNT(*) FROM camera_sessions")
        total_sessions = cursor.fetchone()[0] + 1
        name = session_name or f"Sesión #{total_sessions} ({now.strftime('%d/%m/%Y %H:%M')})"
        
        cursor.execute("""
            INSERT INTO camera_sessions (session_name, start_time, status, total_events, infractions_count)
            VALUES (?, ?, 'active', 0, 0)
        """, (name, now_str))
        conn.commit()
        return cursor.lastrowid

def update_session_counters(session_id: int):
    """Actualiza los contadores de una sesión en base a sus eventos reales."""
    if not session_id:
        return
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM camera_events WHERE session_id = ?", (session_id,))
        t_events = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM camera_events WHERE session_id = ? AND status IN ('danger', 'warning')", (session_id,))
        t_infr = cursor.fetchone()[0]
        
        cursor.execute("""
            UPDATE camera_sessions
            SET total_events = ?, infractions_count = ?
            WHERE id = ?
        """, (t_events, t_infr, session_id))
        conn.commit()

def start_camera_session() -> int:
    """Obtiene o asegura la sesión activa para la transmisión de la cámara."""
    return get_or_create_active_session()

def end_camera_session(session_id: int = None, total_events: int = 0, infractions_count: int = 0):
    """Actualiza los contadores de la sesión al detener la transmisión."""
    if session_id:
        update_session_counters(session_id)

def log_camera_event(category: str, details: str, status: str, personnel_count: int = 1, confidence: float = 0.0, frame_bgr=None, session_id: int = None, worker_id: str = "N/A") -> int:
    """
    Inserta un evento en la tabla normalizada vinculado a la sesión activa y al operario.
    Guarda evidencia JPG si es una infracción.
    """
    if session_id is None:
        session_id = get_or_create_active_session()
        
    evidence_path = None
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    if frame_bgr is not None and status in ["danger", "warning"]:
        try:
            clean_wid = str(worker_id).replace('#', '').replace('-', '_').replace(' ', '')
            filename = f"infraccion_s{session_id}_{clean_wid}_{now.strftime('%Y%m%d_%H%M%S_%f')[:22]}.jpg"
            full_path = os.path.join(CAPTURES_DIR, filename)
            h, w = frame_bgr.shape[:2]
            if w > 1280:
                scale = 1280 / w
                frame_save = cv2.resize(frame_bgr, (1280, int(h * scale)))
            else:
                frame_save = frame_bgr
            cv2.imwrite(full_path, frame_save, [cv2.IMWRITE_JPEG_QUALITY, 80])
            evidence_path = full_path
        except Exception as e:
            print(f"[AVISO] No se pudo guardar la evidencia fotográfica: {e}")
            evidence_path = None

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO camera_events (session_id, worker_id, timestamp, category, details, status, personnel_count, confidence, evidence_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (session_id, worker_id, now_str, category, details, status, personnel_count, confidence, evidence_path))
        event_id = cursor.lastrowid
        conn.commit()
        
    update_session_counters(session_id)
    return event_id

def get_compliance_stats(session_id: int = None):
    """
    Calcula estadísticas. Si session_id es especificado, filtra por esa sesión.
    Si session_id es None, calcula el consolidado global histórico.
    Retorna (total_auditorias, cumplimiento_pct, tasa_redondeada, total_infracciones)
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        if session_id is not None:
            cursor.execute("SELECT COUNT(*) FROM camera_events WHERE session_id = ?", (session_id,))
            total_events = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM camera_events WHERE session_id = ? AND status = 'safe'", (session_id,))
            ok_events = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM camera_events WHERE session_id = ? AND status IN ('danger', 'warning')", (session_id,))
            infractions = cursor.fetchone()[0]
        else:
            cursor.execute("SELECT COUNT(*) FROM camera_events")
            total_events = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM camera_events WHERE status = 'safe'")
            ok_events = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM camera_events WHERE status IN ('danger', 'warning')")
            infractions = cursor.fetchone()[0]
            
    if total_events > 0:
        compliance_rate = round((ok_events / total_events * 100), 1)
        compliance_pct = int(compliance_rate)
    else:
        compliance_rate = 100.0
        compliance_pct = 100
        
    return total_events, compliance_pct, compliance_rate, infractions

def get_recent_incidents(session_id: int = None, limit: int = 5):
    """Obtiene los incidentes más recientes para el HUD."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if session_id is not None:
            cursor.execute("""
                SELECT timestamp, details, status, category, evidence_path
                FROM camera_events
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (session_id, limit))
        else:
            cursor.execute("""
                SELECT timestamp, details, status, category, evidence_path
                FROM camera_events
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
        rows = cursor.fetchall()
        
    incidents = []
    for r in rows:
        try:
            dt = datetime.datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S")
            time_formatted = dt.strftime("%I:%M %p")
        except Exception:
            time_formatted = r["timestamp"]
            
        incidents.append({
            "time": time_formatted,
            "title": r["details"] or r["category"],
            "badge": r["status"],
            "category": r["category"],
            "evidence": r["evidence_path"]
        })
    return incidents

def get_history_dataframe(session_id: int = None) -> pd.DataFrame:
    """Devuelve las categorías agregadas para gráficas de barras."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if session_id is not None:
            cursor.execute("""
                SELECT category AS "Categoría", COUNT(*) AS "Cantidad de Eventos"
                FROM camera_events
                WHERE session_id = ?
                GROUP BY category
                ORDER BY "Cantidad de Eventos" DESC
            """, (session_id,))
        else:
            cursor.execute("""
                SELECT category AS "Categoría", COUNT(*) AS "Cantidad de Eventos"
                FROM camera_events
                GROUP BY category
                ORDER BY "Cantidad de Eventos" DESC
            """)
        rows = cursor.fetchall()
        
    if rows:
        data = [{"Categoría": r["Categoría"], "Cantidad de Eventos": r["Cantidad de Eventos"]} for r in rows]
        return pd.DataFrame(data)
    else:
        return pd.DataFrame([
            {"Categoría": "Cumplimiento Total (OK)", "Cantidad de Eventos": 0},
            {"Categoría": "Sin Casco", "Cantidad de Eventos": 0},
            {"Categoría": "Sin Chaleco", "Cantidad de Eventos": 0}
        ])

def get_detailed_events_dataframe(session_id: int = None) -> pd.DataFrame:
    """Devuelve la bitácora forense enriquecida con el nombre de la sesión."""
    with get_connection() as conn:
        sql = """
            SELECT 
                e.id AS "ID_Evento",
                s.session_name AS "Sesion",
                e.worker_id AS "ID_Operario",
                e.timestamp AS "Fecha_Hora",
                e.category AS "Categoria",
                e.details AS "Detalle_Auditoria",
                e.status AS "Nivel_Riesgo",
                e.personnel_count AS "Personas_Detectadas",
                e.confidence AS "Certeza_Pct",
                e.evidence_path AS "Ruta_Evidencia"
            FROM camera_events e
            JOIN camera_sessions s ON e.session_id = s.id
        """
        if session_id is not None:
            sql += " WHERE e.session_id = ? ORDER BY e.id DESC"
            df = pd.read_sql_query(sql, conn, params=(session_id,))
        else:
            sql += " ORDER BY e.id DESC"
            df = pd.read_sql_query(sql, conn)
    return df

def get_all_sessions_list() -> list:
    """Obtiene la lista de todas las sesiones registradas para selectores en UI."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, session_name, status, total_events, infractions_count, start_time
            FROM camera_sessions
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
    return [dict(r) for r in rows]

def get_hourly_risk_distribution(session_id: int = None) -> pd.DataFrame:
    """Calcula la distribución horaria de infracciones reales."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if session_id is not None:
            cursor.execute("""
                SELECT strftime('%H:00', timestamp) AS hora, COUNT(*) AS count
                FROM camera_events
                WHERE session_id = ? AND status IN ('danger', 'warning')
                GROUP BY hora
                ORDER BY hora ASC
            """, (session_id,))
        else:
            cursor.execute("""
                SELECT strftime('%H:00', timestamp) AS hora, COUNT(*) AS count
                FROM camera_events
                WHERE status IN ('danger', 'warning')
                GROUP BY hora
                ORDER BY hora ASC
            """)
        rows = cursor.fetchall()

    if rows:
        data = [{"Turno": r["hora"], "Infracciones": r["count"]} for r in rows]
        return pd.DataFrame(data)
    else:
        return pd.DataFrame({
            "Turno": ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00"],
            "Infracciones": [0, 0, 0, 0, 0, 0]
        })

def clear_all_data():
    """
    Elimina todos los datos de eventos y sesiones para dejar la base de datos completamente limpia.
    Crea una sesión inicial limpia con 0 eventos e infracciones.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM camera_events")
        cursor.execute("DELETE FROM camera_sessions")
        try:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('camera_events', 'camera_sessions')")
        except Exception:
            pass
        now = datetime.datetime.now()
        cursor.execute("""
            INSERT INTO camera_sessions (session_name, start_time, status, total_events, infractions_count)
            VALUES (?, ?, 'active', 0, 0)
        """, (f"Sesión #1 ({now.strftime('%d/%m/%Y %H:%M')})", now.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
