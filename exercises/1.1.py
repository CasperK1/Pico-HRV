import time
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
import framebuf

button_sw0 = Pin(9, Pin.IN, Pin.PULL_UP) #SW0 (Down)
button_clr = Pin(8, Pin.IN, Pin.PULL_UP) #SW1 (Clear)
button_sw2 = Pin(7, Pin.IN, Pin.PULL_UP) #SW2 (Up)

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

x_current = 0
y_current = 32  # Start in middle of screen

while True:
    if button_clr() == 0:
        x_current = 0
        oled.fill(0)
        
    if button_sw0() == 0:  # Down
        if y_current < oled_height - 1:
            y_current += 1
    
    if button_sw2() == 0:  # Up
        if y_current > 0: 
            y_current -= 1
        
    oled.pixel(x_current, y_current, 1)  # Draw a single pixel
    oled.show()
    x_current += 1
    
    if x_current >= oled_width:
        x_current = 0
    