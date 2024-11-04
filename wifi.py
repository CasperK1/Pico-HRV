import network
from time import sleep, time
import uasyncio

ssid = 'Galaxy'
password = 'salasana1'
timeout = 10  # Timeout in seconds


async def wifi_connect():
    # Clean up the WLAN interface first
    wlan = network.WLAN(network.STA_IF)
    wlan.deinit()

    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print('Waiting for connection...')

    start_time = time()
    try:
        while not wlan.isconnected():
            if time() - start_time > timeout:
                wlan.deinit()  # Clean up
                print("Connection timed out.")
                return
            await uasyncio.sleep_ms(100)  
    except KeyboardInterrupt:
        print("Connection aborted.")
        wlan.deinit()
        return

    print(f"Connected to SSID: {ssid} IP: {wlan.ifconfig()[0]}")
    return
