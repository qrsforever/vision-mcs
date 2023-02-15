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

PIN_PHOTO_ELE = 5
PIN_FLASH_LED = 6

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(PIN_PHOTO_ELE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_FLASH_LED, GPIO.OUT)

# 频闪时
led_pwm = GPIO.PWM(PIN_FLASH_LED, 120)
led_pwm.start(0)

count = 0

if __name__ == "__main__":
    try:
        os.system('rm -f /home/pi/*.png')
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise

        # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 2)
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        cap.set(cv2.CAP_PROP_EXPOSURE, 170) # ms

        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FPS, 60.0) # may be only 30
        print(cap.get(cv2.CAP_PROP_FPS))
        print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

        GPIO.setup(PIN_PHOTO_ELE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        def _mycallback(channel):
            global count
            if channel == PIN_PHOTO_ELE:
                print('Count: %d, Input: %d' % (count, GPIO.input(PIN_PHOTO_ELE)))
                led_pwm.ChangeDutyCycle(25)
                GPIO.output(PIN_FLASH_LED, GPIO.HIGH)
                cap.grab(); # noqa: remove old frames
                ret, frame = cap.read()
                if ret:
                    cv2.imwrite(f'/home/pi/pic{count}.png', frame)
                count += 1
                time.sleep(0.3)
                GPIO.output(PIN_FLASH_LED, GPIO.LOW)
                led_pwm.ChangeDutyCycle(0)

        GPIO.add_event_detect(PIN_PHOTO_ELE, GPIO.FALLING, callback=_mycallback, bouncetime=500)
        
        frames = []
        times = []
        while count < 5:
            ret, frame = cap.read()
            if ret:
                times.append(time.time())
                frames.append(frame)
        i = 0
        print('len = ', len(frames))
        for frame, t in zip(frames, times):
            cv2.putText(frame, '%f' % t,
                    (100, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 0), 1)
            cv2.imwrite(f'/home/pi/test{i}.png', frame)
            i += 1

        # while True:
        #     time.sleep(1)

    except KeyboardInterrupt:
        cap.release()
    finally:
        led_pwm.stop()
        GPIO.cleanup()
