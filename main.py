import paho.mqtt.client as mqtt
from control_device import * 
from mqtt_methods import *

LED_DID = "L001"
CTN_DID = "C001"

LED_PIN = 17 
CTN_PIN = 18

# MQTT 브로커 설정
MQTT_BROKER = "192.168.203.116" # 근찬 IP
# MQTT_BROKER = "192.168.203.118" # 내 맥북IP
MQTT_PORT = 1883

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