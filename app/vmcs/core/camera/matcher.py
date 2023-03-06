#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file matcher.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-02-24 21:18


import cv2
import numpy as np
# import open3d as o3d


class StereoMatcherSGBM(cv2.StereoSGBM):
    def __init__(self):
        window_size = 11
        min_disp = 0
        num_disp = 320 - min_disp
        self.matcher = cv2.StereoSGBM.create(
                minDisparity=min_disp,
                numDisparities=num_disp,
                uniquenessRatio=5,
                speckleRange=5,
                disp12MaxDiff=1,
                P1=8 * 2 * window_size**2,
                P2=32 * 2 * window_size**2)

    def match(self, img1, img2):
        disparity = self.matcher.compute(img1, img2).astype(np.float32) / 16.0
        return disparity

    def reconstruct(self, img_disp0, img_rect0, Q, P=None):
        xyz = cv2.reprojectImageTo3D(img_disp0, Q)

        mask_depth = (xyz[:, :, 2] < 5.0) & (xyz[:, :, 2] > 0.1)
        mask_brght = (img_rect0[:, :, 0] > 30) & (img_rect0[:, :, 0] < 250)

        xyz_linear = xyz.reshape((-1, 3))
        # TODO
        # colors_linear = img_rect0.reshape((-1, 3))
        # mask_linear = (mask_brght & mask_depth).flatten()

        if P is not None:
            xyz_linear = (P.r @ xyz_linear.T).T + P.t

        return None