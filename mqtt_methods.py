from handle_topic import *
import json

devices = None

def set_devices(devs):
    global devices
    devices = devs

def on_connect(client, userdata, flags, rc):
    # 여러 토픽 구독
    for device_id, device in devices.items():  # 디바이스 객체에 직접 접근
        client.subscribe(device.get_check_topic())
        client.subscribe(device.get_control_topic())
        print("Subscribed to check & control topic for device:", device_id)
        
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(f"<< Received message: {payload}")

    for _, device in devices.items():
        
        check_topic = device.get_check_topic()
        response_topic = device.get_response_topic()
        control_topic = device.get_control_topic()
        result_topic = device.get_result_topic()
        
        publish_topic = None
        result = None
        
        try:
            if msg.topic == check_topic:
                publish_topic = response_topic
                result = check(device)
            
            elif msg.topic == control_topic:
                publish_topic = result_topic
                message = json.loads(payload)
                result = control(device, message)
        
        except json.JSONDecodeError as e:
            error_message = f"Error parsing JSON: {e}"
            result = {"result": "fail", "message": error_message}
        except Exception as e:
            result = {"result": "fail", "message": str(e)}

        
        if publish_topic:
            print(">> Response message: ", result)
            client.publish(publish_topic, json.dumps(result))
            publish_topic = None
            return
    
        
