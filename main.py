import paho.mqtt.client as mqtt
from control_device import * 
from mqtt_methods import *
from config_loader import load_config

config = load_config()

LED_DID = config["LED_DID"]
CTN_DID = config["CTN_DID"]
LED_PIN = config["LED_PIN"]
CTN_PIN = config["CTN_PIN"]
MQTT_BROKER = config["MQTT_BROKER"]
MQTT_PORT = config["MQTT_PORT"]

if __name__ == '__main__':
    
    sys_setup()
    
    devices = {LED_DID: LED(LED_DID, LED_PIN), CTN_DID: CTN(CTN_DID, CTN_PIN, 50)}
    
    # devices 전달
    set_devices(devices)
    
    client = mqtt.Client()
    
    # MQTT 콜백 함수 설정
    client.on_connect = on_connect
    client.on_message = on_message

    # MQTT 서버에 연결
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
    client.loop_forever()