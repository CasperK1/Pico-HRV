import network
import os
import mip
from time import sleep, time
import uasyncio

ssid = 'Galaxy'
password = 'salasana1'
timeout = 30  # Timeout in seconds

# Check if MQTT is installed, so installation is not attempted every time
def is_mqtt_installed():
    try:
        os.stat('lib/umqtt/simple.mpy')  
        return True
    except OSError:
        return False


async def wifi_connect_install_mqtt(wlan, main_menu, history_menu):
    mqtt_installed = is_mqtt_installed()

    while True:
        if wlan.isconnected():
            print(f"Connected to SSID: {ssid} Pico IP: {wlan.ifconfig()[0]} Checking connection status every 15 sec.")
            main_menu.wifi_conn = True
            history_menu.wifi_conn = True

            # Install MQTT
            if mqtt_installed == False:
                print("Installing MQTT. This will freeze the menu for a while...")
                try:
                    mip.install("umqtt.simple")
                    mqtt_installed = True
                except Exception as e:
                    print(f"Could not install MQTT: {e}")

            await uasyncio.sleep(15)  
            continue

        # Not connected, try to connect
        print('Attempting to connect to WLAN...')
        main_menu.wifi_conn = False
        history_menu.wifi_conn = False

        # Connect to WLAN
        wlan.active(True)
        wlan.connect(ssid, password)
        start_time = time()
        try:
            while not wlan.isconnected():
                if time() - start_time > timeout:
                    print("Connection attempt timed out.")
                    await uasyncio.sleep(5)  # Wait before next attempt
                    break
                await uasyncio.sleep_ms(100)

        except Exception as e:
            print("Connection error: ", e)            
            await uasyncio.sleep(5)  # Wait before next attempt
            continue

        if wlan.isconnected():
            print(f"Connected to SSID: {ssid} Pico IP: {wlan.ifconfig()[0]} Checking connection status every 15 sec.")
            main_menu.wifi_conn = True
            history_menu.wifi_conn = True

        await uasyncio.sleep(1)
