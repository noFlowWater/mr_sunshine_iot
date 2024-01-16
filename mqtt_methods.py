from handle_topic import *

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
    print(f"Received message: {payload}")

    for device_id, device in devices.items():
        
        check_topic = device.get_check_topic()
        response_topic = device.get_response_topic()
        control_topic = device.get_control_topic()

        if msg.topic == check_topic:
            check(client, device, response_topic)
            return
        elif msg.topic == control_topic:
            control(device, payload, device_id)
            return
                
