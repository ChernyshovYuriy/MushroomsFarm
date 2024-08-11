import threading
from time import sleep

import RPi.GPIO as GPIO

from abs_worker import AbstractWorker

MOISTURE_STATE_NONE = -1
MOISTURE_STATE_OFF = 0
MOISTURE_STATE_ON = 1
PIN_MOISTURE = 26


class UsbController(AbstractWorker):

    def __init__(self, shared_data):
        super().__init__("USB Controller", 0, None, None)
        self.shared_data = shared_data
        self.moisture_state = MOISTURE_STATE_NONE
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_MOISTURE, GPIO.OUT, initial=GPIO.LOW)
        self.turn_moisture_off()

    def runnable(self):
        print("[{0}] USB controller - temp:{1}, humd:{2}".format(threading.current_thread().name,
                                                                 self.shared_data.temp_c,
                                                                 self.shared_data.humd))
        # if 90 < self.shared_data.humd < 100:
        #     self.turn_moisture_off()
        # else:
        #     self.turn_moisture_on()
        sleep(1)

    def stop(self):
        super().stop()
        GPIO.cleanup()

    def turn_moisture_off(self):
        if self.moisture_state == MOISTURE_STATE_OFF:
            return
        self.moisture_state = MOISTURE_STATE_OFF
        GPIO.output(PIN_MOISTURE, GPIO.LOW)
        print("Moisturizer OFF {0}".format(GPIO.input(PIN_MOISTURE)))

    def turn_moisture_on(self):
        if self.moisture_state == MOISTURE_STATE_ON:
            return
        self.moisture_state = MOISTURE_STATE_ON
        GPIO.output(PIN_MOISTURE, GPIO.HIGH)
        print("Moisturizer ON {0}".format(GPIO.input(PIN_MOISTURE)))
