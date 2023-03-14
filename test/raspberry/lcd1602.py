#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file LCD1602.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-02-13 21:04


import socket
import uuid
import time
from subprocess import check_output
from RPLCD.i2c import CharLCD


def get_ip():
    val = '0.0.0.0'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        val = s.getsockname()[0]
    except:
        cmd = "hostname -I | cut -d\' \' -f1"
        val = check_output(cmd, shell=True).decode("utf-8").strip()
    finally:
        s.close()
    return val


def get_mac():
    node = uuid.getnode()
    return uuid.UUID(int=node).hex[-12:]

lcd = CharLCD('PCF8574', 0x27, auto_linebreaks=False)
lcd.clear()

while True:
    lcd_line_1 = "IP:" + get_ip()
    lcd_line_2 = "Mac:" + get_mac()

    lcd.home()
    lcd.write_string(f'{lcd_line_1}\r\n{lcd_line_2}')
    time.sleep(10)
