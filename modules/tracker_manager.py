import time

class WorkerTrackManager:
    """
    Gestiona el ciclo de vida, persistencia y deduplicación de auditorías por cada operario rastreado (MOT).
    Evita saturar la base de datos aplicando deduplicación individual por ID y control de anti-parpadeo.
    """
    def __init__(self, infraction_cooldown: float = 60.0, compliance_cooldown: float = 120.0, purge_timeout: float = 12.0):
        self.infraction_cooldown = infraction_cooldown
        self.compliance_cooldown = compliance_cooldown
        self.purge_timeout = purge_timeout
        self.tracked_workers = {}  # {worker_id_str: dict}
        
    def reset(self):
        """Reinicia la memoria de seguimiento (al apagar cámara o iniciar nuevo turno)."""
        self.tracked_workers.clear()

    def evaluate_worker_event(self, worker_dict: dict) -> dict:
        """
        Evalúa si un operario detectado califica para generar un nuevo evento en SQLite.
        Aplica filtro de 2 fotogramas consecutivos para evitar falsas alarmas por parpadeos.
        Retorna:
            dict con:
            - should_record (bool): Si debe guardarse en SQLite.
            - reason (str): Causa ('new_infraction', 'repeat_infraction_cooldown', 'first_compliance', 'remedied', 'suppressed').
            - category (str): Categoría normalizada.
            - title (str): Título detallado con ID de operario.
            - status (str): 'safe', 'danger', 'warning'.
            - worker_id (str): Identificador único del operario (ej. #Operario-01).
        """
        now = time.time()
        w_id = worker_dict["ID"]
        is_compliant = worker_dict["is_compliant"]
        badge = worker_dict["badge"]
        veredicto = worker_dict["Veredicto"]
        
        # Determinar categoría y título descriptivo con ID
        if not is_compliant:
            if "CASCO" in veredicto and "CHALECO" in veredicto:
                category = "Sin EPP"
                title = f"{w_id}: Sin Casco ni Chaleco reglamentario"
            elif "CASCO" in veredicto:
                category = "Sin Casco"
                title = f"{w_id}: Falta de Casco de Seguridad"
            elif "CHALECO" in veredicto:
                category = "Sin Chaleco"
                title = f"{w_id}: Falta de Chaleco Reflectante"
            else:
                category = "Sin EPP"
                title = f"{w_id}: En Infracción de Seguridad"
            status = badge  # 'danger' o 'warning'
        else:
            category = "Cumplimiento Total (OK)"
            title = f"{w_id}: EPP Completo Verificado"
            status = "safe"

        # 1. Operario nuevo en escena
        if w_id not in self.tracked_workers:
            self.tracked_workers[w_id] = {
                "first_seen": now,
                "last_seen": now,
                "current_status": status,
                "consecutive_infraction_frames": 1 if not is_compliant else 0,
                "last_alert_time": now if not is_compliant else 0,
                "has_alerted_infraction": False,
                "has_alerted_compliance": False
            }
            
            # Para infracciones, requerir confirmación en segundo frame para evitar falsos positivos
            if not is_compliant:
                return {
                    "should_record": False,
                    "reason": "confirming",
                    "category": category,
                    "title": title,
                    "status": status,
                    "worker_id": w_id
                }
            else:
                # Si entra con EPP completo, registrar el acceso seguro
                self.tracked_workers[w_id]["has_alerted_compliance"] = True
                self.tracked_workers[w_id]["last_alert_time"] = now
                return {
                    "should_record": True,
                    "reason": "first_compliance",
                    "category": category,
                    "title": title,
                    "status": status,
                    "worker_id": w_id
                }

        # 2. Operario ya registrado en memoria
        tracker = self.tracked_workers[w_id]
        tracker["last_seen"] = now
        
        # Caso A: Está en infracción
        if not is_compliant:
            tracker["consecutive_infraction_frames"] += 1
            
            # A.1: Primera alerta confirmada (al menos 2 frames)
            if not tracker["has_alerted_infraction"] and tracker["consecutive_infraction_frames"] >= 2:
                tracker["has_alerted_infraction"] = True
                tracker["last_alert_time"] = now
                tracker["current_status"] = status
                return {
                    "should_record": True,
                    "reason": "new_infraction",
                    "category": category,
                    "title": title,
                    "status": status,
                    "worker_id": w_id
                }
                
            # A.2: Ya fue alertado. Solo re-alertar si transcurrió el tiempo de cooldown individual
            elif tracker["has_alerted_infraction"] and (now - tracker["last_alert_time"] >= self.infraction_cooldown):
                tracker["last_alert_time"] = now
                return {
                    "should_record": True,
                    "reason": "repeat_infraction_cooldown",
                    "category": category,
                    "title": f"{w_id}: Reincidencia en falta de EPP",
                    "status": status,
                    "worker_id": w_id
                }
                
            # A.3: Sigue en la misma infracción dentro del periodo de gracia -> SUPRIMIR (0 duplicados)
            return {
                "should_record": False,
                "reason": "suppressed",
                "category": category,
                "title": title,
                "status": status,
                "worker_id": w_id
            }

        # Caso B: Cumple con el EPP
        else:
            # B.1: Si antes estaba en infracción y ahora cumple (se colocó el casco/chaleco)
            if tracker["current_status"] in ["danger", "warning"]:
                tracker["current_status"] = "safe"
                tracker["has_alerted_infraction"] = False  # Resetear por si reincide después
                tracker["last_alert_time"] = now
                return {
                    "should_record": True,
                    "reason": "remedied",
                    "category": category,
                    "title": f"{w_id}: Subsanó Infracción (EPP Reglamentario Colocado)",
                    "status": "safe",
                    "worker_id": w_id
                }
                
            tracker["current_status"] = "safe"
            tracker["consecutive_infraction_frames"] = 0
            return {
                "should_record": False,
                "reason": "compliant_suppressed",
                "category": category,
                "title": title,
                "status": status,
                "worker_id": w_id
            }

    def purge_inactive_tracks(self):
        """Elimina de la memoria los operarios que han salido de la escena tras el tiempo de timeout."""
        now = time.time()
        to_delete = [w_id for w_id, data in self.tracked_workers.items() if (now - data["last_seen"] > self.purge_timeout)]
        for w_id in to_delete:
            del self.tracked_workers[w_id]
