#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file pin.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-02-14 18:01


import RPi.GPIO as GPIO
import time

PIN = 5
GPIO.setmode(GPIO.BCM)

if __name__=="__main__":
    try:
        GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # method: 1
        # while True:
        #     print(GPIO.input(PIN))
        #     time.sleep(1)

        # method: 2 
        # while True:
        #     GPIO.wait_for_edge(PIN, GPIO.FAILING)
        #     print(GPIO.input(PIN))

        # method: 3
        def _mycallback(channel):
            if channel == PIN:
                print(GPIO.input(PIN))
        
        GPIO.add_event_detect(PIN, GPIO.FALLING, callback= _mycallback, bouncetime=500)
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
