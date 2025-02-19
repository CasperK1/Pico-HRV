import time
from machine import ADC
from lib.led import Led
from fifo import Fifo
from piotimer import Piotimer
import micropython
from src.components.hr_display import SignalPlotter
micropython.alloc_emergency_exception_buf(200)

SAMPLE_RATE = 250 
BUFFER_SIZE = 250

class Sensor:
    def __init__(self, pin=26, sampling_rate=250):
        self.sensor = ADC(pin)
        self.sampling_rate = sampling_rate
        self.fifo = Fifo(300, 'H')

    def start(self):
        return Piotimer(mode = Piotimer.PERIODIC, freq=250, callback=self.read_sensor)
        
    def read_sensor(self, tid):
        self.fifo.put(self.sensor.read_u16() >> 2)

    def count(self):
        count = ((self.fifo.head - self.fifo.tail) + self.fifo.size) % self.fifo.size
        return count

class Detect_peaks:
    def __init__(self):
        self.timer = None
        self.plotter = SignalPlotter()
        self.reset()
       
    
    def reset(self):
        self.sensor = Sensor(26)
        self.data = self.sensor.fifo
        self.reading = 0
        self.sampling_rate = self.sensor.sampling_rate
        self.window = []
        self.min_val = 0
        self.max_val = 0
        self.threshold = 0
        self.margin = 0
        self.validate_count = 0
        self.prev_update_time = 0
        self.bpm = 0
        self.started = False        

        self.valid_peaks = []

        self.up = False
        self.fall = False
        self.count = []

        self.state = self.rising_edge

        self.ibi = 0
        self.ibi_values = []
        self.ibi_raw = []
        self.plotter.reset()

        if self.timer: self.timer.deinit()
    
    def buffer_maintain(self):
        self.reading = self.data.get()     

        if len(self.window) < BUFFER_SIZE:
            self.window.append(self.reading)
        elif len(self.window) == BUFFER_SIZE:
            self.window.pop(0)
            self.window.append(self.reading)
    
    def min_max(self):
        if len(self.window) == BUFFER_SIZE:
            self.min_val = min(self.window)
            self.max_val = max(self.window)

            baseline = sum(self.window) // len(self.window)
            peak_range = self.max_val - self.min_val
            
            self.threshold = baseline + int(peak_range * 0.4)
            self.margin = baseline + int(peak_range * 0.2)

    def rising_edge(self):
        if self.window[0] >= self.threshold and not self.up:
            if self.validate_count == 10:
                self.up = True
                self.fall = False
                self.validate_count = 0

            self.count.append(self.window[0])
            self.validate_count += 1           
        
        if self.window[0] <= self.threshold:
            self.validate_count = 0
            self.count.clear()

        if self.window[0] > self.margin and self.up:
            self.fall = True
            self.count.append(self.window[0])
        
        else:
            self.valid_peaks.append(time.time_ns() // 1_000_000)
            self.up = False
            self.state = self.falling_edge
        
    
    def falling_edge(self):
        if self.window[0] <= self.margin:
            if self.validate_count == 10:
                self.fall = True
            
            self.count.append(self.window[0])
            self.validate_count += 1
            
        if self.window[0] > self.threshold and not self.fall:
            self.validate_count = 0
            self.valid_peaks.pop()
            self.count.clear()
            self.state = self.rising_edge
            
        if self.window[0] > self.threshold and self.fall: 
            self.fall = False
            if len(self.valid_peaks) == 2:
                ibi = self.valid_peaks[1] - self.valid_peaks[0]
                self.ibi_raw.append(ibi)
                if len(self.ibi_values) < 20:
                    self.ibi_values.append(ibi)
                else:
                    self.ibi_values.pop() 
                bpm = 60000 / ibi
                if 40 <= bpm <= 180:
                    self.bpm = bpm
                self.valid_peaks.clear()
            self.state = self.rising_edge

    def get_ibi(self):
        if self.ibi_raw:
            return self.ibi_raw
        raise RuntimeWarning("NO IBI DATA")

            
    def run(self, countdown=None):
        if not self.started:
            self.reset()
            self.timer = self.sensor.start()
            self.started = True

        while self.data.has_data():
            self.buffer_maintain()
            self.min_max()
            self.state()

            if (time.ticks_diff(time.ticks_ms(), self.prev_update_time) > int(60000 / 180 / 10)):
                self.prev_update_time = time.ticks_ms()
                self.plotter.update_display(
                    self.reading, self.min_val, self.max_val)

                if countdown is not None:
                    self.plotter.display_countdown(countdown)

                self.plotter.show_oled()
                self.plotter.display_bpm(self.bpm)
