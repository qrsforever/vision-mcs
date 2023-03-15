#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file lcd1602.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-03-14 19:59

import time
import socket
import uuid
import smbus
from subprocess import check_output


BL = 0B00001000  # Backlight            0:off   1:on
EN = 0B00000100  # Enable bit
RW = 0B00000010  # Read/Write bit       0:write 1:read
RS = 0B00000001  # Register select bit  0:cmd   1:data

LCD_WIDTH = 16     # Maximum characters per line
LCD_LINE_1 = 0x80  # 10000000 LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # 11000000 LCD RAM address for the 2nd line

BUS = smbus.SMBus(0)  # /dev/i2c-0
LCD_ADDR = 0x27  # sudo i2cdetect -y -a 0


def get_ip():
    val = '0.0.0.0'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        val = s.getsockname()[0]
    except Exception:
        cmd = "hostname -I | cut -d\' \' -f1"
        val = check_output(cmd, shell=True).decode("utf-8").strip()
    finally:
        s.close()
    return val


def get_mac():
    node = uuid.getnode()
    return uuid.UUID(int=node).hex[-12:]


def main():
    init_lcd()
    while True:
        show_on_lcd(LCD_LINE_1, f'IP:{get_ip()}')
        show_on_lcd(LCD_LINE_2, f'ID:{get_mac()}')
        time.sleep(120)


def send_command(cmd):
    print(">>>", hex(cmd),"---", bin(cmd))
    '''
    BIT     D7  D6  D5  D4  D3  D2  D1  D0
            |   |   |   |   |   |   |   |
    LCD     D7  D6  D5  D4  BL  EN  RW  RS

    '''
    # High Bit
    buf = cmd & 0xF0 | BL | EN  # BL = 1, EN = 1, RW = 0, RS = 0
    BUS.write_byte(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB # 11111011 EN = 0
    BUS.write_byte(LCD_ADDR, buf)

    # Low Bit
    buf = ((cmd & 0x0F) << 4) | BL | EN  # BL = 1, EN = 1, RW = 0, RS = 0
    BUS.write_byte(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB
    BUS.write_byte(LCD_ADDR, buf)


def send_data(data):
    # Send bit7-4 firstly
    buf = data & 0xF0 | BL | EN | RS # BL = 1, EN = 1, RW = 0, RS = 1
    BUS.write_byte(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB
    BUS.write_byte(LCD_ADDR, buf)

    # Send bit3-0 secondly
    buf = ((data & 0x0F) << 4) | BL | EN | RS  # BL = 1, EN = 1, RW = 0, RS = 1
    BUS.write_byte(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB
    BUS.write_byte(LCD_ADDR, buf)


def init_lcd():
    send_command(0x33) # Must initialize to 8-line mode at first
    time.sleep(0.005)
    send_command(0x32) # Then initialize to 4-line mode
    time.sleep(0.005)
    send_command(0x06) # Cursor move direction
    time.sleep(0.005)
    send_command(0x0C) # ENable display without cursor
    time.sleep(0.005)
    send_command(0x28) # 2 Lines & 5*7 dots
    time.sleep(0.005)
    send_command(0x01) # Clear Screen
    time.sleep(0.005)


def clear_lcd():
    send_command(0x01) # Clear Screen


def show_on_lcd(line, message):
    message = message.ljust(LCD_WIDTH, " ")
    send_command(line)
    for i in range(LCD_WIDTH):
        send_data(ord(message[i]))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass
    finally:
        clear_lcd()
        show_on_lcd(LCD_LINE_1, 'Goodbye!')
        BUS.close()
