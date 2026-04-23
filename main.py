import signal
import threading
from dataclasses import dataclass

from camera import Camera
from httpserver import HttpServer
from moisture_controller import MoistureController
from shared_data import SensorData
from sht31 import SHT31


@dataclass(frozen=True)
class LoopDelayConfig:
    moisture_controller: float = 2.0   # humidity changes slowly, 2s is sufficient
    sht31: float = 0                   # sleep is inside SHT31.runnable()
    camera: float = 2.0
    http_server: float = 0.5


class Controller:
    """Orchestrates all subsystems of the Mushroom Farm controller."""

    def __init__(self, loop_delays: LoopDelayConfig | None = None) -> None:
        print("Init controller")
        loop_delays = loop_delays or LoopDelayConfig()
        sensor_data = SensorData()
        self.moisture_controller = MoistureController(
            sensor_data, loop_delay=loop_delays.moisture_controller
        )
        self.sht31 = SHT31(sensor_data, loop_delay=loop_delays.sht31)
        self.camera = Camera(loop_delay=loop_delays.camera)
        self.server = HttpServer(
            self.moisture_controller,
            sensor_data,
            camera_output=self.camera,
            loop_delay=loop_delays.http_server,
        )

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
