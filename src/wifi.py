import os
import mip
import network
from time import sleep, time
import uasyncio
from lib.umqtt.simple import MQTTClient
import json

# TODO: REMOVE MQTT DEBUG PRINTS FROM FINAL VERSION

class PicoConnection:
    def __init__(self, ssid, password, broker_ip, broker_port, timeout, menus=[]):
        self.wlan = network.WLAN(network.STA_IF)
        self.ssid = ssid
        self.password = password
        self.broker_ip = broker_ip
        self.broker_port = broker_port  
        self.mqtt_topic = "hr-data"
        self.kubios_request_topic = "kubios-request"
        self.kubios_response_topic = "kubios-response"
        self.menus = menus
        self.connected = False
        self.mqtt_client = None
        self.timeout = timeout
        self.latest_kubios_response = None


    async def connect(self):
        self.wlan.active(True)
        self.wlan.connect(self.ssid, self.password)
        start_time = time()
        try:
            while self.wlan.isconnected() == False:
                if time() - start_time > self.timeout:
                    print("Connection attempt timed out.")
                    await uasyncio.sleep(5)  # Wait before next attempt
                    break
                await uasyncio.sleep_ms(100)
        except Exception as e:
            print("Connection error: ", e)
            await uasyncio.sleep(5)  # Wait before next attempt

        await uasyncio.sleep(1)

    async def check_connection(self):
        while True:
            if self.wlan.isconnected():
                # print(f"Connected to SSID: {self.ssid} Pico IP: {self.wlan.ifconfig()[0]}")
                self.connected = True
                self.menu_conn_status(True)      
                await uasyncio.sleep(15)
                continue
            else:
                # print('Attempting to connect to WLAN...')
                self.connected = False
                self.menu_conn_status(False)
                await self.connect()

    def menu_conn_status(self, boolean):
        for menu in self.menus:
            menu.wifi_conn = boolean

    def set_mqtt_callback(self, topic, msg):
        """Set callback for MQTT messages"""
        if self.mqtt_client and topic == self.kubios_response_topic.encode():
            self.latest_kubios_response = json.loads(msg.decode())

    
    async def connect_mqtt(self):
        try:
            self.mqtt_client = MQTTClient(
                "pico", self.broker_ip, port=self.broker_port)
            self.mqtt_client.set_callback(self.set_mqtt_callback)
            self.mqtt_client.connect(clean_session=True)
            # Subscribe to Kubios response topic
            self.mqtt_client.subscribe(self.kubios_response_topic.encode())
            print(f"Connected to MQTT broker. Subscribed to topic: {self.kubios_response_topic}")

        except Exception as e:
            print(f"Failed to connect to MQTT: {e}")
            self.mqtt_client = None

    async def mqtt_publish(self, message, topic=None):
        """Publish message to MQTT broker. If topic not specified, uses default topic."""
        if not self.mqtt_client:
            return False

        try:
            publish_topic = topic or self.mqtt_topic
            self.mqtt_client.publish(publish_topic.encode(), message)
            await uasyncio.sleep_ms(500)
            return True
        except Exception as e:
            print(f"Failed to send MQTT message: {e}")
            return False

