import paho.mqtt.client as mqtt
from device_controller import * 
from mqtt_methods import *
from utils import *

config = load_config()

MQTT_BROKER = config["MQTT_BROKER"]
MQTT_PORT = config["MQTT_PORT"]
devices_config = config["DEVICES"]

if __name__ == '__main__':
    try:
        sys_setup()
        devices = {}
        
        # LED 장치 초기화
        for led_info in devices_config["LED"]:
            devices[led_info["DID"]] = LED(led_info["DID"], 
                                           led_info["PIN"])

        # CTN 장치 초기화
        for ctn_info in devices_config["CTN"]:
            devices[ctn_info["DID"]] = CTN(ctn_info["DID"], 
                                           ctn_info["PIN"])
            
        # SEN 장치 초기화
        for sen_info in devices_config["SEN"]:
            devices[sen_info["DID"]] = SEN(sen_info["DID"], 
                                           sen_info["I2C_CH"], 
                                           sen_info["BH1750_DEV_ADDR"], 
                                           config["CONT_H_RES_MODE"])


        # devices 전달
        set_devices(devices)

        client = mqtt.Client()
        
        # MQTT 콜백 함수 설정
        client.on_connect = on_connect
        client.on_message = on_message

        # MQTT 서버에 연결
        client.connect(host=MQTT_BROKER,port=MQTT_PORT)
        
        client.loop_forever()

    except (KeyboardInterrupt, SystemExit):
        print("Program terminated by user")
        sys_end()