import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
import time

class Device:  # 부모 클래스 정의
    def __init__(self, did, pin):
        self.pin = pin
        self.did = did

    def get_pin(self):
        return self.pin

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
        super().__init__(did, pin)
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, 1000)
        self.pwm.start(0)
        self.current_brightness = 0

    def _gradual_change(self, target_brightness, duration=1):
        step_duration = 0.01
        step = (target_brightness - self.current_brightness) / (duration / step_duration)
        for _ in range(int(duration / step_duration)):
            self.current_brightness += step
            # 현재 밝기를 반올림하여 처리
            adjusted_brightness = round(max(0, min(100, self.current_brightness)), 4)
            self.pwm.ChangeDutyCycle(adjusted_brightness)
            time.sleep(step_duration)

        # 현재 밝기가 매우 낮은 경우 명확하게 0으로 설정
        if abs(self.current_brightness) < 0.0001:
            self.current_brightness = 0
            self.pwm.ChangeDutyCycle(0)

    def set(self, brightness):
        # brightness 값이 유효한 범위 내에 있는지 확인
        if 0 <= brightness <= 100:
            def operation():
                self._gradual_change(brightness)

            success_message = f"Set brightness of {self.did} to {brightness}%"
            error_message_prefix = "Error changing brightness"
            return Device.execute_operation(operation, 
                                            success_message=success_message, 
                                            error_message_prefix=error_message_prefix)
        else:
            # brightness 값이 유효 범위를 벗어나면 실패 메시지 반환
            return "fail", "Brightness value must be between 0 and 100"
    
    
class CTN(Device):  # Device 클래스 상속
    
    def __init__(self, did, pin):
        super().__init__(did, pin)  
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
        
def sys_setup():
    # GPIO 모드 설정
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
def sys_end():
    GPIO.cleanup()