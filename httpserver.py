import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from abs_worker import AbstractWorker

PORT_NUMBER = 8080


class HttpServer(AbstractWorker):

    def __init__(self, usb_controller, shared_data_sht31):
        super().__init__("HTTP Server", 0, None, self.on_stop_cb)
        # Create a web server and define the handler to manage the incoming request.
        self.server = HTTPServer(('', PORT_NUMBER), self.create_handler(usb_controller, shared_data_sht31))

    def create_handler(self, usb_controller, shared_data_sht31):
        # This class will handle any incoming request from the browser.
        class ConnectionHandler(BaseHTTPRequestHandler):

            def __init__(self, request, client_address, server):
                super().__init__(request, client_address, server)

            # Handler for the GET requests
            def do_GET(self):
                print("GET: %s" % self.path)
                try:
                    # Check the file extension required and
                    # set the right mime type
                    if self.path.endswith(".html"):
                        mimetype = 'text/html'
                    if self.path.endswith(".jpg"):
                        mimetype = 'image/jpg'
                    if self.path.endswith(".gif"):
                        mimetype = 'image/gif'
                    if self.path.endswith(".js"):
                        mimetype = 'application/javascript'
                    if self.path.endswith(".css"):
                        mimetype = 'text/css'
                    if self.path.endswith("/temp"):
                        self.send_temp()
                    if self.path.endswith("/humd"):
                        self.send_humd()
                except IOError:
                    self.send_error(404, 'File Not Found: %s' % self.path)

            # Handler for the POST requests
            def do_POST(self):
                print("POST: %s" % self.path)
                if self.path == "/humd/stop":
                    usb_controller.turn_moisture_off()
                if self.path == "/humd/start":
                    usb_controller.turn_moisture_on()
                self.send_response(200)

            def send_temp(self):
                mime_type = 'text/plain'
                self.send_response(200)
                self.send_header('Content-type', mime_type)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                message = str(shared_data_sht31.temp_c)
                self.wfile.write(bytes(message, "utf-8"))

            def send_humd(self):
                mime_type = 'text/plain'
                self.send_response(200)
                self.send_header('Content-type', mime_type)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                message = str(shared_data_sht31.humd)
                self.wfile.write(bytes(message, "utf-8"))

        return ConnectionHandler

    def on_stop_cb(self):
        self.server.socket.close()
        self.server.shutdown()

    def runnable(self):
        while self.is_run():
            print("[{0}] Starting http server on port {1}".format(threading.current_thread().name, PORT_NUMBER))
            # Wait forever for incoming http requests
            self.server.serve_forever()
        print('Exit runnable of http server')


class HttpServerData:

    def __init__(self):
        print("Init http server data")
        self.echo = ""
