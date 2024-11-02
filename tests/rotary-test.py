from machine import Pin
import time
from lib.fifo import Fifo

rot_a = Pin(10, Pin.IN, Pin.PULL_UP)
rot_b = Pin(11, Pin.IN, Pin.PULL_UP)
rot_sw = Pin(12, Pin.IN, Pin.PULL_UP)

class Encoder:
    def __init__(self, rot_a, rot_b, rot_sw):
        self.fifo = Fifo(30, typecode='i')
        self.a = Pin(rot_a, mode=Pin.IN, pull=Pin.PULL_UP)
        self.b = Pin(rot_b, mode=Pin.IN, pull=Pin.PULL_UP)
        self.sw = Pin(rot_sw, mode=Pin.IN, pull=Pin.PULL_UP)
        self.last_sw_time = 0
        self.debounce = 100
        
        self.a.irq(handler=self.rotary_handler, trigger=Pin.IRQ_RISING, hard=True)
        self.sw.irq(handler=self.switch_handler, trigger=Pin.IRQ_RISING, hard=True)

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


rot = Encoder(10, 11, 12)

while True:
    if rot.fifo.has_data():
        print(rot.fifo.get())
