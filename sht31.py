import threading
from time import sleep

import smbus

from abs_worker import AbstractWorker
from shared_data import SensorData

SHT31_I2C_ADDRESS = 0x44
SHT31_BUS = 1


class SHT31(AbstractWorker):
    """Reads temperature and humidity from the SHT31 sensor over I2C."""

    def __init__(self, shared_data: SensorData, loop_delay: float = 0) -> None:
        super().__init__("SHT31", loop_delay, None, None)
        self.shared_data = shared_data
        self.bus = smbus.SMBus(SHT31_BUS)

    def runnable(self) -> None:
        self.bus.write_i2c_block_data(SHT31_I2C_ADDRESS, 0x2C, [0x06])
        sleep(0.05)
        data = self.bus.read_i2c_block_data(SHT31_I2C_ADDRESS, 0x00, 6)
        raw_temp = data[0] * 256 + data[1]
        self.shared_data.temp_c = int(-45 + (175 * raw_temp / 65535.0))
        self.shared_data.humd = int(100 * (data[3] * 256 + data[4]) / 65535.0)
        print("[{0}] SHT31 - temp:{1}°C, humd:{2}%".format(
            threading.current_thread().name,
            self.shared_data.temp_c,
            self.shared_data.humd,
        ))
        sleep(1.5)  # Pi 3: rate-limit I2C reads to reduce CPU overhead
