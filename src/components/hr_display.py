from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from fifo import Fifo
from filefifo import Filefifo 

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

class SignalPlotter:
    def __init__(self):
        self.display = oled
        self.reset()

    def reset(self):
        oled.fill(0)
        self.width = oled_width
        self.head = oled_width
        self.x = 0
        self.x_head = -1
        self.y_head = -1
        self.box_y = 14
        self.box_h = 38
        #Round numbers only
        self.pace = 1
        self.t = 0

    def _clear_ahead(self):
        clean_width = self.width // 7
        x_start = (self.x + 1) % self.width
        
        if x_start + clean_width <= self.width:
            self.display.fill_rect(x_start, self.box_y, clean_width, self.box_h, 0)
        else:
            first_part = self.width - x_start
            self.display.fill_rect(x_start, self.box_y, first_part, self.box_h, 0)
            self.display.fill_rect(0, self.box_y, clean_width - first_part, self.box_h, 0)


    def update_display(self, value, min_val, max_val):
        self._clear_ahead()
        
        y_range = max(1, max_val - min_val)
        y = int(self.box_y + self.box_h * (1 - (value - min_val) / y_range))
        y = max(self.box_y + 1, min(y, self.box_y + self.box_h - 1))
        
        self.x = (self.x + self.pace) % self.width
        
        if self.x == 0:
            self.x_head, self.y_head = -1, -1
        
        if self.x_head != -1:
            self.display.line(self.x_head, self.y_head, self.x, y, 1)
        
        self.x_head, self.y_head = self.x, y

    def display_bpm(self, value):
        oled.fill_rect(0, 56, 64, 8, 0) 

        oled.text(f"{"BPM"}:{int(value)}", 0, 56, 1)


    def display_countdown(self, seconds):
        self.display.fill_rect(80, 56, 48, 8, 0)  
        self.display.text(f"{seconds}s", 90, 56, 1)  

    
    def show_oled(self):
        if self.t % 2 == 0:
            oled.show()
            self.t = 0
        self.t += 1
