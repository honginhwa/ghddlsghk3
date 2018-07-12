# -*- coding: utf-8 -*-
import numpy as np
import cv2
import time

import RPi.GPIO as GPIO

# 초음파 센서
pin_trigger = 17
pin_echo = 4

# 모터 상태
STOP  = 0
FORWARD  = 1
BACKWORD = 2

 
# 모터 채널
CH1 = 0
CH2 = 1
 
# PIN 입출력 설정
OUTPUT = 1
INPUT = 0
 
# PIN 설정
HIGH = 1
LOW = 0
 
# 실제 핀 정의
#PWM PIN
ENA = 26  #37 pin
ENB = 0   #27 pin
 
#GPIO PIN
IN1 = 19  #37 pin
IN2 = 13  #35 pin
IN3 = 6   #31 pin
IN4 = 5   #29 pin

# 초음파센서 측정함수
def signal():    
    GPIO.output(pin_trigger, GPIO.HIGH) #shoot the signal for 10us
    time.sleep(.00001)
    GPIO.output(pin_trigger, GPIO.LOW)
    # waiting for the return signal
    while GPIO.input(pin_echo)==GPIO.LOW :
        pass
    start=time.time()

    # receiving signal
    while GPIO.input(pin_echo)==GPIO.HIGH :
        pass
    stop=time.time()

    d=(stop-start)*170*100 #cm, speed of sound 34m/s in air, d=340/2
    print(format(d,".2f")+"cm")

    time.sleep(.5)
    
    return d

# 핀 설정 함수
def setPinConfig(EN, INA, INB):        
    GPIO.setup(EN, GPIO.OUT)
    GPIO.setup(INA, GPIO.OUT)
    GPIO.setup(INB, GPIO.OUT)
    # 100khz 로 PWM 동작 시킴 
    pwm = GPIO.PWM(EN, 100) 
    # 우선 PWM 멈춤.   
    pwm.start(0) 
    return pwm
 
# 모터 제어 함수
def setMotorContorl(pwm, INA, INB, speed, stat):
 
    #모터 속도 제어 PWM
    pwm.ChangeDutyCycle(speed)  
    
    if stat == FORWARD:
        GPIO.output(INA, HIGH)
        GPIO.output(INB, LOW)
        
    #뒤로
    elif stat == BACKWORD:
        GPIO.output(INA, LOW)
        GPIO.output(INB, HIGH)
        
    #정지
    elif stat == STOP:
        GPIO.output(INA, LOW)
        GPIO.output(INB, LOW)
 
        
# 모터 제어함수 간단하게 사용하기 위해 한번더 래핑(감쌈)
def setMotor(ch, speed, stat):
    if ch == CH1:
        #pwmA는 핀 설정 후 pwm 핸들을 리턴 받은 값이다.
        setMotorContorl(pwmA, IN1, IN2, speed, stat)
    else:
        #pwmB는 핀 설정 후 pwm 핸들을 리턴 받은 값이다.
        setMotorContorl(pwmB, IN3, IN4, speed, stat)

# GPIO 모드 설정 
GPIO.setmode(GPIO.BCM)
      
#모터 핀 설정
#핀 설정후 PWM 핸들 얻어옴 
pwmA = setPinConfig(ENA, IN1, IN2)
pwmB = setPinConfig(ENB, IN3, IN4)

font = cv2.FONT_HERSHEY_SIMPLEX

GPIO.setup(pin_trigger, GPIO.OUT) #trigger signal
GPIO.output(pin_trigger, GPIO.LOW)

GPIO.setup(pin_echo, GPIO.IN) #echo signal


def Detect() :
    tl_cascade = cv2.CascadeClassifier('TrafficLight.xml')
    info = ''
    
    try :
        cap = cv2. VideoCapture(0)
        
    except :
        print('False')
        return

    while True :
        ret, frame = cap.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Convert the HSV colorspace
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        tl=tl_cascade.detectMultiScale(gray, 1.3,5)

        cv2.putText(frame, info, (5, 15), font, 0.5, (255,0,255),1)
        
        # It is red
        lower1 = np.array([166,84,141])
        upper1 = np.array([186,255,255])
        
        # It is green
        lower2 = np.array([40,60,60])
        upper2 = np.array([90,255,255])
        
        if signal()<25 :
            setMotor(CH1, 80, STOP)
            setMotor(CH2, 80, STOP)
        else :    
            setMotor(CH1, 10, FORWARD)
            setMotor(CH2, 10, FORWARD)
                 
        for (x,y,w,h) in tl:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0),2)
            cv2.putText(frame, 'Detect', (x-5, y-5), font, 0.5, (255, 255, 0),2)
            
            #cropping the image
            cropping = hsv[x:x+w, y:y+h]
       
            # Threshold the HSV image to get red, green 
            mask1 = cv2.inRange(cropping, lower1, upper1)
            mask2 = cv2.inRange(cropping, lower2, upper2)
            
            if cv2.countNonZero(mask1)>(1*1) :
                print('RED!!')
                cv2.putText(frame, 'Red', (x+10, y+10), font, 0.5, (200, 10, 255),2)
                setMotor(CH1, 80, STOP)
                setMotor(CH2, 80, STOP)                    
                    
            if cv2.countNonZero(mask2)>(1*1) :
                print('GREEN!!')
                cv2.putText(frame, 'Green', (x+10, y+10), font, 0.5, (94, 140, 49),2)
                if signal()<25 :
                    setMotor(CH1, 80, STOP)
                    setMotor(CH2, 80, STOP)
                else :    
                    setMotor(CH1, 10, FORWARD)
                    setMotor(CH2, 10, FORWARD)
                        
        cv2.imshow('I can detect', frame)
        key = cv2.waitKey(30)
        if key == 27 :
            GPIO.cleanup()
            break    
    cap.release()      
    cv2.destroyAllWindows()


Detect()
