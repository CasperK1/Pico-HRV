import network
import mip
from time import sleep, time
import uasyncio

ssid = 'Galaxy'
password = 'salasana1'
def connect_wlan():
    # Connecting to the group WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    count = 1
    # Attempt to connect once per second
    while wlan.isconnected() == False:
        print(count,  "Connecting... ")
        sleep(1)
        count += 1

    # Print the IP address of the Pico
    print("Connection successful. Pico IP:", wlan.ifconfig()[0])
connect_wlan()

