import threading
from time import sleep

import RPi.GPIO as GPIO

from abs_worker import AbstractWorker
from gpio_pins_distribution import PIN_MOISTURE_POWER, PIN_MOISTURE_TRIGGER

MOISTURE_STATE_NONE = -1
MOISTURE_STATE_OFF = 0
MOISTURE_STATE_ON = 1


class MoistureController(AbstractWorker):

    def __init__(self, shared_data):
        super().__init__("Moisture Controller", 0, None, None)
        self.shared_data = shared_data
        self.moisture_state = MOISTURE_STATE_NONE
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_MOISTURE_POWER, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(PIN_MOISTURE_TRIGGER, GPIO.OUT, initial=GPIO.LOW)
        self.turn_moisture_off()

    def runnable(self):
        print("[{0}] Moisture controller - temp:{1}, humd:{2}".format(threading.current_thread().name,
                                                                      self.shared_data.temp_c,
                                                                      self.shared_data.humd))
        if 90 <= self.shared_data.humd <= 100:
            self.turn_moisture_off()
        else:
            self.turn_moisture_on()
        sleep(1)

    def stop(self):
        super().stop()
        GPIO.cleanup()

    def turn_moisture_off(self):
        if self.moisture_state == MOISTURE_STATE_OFF:
            return
        self.moisture_state = MOISTURE_STATE_OFF
        GPIO.output(PIN_MOISTURE_POWER, GPIO.LOW)
        GPIO.output(PIN_MOISTURE_TRIGGER, GPIO.LOW)
        print("Moisturizer OFF {0}".format(GPIO.input(PIN_MOISTURE_POWER)))

    def turn_moisture_on(self):
        if self.moisture_state == MOISTURE_STATE_ON:
            return
        self.moisture_state = MOISTURE_STATE_ON
        GPIO.output(PIN_MOISTURE_POWER, GPIO.HIGH)
        GPIO.output(PIN_MOISTURE_TRIGGER, GPIO.HIGH)
        sleep(1)
        GPIO.output(PIN_MOISTURE_TRIGGER, GPIO.LOW)
        print("Moisturizer ON {0}".format(GPIO.input(PIN_MOISTURE_POWER)))
