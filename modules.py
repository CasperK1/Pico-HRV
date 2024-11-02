import time
from machine import Pin, I2C, PWM
from ssd1306 import SSD1306_I2C
from lib.fifo import Fifo

led_pins = [22, 21, 20]
leds = [PWM(Pin(pin, Pin.OUT), freq=1000) for pin in led_pins]


class RotaryEncoder:
    def __init__(self, rot_a, rot_b, rot_sw):
        self.fifo = Fifo(30, typecode='i')
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


class Menu:
    def __init__(self, oled, items, line_spacing):
        self.oled = oled
        self.items = items
        self.font_width = 8  
        self.selector_pos_y = 0
        self.spacing = line_spacing

    def select_next(self):
        if self.selector_pos_y < len(self.items) - 1:
            self.selector_pos_y += 1

    def select_previous(self):
        if self.selector_pos_y > 0:
            self.selector_pos_y -= 1

    def select_item(self):
        pass

    def display(self):
        self.oled.fill(0)
        for item_index, item in enumerate(self.items):
            item_position_y = item_index * 15
            text_width = len(item) * self.font_width + 8
            self.oled.text(f'{item}', 4, item_position_y + 3, 1)

            if item_index == self.selector_pos_y:
                self.oled.rect(0, self.selector_pos_y * 15,
                               text_width, 12, 1)

        self.oled.show()
