#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file mcs.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-01-09 22:29

import yaml

from vmsc.utils.logger import EasyLoggerMP as logger
from vmsc.core.camera import Camera


class MultiCameraSystem(object):
    '''
    '''

    def __init__(self):
        self.cameras = {}

    def load_and_init(self, yaml_path, pairs):
        with open(yaml_path, "r") as f:
            self.calibration_parameters = yaml.load(f, Loader=yaml.FullLoader)
        # logger.info(self.calibration_parameters)

        # parse cameras
        for cam, params in self.calibration_parameters["sensors"].items():
            extrinsics = params['extrinsics']
            intrinsics = params['intrinsics']
            self.cameras[cam] = Camera(cam, intrinsics, extrinsics)
            # self.cameras[cam] = {
            #         'type': intrinsics['type'],
            #         'image_size': intrinsics['image_size']}

            for key in intrinsics['parameters']:
                print(key)

        # elif cam1_parameters['intrinsics']['type'] == 'KannalaBrandt' and cam2_parameters['intrinsics']['type'] == 'KannalaBrandt':
        # image_size = cam1_intrinsics['image_size']
        # cam1_camera_matrix = np.array([[cam1_intrinsics['fx'], 0, cam1_intrinsics['cx']],
        #                                [0, cam1_intrinsics['fy'], cam1_intrinsics['cy']],
        #                                [0, 0, 1]])


if __name__ == "__main__":
    import os
    import time

    curdir = os.path.abspath(os.path.dirname(__file__))

    mcs = MultiCameraSystem()
    camera_pairs = [("cam1", "cam2"), ("cam2", "cam3"), ("cam4", "cam2")]
    mcs.load_and_init(f'{curdir}/../../../asset/calibration_result.yaml', camera_pairs)

    time.sleep(1)
