from device_controller import *
import json

def check(client, device, response_topic):
    print(f"Received check message on {device.get_check_topic()}")
    response = {
        "device_status": "connected"
    }
    client.publish(response_topic, json.dumps(response))
    print("Response sent on", response_topic)
    

def control(device, payload, device_id):
    try:
        message = json.loads(payload)
        device_value = message.get("device_value")

        if isinstance(device, LED):
            device.set_brightness(device_value)
        else:
            print(f"Device {device_id} is not an LED")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        pass
