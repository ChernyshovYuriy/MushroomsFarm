import signal
import sys
import threading

from camera import Camera
from httpserver import HttpServer, HttpServerData
from shared_data import SharedSHT31
from sht31 import SHT31
from usb_controller import UsbController


class Controller:
    """
    Main controller of the Mushrooms Controller.
    """

    def __init__(self):
        print("Init controller")
        shared_data_sht31 = SharedSHT31()
        self.usb_controller = UsbController(shared_data_sht31)
        self.sht31 = SHT31(shared_data_sht31)
        self.server_data = HttpServerData()
        self.camera = Camera()
        self.server = HttpServer(self.usb_controller, shared_data_sht31)

    def start(self):
        self.usb_controller.start()
        self.sht31.start()
        self.camera.start()
        self.server.start()
        self.sht31.join()
        self.camera.join()
        self.server.join()

    def stop(self):
        self.usb_controller.stop()
        self.sht31.stop()
        self.camera.stop()
        self.server.stop()


if __name__ == "__main__":
    print("[{0}] Mushrooms Controller started".format(threading.current_thread().name))

    controller = Controller()

    def signal_handler(sig, frame):
        controller.stop()
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        controller.start()
    except KeyboardInterrupt:
        pass

    print("Mushrooms Controller stopped")
