import uasyncio
import network
from wifi import wifi_connect_install_mqtt
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from utils import RotaryEncoder, load_capture_files, SSD1306Wrapper
from menus import MainMenu, HistoryMenu, SettingsMenu
import micropython

# Configure emergency exception buffer
micropython.alloc_emergency_exception_buf(200)

# Initialize hardware
wlan = network.WLAN(network.STA_IF)
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306Wrapper(SSD1306_I2C(oled_width, oled_height, i2c))
rot = RotaryEncoder(10, 11, 12)

# Menu instances
main_menu = MainMenu(oled, ["MEASURE HR", "HRV ANALYSIS", "KUBIOS", "HISTORY", "SETTINGS"], rot)
history_items = load_capture_files() or []
history_items.append("Back")
history_menu = HistoryMenu(oled, history_items, rot)
settings_menu = SettingsMenu(oled, ["WiFi", "MQTT", "Back"], rot,  wlan)



async def menu_manager():
    current_menu = "MAIN"
    while True:
        if current_menu == "MAIN":
            current_menu = await main_menu.handle_input()
        elif current_menu == "HISTORY":
            current_menu = await history_menu.handle_input()
        elif current_menu == "SETTINGS":
            current_menu = await settings_menu.handle_input()



async def main():
    wifi_task = uasyncio.create_task(wifi_connect_install_mqtt(wlan, main_menu, history_menu, settings_menu))
    menu_task = uasyncio.create_task(menu_manager())

    """ Wait for both tasks
     uasyncio.gather: Runs multiple coroutines concurrently and waits for all of them to complete. Used within async functions to run multiple tasks in parallel
     uasyncio.run: Used to run the main event loop. Can be called once in the program"""
    await uasyncio.gather(wifi_task, menu_task)

if __name__ == '__main__':
    try:
        uasyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted")

