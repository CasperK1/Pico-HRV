import time, os
from machine import Pin, I2C, PWM
from lib.fifo import Fifo

class RotaryEncoder:
    def __init__(self, rot_a, rot_b, rot_sw):
        self.fifo = Fifo(10, typecode='i')
        self.a = Pin(rot_a, mode=Pin.IN, pull=Pin.PULL_UP)  # Clockwise
        self.b = Pin(rot_b, mode=Pin.IN, pull=Pin.PULL_UP)  # Counter-clockwise
        self.sw = Pin(rot_sw, mode=Pin.IN, pull=Pin.PULL_UP)  # Switch
        self.last_sw_time = 0
        self.debounce = 100

        self.a.irq(handler=self.rotary_handler,
                   trigger=Pin.IRQ_RISING, hard=True)
        self.sw.irq(handler=self.switch_handler,
                    trigger=Pin.IRQ_RISING, hard=True)

    def rotary_handler(self, pin):
        if self.b():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)

    def switch_handler(self, pin):
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_sw_time) > self.debounce:
            self.fifo.put(0)
            self.last_sw_time = current_time



def load_capture_files():
    try:
        files = os.listdir("/captures")
        if not files:
            return None
        return files
    except Exception as e:
        print("Error accessing captures folder:", e)
        return None
