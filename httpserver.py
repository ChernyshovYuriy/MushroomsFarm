import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from abs_worker import AbstractWorker
from moisture_controller import MoistureController
from shared_data import SensorData

PORT_NUMBER = 8080
WEB_DIR = os.path.join(os.path.dirname(__file__), "web")


class HttpServer(AbstractWorker):
    """HTTP server: serves the web dashboard and exposes the sensor/control API."""

    def __init__(self, moisture_controller: MoistureController, sensor_data: SensorData) -> None:
        super().__init__("HTTP Server", 0, None, self._on_stop)
        self._server = HTTPServer(
            ('', PORT_NUMBER),
            self._create_handler(moisture_controller, sensor_data),
        )

    def _create_handler(self, moisture_controller: MoistureController, sensor_data: SensorData):

        class ConnectionHandler(BaseHTTPRequestHandler):

            def log_message(self, fmt, *args) -> None:
                print("[HTTP] %s" % (fmt % args))

            # ------------------------------------------------------------------ helpers

            def _send_text(self, body: str) -> None:
                encoded = body.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(encoded)

            def _send_json(self, data: dict) -> None:
                encoded = json.dumps(data).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(encoded)

            def _send_file(self, path: str, mime: str) -> None:
                with open(path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            # ------------------------------------------------------------------ CORS preflight

            def do_OPTIONS(self) -> None:
                self.send_response(204)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()

            # ------------------------------------------------------------------ GET

            def do_GET(self) -> None:
                # API endpoints
                if self.path == "/status":
                    self._send_json({
                        "temp_c": sensor_data.temp_c,
                        "humd": sensor_data.humd,
                        "moisturizer_on": moisture_controller.is_on,
                    })
                elif self.path == "/temp":
                    self._send_text(str(sensor_data.temp_c))
                elif self.path == "/humd":
                    self._send_text(str(sensor_data.humd))
                # Serve web dashboard
                elif self.path in ("/", "/index.html"):
                    index = os.path.join(WEB_DIR, "index.html")
                    if os.path.exists(index):
                        self._send_file(index, "text/html; charset=utf-8")
                    else:
                        self.send_error(404, "index.html not found")
                else:
                    self.send_error(404)

            # ------------------------------------------------------------------ POST

            def do_POST(self) -> None:
                if self.path == "/humd/stop":
                    moisture_controller.turn_off()
                    self._send_json({"ok": True, "moisturizer_on": False})
                elif self.path == "/humd/start":
                    moisture_controller.turn_on()
                    self._send_json({"ok": True, "moisturizer_on": True})
                else:
                    self.send_error(404)

        return ConnectionHandler

    def _on_stop(self) -> None:
        self._server.socket.close()
        self._server.shutdown()

    def runnable(self) -> None:
        print("[{0}] HTTP server listening on port {1}".format(
            threading.current_thread().name, PORT_NUMBER,
        ))
        self._server.serve_forever()
