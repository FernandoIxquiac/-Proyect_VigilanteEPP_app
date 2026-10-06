import os
import cv2
import numpy as np
import streamlit as st  # Necesario para @st.cache_resource en load_detector_model

# Mapeo de clases del modelo de seguridad a español
CLASS_TRANSLATIONS = {
    "Hardhat": "Casco de Seguridad",
    "NO-Hardhat": "Sin Casco",
    "Safety Vest": "Chaleco Reflectante",
    "NO-Safety Vest": "Sin Chaleco",
    "Mask": "Mascarilla",
    "NO-Mask": "Sin Mascarilla",
    "Person": "Persona",
    "person": "Persona",
    "Safety Cone": "Cono de Seguridad",
    "machinery": "Maquinaria",
    "vehicle": "Vehículo"
}

VIOLATION_CLASSES = {"NO-Hardhat", "NO-Safety Vest", "Sin Casco", "Sin Chaleco"}
COMPLIANT_CLASSES = {"Hardhat", "Safety Vest", "Casco de Seguridad", "Chaleco Reflectante"}

@st.cache_resource
def load_detector_model():
    """
    Carga el modelo de detección YOLO.
    Prioriza el modelo entrenado en models/ppe_model.pt. Si no existe, usa yolov8n.pt.
    """
    try:
        from ultralytics import YOLO
        custom_model_path = os.path.join("models", "ppe_model.pt")
        if os.path.exists(custom_model_path):
            return YOLO(custom_model_path), "Modelo Especializado EPP (Local 100% Offline)"
        else:
            return YOLO("yolov8n.pt"), "YOLOv8 Base (Detección General / Demo)"
    except Exception as e:
        return None, f"Modo Simulación Visual (Error: {e})"

def detect_objects(image_bgr, model, conf_threshold=0.45, filter_masks=True, check_helmet=True, check_vest=True, use_tracking=False):
    """
    Ejecuta la inferencia de YOLO sobre una imagen en formato BGR (OpenCV).
    Soporta Multi-Object Tracking (ByteTrack) cuando use_tracking=True para asignar IDs persistentes.
    Retorna:
        annotated_image_rgb (np.ndarray): Imagen con cajas delimitadoras en RGB.
        persons_count (int): Cantidad de personas detectadas.
        detections_list (list): Lista de detecciones con clase, confianza, etiquetas y track_id.
    """
    if model is None:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        return image_rgb, 1, [{
            "label": "Person",
            "label_es": "Persona",
            "confidence": 98.5,
            "cls_id": 0,
            "track_id": 1,
            "is_violation": False,
            "is_compliant": False
        }]

    # Filtrar clases según los parámetros activos en la barra lateral
    target_classes = None
    if hasattr(model, "names") and isinstance(model.names, dict):
        excluded = []
        if filter_masks:
            excluded.extend(["Mask", "NO-Mask"])
        if not check_helmet:
            excluded.extend(["Hardhat", "NO-Hardhat"])
        if not check_vest:
            excluded.extend(["Safety Vest", "NO-Safety Vest"])

        target_classes = [k for k, v in model.names.items() if v not in excluded]

    # Ejecutar inferencia: Tracking persistente en video o detección estándar en fotos
    if use_tracking and hasattr(model, "track"):
        try:
            if target_classes is not None:
                results = model.track(image_bgr, persist=True, conf=conf_threshold, classes=target_classes, tracker="bytetrack.yaml", verbose=False)
            else:
                results = model.track(image_bgr, persist=True, conf=conf_threshold, tracker="bytetrack.yaml", verbose=False)
        except Exception:
            # Fallback en caso de incompatibilidad con el tracker
            if target_classes is not None:
                results = model(image_bgr, conf=conf_threshold, classes=target_classes, verbose=False)
            else:
                results = model(image_bgr, conf=conf_threshold, verbose=False)
    else:
        if target_classes is not None:
            results = model(image_bgr, conf=conf_threshold, classes=target_classes, verbose=False)
        else:
            results = model(image_bgr, conf=conf_threshold, verbose=False)

    annotated_bgr = results[0].plot()
    annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
    
    detections_list = []
    persons_count = 0
    if results[0].boxes:
        classes = results[0].boxes.cls.tolist()
        confs = results[0].boxes.conf.tolist()
        xyxy = results[0].boxes.xyxy.tolist()
        names = results[0].names
        
        track_ids = [None] * len(classes)
        if hasattr(results[0].boxes, "id") and results[0].boxes.id is not None:
            try:
                track_ids = results[0].boxes.id.int().tolist()
            except Exception:
                pass

        for cls_id, conf, box, t_id in zip(classes, confs, xyxy, track_ids):
            raw_name = names.get(int(cls_id), f"Clase {int(cls_id)}")
            cls_es = CLASS_TRANSLATIONS.get(raw_name, raw_name)

            if raw_name.lower() in ["person", "persona"]:
                persons_count += 1

            is_violation = (raw_name in VIOLATION_CLASSES or cls_es in VIOLATION_CLASSES)
            is_compliant = (raw_name in COMPLIANT_CLASSES or cls_es in COMPLIANT_CLASSES)

            detections_list.append({
                "label": raw_name,
                "label_es": cls_es,
                "confidence": round(conf * 100, 1),
                "cls_id": int(cls_id),
                "box": [round(float(c), 1) for c in box],
                "track_id": t_id,
                "is_violation": is_violation,
                "is_compliant": is_compliant
            })

    # Si no detectó la persona entera pero sí detectó equipo o infracciones (cabeza, torso)
    if persons_count == 0 and len(detections_list) > 0:
        relevant = [d for d in detections_list if d["is_violation"] or d["is_compliant"]]
        if relevant:
            persons_count = max(1, len(relevant) // 2 or 1)

    return annotated_rgb, persons_count, detections_list

def analyze_workers_spatial(detections_list, check_helmet=True, check_vest=True):
    """
    Agrupa las detecciones por trabajador según solapamiento espacial.
    Evalúa si cada persona cumple simultáneamente con Casco y Chaleco.
    Retorna:
        workers_list (list): Lista de diccionarios con el estado integral por persona.
        summary_kpis (dict): Totales de cumplimiento, infracciones y porcentaje.
    """
    if not detections_list:
        return [], {"total": 0, "compliant": 0, "infractions": 0, "rate": 100.0}

    persons = [d for d in detections_list if d["label"].lower() in ["person", "persona"] and "box" in d]
    gear = [d for d in detections_list if d["label"].lower() not in ["person", "persona", "safety cone", "machinery", "vehicle"] and "box" in d]

    workers = []

    if persons:
        # Ordenar de izquierda a derecha por coordenada x1
        persons.sort(key=lambda p: p["box"][0])
        unassigned_gear = list(gear)

        for idx, p in enumerate(persons, 1):
            px1, py1, px2, py2 = p["box"]
            pw = max(1.0, px2 - px1)
            ph = max(1.0, py2 - py1)

            p_helmets = []
            p_vests = []
            p_no_helmets = []
            p_no_vests = []

            remaining = []
            for g in unassigned_gear:
                gx1, gy1, gx2, gy2 = g["box"]
                gcx = (gx1 + gx2) / 2.0
                gcy = (gy1 + gy2) / 2.0

                if (px1 - 0.15 * pw <= gcx <= px2 + 0.15 * pw) and (py1 - 0.10 * ph <= gcy <= py2 + 0.10 * ph):
                    glbl = g["label"]
                    if glbl == "Hardhat":
                        p_helmets.append(g)
                    elif glbl == "NO-Hardhat":
                        p_no_helmets.append(g)
                    elif glbl == "Safety Vest":
                        p_vests.append(g)
                    elif glbl == "NO-Safety Vest":
                        p_no_vests.append(g)
                else:
                    remaining.append(g)
            unassigned_gear = remaining

            # Evaluación de Casco
            if not check_helmet:
                helmet_str = "N/R - No Requerido"
                helmet_ok = True
            elif p_helmets:
                best = max(p_helmets, key=lambda x: x["confidence"])
                helmet_str = f"SI ({best['confidence']}%)"
                helmet_ok = True
            elif p_no_helmets:
                best = max(p_no_helmets, key=lambda x: x["confidence"])
                helmet_str = f"NO - Sin Casco ({best['confidence']}%)"
                helmet_ok = False
            else:
                helmet_str = "NO - No Detectado"
                helmet_ok = False

            # Evaluación de Chaleco
            if not check_vest:
                vest_str = "N/R - No Requerido"
                vest_ok = True
            elif p_vests:
                best = max(p_vests, key=lambda x: x["confidence"])
                vest_str = f"SI ({best['confidence']}%)"
                vest_ok = True
            elif p_no_vests:
                best = max(p_no_vests, key=lambda x: x["confidence"])
                vest_str = f"NO - Sin Chaleco ({best['confidence']}%)"
                vest_ok = False
            else:
                vest_str = "NO - No Detectado"
                vest_ok = False

            # Veredicto Integral por Sujeto
            is_compliant = True
            infractions = []
            if check_helmet and not helmet_ok:
                is_compliant = False
                infractions.append("Falta Casco")
            if check_vest and not vest_ok:
                is_compliant = False
                infractions.append("Falta Chaleco")

            if is_compliant:
                if check_helmet and check_vest:
                    veredicto = "CUMPLE (EPP Completo)"
                elif check_helmet:
                    veredicto = "CUMPLE (Casco OK)"
                elif check_vest:
                    veredicto = "CUMPLE (Chaleco OK)"
                else:
                    veredicto = "AREA SIN REQUERIMIENTO"
                accion = "Pase Aprobado"
                badge = "safe"
            elif len(infractions) >= 2:
                veredicto = "INFRACCION: SIN EPP REGLAMENTARIO"
                accion = "Detener: Exigir Casco y Chaleco"
                badge = "danger"
            elif "Falta Casco" in infractions:
                veredicto = "INFRACCION: FALTA CASCO"
                accion = "Detener: Colocar Casco"
                badge = "danger"
            else:
                veredicto = "ADVERTENCIA: FALTA CHALECO"
                accion = "Detener: Colocar Chaleco"
                badge = "warning"

            t_id = p.get("track_id")
            w_label = f"#Operario-{t_id:02d}" if t_id is not None else f"#Operario-{idx:02d}"
            workers.append({
                "ID": w_label,
                "track_id": t_id,
                "Casco": helmet_str,
                "Chaleco": vest_str,
                "Veredicto": veredicto,
                "Acción Sugerida": accion,
                "is_compliant": is_compliant,
                "badge": badge,
                "box": [px1, py1, px2, py2]
            })
    else:
        # Modo fallback si no hubo recuadros de personas pero sí de EPP
        for idx, g in enumerate(gear, 1):
            is_viol = g["is_violation"]
            is_comp = g["is_compliant"]
            lbl = g["label"]
            conf = g["confidence"]

            h_str = f"SI ({conf}%)" if lbl == "Hardhat" else (f"NO - Sin Casco ({conf}%)" if lbl == "NO-Hardhat" else "—")
            v_str = f"SI ({conf}%)" if lbl == "Safety Vest" else (f"NO - Sin Chaleco ({conf}%)" if lbl == "NO-Safety Vest" else "—")

            veredicto = "INFRACCION" if is_viol else ("CUMPLE" if is_comp else "OBSERVACION")
            accion = "Notificar Supervisor" if is_viol else "Pase Aprobado"
            badge = "danger" if is_viol else ("safe" if is_comp else "info")

            workers.append({
                "ID": f"#Sujeto-{idx:02d}",
                "Casco": h_str,
                "Chaleco": v_str,
                "Veredicto": veredicto,
                "Acción Sugerida": accion,
                "is_compliant": not is_viol,
                "badge": badge
            })

    total_w = len(workers)
    comp_w = sum(1 for w in workers if w["is_compliant"])
    infr_w = total_w - comp_w
    rate = round((comp_w / total_w * 100), 1) if total_w > 0 else 100.0

    summary_kpis = {
        "total": total_w,
        "compliant": comp_w,
        "infractions": infr_w,
        "rate": rate
    }

    return workers, summary_kpis

def evaluate_compliance(detections_list, check_helmet=True, check_vest=True):
    """
    Evalúa la lista de detecciones según los parámetros de seguridad activos.
    Retorna un diccionario con estado ('safe', 'danger', 'warning', 'standby'),
    título, mensaje explicativo y la categoría recomendada para registrar en la auditoría.
    """
    if not detections_list:
        return {
            "status": "standby",
            "title": "ZONA DESPEJADA",
            "message": "No se detecta personal en el encuadre.",
            "category": None,
            "has_violation": False
        }

    # Usar análisis por trabajador si hay personas detectadas
    workers, summary = analyze_workers_spatial(detections_list, check_helmet=check_helmet, check_vest=check_vest)

    if workers:
        if summary["infractions"] > 0:
            sin_casco = any("FALTA CASCO" in w["Veredicto"] or "SIN EPP" in w["Veredicto"] for w in workers)
            if sin_casco:
                return {
                    "status": "danger",
                    "title": "INFRACCION: FALTA DE CASCO",
                    "message": f"{summary['infractions']} de {summary['total']} operarios detectados sin casco obligatorio.",
                    "category": "Sin Casco",
                    "has_violation": True
                }
            else:
                return {
                    "status": "warning",
                    "title": "ADVERTENCIA: FALTA DE CHALECO",
                    "message": f"{summary['infractions']} de {summary['total']} operarios detectados sin chaleco reflectante.",
                    "category": "Sin Chaleco",
                    "has_violation": True
                }
        else:
            return {
                "status": "safe",
                "title": "CONDICION SEGURA (100% CUMPLIMIENTO)",
                "message": f"Todos los operarios ({summary['total']}) portan Casco y Chaleco reglamentario.",
                "category": "Cumplimiento Total (OK)",
                "has_violation": False
            }

    # Fallback si no hay cajas de personas:
    has_no_helmet = any(d["label"] in ["NO-Hardhat", "Sin Casco"] for d in detections_list)
    has_no_vest = any(d["label"] in ["NO-Safety Vest", "Sin Chaleco"] for d in detections_list)

    if check_helmet and has_no_helmet:
        return {
            "status": "danger",
            "title": "INFRACCION CRITICA",
            "message": "Personal detectado SIN CASCO de seguridad reglamentario.",
            "category": "Sin Casco",
            "has_violation": True
        }
    if check_vest and has_no_vest:
        return {
            "status": "warning",
            "title": "ADVERTENCIA: INFRACCION DETECTADA",
            "message": "Personal detectado SIN CHALECO reflectante reglamentario.",
            "category": "Sin Chaleco",
            "has_violation": True
        }

    return {
        "status": "safe",
        "title": "CONDICION SEGURA",
        "message": "Supervision activa: EPP reglamentario verificado.",
        "category": "Cumplimiento Total (OK)",
        "has_violation": False
    }

