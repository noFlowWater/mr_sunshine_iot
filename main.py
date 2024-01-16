import paho.mqtt.client as mqtt
from device_controller import * 
from mqtt_methods import *
from utils import load_config, start_pigpiod, stop_pigpiod

config = load_config()

LED_DID_1 = config["LED_DID_1"]
LED_PIN_1 = config["LED_PIN_1"]

CTN_DID_1 = config["CTN_DID_1"]
CTN_PIN_1 = config["CTN_PIN_1"]

MQTT_BROKER = config["MQTT_BROKER"]
MQTT_PORT = config["MQTT_PORT"]

if __name__ == '__main__':
    
    try:
        start_pigpiod()  # pigpiod 시작
        sys_setup()
        led1 = LED(LED_DID_1, LED_PIN_1)
        ctn1 = CTN(CTN_DID_1, CTN_PIN_1)
        devices = {LED_DID_1: led1, CTN_DID_1: ctn1}

        # devices 전달
        set_devices(devices)

        client = mqtt.Client()
        
        # MQTT 콜백 함수 설정
        client.on_connect = on_connect
        client.on_message = on_message

        # MQTT 서버에 연결
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        client.loop_forever()

    except KeyboardInterrupt:
        print("Program terminated by user")
        ctn1.end()
        sys_end()
        stop_pigpiod()  # pigpiod 종료