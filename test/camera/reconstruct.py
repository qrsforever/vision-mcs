#!/usr/bin/python3
# -*- coding: utf-8 -*-

from vmcs.core.mcs import MultiCameraSystem
import os

if __name__ == "__main__":

    images_root = 'out'
    images = sorted(list(os.listdir(f'{images_root}/cam1')))
    test_image = images[-6]
    mcs = MultiCameraSystem()
    camera_pairs = [('cam1', 'cam3'), ('cam2', 'cam3'), ('cam4', 'cam3')]
    # mcs.load_and_init(f'{images_root}/result2.yaml', camera_pairs, 'cam3')
    mcs.load_and_init(f'{images_root}/calibration_result.yaml', camera_pairs, 'cam3')

    images = {cam: '%s/%s/%s' % (images_root, cam, test_image) for cam in mcs.cameras.keys()}
    mcs.reconstruct_points_3d(images, draw=True)
