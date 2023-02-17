#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file photoelectrici_trigger_cammera_led.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-02-15 16:18


import RPi.GPIO as GPIO
import cv2
import os
import time

# 光电
PIN_PHOTO_ELE = 5
# 继电器
PIN_RELAY_LAM = 19

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(PIN_PHOTO_ELE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_RELAY_LAM, GPIO.OUT)

count = 0

if __name__ == "__main__":
    try:
        os.system('rm -f /home/pi/caps/*.png')
        cap = cv2.VideoCapture(2)
        if not cap.isOpened():
            raise

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc('M','J','P','G'))

        cap.set(cv2.CAP_PROP_BRIGHTNESS, 1)
        cap.set(cv2.CAP_PROP_CONTRAST,40)
        cap.set(cv2.CAP_PROP_SATURATION, 50)
        cap.set(cv2.CAP_PROP_HUE, 50)
        cap.set(cv2.CAP_PROP_AUTO_WB, 1)

        # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        cap.set(cv2.CAP_PROP_EXPOSURE, 120) # ms
        cap.set(cv2.CAP_PROP_GAIN, 60)

        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        print(cap.get(cv2.CAP_PROP_FPS))
        print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        print(cap.get(cv2.CAP_PROP_AUTO_EXPOSURE))
        print(cap.get(cv2.CAP_PROP_EXPOSURE))
        print(cap.get(cv2.CAP_PROP_GAIN))

        GPIO.setup(PIN_PHOTO_ELE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        def _mycallback(channel):
            global count
            if channel == PIN_PHOTO_ELE:
                print('Count: %d, Input: %d' % (count, GPIO.input(PIN_PHOTO_ELE)))
                GPIO.output(PIN_RELAY_LAM, GPIO.HIGH)
                time.sleep(0.2)
                cap.grab(); # noqa: remove old frames
                ret, frame = cap.read()
                if ret:
                    cv2.imwrite(f'/home/pi/caps/pic{count}.png', frame)
                count += 1
                GPIO.output(PIN_RELAY_LAM, GPIO.LOW)

        GPIO.add_event_detect(PIN_PHOTO_ELE, GPIO.FALLING, callback=_mycallback, bouncetime=500)

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        cap.release()
    finally:
        GPIO.cleanup()
