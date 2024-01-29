from handle_topic import check, control
import json
import threading

def on_connect(client, userdata, flags, rc):
    # Access devices from user_data
    devices = userdata['devices']
    
    # Subscribe to multiple topics
    for device_id, device in devices.items():  # Direct access to device objects
        client.subscribe(device.get_check_topic())
        client.subscribe(device.get_control_topic())
        print("Subscribed to check & control topic for device:", device_id)
        
def on_message(client, userdata, msg):
    # Access devices from user_data
    devices = userdata['devices']
    print("msg.topic: ",msg.topic)
    # print(devices)
    
    # Starts a thread that calls function each time a message arrives
    threading.Thread(target=process_mqtt_message, args=(client, msg, devices)).start()
    
        
def process_mqtt_message(client, msg, devices):
    payload = msg.payload.decode('utf-8')
    print(f"<< Received message: {payload}")
    
    publish_topic = None
    
    result = {"result": "fail", "message": None}

    for _, device in devices.items():
        check_topic = device.get_check_topic()
        response_topic = device.get_response_topic()
        control_topic = device.get_control_topic()
        result_topic = device.get_result_topic()
        
        try:
            if msg.topic == check_topic:
                
                publish_topic = response_topic
                result = check(device)
            
            elif msg.topic == control_topic:
                
                publish_topic = result_topic
                message = json.loads(payload)
                result = control(device, message)
        
        except json.JSONDecodeError as e:
            result["message"] = f"Error parsing JSON: {e}"
        except Exception as e:
            result["message"] = str(e)
            
        if publish_topic:
            print(">> Response message: ", result)
            client.publish(publish_topic, json.dumps(result))
            return
        
