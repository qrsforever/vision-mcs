#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file const.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-03-10 17:21


from enum import IntEnum


class StereoPos(IntEnum):
    L = 1
    R = 2


class CameraModel(IntEnum):
    PINHOLE = 1
    PINHOLE_RADTAN = 2
    FISHEYE = 3
