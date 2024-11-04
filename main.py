import uasyncio
import machine
from wifi import wifi_connect
import micropython
import time
from machine import Pin, I2C, PWM
from ssd1306 import SSD1306_I2C
from modules import RotaryEncoder, Menu

# Configure emergency exception buffer
micropython.alloc_emergency_exception_buf(200)

# Initialize hardware
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)
rot = RotaryEncoder(10, 11, 12)
main_menu = Menu(oled, ["MEASURE HR", "HRV ANALYSIS", "KUBIOS", "HISTORY"], 15)


async def menu_loop():
    while True:
        if rot.fifo.has_data():
            data = rot.fifo.get()
            if data == 1:
                main_menu.select_next()
            elif data == -1:
                main_menu.select_previous()
            elif data == 0:
                main_menu.select_item()
                
                
        main_menu.display()
        await uasyncio.sleep_ms(20)

# wifi_connect() has to be called in a separate task to avoid crashing, when the wifi icon changes
async def wifi_connection(): 
    is_wifi_connected = await wifi_connect(main_menu)
    if is_wifi_connected:
        main_menu.wifi_conn = True
    else:
        main_menu.wifi_conn = False


async def main():
    wifi_task = uasyncio.create_task(wifi_connect(main_menu))
    main_task = uasyncio.create_task(menu_loop())

    """ Wait for both tasks
     uasyncio.gather: Runs multiple coroutines concurrently and waits for all of them to complete. Used within async functions to run multiple tasks in parallel
     uasyncio.run: Used to run the main event loop. Can be called once in the program"""
    await uasyncio.gather(wifi_task, main_task)

if __name__ == '__main__':
    try:
        uasyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted")
