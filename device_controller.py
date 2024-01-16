import RPi.GPIO as GPIO
import pigpio

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
            print(f"Set brightness of {self.did} to {brightness}%")
        else:
            print("Invalid brightness: Enter a value between 0 and 100")
    
    
class CTN(Device):  # Device 클래스 상속
    
    def __init__(self, did, pin):
        super().__init__(did, pin)  # 부모 클래스의 생성자 호출
        self.pi = pigpio.pi()
    ## 인스턴스 생성시 자동으로 핀, freq 설정
    
    def setServoPos(self, degree):
        # 0~100 범위를 500~2200 범위로 변환
        pulse_width = ((degree / 100) * 1700) + 500
        self.pi.set_servo_pulsewidth(self.pin, pulse_width)
        
    def end(self):
        self.pi.stop()
        
def sys_setup():
    # GPIO 모드 설정
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
def sys_end():
    GPIO.cleanup()