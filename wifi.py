import network
from time import sleep, time
import uasyncio

ssid = 'Galaxy'
password = 'salasana1'
timeout = 30  # Timeout in seconds


async def wifi_connect(main_menu):
    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print('Waiting for connection...')

    start_time = time()
    try:
        while wlan.isconnected() == False:
            if time() - start_time > timeout:
                wlan.deinit()  # Clean up WLAN interface
                print("Connection timed out.")
                return False
            await uasyncio.sleep_ms(100)  
            
    except KeyboardInterrupt:
        print("Connection aborted.")
        wlan.deinit()
        return False
    
    except Exception as e:
        print("Error: ", e)
        wlan.deinit()
        return False

    print(f"Connected to SSID: {ssid} IP: {wlan.ifconfig()[0]}")
    main_menu.wifi_conn = True
    return True
