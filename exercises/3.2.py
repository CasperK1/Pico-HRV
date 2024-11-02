import time
from machine import Pin, I2C, PWM
from ssd1306 import SSD1306_I2C
from lib.fifo import Fifo
import micropython
micropython.alloc_emergency_exception_buf(200)

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

led_pins = [22, 21, 20]
leds = [PWM(Pin(pin, Pin.OUT), freq=1000) for pin in led_pins]
led_states = ["OFF"] * len(led_pins)


class RotaryEncoder:
    def __init__(self, rot_a, rot_b, rot_sw):
        self.fifo = Fifo(30, typecode='i')
        self.a = Pin(rot_a, mode=Pin.IN, pull=Pin.PULL_UP) # Clockwise
        self.b = Pin(rot_b, mode=Pin.IN, pull=Pin.PULL_UP) # Counter-clockwise
        self.sw = Pin(rot_sw, mode=Pin.IN, pull=Pin.PULL_UP) # Switch
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
    def __init__(self, oled, items):
        self.oled = oled
        self.items = items
        self.selector_pos_y = 0

    def display(self):
        self.oled.fill(0)
        for item_index, item in enumerate(self.items):
            item_position_y = item_index * 15
            state = led_states[item_index]
            self.oled.text(f'{item} - {state}', 4, item_position_y + 3, 1)

        self.oled.rect(0, self.selector_pos_y * 15, 85, 12, 1)
        self.oled.show()

    def select_next(self):
        if self.selector_pos_y < len(self.items) - 1:
            self.selector_pos_y += 1

    def select_previous(self):
        if self.selector_pos_y > 0:
            self.selector_pos_y -= 1

    def toggle_selected_led(self):
        led_index = self.selector_pos_y
        if led_states[led_index] == "OFF":
            led_states[led_index] = "ON"
            leds[led_index].duty_u16(500)
        else:
            led_states[led_index] = "OFF"
            leds[led_index].duty_u16(0)

rot = RotaryEncoder(10, 11, 12)


def main():
    menu = Menu(oled, ["LED1", "LED2", "LED3"])

    while True:
        if rot.fifo.has_data():
            data = rot.fifo.get()
            if data == 1:
                menu.select_next()
            elif data == -1:
                menu.select_previous()
            elif data == 0:
                menu.toggle_selected_led()

        menu.display()


if __name__ == '__main__':
    main()
