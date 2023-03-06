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
from .matcher import StereoMatcherSGBM
from .pose import CameraPose
from enum import IntEnum

np.set_printoptions(suppress=True)


class StereoPos(IntEnum):
    L = 1
    R = 2


class CameraModel(IntEnum):
    PINHOLE = 1
    PINHOLE_RADTAN = 2
    FISHEYE = 3


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
    def pose_cam_world(self):
        return self._pose

    def __str__(self):
        s = '\n'
        s += '-' * 20 + '[' + self.name + f'({self.image_size})]' + '-' * 20
        s += f'\nK = {self.K}\nD = {self.D}\n{self.pose_cam_world}\n'
        return s


class StereoPair(object):
    """
    """
    lazy = False

    def __init__(self, cam1:CameraParam, cam2:CameraParam):
        assert cam1.mtype == cam2.mtype, f'{cam1.mtype} vs {cam2.mtype}'
        assert cam1.image_size == cam2.image_size, '{cam1.image_size} vs {cam2.image_size}'

        if cam1.mtype == CameraModel.FISHEYE:
            self.model = FishEyeModel(self.lazy)
        elif cam1.mtype == CameraModel.PINHOLE:
            self.model = PinHoleModel(self.lazy)
        elif cam1.mtype == CameraModel.PINHOLE_RADTAN:
            self.model = PinHoleRadTanModel(self.lazy)

        self._pose_cam2_cam1 = None
        self.cam1, self.cam2 = cam1, cam2
        self._R1, self._R2, self._P1, self._P2, self._Q, \
                self._map1, self._map2 = self.stereo_rectify(cam1, cam2)

    @property
    def pose_r(self):
        return self._pose_cam2_cam1.r

    @property
    def pose_t(self):
        return self._pose_cam2_cam1.t

    def R(self, pos:StereoPos):
        return self._R1 if pos == StereoPos.L else self._R2

    def P(self, pos:StereoPos):
        return self._P1 if pos == StereoPos.L else self._P2

    @property
    def R1(self):
        return self._R1
    
    @property
    def R2(self):
        return self._R2

    @property
    def P1(self):
        return self._P1

    @property
    def P2(self):
        return self._P2

    @property
    def Q(self):
        return self._Q

    @property
    def pose_cam2_cam1(self):
        return self._pose_cam2_cam1

    @property
    def pose_rect_cam(self):
        return CameraPose(self._R1, np.zeros(3))

    def get_rect_map(self, pos:StereoPos):
        return self._map1 if pos == StereoPos.L else self._map2

    def stereo_rectify(self, cam1, cam2):
        # transforms points from the cam1 frame to the cam2 frame
        self._pose_cam2_cam1 = cam2.pose_cam_world @ cam1.pose_cam_world.I
        image_size = cam1.image_size
        R1, R2, P1, P2, Q = self.model.stereo_rectify(
                cam1.K, cam1.D, cam2.K, cam2.D, image_size,
                self._pose_cam2_cam1.r, self._pose_cam2_cam1.t, flags=cv2.CALIB_ZERO_DISPARITY)

        mapx1, mapy1 = self.model.undistort_rectify_map(cam1.K, cam1.D, R1, P1, image_size, cv2.CV_32F)
        mapx2, mapy2 = self.model.undistort_rectify_map(cam2.K, cam2.D, R2, P2, image_size, cv2.CV_32F)
        return R1, R2, P1, P2, Q, (mapx1, mapy1), (mapx2, mapy2)

    def stereo_disparity(self, img1, img2):
        if isinstance(img1, str):
            img1 = cv2.imread(img1)
        if isinstance(img2, str):
            img2 = cv2.imread(img2)
        rect_img1 = cv2.remap(img1, *self._map1, cv2.INTER_LANCZOS4)
        rect_img2 = cv2.remap(img2, *self._map2, cv2.INTER_LANCZOS4)

        # TODO
        # 对图片进行特征sift或者其他方式，计算出合理的matcher参数
        # 结合统计的方法，筛选出

        matcher = StereoMatcherSGBM()
        return rect_img1, rect_img2, matcher, matcher.match(rect_img1, rect_img2)

    def __str__(self):
        s = '\n'
        s += '-' * 20 + '[' + self.cam1.name + ',' + self.cam2.name + ']' + '-' * 20
        s += f'\nR = {self.pose_r}\nT = {self.pose_t}'
        s += f'\nR1 = {self._R1}\nR2 = {self._R2}'
        s += f'\nP1 = {self._P1}\nP2 = {self._P2}'
        s += f'\nQ = {self._Q}'
        return s
