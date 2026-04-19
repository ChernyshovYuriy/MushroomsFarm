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
    """Controls the USB humidifier via GPIO based on humidity readings.

    Manual overrides (turn_on/turn_off called externally) are respected
    indefinitely until the humidity crosses the opposite threshold, at which
    point automatic control resumes.

    Auto logic:
      humd < HUMIDITY_TARGET_MIN  → turn on  (unless manually turned off)
      humd > HUMIDITY_TARGET_MAX  → turn off  (always — prevents over-humidifying)
      within range                → keep current state
    """

    def __init__(self, shared_data: SensorData) -> None:
        super().__init__("Moisture Controller", 0, None, None)
        self.shared_data = shared_data
        self._state = MoistureState.NONE
        self._manual_off = False  # True = user explicitly turned off, skip auto-on
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_MOISTURE_POWER, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(PIN_MOISTURE_TRIGGER, GPIO.OUT, initial=GPIO.LOW)
        self.turn_off(manual=False)

    def runnable(self) -> None:
        humd = self.shared_data.humd
        temp = self.shared_data.temp_c
        print("[{0}] MoistureController - temp:{1}°C  humd:{2}%  state:{3}  manual_off:{4}".format(
            threading.current_thread().name, temp, humd,
            self._state.name, self._manual_off,
        ))

        if humd > HUMIDITY_TARGET_MAX:
            # Always turn off if over-humidified, and clear the manual lock
            # so auto-control can resume normally once humidity drops.
            if self._manual_off:
                print("[MoistureController] Humidity exceeded max ({0}%) — clearing manual override".format(humd))
                self._manual_off = False
            self.turn_off(manual=False)

        elif humd < HUMIDITY_TARGET_MIN:
            if self._manual_off:
                print("[MoistureController] Auto-on skipped — manual override active (humd:{0}%)".format(humd))
            else:
                self.turn_on()

        else:
            # Within target range — hold current state, clear manual lock
            if self._manual_off:
                print("[MoistureController] Humidity in range ({0}%) — clearing manual override".format(humd))
                self._manual_off = False

        sleep(1)

    def stop(self) -> None:
        super().stop()
        GPIO.cleanup()

    @property
    def is_on(self) -> bool:
        return self._state == MoistureState.ON

    def turn_off(self, manual: bool = True) -> None:
        if manual:
            self._manual_off = True
            print("[MoistureController] Manual OFF requested")
        if self._state == MoistureState.OFF:
            return
        self._state = MoistureState.OFF
        GPIO.output(PIN_MOISTURE_POWER, GPIO.LOW)
        GPIO.output(PIN_MOISTURE_TRIGGER, GPIO.LOW)
        print("[MoistureController] Humidifier OFF (power:{0})".format(GPIO.input(PIN_MOISTURE_POWER)))

    def turn_on(self, manual: bool = False) -> None:
        if manual:
            self._manual_off = False
            print("[MoistureController] Manual ON requested")
        if self._state == MoistureState.ON:
            return
        self._state = MoistureState.ON
        GPIO.output(PIN_MOISTURE_POWER, GPIO.HIGH)
        GPIO.output(PIN_MOISTURE_TRIGGER, GPIO.HIGH)
        sleep(1)
        GPIO.output(PIN_MOISTURE_TRIGGER, GPIO.LOW)
        print("[MoistureController] Humidifier ON (power:{0})".format(GPIO.input(PIN_MOISTURE_POWER)))
