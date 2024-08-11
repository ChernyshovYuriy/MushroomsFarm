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


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class StreamingOutput(io.BufferedIOBase):

    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


# Camera's class.
class Camera(AbstractWorker):

    def __init__(self):
        self.encoder = JpegEncoder()
        self.output = StreamingOutput()
        self.camera = Picamera2()
        self.camera.resolution = (1280, 720)
        self.camera.framerate = 60
        super().__init__("Camera", 0, None, self.on_stop_cb)

    def on_stop_cb(self):
        try:
            self.camera.stop_recording()
        except Exception as e:
            print("Exception while stop streaming %s" % e)

    def runnable(self):
        print("[{0}] Starting record camera".format(threading.current_thread().name))
        self.camera.start_recording(self.encoder, FileOutput(self.output), quality=Quality.HIGH)
        try:
            address = ('', 8000)
            streaming_server = StreamingServer(address, self.create_handler(self.output))
            streaming_server.serve_forever()
        finally:
            pass

    def create_handler(self, output):
        class StreamingHandler(server.BaseHTTPRequestHandler):

            def do_GET(self):
                if self.path == '/camera':
                    self.send_response(200)
                    self.send_header('Age', str(0))
                    self.send_header('Cache-Control', 'no-cache, private')
                    self.send_header('Pragma', 'no-cache')
                    self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
                    self.end_headers()
                    try:
                        while True:
                            with output.condition:
                                output.condition.wait()
                                frame = output.frame
                            self.wfile.write(b'--FRAME\r\n')
                            self.send_header('Content-Type', 'image/jpeg')
                            self.send_header('Content-Length', str(len(frame)))
                            self.end_headers()
                            self.wfile.write(frame)
                            self.wfile.write(b'\r\n')
                    except Exception as e:
                        logging.warning(
                            'Removed streaming client %s: %s',
                            self.client_address, str(e))

        return StreamingHandler
