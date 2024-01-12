import RPi.GPIO as GPIO
import time

class Device:  # 부모 클래스 정의
    def __init__(self, did, pin):
        self.pin = pin
        self.did = did

    def get_pin(self):
        return self.pin

    def get_DID(self):
        return self.did

    def get_control_topic(self):
        return f"control/{self.get_DID()}"
    
    def get_check_topic(self):
        return f"check/{self.get_DID()}"
    
    def get_response_topic(self):
        return f"response/{self.get_DID()}"

class LED(Device):  # Device 클래스 상속
    def __init__(self, did, pin):
        super().__init__(did, pin)  # 부모 클래스의 생성자 호출
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, 1000)  # 1000Hz의 주파수로 PWM 설정
        self.pwm.start(0)  # 초기 밝기를 0%로 설정

    def turn_on(self):
        self.pwm.ChangeDutyCycle(100)  # 밝기를 100%로 설정

    def turn_off(self):
        self.pwm.ChangeDutyCycle(0)  # 밝기를 0%로 설정

    def set_brightness(self, brightness):
        if 0 <= brightness <= 100:
            self.pwm.ChangeDutyCycle(brightness)  # 밝기 조절
        else:
            print("Invalid brightness: Enter a value between 0 and 100")
    
    
class CTN(Device):  # Device 클래스 상속
    
    def __init__(self, did, pin, freq):
        super().__init__(did, pin)  # 부모 클래스의 생성자 호출
        self.freq = freq
        GPIO.setup(self.pin, GPIO.OUT)  
        self.pwm = GPIO.PWM(self.pin, self.freq)
    ## 인스턴스 생성시 자동으로 핀, freq 설정
    
    def angle_to_percent(self, angle):
            if angle > 180 or angle < 0:
                return False
            start = 4
            end = 12.5
            ratio = (end - start) / 180
            angle_as_percent = angle * ratio
            return start + angle_as_percent
    ## 회전각 계산
    
    def turn_on(self):
        for angle in [0, 90, 180]:  # 0도, 90도, 180도 각도에 대해
            self.pwm.start(self.angle_to_percent(angle))  # 해당 각도에 대한 duty cycle 설정
            time.sleep(1)  # 1초 동안 유지
        self.pwm.stop()  # PWM 정지
    ## 동작
    
def sys_setup():
        # GPIO 모드 설정
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)