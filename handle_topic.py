import json

def check(client, device, response_topic):
    print(f"Received check message on {device.get_check_topic()}")
    response = {
        "device_status": "connected"
    }
    client.publish(response_topic, json.dumps(response))
    print("Response sent on", response_topic)
    


def control(device, payload, device_id):
    message = json.loads(payload)
    action = message.get("action")

    if action == "turn_on":
        device.turn_on()
        print(f"Turned on {device_id}")
    elif action == "turn_off":
        device.turn_off()
        print(f"Turned off {device_id}")
    else:
        print(f"Unknown action: {action}")
