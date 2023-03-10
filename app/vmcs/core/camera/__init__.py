#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __init__.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-02-27 21:54


import numpy as np
from .pose import CameraPose
from vmcs.core.const import CameraModel

np.set_printoptions(suppress=True)


class CameraParam(object):
    """
    """
    def __init__(self, name, intrinsics, extrinsics):
        mtype = intrinsics['type']
        if mtype == 'KannalaBrandt':
            dist_keys = ['k1', 'k2', 'k3', 'k4']
            mtype = CameraModel.FISHEYE
        elif mtype == 'Pinhole':
            dist_keys = []
            mtype = CameraModel.PINHOLE
        elif mtype == 'PinholeRadTan':
            dist_keys = ['k1', 'k2', 'p1', 'p2']
            mtype = CameraModel.PINHOLE_RADTAN
        else:
            raise 'unkown type:[%s]' % intrinsics['type']
        self._name = name
        self.mtype = mtype
        intrinsics = intrinsics['parameters']
        self._image_size = intrinsics['image_size']
        self._K = np.array(
                [
                    [intrinsics['fx'] , 0                , intrinsics['cx']] ,
                    [0                , intrinsics['fy'] , intrinsics['cy']] ,
                    [0                , 0                , 1]
                ])
        self._D = np.array([intrinsics[k] for k in dist_keys])
        self._pose = CameraPose.from_axis_angle(extrinsics['axis_angle'], extrinsics['translation'])

    @property
    def name(self):
        return self._name

    @property
    def image_size(self):
        return self._image_size

    @property
    def w(self):
        return self._image_size[0]

    @property
    def h(self):
        return self._image_size[1]

    @property
    def K(self):
        return self._K

    @property
    def D(self):
        return self._D

    @property
    def r(self):
        return self._pose.r

    @property
    def t(self):
        return self._pose.t

    @property
    def fx(self):
        return self._K[0][0]

    @property
    def fy(self):
        return self._K[1][1]

    @property
    def cx(self):
        return self._K[0][2]

    @property
    def cy(self):
        return self._K[1][2]

    @property
    def pose_cam_world(self):
        return self._pose

    def __str__(self):
        s = '\n'
        s += '-' * 20 + '[' + self.name + f'({self.image_size})]' + '-' * 20
        s += f'\nK = {self.K}\nD = {self.D}\n{self.pose_cam_world}\n'
        return s


from .disparity import StereoPair

__all__ = [CameraParam, StereoPair]
