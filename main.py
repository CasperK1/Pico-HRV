import uasyncio
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from src.utils import RotaryEncoder, SSD1306Wrapper, load_config
from src.menus import MainMenu, MeasureHRMenu, HRVAnalysisMenu, HistoryMenu, SettingsMenu, KubiosMenu
from src.wifi import PicoConnection
import micropython
# Config
micropython.alloc_emergency_exception_buf(200)
config = load_config()
# Initialize hardware
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306Wrapper(SSD1306_I2C(oled_width, oled_height, i2c))

rot = RotaryEncoder(10, 11, 12)
pico_conn = PicoConnection(
    config["ssid"],
    config["password"],
    config["mqtt_broker_ip"],
    config["mqtt_port"],
    config["wifi_timeout"],
)
# Menu instances
main_menu = MainMenu(oled, pico_conn, ["MEASURE HR", "HRV ANALYSIS", "KUBIOS", "HISTORY", "SETTINGS"], rot)
measure_hr_menu = MeasureHRMenu(oled, pico_conn, rot)
hrv_analysis_menu = HRVAnalysisMenu(oled, pico_conn, rot)
history_menu = HistoryMenu(oled, pico_conn, ["Back"], rot)
settings_menu = SettingsMenu(oled, pico_conn ,["WiFi", "Brightness", "Back"], rot)
kubios_menu = KubiosMenu(oled, pico_conn, rot)
menus = (main_menu, measure_hr_menu, hrv_analysis_menu, history_menu, settings_menu, kubios_menu)
pico_conn.menus = menus

async def menu_manager():
    current_menu = "MAIN"
    while True:
        if current_menu == "MAIN":
            current_menu = await main_menu.handle_input()
        elif current_menu == "MEASURE HR":
            current_menu = await measure_hr_menu.handle_input()
        elif current_menu == "HRV ANALYSIS":
            current_menu = await hrv_analysis_menu.handle_input()
        elif current_menu == "HISTORY":
            current_menu = await history_menu.handle_input()
        elif current_menu == "SETTINGS":
            current_menu = await settings_menu.handle_input()
        elif current_menu == "KUBIOS":
            current_menu = await kubios_menu.handle_input()

async def main():
    # Create tasks for connection management and menu handling
    connection_task = uasyncio.create_task(pico_conn.check_connection())
    menu_task = uasyncio.create_task(menu_manager())

    await uasyncio.gather(connection_task, menu_task)


if __name__ == '__main__':
    try:
        uasyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted")