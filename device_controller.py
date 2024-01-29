import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
from utils import map_value
from smbus2 import SMBus
import threading
import time
import json

class Device:  # Defining a Parent Class
    def __init__(self, did):
        self.did = did

    def get_DID(self):
        return self.did
    
    def get_check_topic(self):
        return f"check/{self.get_DID()}"
    
    def get_response_topic(self):
        return f"response/{self.get_DID()}"

    def get_control_topic(self):
        return f"control/{self.get_DID()}"
    
    def get_result_topic(self):
        return f"result/{self.get_DID()}"
    
    @staticmethod
    def execute_operation(operation, *args, 
                          success_message="Operation successful", 
                          error_message_prefix="Error in operation"):
        try:
            operation(*args)
            return "success", success_message
        except Exception as e:
            return "fail", f"{error_message_prefix}: {e}"

class LED(Device):
    def __init__(self, did, pin):
        super().__init__(did)
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, 1000)
        self.pwm.start(0)
        self.current_brightness = 0

    def _gradual_change(self, target_brightness, duration=1):
        step_duration = 0.01
        step = (target_brightness - self.current_brightness) / (duration / step_duration)
        for _ in range(int(duration / step_duration)):
            self.current_brightness += step
            # Process by rounding the current brightness
            adjusted_brightness = round(max(0, min(100, self.current_brightness)), 4)
            self.pwm.ChangeDutyCycle(adjusted_brightness)
            time.sleep(step_duration)

        # Clearly set to 0 if the current brightness is very low
        if abs(self.current_brightness) < 0.0001:
            self.current_brightness = 0
            self.pwm.ChangeDutyCycle(0)

    def set(self, brightness):
        # Verify that brightness values are within a valid range
        if 0 <= brightness <= 100:
            def operation():
                self._gradual_change(brightness)

            success_message = f"Set brightness of {self.did} to {brightness}%"
            error_message_prefix = "Error changing brightness"
            return Device.execute_operation(operation, 
                                            success_message=success_message, 
                                            error_message_prefix=error_message_prefix)
        else:
            # Returns a failure message if the brightness value is outside the valid range
            return "fail", "Brightness value must be between 0 and 100"
    
    
class CTN(Device): # Device class inheritance

    def __init__(self, did, pin):
        super().__init__(did)  
        self.pin = pin
        self.motor = RpiMotorLib.BYJMotor(did, "28BYJ")
    
    def set(self, degree):
        counterclockwise = degree < 0
        abs_degree = abs(degree)
        
        # abs_degree를 0~1300 범위로 매핑
        mapped_degree = map_value(abs_degree, 0, 100, 0, 1300)
        
        # 매핑된 값으로 steps 계산
        steps = int(512 / 360 * mapped_degree)

        def operation():
            self.motor.motor_run(self.pin, .001, steps, counterclockwise, False, "half", .05)

        success_message = f"Motor run successful. Degree: {degree}, Steps: {steps}, Counterclockwise: {str(not counterclockwise)}"
        error_message_prefix = "Error in running motor"
        return Device.execute_operation(operation, 
                                        success_message=success_message, 
                                        error_message_prefix=error_message_prefix)


    def stop(self):
        return Device.execute_operation(self.motor.motor_stop, 
                                        success_message="Motor stop successful.", 
                                        error_message_prefix="Error in stopping motor")
        
class SEN(Device):
    def __init__(self, client, did, i2c_ch, bh1750_dev_addr, mode, interval = 10 ):
        super().__init__(did)
        self.client = client
        self.i2c_ch = i2c_ch
        self.bh1750_dev_addr = int(bh1750_dev_addr, 16)
        self.mode = int(mode, 16)
        self.i2c = SMBus(self.i2c_ch)
        self.interval = interval
        self.running = True
        self.thread = threading.Thread(target=self._periodic_read)
        self.thread.start()

    def _periodic_read(self): # Periodically call the read_light function
        while self.running:
            lux = self.read_light()
            if lux is not None:
                # lux 값을 0~100으로 매핑
                mapped_lux = map_value(lux, 0, 150, 0, 100)
                result = { "sensor_value": int(mapped_lux) }  # 정수형으로 변환하여 저장
                print(result)
                self.client.publish(self.get_sensor_topic(), json.dumps(result))
            time.sleep(self.interval)

    def read_light(self):
        try:
            luxBytes = self.i2c.read_i2c_block_data(self.bh1750_dev_addr, self.mode, 2)
            lux = int.from_bytes(luxBytes, byteorder='big')
            return lux
        except Exception as e:
            print("Error reading from sensor:", e)
            return None
        
    def get_sensor_topic(self):
        return f"sensor/{self.get_DID()}"

    def cleanup(self):
        self.running = False
        self.thread.join()
        self.i2c.close()
    
def initialize_devices(client, config):
    # Setting GPIO Mode
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    devices = {}
    devices_config = config["DEVICES"]

    # Initialize LED device
    for led_info in devices_config.get("LED", []):
        devices[led_info["DID"]] = LED(led_info["DID"], 
                                       led_info["PIN"])

    # Initialize CTN device
    for ctn_info in devices_config.get("CTN", []):
        devices[ctn_info["DID"]] = CTN(ctn_info["DID"], 
                                       ctn_info["PIN"])

    # Initialize SEN device
    for sen_info in devices_config.get("SEN", []):
        devices[sen_info["DID"]] = SEN(client, 
                                       sen_info["DID"], 
                                       sen_info["I2C_CH"], 
                                       sen_info["BH1750_DEV_ADDR"], 
                                       config["CONT_H_RES_MODE"])

    return devices
    
def sys_end(devices):
    for device in devices.values():
        if isinstance(device, SEN):
            device.cleanup()
    GPIO.cleanup()