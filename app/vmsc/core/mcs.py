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

from vmsc.utils.logger import EasyLoggerMP as logger
from vmsc.core.camera import CameraParam, CameraPair


class MultiCameraSystem(object):
    '''
    '''

    def __init__(self):
        self.cameras = {}
        self.camera_pairs = {}
        self.reference_camera = ''

    def load_and_init(self, yaml_path, pairs):
        with open(yaml_path, 'r') as f:
            self.calibration_parameters = yaml.load(f, Loader=yaml.FullLoader)

        # parse cameras
        for cam, params in self.calibration_parameters['sensors'].items():
            extrinsics = params['extrinsics']
            intrinsics = params['intrinsics']
            self.cameras[cam] = CameraParam(cam, intrinsics, extrinsics)

        for camera in self.cameras.values():
            logger.info(camera)

        # cameras pairs
        cams = []
        for cam1, cam2 in pairs:
            self.camera_pairs[(cam1, cam2)] = CameraPair(self.cameras[cam1], self.cameras[cam2])
            if self.reference_camera == '':
                if len(cams) > 0:
                    self.reference_camera = cam1 if cam1 in cams else cam2
                    logger.info('reference_camera: %s' % self.reference_camera)
                cams.extend([cam1, cam2])

        for pair in self.camera_pairs.values():
            logger.info(pair)

    def remap_images(self, multiviews):
        rect_imgs = {}
        for (cam1, cam2), cam_pair in self.camera_pairs.items():
            print(cam1, cam2)
            rect_img1 = cv2.remap(multiviews[cam1], *cam_pair.rect_map(pos=1), cv2.INTER_LANCZOS4)
            rect_img2 = cv2.remap(multiviews[cam2], *cam_pair.rect_map(pos=2), cv2.INTER_LANCZOS4)
            rect_imgs[(cam1, cam2)] = (rect_img1, rect_img2)
        return rect_imgs


if __name__ == "__main__":
    import os
    import time
    import matplotlib.pyplot as plt

    curdir = os.path.abspath(os.path.dirname(__file__))
    assets = f'{curdir}/../../../asset'

    mcs = MultiCameraSystem()
    camera_pairs = [('cam1', 'cam2'), ('cam2', 'cam3'), ('cam4', 'cam2')]
    mcs.load_and_init(f'{assets}/calibration_result.yaml', camera_pairs)

    multiview_images = {cam:cv2.imread(f'{assets}/{cam}/001.png'.format(cam=cam)) for cam in mcs.cameras.keys()}
    rect_images = mcs.remap_images(multiview_images)
    for (cam1, cam2), (rect_img1, rect_img2) in rect_images.items():
        plt.figure()
        tmp_img = np.hstack((rect_img1, rect_img2))
        tmp_img[0::100, :, 1] = 255
        plt.imshow(tmp_img)
        plt.title(f'{cam1}, {cam2}')
    plt.show()

    time.sleep(1)
