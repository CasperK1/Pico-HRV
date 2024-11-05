import os


def is_mqtt_installed():
    try:
        os.stat('lib/umqtt/simple.mpy')  # Try to get file stats
        return True
    except OSError:
        return False
    
    
print(is_mqtt_installed())