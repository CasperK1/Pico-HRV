import network
from time import sleep, time
import json
from lib.umqtt.simple import MQTTClient

ssid = "KME759_GROUP_9"
password = "Mvh38deHJ&S3NGr"
broker_ip = "192.168.9.253"
broker_port = 21883

kubios_request_topic = "kubios-request".encode()
kubios_response_topic = "kubios-response".encode()
hrv_analysis_topic = "hr-data".encode()

# Kubios analysis request
kubios_request = {
    "id": 123,
    "type": "RRI",
    "data": [
        828, 836, 852, 760, 800, 796, 856, 824, 808, 776,
        724, 816, 800, 812, 812, 812, 756, 820, 812, 800
    ],
    "analysis": {"type": "readiness"}
}

# Heart rate history data
hr_data = {
    "id": 123,
    "time": int(time()), 
    "mean_hr": 78
}


def mqtt_callback(topic, msg):
    """Callback function to handle incoming MQTT messages"""
    if topic == kubios_response_topic:
        print(f"Received Kubios response: {msg.decode()}")
        try:
            response = json.loads(msg.decode())
            print("Parsed response:", json.dumps(response))
        except Exception as e:
            print(f"Error parsing response: {e}")


def connect_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print("Connecting... ")
        sleep(1)
    print("Connection successful. Pico IP:", wlan.ifconfig()[0])
    return wlan


def connect_mqtt():
    mqtt_client = MQTTClient("pico", broker_ip, port=broker_port)
    mqtt_client.set_callback(mqtt_callback)
    mqtt_client.connect(clean_session=True)
    mqtt_client.subscribe(kubios_response_topic)
    print(f"Subscribed to topic: {kubios_response_topic}")
    return mqtt_client


def main():
    connect_wlan()
    mqtt_client = None

    try:
        mqtt_client = connect_mqtt()

        # Send heart rate data. This is for HRV analysis menu option
        print("Sending HR data...")
        hr_json = json.dumps(hr_data)
        mqtt_client.publish(hrv_analysis_topic, hr_json)
        print(f"Sent HR data: {hr_json}")
        sleep(1)  

        # Send Kubios request
        print("Sending Kubios request...")
        kubios_json = json.dumps(kubios_request)
        mqtt_client.publish(kubios_request_topic, kubios_json)
        print(f"Sent Kubios request: {kubios_json}")

        print("Waiting for responses...")
        while True:
            mqtt_client.check_msg()
            sleep(1)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if mqtt_client:
            mqtt_client.disconnect()


if __name__ == "__main__":
    main()
