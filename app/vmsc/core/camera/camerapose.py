#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file camerapose.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-01-09 22:18

import numpy as np
import cv2


class CameraPose(object):
    '''
    '''

    @classmethod
    def from_axis_angle(cls, r, t):
        return CameraPose(cv2.Rodrigues(np.array(r))[0], np.array(t))

    def __init__(self, r, t):
        self.r = r
        self.t = t

    @property
    def I(self): # noqa: E743
        return CameraPose(self.r.T, - (self.r.T @ self.t))

    def __matmul__(self, other):
        return CameraPose(self.r @ other.r, self.r @ other.t + self.t)
