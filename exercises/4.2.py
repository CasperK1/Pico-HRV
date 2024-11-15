import time
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
import framebuf

data = open("exercises/capture_250Hz_02.txt")
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

x_current = 0
y_current = 0


def read_min_max(lines):
    file_min_val = float('inf')
    file_max_val = float('-inf')
    for line in lines:
        value = int(line.strip())
        if value < file_min_val:
            file_min_val = value
        if value > file_max_val:
            file_max_val = value
    return file_min_val, file_max_val


def plotter(file):
    x_coordinate = 0
    lines = file.readlines()

    for index in range(0, len(lines), 250):
        # Get min and max for the current 250-sample window
        sample_piece = lines[index:index + 250]
        file_min_val, file_max_val = read_min_max(sample_piece)

        for i, line in enumerate(sample_piece):
            if x_coordinate >= 128:
                break
                    
            if (index + i) % 5 == 0: # five samples per pixel
                value = int(line.strip())
                y_coordinate = round(63 * (value - file_min_val) / (file_max_val - file_min_val))
                oled.pixel(x_coordinate, y_coordinate, 1)
                x_coordinate += 1

    oled.show()


plotter(data)

