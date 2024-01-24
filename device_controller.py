import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
from smbus2 import SMBus
import time

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
        steps = int(512 / 360 * abs_degree)

        def operation():
            self.motor.motor_run(self.pin, .001, steps, not counterclockwise, False, "half", .05)

        success_message = f"Motor run successful. Degree: {degree}, Steps: {steps}, Counterclockwise: {str(not counterclockwise)}"
        error_message_prefix = "Error in running motor"
        return Device.execute_operation(operation, 
                                        success_message=success_message, 
                                        error_message_prefix=error_message_prefix)

    def stop(self):
        return Device.execute_operation(self.motor.motor_stop, 
                                        success_message="Motor stop successful.", 
                                        error_message_prefix="Error in stopping motor")
        
class SEN(Device):  # Light sensor class
    def __init__(self, did, i2c_ch, bh1750_dev_addr, mode):
        super().__init__(did)
        self.i2c_ch = i2c_ch
        self.bh1750_dev_addr = bh1750_dev_addr
        self.mode = int(mode, 16)
        self.bh1750_dev_addr = int(bh1750_dev_addr, 16)
        self.i2c = SMBus(self.i2c_ch)

    def read_light(self):
        try:
            luxBytes = self.i2c.read_i2c_block_data(self.bh1750_dev_addr, self.mode, 2)
            lux = int.from_bytes(luxBytes, byteorder='big')
            return lux
        except Exception as e:
            print("Error reading from sensor:", e)
            return None

    def cleanup(self):
        self.i2c.close()
        
def sys_setup():
    # Setting GPIO Mode
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
def sys_end():
    GPIO.cleanup()