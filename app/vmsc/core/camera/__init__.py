#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __init__.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-02-27 21:54


import numpy as np
from models import PinHoleModel, FishEyeModel, PinHoleRadTanModel
from pose import CameraPose


class Camera(object):
    """
    """

    def __init__(self, name, intrinsics, extrinsics):
        self.name = name
        if intrinsics['type'] == 'KannalaBrandt':
            self.model = FishEyeModel(lazy=True)
            dist_keys = ['k1', 'k2', 'k3', 'k4']
        elif intrinsics['type'] == 'Pinhole':
            self.model = PinHoleModel(lazy=True)
            dist_keys = []
        elif intrinsics['type'] == 'PinholeRadTan':
            self.model = PinHoleRadTanModel(lazy=True)
            dist_keys = ['k1', 'k2', 'p1', 'p2']
        intrinsics = intrinsics['parameters']
        self.image_size = intrinsics['image_size']
        self.K = np.array(
                [
                    [intrinsics['fx'] , 0                , intrinsics['cx']] , 
                    [0                , intrinsics['fy'] , intrinsics['cy']] , 
                    [0                , 0                , 1]
                ])
        self.D = np.array([intrinsics[k] for k in dist_keys])
        self.pose = CameraPose.from_axis_angle(extrinsics['axis_angle'], extrinsics['translation'])

    def __str__(self):
        return f'{self.name}:\n K = {self.K}\n D = {self.D}\n Pose: {self.pose}'
