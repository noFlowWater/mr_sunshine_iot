import paho.mqtt.client as mqtt
from device_controller import * 
from mqtt_methods import *
from utils import *

if __name__ == '__main__':
    try:
        config = load_config()
        client = mqtt.Client() 
        
        devices = initialize_devices(client, config)
        
        client.user_data_set({'devices': devices})

        # MQTT Callback Function Settings
        client.on_connect = on_connect
        client.on_message = on_message

        # Connecting to MQTT Server
        client.connect(host=config["MQTT_BROKER"],port=config["MQTT_PORT"])
        
        client.loop_forever()

    except (KeyboardInterrupt, SystemExit):
        print("Program terminated by user")
        sys_end(devices)
        
        
