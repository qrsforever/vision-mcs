#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file eventele.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-03-15 20:18

import time
import RPi.GPIO as GPIO

# 光电
PIN_PHOTO_ELE = 5

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


def test_ele_event(callback):
    GPIO.setup(PIN_PHOTO_ELE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(PIN_PHOTO_ELE, GPIO.FALLING, callback=callback, bouncetime=500)


if __name__ == "__main__":
    def _cb(channel):
        print(channel)

    test_ele_event(_cb)
    time.sleep(10)
