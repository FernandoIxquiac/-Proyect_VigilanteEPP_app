import numpy as np
import cv2
from PIL import Image

def generate_demo_sample(sample_type: str) -> Image.Image:
    """
    Genera una imagen gráfica simulada de planta industrial para pruebas rápidas en la feria.
    """
    # Fondo con tono industrial oscuro
    img = np.zeros((450, 650, 3), dtype=np.uint8)
    img[:] = (23, 31, 49) # #171f33 Slate
    
    # Cuadrícula técnica de fondo (HUD grid)
    for y in range(0, 450, 45):
        cv2.line(img, (0, y), (650, y), (35, 45, 65), 1)
    for x in range(0, 650, 65):
        cv2.line(img, (x, 0), (x, 450), (35, 45, 65), 1)

    # Cabecera de telemetría de cámara
    cv2.rectangle(img, (20, 20), (320, 55), (11, 19, 38), -1)
    cv2.rectangle(img, (20, 20), (320, 55), (66, 71, 84), 1)
    cv2.putText(img, "CAM 01 - LINEA DE ENSAMBLAJE", (30, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (218, 226, 253), 1)

    if "Infracción" in sample_type or "Sin Casco" in sample_type:
        # Trabajador 1 (Infracción de casco)
        cv2.rectangle(img, (180, 100), (340, 380), (70, 70, 255), 2)
        cv2.rectangle(img, (180, 75), (340, 100), (70, 70, 255), -1)
        cv2.putText(img, "FALTA CASCO - NO HELMET (94%)", (185, 93), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Trabajador 2 (Cumplimiento OK)
        cv2.rectangle(img, (380, 120), (510, 370), (100, 220, 120), 2)
        cv2.rectangle(img, (380, 95), (510, 120), (100, 220, 120), -1)
        cv2.putText(img, "EPP COMPLETO (98%)", (385, 113), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 40, 0), 1)
    else:
        # Trabajador 1 y 2 con EPP Completo
        cv2.rectangle(img, (180, 100), (330, 380), (100, 220, 120), 2)
        cv2.rectangle(img, (180, 75), (330, 100), (100, 220, 120), -1)
        cv2.putText(img, "CASCO OK | CHALECO OK (99%)", (185, 93), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 40, 0), 1)

        cv2.rectangle(img, (370, 110), (510, 370), (100, 220, 120), 2)
        cv2.rectangle(img, (370, 85), (510, 110), (100, 220, 120), -1)
        cv2.putText(img, "CASCO OK | CHALECO OK (97%)", (375, 103), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 40, 0), 1)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img_rgb)

