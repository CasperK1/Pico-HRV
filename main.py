import uasyncio
import network
from wifi import wifi_connect_install_mqtt
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from modules import RotaryEncoder, load_capture_files
from menus import MainMenu, HistoryMenu, SettingsMenu
import micropython

# Configure emergency exception buffer
micropython.alloc_emergency_exception_buf(200)

# Initialize hardware
wlan = network.WLAN(network.STA_IF)
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)
rot = RotaryEncoder(10, 11, 12)

main_menu = MainMenu(oled, ["MEASURE HR", "HRV ANALYSIS", "KUBIOS", "HISTORY", "SETTINGS"])
history_items = load_capture_files() + ["Back"]
history_menu = HistoryMenu(oled, history_items)
settings_menu = SettingsMenu(oled, ["WiFi", "Logs", "Back"])


current_menu = "MAIN"


def get_last_input(fifo):
    """Get only the most recent input, clearing any old ones. Prevents fifo's buffer overflowing and makes the menu more responsive"""
    last_input = None
    while fifo.has_data():
        last_input = fifo.get()
    return last_input


async def main_menu_loop():
    global current_menu
    while current_menu == "MAIN":
        if rot.fifo.has_data():
            data = get_last_input(rot.fifo)
            if data == 1:
                main_menu.select_next()
            elif data == -1:
                main_menu.select_previous()
            elif data == 0:
                selected_item = main_menu.select_item()
                if selected_item == "HISTORY":
                    current_menu = "HISTORY"
                    history_menu.display()
                    break
                elif selected_item == "SETTINGS":
                    current_menu = "SETTINGS"
                    settings_menu.display()
                    break

        main_menu.display()
        await uasyncio.sleep_ms(20)


async def history_menu_loop():
    global current_menu
    while current_menu == "HISTORY":
        if rot.fifo.has_data():
            data = get_last_input(rot.fifo)
            if data == 1:
                history_menu.select_next()
            elif data == -1:
                history_menu.select_previous()
            elif data == 0:
                menu_select = history_menu.select_item()
                if menu_select == "Back":
                    current_menu = "MAIN"
                    main_menu.display()
                    break

        history_menu.display()
        await uasyncio.sleep_ms(20)


async def settings_menu_loop():
    global current_menu
    while current_menu == "SETTINGS":
        if rot.fifo.has_data():
            data = get_last_input(rot.fifo)
            if data == 1:
                settings_menu.select_next()
            elif data == -1:
                settings_menu.select_previous()
            elif data == 0:
                menu_select = settings_menu.select_item()
                if menu_select == "Back":
                    current_menu = "MAIN"
                    main_menu.display()
                    break

        settings_menu.display()
        await uasyncio.sleep_ms(20)


async def menu_manager():
    global current_menu
    while True:
        if current_menu == "MAIN":
            await main_menu_loop()
        elif current_menu == "HISTORY":
            await history_menu_loop()
        elif current_menu == "SETTINGS":
            await settings_menu_loop()



async def main():
    wifi_task = uasyncio.create_task(wifi_connect_install_mqtt(wlan, main_menu, history_menu))
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

