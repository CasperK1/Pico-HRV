from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

y_position = 0
line_height = 8

while True:
    user_input = input()
    if y_position >= oled_height - line_height:
        oled.scroll(0, -line_height)
        oled.fill_rect(0, oled_height - line_height, oled_width, line_height, 0)
    else:
        y_position += line_height
            
    oled.text(user_input, 0, y_position)
    oled.show()