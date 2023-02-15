#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file hw481.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-02-14 17:27


import RPi.GPIO as GPIO
import time

PIN = 16
GPIO.setmode(GPIO.BCM)

if __name__=="__main__":
    try:
        GPIO.setup(PIN, GPIO.OUT)
        GPIO.output(PIN, GPIO.HIGH)
        while True:
            time.sleep(3)
    except KeyboardInterrupt:
        GPIO.cleanup()
