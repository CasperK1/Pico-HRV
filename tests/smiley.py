import time
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C

button_right = Pin(9, Pin.IN, Pin.PULL_UP) #SW0
button_left = Pin(7, Pin.IN, Pin.PULL_UP) #SW2

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)


def draw_circle(x0, y0, radius):
    x = radius
    y = 0
    err = 0
    
    while x >= y:
        oled.pixel(x0 + x, y0 + y, 1)
        oled.pixel(x0 + y, y0 + x, 1)
        oled.pixel(x0 - y, y0 + x, 1)
        oled.pixel(x0 - x, y0 + y, 1)
        oled.pixel(x0 - x, y0 - y, 1)
        oled.pixel(x0 - y, y0 - x, 1)
        oled.pixel(x0 + y, y0 - x, 1)
        oled.pixel(x0 + x, y0 - y, 1)
        
        y += 1
        err += 1 + 2 * y
        if 2 * (err - x) + 1 > 0:
            x -= 1
            err += 1 - 2 * x

# Draw face outline
draw_circle(64, 32, 20)

# Draw eyes
oled.fill_rect(52, 25, 4, 4, 1)  # Left eye
oled.fill_rect(72, 25, 4, 4, 1)  # Right eye

# Draw smile
oled.line(54, 35, 64, 42, 1)  # Left part of smile
oled.line(64, 42, 74, 35, 1)  # Right part of smile

# Update the display
oled.show()