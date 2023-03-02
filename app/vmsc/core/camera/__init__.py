#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __init__.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-02-27 21:54


import numpy as np
import cv2
from .models import PinHoleModel, FishEyeModel, PinHoleRadTanModel
from .pose import CameraPose

np.set_printoptions(suppress=True)


class CameraParam(object):
    """
    """
    def __init__(self, name, intrinsics, extrinsics):
        mtype = intrinsics['type']
        if mtype == 'KannalaBrandt':
            dist_keys = ['k1', 'k2', 'k3', 'k4']
        elif mtype == 'Pinhole':
            dist_keys = []
        elif mtype == 'PinholeRadTan':
            dist_keys = ['k1', 'k2', 'p1', 'p2']
        else:
            raise 'unkown type:[%s]' % intrinsics['type']
        self.name = name
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
    def image_size(self):
        return self._image_size

    @property
    def K(self):
        return self._K

    @property
    def D(self):
        return self._D

    @property
    def pose(self):
        return self._pose

    def __str__(self):
        s = '\n'
        s += '-' * 20 + '[' + self.name + f'({self.image_size})]' + '-' * 20
        s += f'\nK = {self.K}\nD = {self.D}\n{self.pose}\n'
        return s


class CameraPair(object):
    """
    """
    lazy = False

    def __init__(self, cam1:CameraParam, cam2:CameraParam):
        assert cam1.mtype == cam2.mtype, f'{cam1.mtype} vs {cam2.mtype}'
        assert cam1.image_size == cam2.image_size, '{cam1.image_size} vs {cam2.image_size}'
        model = None
        if cam1.mtype == 'KannalaBrandt':
            model = FishEyeModel(self.lazy)
        elif cam1.mtype == 'Pinhole':
            model = PinHoleModel(self.lazy)
        elif cam1.mtype == 'PinholeRadTan':
            model = PinHoleRadTanModel(self.lazy)
        self.cam1, self.cam2 = cam1, cam2
        self.c_pose = cam2.pose @ cam1.pose.I  # pose difference between camera 1 and 2

        image_size = cam1.image_size
        R1, R2, P1, P2, Q = model.stereo_rectify(
                cam1.K, cam1.D, cam2.K, cam2.D, image_size,
                self.c_pose.r, self.c_pose.t, flags=cv2.CALIB_ZERO_DISPARITY)

        map1 = model.undistort_rectify_map(cam1.K, cam1.D, R1, P1, image_size, cv2.CV_32F)
        map2 = model.undistort_rectify_map(cam2.K, cam2.D, R2, P2, image_size, cv2.CV_32F)

        self._R1, self._P1, self._map1 = R1, P1, map1
        self._R2, self._P2, self._map2 = R2, P2, map2
        self._Q = Q

    @property
    def pose_r(self):
        return self.c_pose.r

    @property
    def pose_t(self):
        return self.c_pose.t

    def R(self, pos):
        return self._R1 if pos == 1 else self._R2

    def P(self, pos):
        return self._P1 if pos == 1 else self._P2

    @property
    def Q(self):
        return self._Q

    def rect_map(self, pos):
        return self._map1 if pos == 1 else self._map2

    def disparity(self, matcher):
        pass

    def __str__(self):
        s = '\n'
        s += '-' * 20 + '[' + self.cam1.name + ',' + self.cam2.name + ']' + '-' * 20
        s += f'\nR = {self.pose_r}\nT = {self.pose_t}'
        s += f'\nR1 = {self._R1}\nR2 = {self._R2}'
        s += f'\nP1 = {self._P1}\nP2 = {self._P2}'
        s += f'\nQ = {self._Q}'
        return s
