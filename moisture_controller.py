import threading
from enum import IntEnum
from time import sleep

import RPi.GPIO as GPIO

from abs_worker import AbstractWorker
from gpio_pins_distribution import PIN_MOISTURE_POWER, PIN_MOISTURE_TRIGGER
from shared_data import SensorData

HUMIDITY_TARGET_MIN = 90
HUMIDITY_TARGET_MAX = 100


class MoistureState(IntEnum):
    NONE = -1
    OFF = 0
    ON = 1


class MoistureController(AbstractWorker):
    """Controls the USB humidifier via GPIO based on humidity readings."""

    def __init__(self, shared_data: SensorData) -> None:
        super().__init__("Moisture Controller", 0, None, None)
        self.shared_data = shared_data
        self._state = MoistureState.NONE
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_MOISTURE_POWER, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(PIN_MOISTURE_TRIGGER, GPIO.OUT, initial=GPIO.LOW)
        self.turn_off()

    def runnable(self) -> None:
        humd = self.shared_data.humd
        print("[{0}] MoistureController - temp:{1}, humd:{2}".format(
            threading.current_thread().name,
            self.shared_data.temp_c,
            humd,
        ))
        if HUMIDITY_TARGET_MIN <= humd <= HUMIDITY_TARGET_MAX:
            self.turn_off()
        else:
            self.turn_on()
        sleep(1)

    def stop(self) -> None:
        super().stop()
        GPIO.cleanup()

    @property
    def is_on(self) -> bool:
        return self._state == MoistureState.ON

    def turn_off(self) -> None:
        if self._state == MoistureState.OFF:
            return
        self._state = MoistureState.OFF
        GPIO.output(PIN_MOISTURE_POWER, GPIO.LOW)
        GPIO.output(PIN_MOISTURE_TRIGGER, GPIO.LOW)
        print("Moisturizer OFF")

    def turn_on(self) -> None:
        if self._state == MoistureState.ON:
            return
        self._state = MoistureState.ON
        GPIO.output(PIN_MOISTURE_POWER, GPIO.HIGH)
        GPIO.output(PIN_MOISTURE_TRIGGER, GPIO.HIGH)
        sleep(1)
        GPIO.output(PIN_MOISTURE_TRIGGER, GPIO.LOW)
        print("Moisturizer ON")
