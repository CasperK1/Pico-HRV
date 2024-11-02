import time
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C

button_right = Pin(9, Pin.IN, Pin.PULL_UP) #SW0
button_left = Pin(7, Pin.IN, Pin.PULL_UP) #SW2

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

x_max = 105
x_current = 0

while True:
    oled.fill(0)
    
    if button_right() == 0:
        x_current -= 2
        
    if button_left() == 0:
        x_current += 2
    
    if x_current < 0:
        x_current = 0
    if x_current > x_max:
        x_current = x_max
        
    oled.text('<=>', x_current, 0, 1)
    
    oled.show()
    
    time.sleep(0.05)