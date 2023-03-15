#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file freqled.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-03-15 20:03


import time
import RPi.GPIO as GPIO

# 频闪
PIN_FLASH_LED = 6

g_led_pwm = None


def test_freqled_open(freq=300, duty=25):
    global g_led_pwm
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(PIN_FLASH_LED, GPIO.OUT)
    GPIO.output(PIN_FLASH_LED, GPIO.HIGH)

    # 频闪时
    g_led_pwm = GPIO.PWM(PIN_FLASH_LED, freq)
    g_led_pwm.start(duty)


def test_freqled_close():
    g_led_pwm.stop()
    GPIO.cleanup()


if __name__ == "__main__":
    test_freqled_open()
    time.sleep(5)
    test_freqled_close()
