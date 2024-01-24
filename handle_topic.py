from device_controller import *


def check(device):
    print(f"Received check message on {device.get_check_topic()}")
    result = {
        "device_status": "connected"
    }
    return result
    
def control(device, message):
    try:
        device_value = message.get("device_value")
        target_did = device.get_DID()
        result = {
            "target_device": target_did,
            "control_value": device_value,
            "result": "fail",
            "message": None
        }
        
        # Processing of LEDs and CTN devices
        if isinstance(device, (LED, CTN)):
            result["result"], result["message"] = device.set(device_value)
        else:
            result["message"] = f"Device {target_did} is not valid"

    except Exception as e:
        result["message"] = str(e)

    return result