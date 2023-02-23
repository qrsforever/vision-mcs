#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file photoelectrici_trigger_cammera_led.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-02-15 16:18


import RPi.GPIO as GPIO
import cv2
import time
from Camera import Camera

# 光电
PIN_PHOTO_ELE = 5
# 频闪
PIN_FLASH_LED = 6

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(PIN_PHOTO_ELE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_FLASH_LED, GPIO.OUT)

# 频闪时
led_pwm = GPIO.PWM(PIN_FLASH_LED, 400)

if led_pwm is not None:
    led_pwm.start(0)

camera = None
wintitle = 'freqflash'
video_index = 0
frame_count = 0
frame_take = None


if __name__ == "__main__":
    try:
        camera = Camera(video_index, (640, 480))
        camera.parse_ctrls()
        camera.info()
        camera.open()
        frame_take = camera.read()[1]

        cv2.namedWindow(wintitle)
        wintitle = 'test'
        cv2.namedWindow(wintitle)
        for key, args in camera.properties.items():
            cv2.createTrackbar(key, wintitle, args['value'], args['max'], lambda v, k=key: camera.set(k, v))
            cv2.setTrackbarMin(key, wintitle, args['min'])

        GPIO.setup(PIN_PHOTO_ELE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        def _mycallback(channel):
            global frame_count, frame_take
            if channel == PIN_PHOTO_ELE:
                if led_pwm is not None:
                    led_pwm.ChangeDutyCycle(25)
                GPIO.output(PIN_FLASH_LED, GPIO.HIGH)
                time.sleep(0.2)
                ret, frame = camera.read()
                if ret:
                    frame_take = frame
                frame_count += 1
                GPIO.output(PIN_FLASH_LED, GPIO.LOW)
                if led_pwm is not None:
                    led_pwm.ChangeDutyCycle(0)

        GPIO.add_event_detect(PIN_PHOTO_ELE, GPIO.FALLING, callback=_mycallback, bouncetime=500)

        while True:
            cv2.putText(frame_take, '%d' % frame_count,
                        (100, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2, (0, 0, 0), 2)
            cv2.imshow(wintitle, frame_take)
            key = cv2.waitKey(200)
            if key & 0xFF == ord('q') or key & 0xFF == 27:
                break

    except KeyboardInterrupt:
        pass
    finally:
        if led_pwm is not None:
            led_pwm.stop()
        GPIO.cleanup()
        camera.close()
        cv2.destroyAllWindows()
