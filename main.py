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
        
        # Initialize LED device
        for led_info in devices_config["LED"]:
            devices[led_info["DID"]] = LED(led_info["DID"], 
                                           led_info["PIN"])

        # Initialize CTN device
        for ctn_info in devices_config["CTN"]:
            devices[ctn_info["DID"]] = CTN(ctn_info["DID"], 
                                           ctn_info["PIN"])
            
        # Initialize SEN device
        for sen_info in devices_config["SEN"]:
            devices[sen_info["DID"]] = SEN(sen_info["DID"], 
                                           sen_info["I2C_CH"], 
                                           sen_info["BH1750_DEV_ADDR"], 
                                           config["CONT_H_RES_MODE"])

        # Delivering devices
        set_devices(devices)

        client = mqtt.Client()
        
        # MQTT Callback Function Settings
        client.on_connect = on_connect
        client.on_message = on_message

        # Connecting to MQTT Server
        client.connect(host=MQTT_BROKER,port=MQTT_PORT)
        
        client.loop_forever()

    except (KeyboardInterrupt, SystemExit):
        print("Program terminated by user")
        sys_end()