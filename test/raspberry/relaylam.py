#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file relaylam.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-03-16 11:07


import RPi.GPIO as GPIO
import time

# 继电器
PIN_RELAY_LAM = 19

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PIN_RELAY_LAM, GPIO.OUT)


def test_relaylam_open():
    GPIO.output(PIN_RELAY_LAM, GPIO.HIGH)


def test_relaylam_close():
    GPIO.output(PIN_RELAY_LAM, GPIO.LOW)


if __name__ == "__main__":
    test_relaylam_open()
    time.sleep(3)
    test_relaylam_close()
    GPIO.cleanup()
