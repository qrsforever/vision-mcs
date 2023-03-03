#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file mcs.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-01-09 22:29

import yaml
import cv2
import numpy as np
import os.path as osp

from vmsc.utils.logger import EasyLoggerMP as logger
from vmsc.core.camera import CameraParam, StereoPair, StereoPos

DEBUG_INFO = False
STEREO_MATCHER = 'SGBM'


class MultiCameraSystem(object):
    '''
    '''

    def __init__(self):
        self.cameras = {}
        self.camera_pairs = {}
        self.reference_camera = ''

    def load_and_init(self, yaml_path, pairs, reference_camera):
        with open(yaml_path, 'r') as f:
            self.calibration_parameters = yaml.load(f, Loader=yaml.FullLoader)

        # parse cameras
        for cam, params in self.calibration_parameters['sensors'].items():
            extrinsics = params['extrinsics']
            intrinsics = params['intrinsics']
            self.cameras[cam] = CameraParam(cam, intrinsics, extrinsics)

        if DEBUG_INFO:
            for camera in self.cameras.values():
                logger.info(camera)

        # cameras pairs
        self.reference_camera = reference_camera
        for cam1, cam2 in pairs:
            self.camera_pairs[(cam1, cam2)] = StereoPair(self.cameras[cam1], self.cameras[cam2])

        if DEBUG_INFO:
            for pair in self.camera_pairs.values():
                logger.info(pair)

    def remap_images(self, multiviews):
        rect_imgs = {}
        view_imgs = {}
        for cam, view in multiviews.items():
            if isinstance(view, str):
                assert osp.exists(view), f'not exist image path: {view}'
                view = cv2.imread(view)
            view_imgs[cam] = view
        for (cam1, cam2), cam_pair in self.camera_pairs.items():
            rect_img1 = cv2.remap(view_imgs[cam1], *cam_pair.get_rect_map(pos=StereoPos.L), cv2.INTER_LANCZOS4)
            rect_img2 = cv2.remap(view_imgs[cam2], *cam_pair.get_rect_map(pos=StereoPos.R), cv2.INTER_LANCZOS4)
            rect_imgs[(cam1, cam2)] = (rect_img1, rect_img2)
        return rect_imgs


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    curdir = osp.abspath(osp.dirname(__file__))
    assets = f'{curdir}/../../../asset'

    mcs = MultiCameraSystem()
    camera_pairs = [('cam1', 'cam2'), ('cam2', 'cam3'), ('cam4', 'cam2')]
    mcs.load_and_init(f'{assets}/calibration_result.yaml', camera_pairs, 'cam1')

    images = {cam:f'{assets}/{cam}/001.png'.format(cam=cam) for cam in mcs.cameras.keys()}
    for (cam1, cam2), cam_pair in mcs.camera_pairs.items():
        disparity = cam_pair.stereo_disparity(images['cam1'], images['cam2'])
        plt.fgure()
        plt.imshow(disparity, cmap='gray')
        plt.title(f'{cam1}, {cam2}')
    rect_images = mcs.remap_images(images)
    for (cam1, cam2), (rect_img1, rect_img2) in rect_images.items():
        plt.figure()
        tmp_img = np.hstack((rect_img1, rect_img2))
        tmp_img[0::100, :, 1] = 255
        plt.imshow(tmp_img)
        plt.title(f'{cam1}, {cam2}')
    plt.show()
