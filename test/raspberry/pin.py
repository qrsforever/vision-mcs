#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file pin.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-02-14 18:01


import RPi.GPIO as GPIO
import time

PIN = 19
GPIO.setmode(GPIO.BCM)


if __name__ == "__main__":
    try:
        GPIO.setup(PIN, GPIO.OUT)
        GPIO.output(PIN, GPIO.HIGH)
        time.sleep(5)
        GPIO.output(PIN, GPIO.LOW)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()


# PIN = 5
# GPIO.setmode(GPIO.BCM)
#
# if __name__=="__main__":
#     try:
#         GPIO.setup(PIN, GPIO.IN) # pull_up_down=GPIO.PUD_UP)
#         while True:
#             print(GPIO.input(PIN))
#             time.sleep(1)
#
#     except KeyboardInterrupt:
#         pass
#     finally:
#         GPIO.cleanup()
