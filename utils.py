import time, os
from machine import Pin
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

    def get_last_input(self):
        """Get only the most recent input, clearing any old ones. Prevents fifo's buffer overflowing and makes the menu more responsive"""
        last_input = None
        while self.fifo.has_data():
            last_input = self.fifo.get()
        return last_input



class SSD1306Wrapper:
    """ 🎉This wrapper prevents crashing from timing issues with I2C and WLAN initialization that comes with the async execution.
    Calls SSD1306 driver's show() method with retries. If the I2C write fails due to WiFi timing conflicts, it waits and retries up to 3 times."""
    def __init__(self, oled):
        self.oled = oled

    def __getattr__(self, name):
        return getattr(self.oled, name)

    def show(self):
        for _ in range(3):
            try:
                self.oled.show()
                return
            except OSError:
                time.sleep_ms(100)
        self.oled.show()


def load_capture_files():
    try:
        files = os.listdir("/captures")
        if not files:
            return None
        return files
    except Exception as e:
        print("Error accessing captures folder:", e)
        return None
