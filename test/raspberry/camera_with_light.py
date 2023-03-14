#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file camera_with_light.py
# @brief
# @author QRS
# @blog qrsforever.gitee.io
# @version 1.0
# @date 2023-02-14 18:53

import RPi.GPIO as GPIO
import cv2
import os
from time import sleep

# PIN = 23 # 频闪
PIN = 22 # 爆闪
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PIN, GPIO.OUT)

if PIN == 23: # 频闪
    pwm_pin = GPIO.PWM(PIN, 100)
else:
    pwm_pin = GPIO.PWM(PIN, 100)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_EXPOSURE, 100)
print(cap.get(cv2.CAP_PROP_EXPOSURE))
print(cap.get(cv2.CAP_PROP_FPS))

if __name__ == "__main__":
    try:
        os.system('rm -f /tmp/*.png')
        while cap.isOpened():
            pwm_pin.start(25)
            GPIO.output(PIN, GPIO.HIGH)
            ret, frame = cap.read()
            if ret:
                cv2.imwrite('/tmp/pic.png', frame)
            pwm_pin.stop()
            GPIO.output(PIN, GPIO.LOW)
            break
    except KeyboardInterrupt:
        pass
    finally:
        sleep(3)
        pwm_pin.stop()
        GPIO.cleanup()
        cap.release()
