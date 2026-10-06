import cv2
import threading
import time
import streamlit as st

class ThreadedCamera:
    """
    Gestor de captura de video desacoplado en segundo plano (Threaded Stream).
    Mantiene la cámara abierta de forma continua en un hilo demonio independiente,
    aislando el hardware de las re-ejecuciones de interfaz de Streamlit.
    """
    def __init__(self, source=0, width=1280, height=720):
        self.source = source
        self.width = width
        self.height = height
        self.cap = None
        self.frame = None
        self.ret = False
        self.is_running = False
        self.lock = threading.Lock()
        self.thread = None
        self.consecutive_drops = 0

    def start(self):
        """
        Inicializa el hardware de captura y arranca el hilo de lectura continua.
        Retorna True si la conexión fue exitosa.
        """
        if self.is_running and self.cap is not None and self.cap.isOpened():
            return True

        self.is_running = True

        # 1. Apertura segura con backend DirectShow en Windows para USB / integrada
        try:
            if isinstance(self.source, int):
                self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
                if not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.source)
            else:
                # Flujo RTSP / IP / Archivo
                self.cap = cv2.VideoCapture(self.source)
        except Exception:
            self.is_running = False
            return False

        if not self.cap or not self.cap.isOpened():
            self.is_running = False
            return False

        # 2. Configuración de resolución blindada contra C++ SEH exceptions
        try:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Buffer mínimo = Cero latencia
        except Exception:
            pass

        # 3. Lanzar hilo de lectura en segundo plano
        self.thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.thread.start()

        # 4. Esperar de forma no bloqueante a recibir el primer cuadro válido
        t0 = time.time()
        while time.time() - t0 < 1.2:
            if self.frame is not None and self.ret:
                break
            time.sleep(0.04)

        return True

    def _reader_loop(self):
        """
        Ciclo de lectura continuo ejecutado en el hilo secundario.
        Descarta frames acumulados y siempre mantiene el cuadro más fresco.
        """
        while self.is_running and self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    with self.lock:
                        self.frame = frame
                        self.ret = True
                    self.consecutive_drops = 0
                else:
                    self.consecutive_drops += 1
                    # Tolerancia a caídas: solo se declara fallo si supera ~1.5 seg continuos sin señal
                    if self.consecutive_drops > 45:
                        with self.lock:
                            self.ret = False
                        break
            except Exception:
                break
            time.sleep(0.01)

    def read(self):
        """
        Retorna (ret, frame) con el fotograma más reciente disponible.
        Operación thread-safe y de tiempo constante O(1).
        """
        with self.lock:
            if self.frame is not None and self.ret:
                return True, self.frame.copy()
            return False, None

    def stop(self):
        """
        Detiene el hilo de lectura y libera el recurso de video de forma limpia.
        """
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None
        self.frame = None
        self.ret = False
        self.consecutive_drops = 0


class CameraStreamManager:
    """
    Controlador centralizado del ciclo de vida de los flujos de video.
    Garantiza que solo exista una cámara activa a la vez y previene
    re-aperturas innecesarias al interactuar con controles de la UI.
    """
    def __init__(self):
        self.current_stream = None
        self.current_source = None
        self._lock = threading.Lock()

    def get_stream(self, source, width=1280, height=720):
        with self._lock:
            if self.current_stream is not None:
                if self.current_source == source and self.current_stream.is_running:
                    return self.current_stream
                # Si cambió la fuente de video o la actual no está corriendo, detenerla
                self.current_stream.stop()
                self.current_stream = None

            self.current_source = source
            self.current_stream = ThreadedCamera(source=source, width=width, height=height)
            return self.current_stream

    def stop_all(self):
        with self._lock:
            if self.current_stream is not None:
                self.current_stream.stop()
                self.current_stream = None
                self.current_source = None


@st.cache_resource
def get_camera_manager():
    """
    Retorna el gestor de cámara singleton persistido en la caché de recursos de Streamlit.
    Sobrevive de forma transparente a cualquier cambio de widgets o re-runs del script.
    """
    return CameraStreamManager()
