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
# 继电器
PIN_RELAY_LAM = 19

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(PIN_PHOTO_ELE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_RELAY_LAM, GPIO.OUT)
GPIO.output(PIN_RELAY_LAM, GPIO.LOW)

wintitle = 'camera'
camera = None
video_index = 2
frame_count = 0
frame_take = None


def _on_change_brightness(val):
    print(val)
    camera.set(cv2.CAP_PROP_BRIGHTNESS, val)


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

        def _trigger_callback(channel):
            global frame_count, frame_take
            if channel == PIN_PHOTO_ELE:
                GPIO.output(PIN_RELAY_LAM, GPIO.HIGH)
                time.sleep(0.2)
                ret, frame = camera.read()
                if ret:
                    frame_take = frame
                frame_count += 1
                GPIO.output(PIN_RELAY_LAM, GPIO.LOW)

        GPIO.add_event_detect(PIN_PHOTO_ELE, GPIO.FALLING, callback=_trigger_callback, bouncetime=500)

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
        GPIO.cleanup()
        camera.close()
        cv2.destroyAllWindows()
