import signal
import threading

from camera import Camera
from httpserver import HttpServer
from moisture_controller import MoistureController
from shared_data import SensorData
from sht31 import SHT31


class Controller:
    """Orchestrates all subsystems of the Mushroom Farm controller."""

    def __init__(self) -> None:
        print("Init controller")
        sensor_data = SensorData()
        self.moisture_controller = MoistureController(sensor_data)
        self.sht31 = SHT31(sensor_data)
        self.camera = Camera()
        self.server = HttpServer(self.moisture_controller, sensor_data)

    def start(self) -> None:
        self.moisture_controller.start()
        self.sht31.start()
        self.camera.start()
        self.server.start()
        self.sht31.join()
        self.camera.join()
        self.server.join()

    def stop(self) -> None:
        self.moisture_controller.stop()
        self.sht31.stop()
        self.camera.stop()
        self.server.stop()


if __name__ == "__main__":
    print("[{0}] Mushrooms Controller started".format(threading.current_thread().name))

    controller = Controller()


    def signal_handler(sig, frame) -> None:
        controller.stop()
        raise KeyboardInterrupt


    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        controller.start()
    except KeyboardInterrupt:
        pass

    print("Mushrooms Controller stopped")
