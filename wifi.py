import network
import os
import mip
from time import sleep, time
import uasyncio

ssid = 'Galaxy'
password = 'salasana1'
timeout = 15  # Timeout in seconds

def is_mqtt_installed():
    try:
        os.stat('lib/umqtt/simple.mpy')
        return True
    except OSError:
        return False

async def wifi_connect_install_mqtt(wlan, main_menu, history_menu, settings_menu):
    # Check if MQTT is installed, so installation is not attempted every time
    mqtt_installed = is_mqtt_installed()

    while True:
        if wlan.isconnected():
            print(f"Checking connection status every 10 sec.")
            main_menu.wifi_conn = True
            history_menu.wifi_conn = True
            settings_menu.wifi_conn = True

            # Install MQTT
            if mqtt_installed == False:
                print("Installing MQTT. This will freeze the menu for a while...")
                try:
                    mip.install("umqtt.simple")
                    mqtt_installed = True
                except Exception as e:
                    print(f"Could not install MQTT: {e}")

            await uasyncio.sleep(10)
            continue

        # Not connected, try to connect
        print('Attempting to connect to WLAN...')
        main_menu.wifi_conn = False
        history_menu.wifi_conn = False

        # Connect to WLAN
        wlan.active(True)
        await uasyncio.sleep_ms(100)
        wlan.connect(ssid, password)
        start_time = time()
        try:
            while wlan.isconnected() == False:
                if time() - start_time > timeout:
                    print("Connection attempt timed out.")
                    break
                await uasyncio.sleep_ms(100)

        except Exception as e:
            print("Connection error: ", e)
            await uasyncio.sleep(5)  # Wait before next attempt
            continue

        if wlan.isconnected():
            print(f"Connected to SSID: {ssid} Pico IP: {wlan.ifconfig()[0]}")
            main_menu.wifi_conn = True
            history_menu.wifi_conn = True

        await uasyncio.sleep(1)
