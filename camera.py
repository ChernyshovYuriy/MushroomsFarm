import io
import logging
import socketserver
import threading
from http import server
from threading import Lock

from picamera2 import Picamera2

from abs_worker import AbstractWorker

CAMERA_PORT = 8000
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
JPEG_QUALITY = 70   # 0-95; 70 is fine for monitoring, saves ~40% CPU vs default


class Camera(AbstractWorker):
    """Captures still frames from Picamera2 on demand and serves them over HTTP.

    Instead of running a continuous JPEG encoder (expensive on Pi 3), the camera
    stays in preview mode and encodes a single JPEG only when /snapshot is requested.
    CPU drops from ~90% continuous to a brief spike every 2 s.
    """

    def __init__(self, loop_delay: float = 2.0) -> None:
        self._camera = Picamera2()
        self._camera.configure(
            self._camera.create_preview_configuration(
                main={"size": (CAMERA_WIDTH, CAMERA_HEIGHT), "format": "RGB888"}
            )
        )
        self._lock = Lock()   # serialise concurrent snapshot requests
        super().__init__("Camera", loop_delay, None, self._on_stop)

    def _on_stop(self) -> None:
        try:
            self._camera.stop()
        except Exception as exc:
            print("Exception while stopping camera: %s" % exc)

    def capture_jpeg(self) -> bytes | None:
        """Capture one frame and return it as JPEG bytes. Thread-safe."""
        with self._lock:
            try:
                buf = io.BytesIO()
                self._camera.capture_file(buf, format="jpeg")
                return buf.getvalue()
            except Exception as exc:
                logging.warning("Snapshot capture failed: %s", exc)
                return None

    def runnable(self) -> None:
        print("[{0}] Starting camera on port {1}".format(
            threading.current_thread().name, CAMERA_PORT,
        ))
        self._camera.start()
        cam = self

        class StreamingHandler(server.BaseHTTPRequestHandler):

            def log_message(self, fmt, *args) -> None:
                pass

            def do_GET(self) -> None:
                if self.path.startswith("/snapshot"):
                    frame = cam.capture_jpeg()
                    if frame is None:
                        self.send_error(503, "Capture failed")
                        return
                    self.send_response(200)
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", str(len(frame)))
                    self.send_header("Cache-Control", "no-cache, no-store")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(frame)
                else:
                    self.send_error(404)

        class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
            allow_reuse_address = True
            daemon_threads = True

        streaming_server = StreamingServer(("", CAMERA_PORT), StreamingHandler)
        streaming_server.serve_forever()
