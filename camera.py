import io
import logging
import socketserver
import threading
from http import server
from threading import Condition

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder, Quality
from picamera2.outputs import FileOutput

from abs_worker import AbstractWorker

CAMERA_PORT = 8000
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480


class _StreamingOutput(io.BufferedIOBase):

    def __init__(self) -> None:
        self.frame: bytes | None = None
        self.condition = Condition()

    def write(self, buf: bytes) -> int:
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
        return len(buf)


class Camera(AbstractWorker):
    """Captures MJPEG video from Picamera2 and serves it over HTTP."""

    def __init__(self, loop_delay: float = 2.0) -> None:
        self._encoder = JpegEncoder()
        self._output = _StreamingOutput()
        self._camera = Picamera2()
        self._camera.configure(
            self._camera.create_video_configuration(
                main={"size": (CAMERA_WIDTH, CAMERA_HEIGHT)}
            )
        )
        super().__init__("Camera", loop_delay, None, self._on_stop)

    def _on_stop(self) -> None:
        try:
            self._camera.stop_recording()
        except Exception as exc:
            print("Exception while stopping camera: %s" % exc)

    def runnable(self) -> None:
        print("[{0}] Starting camera on port {1}".format(
            threading.current_thread().name, CAMERA_PORT,
        ))
        self._camera.start_recording(
            self._encoder, FileOutput(self._output), quality=Quality.MEDIUM
        )
        output = self._output

        class StreamingHandler(server.BaseHTTPRequestHandler):

            def log_message(self, fmt, *args) -> None:
                pass

            def do_GET(self) -> None:
                if self.path == "/camera":
                    self.send_response(200)
                    self.send_header("Age", "0")
                    self.send_header("Cache-Control", "no-cache, private")
                    self.send_header("Pragma", "no-cache")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header(
                        "Content-Type", "multipart/x-mixed-replace; boundary=FRAME"
                    )
                    self.end_headers()
                    try:
                        while True:
                            with output.condition:
                                output.condition.wait()
                                frame = output.frame
                            self.wfile.write(b"--FRAME\r\n")
                            self.send_header("Content-Type", "image/jpeg")
                            self.send_header("Content-Length", str(len(frame)))
                            self.end_headers()
                            self.wfile.write(frame)
                            self.wfile.write(b"\r\n")
                    except Exception as exc:
                        logging.warning("Streaming client disconnected: %s", exc)
                elif self.path == "/snapshot":
                    with output.condition:
                        output.condition.wait(timeout=2)
                        frame = output.frame
                    if frame is None:
                        self.send_error(503, "No frame available")
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
