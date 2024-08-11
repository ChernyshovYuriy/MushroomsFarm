import threading
from time import sleep

import smbus

from abs_worker import AbstractWorker

# Define the SHT31 address and bus
SHT31_ADDRESS = 0x40


class SHT31(AbstractWorker):

    def __init__(self, shared_data):
        super().__init__("SHT31", 0, None, None)
        self.shared_data = shared_data
        # Use bus 1 (Raspberry Pi 3 uses bus 1)
        self.bus = smbus.SMBus(1)

    def runnable(self):
        # Send the start conversion command to the SHT31
        self.bus.write_i2c_block_data(0x44, 0x2C, [0x06])
        # wait for the conversion to complete
        sleep(0.5)
        # Read the data from the SHT31 containing
        # the temperature (16-bits + CRC) and humidity (16bits + crc)
        data = self.bus.read_i2c_block_data(0x44, 0x00, 6)
        # Convert the data
        temp = data[0] * 256 + data[1]
        self.shared_data.temp_c = int(-45 + (175 * temp / 65535.0))
        self.shared_data.humd = int(100 * (data[3] * 256 + data[4]) / 65535.0)
        print("[{0}] Read SHT31 - temp:{1}, humd:{2}".format(threading.current_thread().name, self.shared_data.temp_c,
                                                             self.shared_data.humd))
        sleep(1)
