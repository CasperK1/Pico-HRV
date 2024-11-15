from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from lib.filefifo import Filefifo
from lib.fifo import Fifo


class DataViewer:
    def __init__(self, rot_a_pin, rot_b_pin):
        # Initialize I2C and OLED
        i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
        self.oled = SSD1306_I2C(128, 64, i2c)

        # Set up rotary encoder with interrupt
        self.encoder_fifo = Fifo(30, typecode='i')  # For encoder events
        self.rot_a = Pin(rot_a_pin, Pin.IN, Pin.PULL_UP)
        self.rot_b = Pin(rot_b_pin, Pin.IN, Pin.PULL_UP)
        self.rot_a.irq(handler=self.rotary_handler,
                       trigger=Pin.IRQ_RISING, hard=True)

        # Read data from exercise file
        self.data = []
        file_reader = Filefifo(
            1000, name='exercises/capture_250Hz_01.txt', repeat=False)
        try:
            while len(self.data) < 1000:  # Read exactly 1000 values
                self.data.append(file_reader.get())
        except RuntimeError:
            pass  # End of file reached

        # Calculate data properties
        self.data_min = min(self.data)
        self.data_max = max(self.data)

        # Display parameters
        self.values_per_screen = 6  # Number of values we can show at once
        self.current_pos = 0  # Starting position
        self.max_pos = len(self.data) - self.values_per_screen

    def rotary_handler(self, pin):
        """Interrupt handler for rotary encoder"""
        if self.rot_b():
            # Counter-clockwise rotation
            if self.current_pos > 0:
                self.encoder_fifo.put(-1)
        else:
            # Clockwise rotation
            if self.current_pos < self.max_pos:
                self.encoder_fifo.put(1)

    def update_display(self):
        """Update the OLED display with current values"""
        self.oled.fill(0)

        # Show position info
        self.oled.text(f"Position: {self.current_pos}", 0, 0, 1)

        # Show values
        for i in range(self.values_per_screen):
            if i + self.current_pos < len(self.data):
                value = self.data[i + self.current_pos]
                self.oled.text(
                    f"{i+self.current_pos}: {value}", 0, (i+1)*10, 1)

        self.oled.show()

    def run(self):
        """Main program loop"""
        print(f"Data loaded: {len(self.data)} points")
        print(f"Min: {self.data_min}, Max: {self.data_max}")
        self.update_display()

        while True:
            if self.encoder_fifo.has_data():
                direction = self.encoder_fifo.get()
                self.current_pos += direction
                # Ensure we stay within bounds
                self.current_pos = max(0, min(self.current_pos, self.max_pos))
                self.update_display()


# Create and run the data viewer
try:
    viewer = DataViewer(10, 11)  # Using pins 10 and 11 for rotary encoder
    viewer.run()
except Exception as e:
    print(f"Error: {str(e)}")
